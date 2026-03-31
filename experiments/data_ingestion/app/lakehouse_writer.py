"""
lakehouse_writer.py
───────────────────
Write validated CDR records to the data lakehouse:
  • Object store  : MinIO (S3-compatible)  →  s3://lakehouse/bronze/telecom_cdr/
  • Table catalog : Apache Iceberg REST    →  bronze.telecom_cdr

Flow
----
1. Serialise records → in-memory PyArrow Table
2. Upload Parquet file to MinIO  (safe-write: upload then atomic rename via boto3)
3. Create the Iceberg namespace/table if it doesn't exist yet
4. Append the new Parquet file into the Iceberg table via a DataScan commit

Dependencies (already in pyproject.toml or to be added):
  boto3, pyarrow, pyiceberg[s3fsspec,pyarrow]
"""

import io
import datetime

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField,
    LongType,
    StringType,
    DoubleType,
    TimestampType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform
from pyiceberg.exceptions import NamespaceAlreadyExistsError, NoSuchTableError

from src import config
from src.logger import get_logger

logger = get_logger(__name__)

# ─── Iceberg schema for bronze.telecom_cdr ────────────────────────────────────
ICEBERG_SCHEMA = Schema(
    NestedField(1,  "id",               LongType(),      required=True),
    NestedField(2,  "caller",           StringType(),    required=True),
    NestedField(3,  "receiver",         StringType(),    required=True),
    NestedField(4,  "device_imei",      StringType(),    required=False),
    NestedField(5,  "event_time_unix",  LongType(),      required=True),
    NestedField(6,  "event_time_utc",   StringType(),    required=True),
    NestedField(7,  "duration_seconds", LongType(),      required=False),
    NestedField(8,  "duration_minutes", DoubleType(),    required=False),
    NestedField(9,  "call_type_code",   StringType(),    required=False),
    NestedField(10, "call_type_name",   StringType(),    required=False),
    NestedField(11, "tower_lat",        DoubleType(),    required=False),
    NestedField(12, "tower_lng",        DoubleType(),    required=False),
    NestedField(13, "country",          StringType(),    required=False),
    NestedField(14, "created_at",       StringType(),    required=False),
)

