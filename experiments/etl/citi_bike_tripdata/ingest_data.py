import argparse
import gc
import logging
import os
import sys
from contextlib import suppress
from datetime import datetime, timedelta
from time import perf_counter

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, to_timestamp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOB_NAME = "citi_bike_ingest_data"
SOURCE_SCHEMA = "public"
SOURCE_TABLE = "citi_bike_tripdata"
TARGET_SCHEMA = "bronze"
TARGET_TABLE = "citi_bike_tripdata"
SOURCE_JDBC_URL = "jdbc:postgresql://datasource_postgres:5432/postgres"
SOURCE_JDBC_DRIVER = "org.postgresql.Driver"
SOURCE_DB_USER = "admin"
SOURCE_DB_PASSWORD = "postgrespassword"

ICEBERG_CATALOG = "iceberg"
ICEBERG_REST_URI = "http://iceberg-rest:8181"
ICEBERG_WAREHOUSE = "s3://lakehouse/"
MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "miniopassword"

SPARK_DRIVER_CORES = "2"
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_INSTANCES = "2"
SPARK_EXECUTOR_CORES = "6"
SPARK_EXECUTOR_MEMORY = "10g"
SPARK_SQL_SHUFFLE_PARTITIONS = "24"
SPARK_DEFAULT_PARALLELISM = "24"
SPARK_TIMEZONE = "Asia/Ho_Chi_Minh"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processing_date_hour", required=True)
    return parser.parse_args()


def normalize_datetime(value):
    value = str(value or "").strip().replace("T", " ")
    if not value:
        raise ValueError("processing_date_hour must not be empty.")
    return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")


def validate_table_name(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    if not value.replace("_", "").isalnum():
        raise ValueError(f"Invalid {field_name}: {value}")
    return value


def create_spark_session():
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
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.type", "rest")
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.uri", ICEBERG_REST_URI)
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.warehouse", ICEBERG_WAREHOUSE)
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.s3.endpoint", MINIO_ENDPOINT)
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.s3.access-key-id", MINIO_ACCESS_KEY)
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.s3.secret-access-key", MINIO_SECRET_KEY)
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.s3.path-style-access", "true")
        .config(f"spark.sql.catalog.{ICEBERG_CATALOG}.s3.region", "us-east-1")
        .getOrCreate()
    )


def build_date_hour_window(processing_date_hour):
    end_dt = datetime.fromisoformat(processing_date_hour)
    start_dt = end_dt - timedelta(hours=12)
    return start_dt.strftime("%Y-%m-%d %H:%M:%S"), end_dt.strftime("%Y-%m-%d %H:%M:%S")


def build_source_query(source_table, processing_date_hour):
    start_hour, end_hour = build_date_hour_window(processing_date_hour)
    return f"""
        (
            SELECT *
            FROM {SOURCE_SCHEMA}.{source_table}
            WHERE date_hour >= TIMESTAMP '{start_hour}'
              AND date_hour <  TIMESTAMP '{end_hour}'
        ) AS source_batch
    """


def read_source_batch(spark, source_table, processing_date_hour):
    source_query = build_source_query(source_table, processing_date_hour)
    logger.info("Reading source table=%s.%s | processing_date_hour=%s", SOURCE_SCHEMA, source_table, processing_date_hour)
    return (
        spark.read
        .format("jdbc")
        .option("url", SOURCE_JDBC_URL)
        .option("dbtable", source_query)
        .option("user", SOURCE_DB_USER)
        .option("password", SOURCE_DB_PASSWORD)
        .option("driver", SOURCE_JDBC_DRIVER)
        .load()
    )


def write_to_bronze(df, target_table):
    full_target_table = f"{ICEBERG_CATALOG}.{TARGET_SCHEMA}.{target_table}"
    logger.info("Writing bronze table=%s", full_target_table)
    df.writeTo(full_target_table).overwritePartitions()


def stop_spark_session(spark):
    if spark is None:
        return
    with suppress(Exception):
        spark.catalog.clearCache()
    with suppress(Exception):
        spark.sparkContext.cancelAllJobs()
    with suppress(Exception):
        spark.stop()


def main():
    start = perf_counter()
    args = parse_args()
    source_table = validate_table_name(SOURCE_TABLE, "SOURCE_TABLE")
    target_table = validate_table_name(TARGET_TABLE, "TARGET_TABLE")
    processing_date_hour = normalize_datetime(args.processing_date_hour)
    spark = None

    try:
        spark = create_spark_session()
        source_df = read_source_batch(spark, source_table, processing_date_hour)
        bronze_df = source_df.withColumn("processing_date_hour", to_timestamp(lit(processing_date_hour)))
        write_to_bronze(bronze_df, target_table)
        logger.info("[Job Completed] %s finished in %.3f seconds", JOB_NAME, perf_counter() - start)
        return 0
    except Exception:
        logger.exception("[Job Failed] %s | processing_date_hour=%s", JOB_NAME, processing_date_hour)
        return 1
    finally:
        stop_spark_session(spark)
        gc.collect()


if __name__ == "__main__":
    exit_code = main()
    with suppress(Exception):
        sys.stdout.flush()
    with suppress(Exception):
        sys.stderr.flush()
    logging.shutdown()
    os._exit(exit_code)
