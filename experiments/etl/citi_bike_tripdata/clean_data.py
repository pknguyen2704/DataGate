import argparse
import gc
import logging
import os
import sys
from contextlib import suppress
from datetime import datetime
from functools import reduce
from operator import or_
from time import perf_counter

from pyspark.sql import SparkSession, functions as F


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOB_NAME = "citi_bike_clean_data"
ICEBERG_CATALOG = "iceberg"
SOURCE_SCHEMA = "bronze"
SOURCE_TABLE = "citi_bike_tripdata"
TARGET_SCHEMA = "silver"
TARGET_TABLE = "cleaned_citi_bike_tripdata"
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

COLUMNS = [
    "ride_id", "rideable_type", "started_at", "ended_at",
    "start_station_name", "start_station_id", "end_station_name", "end_station_id",
    "start_lat", "start_lng", "end_lat", "end_lng", "member_casual",
    "date_hour", "processing_date_hour",
]

OUTPUT_COLUMNS = COLUMNS + ["ride_duration_minutes"]
CRITICAL_NOT_NULL = [
    "ride_id", "rideable_type", "started_at", "ended_at",
    "start_lat", "start_lng", "end_lat", "end_lng",
    "member_casual", "date_hour", "processing_date_hour",
]
STRING_COLS = [
    "ride_id", "rideable_type", "start_station_name", "start_station_id",
    "end_station_name", "end_station_id", "member_casual",
]
DOUBLE_COLS = ["start_lat", "start_lng", "end_lat", "end_lng"]
TIME_COLS = ["started_at", "ended_at", "date_hour", "processing_date_hour"]


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
    if not value or not value.replace("_", "").isalnum():
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


def validate_columns(df):
    missing = [col for col in COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def normalize_strings(df):
    for col in STRING_COLS:
        df = df.withColumn(col, F.trim(F.col(col).cast("string")))
        df = df.withColumn(col, F.when(F.col(col).isin("", "nan", "NaN", "NULL", "None"), None).otherwise(F.col(col)))
    return df


def cast_columns(df):
    for col in TIME_COLS:
        df = df.withColumn(col, F.to_timestamp(F.col(col)))
    for col in DOUBLE_COLS:
        df = df.withColumn(col, F.col(col).cast("double"))

    df = normalize_strings(df)
    df = df.withColumn("rideable_type", F.lower(F.col("rideable_type")))
    df = df.withColumn("member_casual", F.lower(F.col("member_casual")))
    return df


def clean_data(df):
    validate_columns(df)
    df = cast_columns(df)
    duration = (F.unix_timestamp("ended_at") - F.unix_timestamp("started_at")) / F.lit(60.0)
    df = df.withColumn("ride_duration_minutes", duration)

    invalid = [
        reduce(or_, [F.col(col).isNull() for col in CRITICAL_NOT_NULL]),
        F.col("ended_at") <= F.col("started_at"),
        ~F.col("rideable_type").isin("classic_bike", "electric_bike", "docked_bike"),
        ~F.col("member_casual").isin("member", "casual"),
        (F.col("ride_duration_minutes") <= 0) | (F.col("ride_duration_minutes") > 1440),
        (F.col("start_lat") < 40.0) | (F.col("start_lat") > 41.5),
        (F.col("end_lat") < 40.0) | (F.col("end_lat") > 41.5),
        (F.col("start_lng") < -75.0) | (F.col("start_lng") > -73.0),
        (F.col("end_lng") < -75.0) | (F.col("end_lng") > -73.0),
    ]

    return df.filter(~reduce(or_, invalid)).dropDuplicates(["ride_id"]).select(OUTPUT_COLUMNS)


def read_bronze_batch(spark, source_table, processing_date_hour):
    full_table = f"{ICEBERG_CATALOG}.{SOURCE_SCHEMA}.{source_table}"
    logger.info("Reading bronze table=%s | processing_date_hour=%s", full_table, processing_date_hour)
    return spark.sql(f"""
        SELECT *
        FROM {full_table}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)


def write_to_silver(df, target_table):
    full_table = f"{ICEBERG_CATALOG}.{TARGET_SCHEMA}.{target_table}"
    logger.info("Writing silver table=%s", full_table)
    df.writeTo(full_table).overwritePartitions()


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
        bronze_df = read_bronze_batch(spark, source_table, processing_date_hour)
        before_count = bronze_df.count()
        silver_df = clean_data(bronze_df)
        after_count = silver_df.count()

        logger.info("Clean result | before=%s | after=%s | removed=%s", before_count, after_count, before_count - after_count)
        write_to_silver(silver_df, target_table)
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
