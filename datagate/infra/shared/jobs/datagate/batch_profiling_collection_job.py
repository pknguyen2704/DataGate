import argparse
import logging
import os
import uuid
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.analyzers import (
    AnalysisRunner,
    AnalyzerContext,
    ApproxCountDistinct,
    Completeness,
    Distinctness,
    MaxLength,
    Maximum,
    Mean,
    MinLength,
    Minimum,
    StandardDeviation,
)

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ByteType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    StringType,
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "batch_profiling_collection_job"

SPARK_DRIVER_CORES = "2"
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_INSTANCES = "2"
SPARK_EXECUTOR_CORES = "6"
SPARK_EXECUTOR_MEMORY = "10g"
SPARK_SQL_SHUFFLE_PARTITIONS = "24"
SPARK_DEFAULT_PARALLELISM = "24"
SPARK_TIMEZONE = "Asia/Ho_Chi_Minh"

NUMERIC_TYPES = (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect profiling metrics from Iceberg tables and save to DataGate DB"
    )

    parser.add_argument(
        "--datagate_db_conn_id",
        default="datagate_db_default",
        help="Airflow Postgres connection id for DataGate DB",
    )

    parser.add_argument("--connection_name", required=True)
    parser.add_argument("--schema_name", required=True)
    parser.add_argument("--processing_date_hour", required=True)

    return parser.parse_args()

