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

JOB_NAME = "clean_data"

CATALOG_NAME = "iceberg"
SOURCE_SCHEMA = "bronze"
SOURCE_TABLE = "yellow_tripdata"
TARGET_SCHEMA = "silver"
TARGET_TABLE = "cleaned_yellow_tripdata"
REST_URI = "http://iceberg-rest:8181"
CATALOG_WAREHOUSE = "s3://lakehouse/"
STORAGE_ENDPOINT = "http://minio:9000"
STORAGE_ACCESS_KEY = "admin"
STORAGE_SECRET_KEY = "miniopassword"

SPARK_DRIVER_CORES = "2"
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_INSTANCES = "2"
SPARK_EXECUTOR_CORES = "6"
SPARK_EXECUTOR_MEMORY = "10g"
SPARK_SQL_SHUFFLE_PARTITIONS = "24"
SPARK_DEFAULT_PARALLELISM = "24"
SPARK_TIMEZONE = "Asia/Ho_Chi_Minh"

COLUMNS = [
    "vendor_id", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
    "trip_distance", "ratecode_id", "store_and_fwd_flag", "pu_location_id", "do_location_id",
    "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
    "improvement_surcharge", "total_amount", "congestion_surcharge", "airport_fee",
    "cbd_congestion_fee", "date_hour", "processing_date_hour",
]

CRITICAL_NOT_NULL = [
    "vendor_id", "tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance",
    "pu_location_id", "do_location_id", "fare_amount", "total_amount",
    "date_hour", "processing_date_hour",
]

BIGINT_COLS = ["vendor_id", "passenger_count", "ratecode_id", "pu_location_id", "do_location_id", "payment_type"]
DOUBLE_COLS = ["trip_distance", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "airport_fee", "cbd_congestion_fee"]
TIME_COLS = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "date_hour", "processing_date_hour"]


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
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}. Only letters, numbers, and underscore are allowed.")
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
        .config(f"spark.sql.catalog.{CATALOG_NAME}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{CATALOG_NAME}.type", "rest")
        .config(f"spark.sql.catalog.{CATALOG_NAME}.uri", REST_URI)
        .config(f"spark.sql.catalog.{CATALOG_NAME}.warehouse", CATALOG_WAREHOUSE)
        .config(f"spark.sql.catalog.{CATALOG_NAME}.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .config(f"spark.sql.catalog.{CATALOG_NAME}.s3.endpoint", STORAGE_ENDPOINT)
        .config(f"spark.sql.catalog.{CATALOG_NAME}.s3.access-key-id", STORAGE_ACCESS_KEY)
        .config(f"spark.sql.catalog.{CATALOG_NAME}.s3.secret-access-key", STORAGE_SECRET_KEY)
        .config(f"spark.sql.catalog.{CATALOG_NAME}.s3.path-style-access", "true")
        .config(f"spark.sql.catalog.{CATALOG_NAME}.s3.region", "us-east-1")
        .getOrCreate()
    )


def validate_columns(df):
    missing = [col for col in COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def cast_columns(df):
    for col in TIME_COLS:
        df = df.withColumn(col, F.to_timestamp(F.col(col)))
    for col in BIGINT_COLS:
        df = df.withColumn(col, F.col(col).cast("bigint"))
    for col in DOUBLE_COLS:
        df = df.withColumn(col, F.col(col).cast("double"))

    df = df.withColumn("store_and_fwd_flag", F.upper(F.trim(F.col("store_and_fwd_flag").cast("string"))))
    df = df.withColumn("store_and_fwd_flag", F.when(F.col("store_and_fwd_flag").isin("", "<NA>", "NAN", "NONE", "NULL"), None).otherwise(F.col("store_and_fwd_flag")))
    df = df.withColumn("ratecode_id", F.when(F.col("ratecode_id").isNull(), F.lit(99)).otherwise(F.col("ratecode_id")))
    df = df.withColumn("payment_type", F.when(F.col("payment_type").isNull(), F.lit(5)).otherwise(F.col("payment_type")))
    return df


def clean_data(df):
    validate_columns(df)
    df = cast_columns(df)

    invalid = [
        reduce(or_, [F.col(col).isNull() for col in CRITICAL_NOT_NULL]),
        F.col("tpep_dropoff_datetime") < F.col("tpep_pickup_datetime"),
        ~F.col("vendor_id").isin(1, 2, 6, 7),
        ~F.col("ratecode_id").isin(1, 2, 3, 4, 5, 6, 99),
        ~F.col("payment_type").isin(0, 1, 2, 3, 4, 5, 6),
        F.col("store_and_fwd_flag").isNotNull() & ~F.col("store_and_fwd_flag").isin("Y", "N"),
        F.col("trip_distance") < 0,
        F.col("passenger_count") < 0,
        (F.col("pu_location_id") <= 0) | (F.col("do_location_id") <= 0),
        F.col("fare_amount") < 0,
        F.col("total_amount") < 0,
    ]

    return df.filter(~reduce(or_, invalid)).dropDuplicates(COLUMNS).select(COLUMNS)


def read_bronze_batch(spark, source_table, processing_date_hour):
    full_table = f"{CATALOG_NAME}.{SOURCE_SCHEMA}.{source_table}"
    logger.info("Reading bronze table=%s | processing_date_hour=%s", full_table, processing_date_hour)
    return spark.sql(f"""
        SELECT *
        FROM {full_table}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)


def write_to_silver(df, target_table):
    full_table = f"{CATALOG_NAME}.{TARGET_SCHEMA}.{target_table}"
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
        logger.exception(
            "[Job Failed] %s | processing_date_hour=%s",
            JOB_NAME,
            processing_date_hour,
        )
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
