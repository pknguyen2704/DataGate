import argparse
import logging
from datetime import datetime, timedelta
from time import perf_counter

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, to_timestamp


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "ingest_source_to_bronze"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest source DB data into bronze Iceberg table by date_hour window"
    )

    parser.add_argument("--source_db_user", required=True)
    parser.add_argument("--source_db_password", required=True)

    parser.add_argument(
        "--source_table",
        required=True,
        help="Source table in source DB, example: public.yellow_tripdata",
    )

    parser.add_argument(
        "--target_table",
        required=True,
        help="Target Iceberg table, example: bronze.yellow_tripdata",
    )

    parser.add_argument(
        "--processing_date_hour",
        required=True,
        help="Processing batch hour, format: yyyy-MM-dd HH:mm:ss",
    )

    return parser.parse_args()


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .getOrCreate()
    )


def normalize_datetime_string(value):
    if value is None:
        raise ValueError("processing_date_hour must not be None.")

    value = str(value).strip().replace("T", " ")

    if value == "":
        raise ValueError("processing_date_hour must not be empty.")

    dt = datetime.fromisoformat(value)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_identifier_part(value, field_name):
    value = str(value).strip()

    if value == "":
        raise ValueError(f"{field_name} must not be empty.")

    for char in value:
        if not (char.isalnum() or char == "_"):
            raise ValueError(
                f"Invalid {field_name}: {value}. "
                "Only letters, numbers, and underscore (_) are allowed."
            )

    return value


def validate_table_identifier(table_name, field_name):
    """
    Cho phép:
    - schema.table
    - catalog.schema.table
    """
    table_name = str(table_name).strip()
    parts = table_name.split(".")

    if len(parts) not in (2, 3):
        raise ValueError(
            f"Invalid {field_name}: {table_name}. "
            "Expected format: schema.table or catalog.schema.table."
        )

    for part in parts:
        validate_identifier_part(part, field_name)

    return table_name


def get_spark_conf(spark, key, default_value=None, required=False):
    value = spark.conf.get(key, default_value)

    if required and not value:
        raise ValueError(
            f"Missing Spark config: {key}. "
            "Please define it in SparkSubmitOperator conf."
        )

    return value


def build_date_hour_window(processing_date_hour):
    """
    Tính khung date_hour cần ingest.

    Quy ước:
    - processing_date_hour = 2025-01-20 12:00:00
      -> lấy date_hour từ 2025-01-20 00:00:00 đến trước 2025-01-20 12:00:00

    - processing_date_hour = 2025-01-21 00:00:00
      -> lấy date_hour từ 2025-01-20 12:00:00 đến trước 2025-01-21 00:00:00
    """
    end_dt = datetime.fromisoformat(processing_date_hour)
    start_dt = end_dt - timedelta(hours=12)

    return (
        start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        end_dt.strftime("%Y-%m-%d %H:%M:%S"),
    )


def build_source_query(source_table, start_date_hour, end_date_hour):
    """
    Source table cần có sẵn cột date_hour.

    Job chỉ lấy dữ liệu trong khung date_hour cần xử lý.
    """
    source_table = validate_table_identifier(
        source_table,
        "source_table",
    )

    return f"""
        (
            SELECT *
            FROM {source_table}
            WHERE date_hour >= TIMESTAMP '{start_date_hour}'
              AND date_hour <  TIMESTAMP '{end_date_hour}'
        ) AS source_batch
    """


def resolve_target_table(target_table, iceberg_catalog):
    """
    Nếu target_table = bronze.yellow_tripdata
    -> iceberg.bronze.yellow_tripdata

    Nếu target_table = iceberg.bronze.yellow_tripdata
    -> giữ nguyên.
    """
    target_table = validate_table_identifier(
        target_table,
        "target_table",
    )

    parts = target_table.split(".")

    if len(parts) == 3:
        return target_table

    return f"{iceberg_catalog}.{target_table}"


def read_source_batch(
    spark,
    source_jdbc_url,
    source_jdbc_driver,
    source_db_user,
    source_db_password,
    source_table,
    processing_date_hour,
) -> DataFrame:
    start_date_hour, end_date_hour = build_date_hour_window(
        processing_date_hour
    )

    source_query = build_source_query(
        source_table=source_table,
        start_date_hour=start_date_hour,
        end_date_hour=end_date_hour,
    )

    logger.info(
        "Reading source table=%s | date_hour >= %s and < %s",
        source_table,
        start_date_hour,
        end_date_hour,
    )

    return (
        spark.read
        .format("jdbc")
        .option("url", source_jdbc_url)
        .option("dbtable", source_query)
        .option("user", source_db_user)
        .option("password", source_db_password)
        .option("driver", source_jdbc_driver)
        .load()
    )


def add_processing_date_hour(df, processing_date_hour) -> DataFrame:
    return df.withColumn(
        "processing_date_hour",
        to_timestamp(lit(processing_date_hour)),
    )


def write_to_iceberg(df, target_table):
    """
    overwritePartitions giúp job idempotent.

    Nếu Airflow retry/rerun cùng processing_date_hour,
    partition cũ sẽ được ghi đè.
    """
    (
        df.writeTo(target_table)
        .overwritePartitions()
    )


def main():
    start_time = perf_counter()

    args = parse_args()
    args.processing_date_hour = normalize_datetime_string(
        args.processing_date_hour
    )

    spark = build_spark_session()

    try:
        source_jdbc_url = get_spark_conf(
            spark=spark,
            key="datagate.source.jdbc.url",
            required=True,
        )

        source_jdbc_driver = get_spark_conf(
            spark=spark,
            key="datagate.source.jdbc.driver",
            default_value="org.postgresql.Driver",
        )

        iceberg_catalog = get_spark_conf(
            spark=spark,
            key="datagate.iceberg.catalog",
            default_value="iceberg",
        )

        target_table = resolve_target_table(
            target_table=args.target_table,
            iceberg_catalog=iceberg_catalog,
        )

        source_df = read_source_batch(
            spark=spark,
            source_jdbc_url=source_jdbc_url,
            source_jdbc_driver=source_jdbc_driver,
            source_db_user=args.source_db_user,
            source_db_password=args.source_db_password,
            source_table=args.source_table,
            processing_date_hour=args.processing_date_hour,
        )

        bronze_df = add_processing_date_hour(
            df=source_df,
            processing_date_hour=args.processing_date_hour,
        )

        logger.info(
            "Writing bronze table=%s | processing_date_hour=%s",
            target_table,
            args.processing_date_hour,
        )

        write_to_iceberg(
            df=bronze_df,
            target_table=target_table,
        )

        total_seconds = perf_counter() - start_time

        logger.info(
            "[Job Completed] %s finished in %.3f seconds",
            JOB_NAME,
            total_seconds,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()