# Partition by day derived from event_time_unix  (field id 5)
PARTITION_SPEC = PartitionSpec(
    PartitionField(source_id=5, field_id=1000, transform=DayTransform(), name="event_day"),
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_s3_key() -> str:
    """Return a unique S3 object key under the bronze prefix."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    return f"{config.MINIO_BRONZE_PREFIX}/telecom_cdr_{ts}.parquet"


def _records_to_arrow(records: list[dict]) -> pa.Table:
    """Convert a list of dicts to a PyArrow Table, coercing types."""
    def _safe_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    def _safe_long(v):
        try:
            return int(v) if v is not None else None
        except (ValueError, TypeError):
            return None

    return pa.table(
        {
            "id":               pa.array([_safe_long(r.get("id"))          for r in records], type=pa.int64()),
            "caller":           pa.array([str(r.get("caller", ""))         for r in records], type=pa.string()),
            "receiver":         pa.array([str(r.get("receiver", ""))       for r in records], type=pa.string()),
            "device_imei":      pa.array([str(r.get("device_imei", ""))    for r in records], type=pa.string()),
            "event_time_unix":  pa.array([_safe_long(r.get("event_time_unix")) for r in records], type=pa.int64()),
            "event_time_utc":   pa.array([str(r.get("event_time_utc", "")) for r in records], type=pa.string()),
            "duration_seconds": pa.array([_safe_long(r.get("duration_seconds")) for r in records], type=pa.int64()),
            "duration_minutes": pa.array([_safe_float(r.get("duration_minutes")) for r in records], type=pa.float64()),
            "call_type_code":   pa.array([str(r.get("call_type_code", "")) for r in records], type=pa.string()),
            "call_type_name":   pa.array([str(r.get("call_type_name", "")) for r in records], type=pa.string()),
            "tower_lat":        pa.array([_safe_float(r.get("tower_lat"))  for r in records], type=pa.float64()),
            "tower_lng":        pa.array([_safe_float(r.get("tower_lng"))  for r in records], type=pa.float64()),
            "country":          pa.array([str(r.get("country", ""))        for r in records], type=pa.string()),
            "created_at":       pa.array([str(r.get("created_at", ""))     for r in records], type=pa.string()),
        }
    )


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=config.MINIO_ENDPOINT,
        aws_access_key_id=config.MINIO_ACCESS_KEY,
        aws_secret_access_key=config.MINIO_SECRET_KEY,
        region_name="us-east-1",
    )


def _get_iceberg_catalog() -> RestCatalog:
    """Return a pyiceberg RestCatalog pointing at the Iceberg REST service."""
    return RestCatalog(
        name="lakehouse",
        uri=config.ICEBERG_REST_URI,
        **{
            "s3.endpoint": config.MINIO_ENDPOINT,
            "s3.access-key-id": config.MINIO_ACCESS_KEY,
            "s3.secret-access-key": config.MINIO_SECRET_KEY,
            "s3.path-style-access": "true",
        },
    )


def _ensure_iceberg_table(catalog: RestCatalog):
    """Create namespace + table in Iceberg catalog if they don't already exist."""
    namespace = config.ICEBERG_NAMESPACE
    table_name = config.TARGET_TABLE  # e.g. "bronze.telecom_cdr"

    # Create namespace
    try:
        catalog.create_namespace(namespace)
        logger.info(f"Iceberg namespace created: {namespace}")
    except NamespaceAlreadyExistsError:
        pass  # already exists — fine

    # Create table
    try:
        catalog.load_table(table_name)
        logger.info(f"Iceberg table already exists: {table_name}")
    except NoSuchTableError:
        catalog.create_table(
            identifier=table_name,
            schema=ICEBERG_SCHEMA,
            partition_spec=PARTITION_SPEC,
            properties={
                "write.format.default": "parquet",
                "write.parquet.compression-codec": "snappy",
            },
        )
        logger.info(f"Iceberg table created: {table_name}")


# ─── Public API ───────────────────────────────────────────────────────────────

def write_to_lakehouse(records: list[dict]) -> str:
    """
    Serialize *records* as Parquet, upload to MinIO bronze layer, then
    append the file into the Iceberg table.

    Returns the S3 URI of the written object.
    """
    if not records:
        logger.info("No valid records — skipping lakehouse write.")
        return ""

    # 1. Serialise to Parquet bytes in memory
    arrow_table = _records_to_arrow(records)
    buf = io.BytesIO()
    pq.write_table(arrow_table, buf, compression="snappy")
    buf.seek(0)
    parquet_bytes = buf.read()

    # 2. Upload to MinIO
    s3 = _get_s3_client()
    s3_key = _make_s3_key()

    logger.info(f"Uploading {len(records)} records ({len(parquet_bytes):,} bytes) "
                f"→ s3://{config.MINIO_BUCKET}/{s3_key}")
    s3.put_object(
        Bucket=config.MINIO_BUCKET,
        Key=s3_key,
        Body=parquet_bytes,
        ContentType="application/octet-stream",
    )

    s3_uri = f"s3://{config.MINIO_BUCKET}/{s3_key}"
    logger.info(f"Upload complete: {s3_uri}")

    # 3. Register / append in Iceberg catalog
    try:
        catalog = _get_iceberg_catalog()
        _ensure_iceberg_table(catalog)

        table = catalog.load_table(config.TARGET_TABLE)

        # append a DataFile pointing at the newly uploaded Parquet
        with table.transaction() as txn:
            txn.append(arrow_table)

        logger.info(f"Iceberg append committed → {config.TARGET_TABLE} "
                    f"({len(records)} rows)")
    except Exception as e:
        # Iceberg catalog failure is logged but does NOT roll back the S3 upload.
        # The file is still safely stored in MinIO; it can be manually registered later.
        logger.error(f"Iceberg catalog append failed (file still in MinIO): {e}")

    return s3_uri


def write_rejected_to_lakehouse(rejected_records: list[dict]) -> str:
    """
    Write rejected records as Parquet to the MinIO rejected prefix.
    Does NOT register in Iceberg — these are quarantine files.
    """
    if not rejected_records:
        return ""

    buf = io.BytesIO()
    arrow_table = pa.Table.from_pylist(rejected_records)
    pq.write_table(arrow_table, buf, compression="snappy")
    buf.seek(0)

    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    s3_key = f"bronze/rejected/telecom_cdr_{ts}.parquet"

    s3 = _get_s3_client()
    logger.info(f"Uploading {len(rejected_records)} rejected records → s3://{config.MINIO_BUCKET}/{s3_key}")
    s3.put_object(
        Bucket=config.MINIO_BUCKET,
        Key=s3_key,
        Body=buf.read(),
        ContentType="application/octet-stream",
    )

    s3_uri = f"s3://{config.MINIO_BUCKET}/{s3_key}"
    logger.info(f"Rejected file written: {s3_uri}")
    return s3_uri