def validate_name(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value

def normalize_processing_date_hour(processing_date_hour):
    if processing_date_hour is None:
        raise ValueError("processing_date_hour must not be None.")

    value = str(processing_date_hour).strip().replace("T", " ")

    if value == "":
        raise ValueError("processing_date_hour must not be empty.")

    dt = datetime.fromisoformat(value)

    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_connection_config(pg_hook, connection_name):
    if connection_name is None:
        raise ValueError("connection_name must not be None.")

    connection_name = str(connection_name).strip()

    if connection_name == "":
        raise ValueError("connection_name must not be empty.")

    row = pg_hook.get_first(
        """
        SELECT
            connection_name,
            iceberg_rest_url,
            iceberg_warehouse,
            iceberg_catalog_name,
            minio_endpoint_url,
            minio_access_key,
            minio_secret_key
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,),
    )

    if row is None:
        raise ValueError(
            f"No active connection found with name={connection_name}"
        )

    return {
        "connection_name": row[0],
        "iceberg_rest_url": row[1],
        "iceberg_warehouse": row[2],
        "iceberg_catalog_name": validate_name(row[3], "iceberg_catalog_name"),
        "minio_endpoint_url": row[4],
        "minio_access_key": row[5],
        "minio_secret_key": row[6],
    }

def get_active_tables(pg_hook, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT
            id,
            table_name
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(catalog_name, schema_name),
    )

    tables = []

    for table_id, table_name in rows:
        table_name = validate_name(table_name, "table_name")

        tables.append(
            {
                "table_id": str(table_id),
                "table_name": table_name,
                "full_table_name": f"{catalog_name}.{schema_name}.{table_name}",
            }
        )

    return tables

def save_profiling_rows(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO batch_table_profiling (
            id,
            table_id,
            column_name,
            data_type,
            completeness,
            mean,
            standard_deviation,
            minimum,
            maximum,
            min_length,
            max_length,
            distinctness,
            approx_count_distinct,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (table_id, processing_date_hour, column_name)
        DO UPDATE SET
            data_type = EXCLUDED.data_type,
            completeness = EXCLUDED.completeness,
            mean = EXCLUDED.mean,
            standard_deviation = EXCLUDED.standard_deviation,
            minimum = EXCLUDED.minimum,
            maximum = EXCLUDED.maximum,
            min_length = EXCLUDED.min_length,
            max_length = EXCLUDED.max_length,
            distinctness = EXCLUDED.distinctness,
            approx_count_distinct = EXCLUDED.approx_count_distinct,
            updated_at = NOW()
    """

    values = [
        (
            str(uuid.uuid4()),
            row["table_id"],
            row["column_name"],
            row["data_type"],
            row["completeness"],
            row["mean"],
            row["standard_deviation"],
            row["minimum"],
            row["maximum"],
            row["min_length"],
            row["max_length"],
            row["distinctness"],
            row["approx_count_distinct"],
            row["processing_date_hour"],
        )
        for row in rows
    ]

    conn = pg_hook.get_conn()

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
        )

    conn.commit()

def create_spark_session(connection_config):
    catalog_name = connection_config["iceberg_catalog_name"]

    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .config("spark.driver.cores", SPARK_DRIVER_CORES)
        .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .config("spark.executor.instances", SPARK_EXECUTOR_INSTANCES)
        .config("spark.executor.cores", SPARK_EXECUTOR_CORES)
        .config("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        .config("spark.sql.session.timeZone", SPARK_TIMEZONE)
        .config("spark.sql.shuffle.partitions", SPARK_SQL_SHUFFLE_PARTITIONS)
        .config("spark.default.parallelism", SPARK_DEFAULT_PARALLELISM)
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.sql.extensions","org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config(f"spark.sql.catalog.{catalog_name}","org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{catalog_name}.type","rest")
        .config(f"spark.sql.catalog.{catalog_name}.uri",connection_config["iceberg_rest_url"])
        .config(f"spark.sql.catalog.{catalog_name}.io-impl","org.apache.iceberg.aws.s3.S3FileIO")
        .config(f"spark.sql.catalog.{catalog_name}.warehouse", connection_config["iceberg_warehouse"])
        .config(f"spark.sql.catalog.{catalog_name}.s3.endpoint",connection_config["minio_endpoint_url"])
        .config(f"spark.sql.catalog.{catalog_name}.s3.access-key-id",connection_config["minio_access_key"])
        .config(f"spark.sql.catalog.{catalog_name}.s3.secret-access-key",connection_config["minio_secret_key"])
        .config(f"spark.sql.catalog.{catalog_name}.s3.path-style-access","true")
        .config(f"spark.sql.catalog.{catalog_name}.s3.region", "us-east-1")
        .getOrCreate()
    )

def add_analyzers_for_column(runner, column_name, data_type):
    runner = (
        runner
        .addAnalyzer(Completeness(column_name))
        .addAnalyzer(ApproxCountDistinct(column_name))
        .addAnalyzer(Distinctness(column_name))
    )

    if isinstance(data_type, NUMERIC_TYPES):
        runner = (
            runner
            .addAnalyzer(Minimum(column_name))
            .addAnalyzer(Maximum(column_name))
            .addAnalyzer(Mean(column_name))
            .addAnalyzer(StandardDeviation(column_name))
        )

    if isinstance(data_type, StringType):
        runner = (
            runner
            .addAnalyzer(MinLength(column_name))
            .addAnalyzer(MaxLength(column_name))
        )

    return runner

def run_profile(spark, df):
    runner = AnalysisRunner(spark).onData(df)

    for field in df.schema.fields:
        runner = add_analyzers_for_column(
            runner=runner,
            column_name=field.name,
            data_type=field.dataType,
        )

    result = runner.run()
    return AnalyzerContext.successMetricsAsDataFrame(spark, result)

def safe_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except Exception:
        return None

def metric_to_field_name(metric_name):
    mapping = {
        "Completeness": "completeness",
        "Mean": "mean",
        "StandardDeviation": "standard_deviation",
        "Minimum": "minimum",
        "Maximum": "maximum",
        "MinLength": "min_length",
        "MinimumLength": "min_length",
        "MaxLength": "max_length",
        "MaximumLength": "max_length",
        "Distinctness": "distinctness",
        "ApproxCountDistinct": "approx_count_distinct",
    }

    return mapping.get(metric_name)

def build_profiling_rows(table_info, df, metrics_df, processing_date_hour):
    metric_map = {}

    for row in metrics_df.collect():
        data = row.asDict()

        column_name = data.get("instance")
        metric_name = data.get("name")
        metric_value = safe_float(data.get("value"))

        field_name = metric_to_field_name(metric_name)

        if not column_name or not field_name:
            continue

        metric_map[(column_name, field_name)] = metric_value

    rows = []

    for field in df.schema.fields:
        column_name = field.name

        rows.append(
            {
                "table_id": table_info["table_id"],
                "column_name": column_name,
                "data_type": field.dataType.simpleString(),
                "completeness": metric_map.get((column_name, "completeness")),
                "mean": metric_map.get((column_name, "mean")),
                "standard_deviation": metric_map.get((column_name, "standard_deviation")),
                "minimum": metric_map.get((column_name, "minimum")),
                "maximum": metric_map.get((column_name, "maximum")),
                "min_length": metric_map.get((column_name, "min_length")),
                "max_length": metric_map.get((column_name, "max_length")),
                "distinctness": metric_map.get((column_name, "distinctness")),
                "approx_count_distinct": metric_map.get((column_name, "approx_count_distinct")),
                "processing_date_hour": processing_date_hour,
            }
        )

    return rows

def read_batch_table(spark, full_table_name, processing_date_hour):
    sql = f"""
        SELECT *
        FROM {full_table_name}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """
    return spark.sql(sql)

def collect_one_table_profiling(spark, pg_hook, table_info, processing_date_hour):
    full_table_name = table_info["full_table_name"]

    logger.info(
        "Profiling table=%s | processing_date_hour=%s",
        full_table_name,
        processing_date_hour,
    )

    batch_df = read_batch_table(
        spark=spark,
        full_table_name=full_table_name,
        processing_date_hour=processing_date_hour,
    )

    metrics_df = run_profile(
        spark=spark,
        df=batch_df,
    )

    profiling_rows = build_profiling_rows(
        table_info=table_info,
        df=batch_df,
        metrics_df=metrics_df,
        processing_date_hour=processing_date_hour,
    )

    save_profiling_rows(
        pg_hook=pg_hook,
        rows=profiling_rows,
    )

    logger.info(
        "Saved profiling rows | table=%s | rows=%s",
        full_table_name,
        len(profiling_rows),
    )


def main():
    args = parse_args()
    schema_name = validate_name(args.schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(
        args.processing_date_hour
    )

    pg_hook = PostgresHook(
        postgres_conn_id=args.datagate_db_conn_id
    )

    connection_config = get_connection_config(
        pg_hook=pg_hook,
        connection_name=args.connection_name,
    )

    catalog_name = connection_config["iceberg_catalog_name"]

    active_tables = get_active_tables(
        pg_hook=pg_hook,
        catalog_name=catalog_name,
        schema_name=schema_name,
    )

    if not active_tables:
        logger.warning(
            "No active tables found | connection=%s | catalog=%s | schema=%s",
            connection_config["connection_name"],
            catalog_name,
            schema_name,
        )
        return

    spark = create_spark_session(connection_config)

    try:
        logger.info(
            "Found %s active table(s) | connection=%s | catalog=%s | schema=%s",
            len(active_tables),
            connection_config["connection_name"],
            catalog_name,
            schema_name,
        )

        for table_info in active_tables:
            collect_one_table_profiling(
                spark=spark,
                pg_hook=pg_hook,
                table_info=table_info,
                processing_date_hour=processing_date_hour,
            )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()