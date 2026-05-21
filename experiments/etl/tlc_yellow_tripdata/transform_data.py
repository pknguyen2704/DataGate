import argparse
import gc
import logging
import os
import sys
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import perf_counter

from pyspark.sql import SparkSession, functions as F


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOB_NAME = "transform_data"

CATALOG_NAME = "iceberg"
SOURCE_SCHEMA = "silver"
SOURCE_TABLE = "cleaned_yellow_tripdata"
TARGET_SCHEMA = "gold"
TRIP_HOURLY_METRICS_TABLE = "trip_hourly_metrics"
LOCATION_HOURLY_METRICS_TABLE = "location_hourly_metrics"

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

SEED_PATH = str(Path(__file__).resolve().parent / "seed" / "taxi_zone_lookup.csv")


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


def read_silver_batch(spark, source_table, processing_date_hour):
    table = f"{CATALOG_NAME}.{SOURCE_SCHEMA}.{source_table}"
    logger.info("Reading silver table=%s | processing_date_hour=%s", table, processing_date_hour)
    return spark.sql(f"""
        SELECT *
        FROM {table}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)


def read_zone_seed(spark):
    return (
        spark.read.option("header", "true").csv(SEED_PATH)
        .select(
            F.col("LocationID").cast("bigint").alias("location_id"),
            F.col("Borough").alias("borough"),
            F.col("Zone").alias("zone"),
            F.col("service_zone").alias("service_zone"),
        )
    )


def add_features(df):
    duration = (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / F.lit(60.0)

    return (
        df.withColumn("trip_duration_minutes", duration)
        .withColumn("amount_per_mile", F.when(F.col("trip_distance") > 0, F.col("total_amount") / F.col("trip_distance")))
        .withColumn("tip_rate", F.when(F.col("fare_amount") > 0, F.col("tip_amount") / F.col("fare_amount")))
    )


def build_trip_hourly_metrics(df):
    return (
        df.groupBy("date_hour")
        .agg(
            F.count("*").cast("bigint").alias("trip_count"),
            F.sum("passenger_count").cast("bigint").alias("total_passenger_count"),
            F.sum("trip_distance").alias("total_trip_distance"),
            F.avg("trip_distance").alias("avg_trip_distance"),
            F.sum("fare_amount").alias("total_fare_amount"),
            F.sum("tip_amount").alias("total_tip_amount"),
            F.sum("total_amount").alias("total_amount"),
            F.avg("total_amount").alias("avg_total_amount"),
            F.avg("trip_duration_minutes").alias("avg_trip_duration_minutes"),
            F.avg("amount_per_mile").alias("avg_amount_per_mile"),
            F.avg("tip_rate").alias("avg_tip_rate"),
            F.min("tpep_pickup_datetime").alias("min_pickup_datetime"),
            F.max("tpep_pickup_datetime").alias("max_pickup_datetime"),
            F.max("processing_date_hour").alias("processing_date_hour"),
        )
    )


def build_location_hourly_metrics(df, zone_df):
    pickup_zone = zone_df.select(
        F.col("location_id").alias("pu_location_id"),
        F.col("borough").alias("pickup_borough"),
        F.col("zone").alias("pickup_zone"),
        F.col("service_zone").alias("pickup_service_zone"),
    )

    dropoff_zone = zone_df.select(
        F.col("location_id").alias("do_location_id"),
        F.col("borough").alias("dropoff_borough"),
        F.col("zone").alias("dropoff_zone"),
        F.col("service_zone").alias("dropoff_service_zone"),
    )

    return (
        df.join(F.broadcast(pickup_zone), on="pu_location_id", how="left")
        .join(F.broadcast(dropoff_zone), on="do_location_id", how="left")
        .groupBy(
            "date_hour",
            "pu_location_id",
            "pickup_borough",
            "pickup_zone",
            "pickup_service_zone",
            "do_location_id",
            "dropoff_borough",
            "dropoff_zone",
            "dropoff_service_zone",
        )
        .agg(
            F.count("*").cast("bigint").alias("trip_count"),
            F.sum("passenger_count").cast("bigint").alias("total_passenger_count"),
            F.sum("trip_distance").alias("total_trip_distance"),
            F.avg("trip_distance").alias("avg_trip_distance"),
            F.sum("fare_amount").alias("total_fare_amount"),
            F.sum("tip_amount").alias("total_tip_amount"),
            F.sum("total_amount").alias("total_amount"),
            F.avg("total_amount").alias("avg_total_amount"),
            F.avg("trip_duration_minutes").alias("avg_trip_duration_minutes"),
            F.max("processing_date_hour").alias("processing_date_hour"),
        )
    )


def write_to_gold(df, table_name):
    table = f"{CATALOG_NAME}.{TARGET_SCHEMA}.{table_name}"
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
    trip_table = validate_table_name(TRIP_HOURLY_METRICS_TABLE, "TRIP_HOURLY_METRICS_TABLE")
    location_table = validate_table_name(LOCATION_HOURLY_METRICS_TABLE, "LOCATION_HOURLY_METRICS_TABLE")
    processing_date_hour = normalize_datetime(args.processing_date_hour)

    spark = None

    try:
        spark = create_spark_session()
        silver_df = read_silver_batch(spark, source_table, processing_date_hour)
        base_df = add_features(silver_df)
        zone_df = read_zone_seed(spark)

        write_to_gold(build_trip_hourly_metrics(base_df), trip_table)
        write_to_gold(build_location_hourly_metrics(base_df, zone_df), location_table)

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
