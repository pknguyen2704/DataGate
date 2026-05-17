import argparse
import gc
import logging
import os
import sys
from contextlib import suppress
from datetime import datetime
from time import perf_counter

from pyspark.sql import SparkSession, functions as F


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOB_NAME = "citi_bike_transform_data"
ICEBERG_CATALOG = "iceberg"
SOURCE_SCHEMA = "silver"
SOURCE_TABLE = "cleaned_citi_bike_tripdata"
TARGET_SCHEMA = "gold"
CITI_BIKE_HOURLY_METRICS_TABLE = "citi_bike_hourly_metrics"
CITI_BIKE_STATION_HOURLY_METRICS_TABLE = "citi_bike_station_hourly_metrics"

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


def read_silver_batch(spark, source_table, processing_date_hour):
    table = f"{ICEBERG_CATALOG}.{SOURCE_SCHEMA}.{source_table}"
    logger.info("Reading silver table=%s | processing_date_hour=%s", table, processing_date_hour)
    return spark.sql(f"""
        SELECT *
        FROM {table}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)


def add_distance_feature(df):
    radius_km = F.lit(6371.0)
    start_lat = F.radians(F.col("start_lat"))
    end_lat = F.radians(F.col("end_lat"))
    lat_delta = F.radians(F.col("end_lat") - F.col("start_lat"))
    lng_delta = F.radians(F.col("end_lng") - F.col("start_lng"))

    a = (
        F.pow(F.sin(lat_delta / 2), 2)
        + F.cos(start_lat) * F.cos(end_lat) * F.pow(F.sin(lng_delta / 2), 2)
    )
    distance = radius_km * F.lit(2.0) * F.atan2(F.sqrt(a), F.sqrt(F.lit(1.0) - a))
    return df.withColumn("straight_line_distance_km", distance)


def build_hourly_metrics(df):
    return (
        df.groupBy("date_hour")
        .agg(
            F.count("*").cast("bigint").alias("trip_count"),
            F.sum(F.when(F.col("member_casual") == "member", 1).otherwise(0)).cast("bigint").alias("member_trip_count"),
            F.sum(F.when(F.col("member_casual") == "casual", 1).otherwise(0)).cast("bigint").alias("casual_trip_count"),
            F.sum(F.when(F.col("rideable_type") == "electric_bike", 1).otherwise(0)).cast("bigint").alias("electric_bike_trip_count"),
            F.sum(F.when(F.col("rideable_type") == "classic_bike", 1).otherwise(0)).cast("bigint").alias("classic_bike_trip_count"),
            F.avg("ride_duration_minutes").alias("avg_ride_duration_minutes"),
            F.sum("ride_duration_minutes").alias("total_ride_duration_minutes"),
            F.avg("straight_line_distance_km").alias("avg_straight_line_distance_km"),
            F.sum("straight_line_distance_km").alias("total_straight_line_distance_km"),
            F.min("started_at").alias("min_started_at"),
            F.max("started_at").alias("max_started_at"),
            F.max("processing_date_hour").alias("processing_date_hour"),
        )
    )


def build_station_hourly_metrics(df):
    return (
        df.groupBy(
            "date_hour",
            "start_station_id",
            "start_station_name",
            "end_station_id",
            "end_station_name",
        )
        .agg(
            F.count("*").cast("bigint").alias("trip_count"),
            F.sum(F.when(F.col("member_casual") == "member", 1).otherwise(0)).cast("bigint").alias("member_trip_count"),
            F.sum(F.when(F.col("member_casual") == "casual", 1).otherwise(0)).cast("bigint").alias("casual_trip_count"),
            F.avg("ride_duration_minutes").alias("avg_ride_duration_minutes"),
            F.avg("straight_line_distance_km").alias("avg_straight_line_distance_km"),
            F.max("processing_date_hour").alias("processing_date_hour"),
        )
    )


def write_to_gold(df, table_name):
    table = f"{ICEBERG_CATALOG}.{TARGET_SCHEMA}.{table_name}"
    logger.info("Writing gold table=%s", table)
    df.writeTo(table).overwritePartitions()


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
    hourly_table = validate_table_name(CITI_BIKE_HOURLY_METRICS_TABLE, "CITI_BIKE_HOURLY_METRICS_TABLE")
    station_table = validate_table_name(CITI_BIKE_STATION_HOURLY_METRICS_TABLE, "CITI_BIKE_STATION_HOURLY_METRICS_TABLE")
    processing_date_hour = normalize_datetime(args.processing_date_hour)
    spark = None

    try:
        spark = create_spark_session()
        base_df = add_distance_feature(read_silver_batch(spark, source_table, processing_date_hour))
        write_to_gold(build_hourly_metrics(base_df), hourly_table)
        write_to_gold(build_station_hourly_metrics(base_df), station_table)
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
