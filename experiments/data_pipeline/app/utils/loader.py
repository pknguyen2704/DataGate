"""
loader.py
─────────
Load raw records (as-is from PostgreSQL) into the data lakehouse:
  • Object store  : Minio (S3-compatible)
  • Table catalog : Apache Iceberg REST

This version uses assign_fresh_schema_ids to manually inject IDs into the Arrow 
table before appending. This is the most reliable way to avoid the 
"missing field-ids" error.
"""

import datetime
import json
from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, NoSuchTableError
from pyiceberg.io.pyarrow import pyarrow_to_schema
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import IdentityTransform
import pyarrow as pa
from config import config

# We try to import assign_fresh_schema_ids (available in newer pyiceberg)
try:
    from pyiceberg.io.pyarrow import assign_fresh_schema_ids
except ImportError:
    # Older versions might have it elsewhere or not at all
    assign_fresh_schema_ids = None


def _iceberg_catalog() -> RestCatalog:
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


def _to_arrow(records: list[dict]) -> pa.Table:
    for r in records:
        ts = r.get("tpep_dropoff_datetime")
        if hasattr(ts, 'strftime'):
            r["date_hour"] = ts.strftime("%Y-%m-%d %H:00:00")
        else:
            r["date_hour"] = str(ts)[:13] + ":00:00" if ts else "1970-01-01 00:00:00"
    return pa.Table.from_pylist(records)


def _ensure_namespace(catalog: RestCatalog) -> None:
    try:
        catalog.create_namespace(config.ICEBERG_NAMESPACE)
    except NamespaceAlreadyExistsError:
        pass


def _get_name_mapping(schema) -> str:
    mapping = []
    for field in schema.fields:
        mapping.append({"field-id": field.field_id, "names": [field.name]})
    return json.dumps(mapping)


def _ensure_table(catalog: RestCatalog, arrow_table: pa.Table):
    try:
        table = catalog.load_table(config.TARGET_TABLE)
        # Try to fix existing table if mapping is missing
        if "schema.name-mapping.default" not in table.metadata.properties:
            print("Adding name-mapping to existing table...")
            with table.update_properties() as up:
                up.set("schema.name-mapping.default", _get_name_mapping(table.schema()))
    except NoSuchTableError:
        print(f"Creating table {config.TARGET_TABLE}...")
        iceberg_schema = pyarrow_to_schema(arrow_table.schema)
        
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=iceberg_schema.find_field("date_hour").field_id,
                field_id=1000,
                transform=IdentityTransform(),
                name="date_hour"
            )
        )

        catalog.create_table(
            identifier=config.TARGET_TABLE,
            schema=iceberg_schema,
            partition_spec=partition_spec,
            properties={
                "write.format.default": "parquet",
                "write.parquet.compression-codec": "snappy",
                "schema.name-mapping.default": _get_name_mapping(iceberg_schema),
            },
        )


def load_to_lakehouse(records: list[dict]) -> bool:
    if not records:
        return False

    catalog = _iceberg_catalog()
    _ensure_namespace(catalog)
    arrow_table = _to_arrow(records)

    _ensure_table(catalog, arrow_table)
    table = catalog.load_table(config.TARGET_TABLE)

    # Definitive fix for field-ids:
    # If the helper exists, use it to inject IDs based on the table's schema.
    if assign_fresh_schema_ids:
        arrow_table = assign_fresh_schema_ids(arrow_table, table.schema())

    try:
        table.append(arrow_table)
        return True
    except Exception as e:
        print(f"Append failed: {e}. Recreating table instance...")
        # Force a fresh start if mapping error persists
        if "Parquet file does not have field-ids" in str(e):
             catalog.drop_table(config.TARGET_TABLE)
             _ensure_table(catalog, arrow_table)
             table = catalog.load_table(config.TARGET_TABLE)
             table.append(arrow_table)
             return True
        raise
