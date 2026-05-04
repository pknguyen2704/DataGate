import argparse
import logging
from datetime import datetime
from time import perf_counter

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "transform_silver_to_gold"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transform one silver batch into two gold tables"
    )

    parser.add_argument("--source_table", required=True)
    parser.add_argument("--trip_hourly_metrics_table", required=True)
    parser.add_argument("--location_hourly_metrics_table", required=True)
    parser.add_argument("--taxi_zone_seed_path", required=True)
    parser.add_argument("--processing_date_hour", required=True)

    return parser.parse_args()


def build_spark_session():
    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .getOrCreate()
    )


def normalize_datetime_string(value):
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


def get_spark_conf(spark, key, default_value=None):
    return spark.conf.get(key, default_value)


def resolve_table_name(table_name, iceberg_catalog):
    table_name = validate_table_identifier(table_name, "table_name")

    if len(table_name.split(".")) == 3:
        return table_name

    return f"{iceberg_catalog}.{table_name}"


def read_silver_batch(spark, source_table, processing_date_hour):
    return spark.sql(
        f"""
        SELECT *
        FROM {source_table}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
        """
    )


def read_taxi_zone_seed(spark, seed_path):
    return (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(seed_path)
        .select(
            F.col("LocationID").cast("bigint").alias("location_id"),
            F.col("Borough").alias("borough"),
            F.col("Zone").alias("zone"),
            F.col("service_zone").alias("service_zone"),
        )
    )


def add_basic_features(df):
    return (
        df
        .withColumn(
            "trip_duration_minutes",
            (
                F.unix_timestamp(F.col("tpep_dropoff_datetime"))
                - F.unix_timestamp(F.col("tpep_pickup_datetime"))
            ) / F.lit(60.0),
        )
        .withColumn(
            "amount_per_mile",
            F.when(
                F.col("trip_distance") > 0,
                F.col("total_amount") / F.col("trip_distance"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .withColumn(
            "tip_rate",
            F.when(
                F.col("fare_amount") > 0,
                F.col("tip_amount") / F.col("fare_amount"),
            ).otherwise(F.lit(None).cast("double")),
        )
    )


def build_trip_hourly_metrics(df):
    return (
        df
        .groupBy("date_hour")
        .agg(
            F.count(F.lit(1)).cast("bigint").alias("trip_count"),
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
    pickup_zone_df = (
        zone_df
        .select(
            F.col("location_id").alias("pulocationid"),
            F.col("borough").alias("pickup_borough"),
            F.col("zone").alias("pickup_zone"),
            F.col("service_zone").alias("pickup_service_zone"),
        )
    )

    dropoff_zone_df = (
        zone_df
        .select(
            F.col("location_id").alias("dolocationid"),
            F.col("borough").alias("dropoff_borough"),
            F.col("zone").alias("dropoff_zone"),
            F.col("service_zone").alias("dropoff_service_zone"),
        )
    )

    enriched_df = (
        df
        .join(F.broadcast(pickup_zone_df), on="pulocationid", how="left")
        .join(F.broadcast(dropoff_zone_df), on="dolocationid", how="left")
    )

    return (
        enriched_df
        .groupBy(
            "date_hour",
            "pulocationid",
            "pickup_borough",
            "pickup_zone",
            "pickup_service_zone",
            "dolocationid",
            "dropoff_borough",
            "dropoff_zone",
            "dropoff_service_zone",
        )
        .agg(
            F.count(F.lit(1)).cast("bigint").alias("trip_count"),
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


def write_to_iceberg(df, target_table):
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
        iceberg_catalog = get_spark_conf(
            spark=spark,
            key="datagate.iceberg.catalog",
            default_value="iceberg",
        )

        source_table = resolve_table_name(args.source_table, iceberg_catalog)
        trip_table = resolve_table_name(args.trip_hourly_metrics_table, iceberg_catalog)
        location_table = resolve_table_name(args.location_hourly_metrics_table, iceberg_catalog)

        logger.info(
            "Reading silver table=%s | processing_date_hour=%s",
            source_table,
            args.processing_date_hour,
        )

        silver_df = read_silver_batch(
            spark=spark,
            source_table=source_table,
            processing_date_hour=args.processing_date_hour,
        )

        base_df = add_basic_features(silver_df)
        zone_df = read_taxi_zone_seed(
            spark=spark,
            seed_path=args.taxi_zone_seed_path,
        )

        trip_hourly_df = build_trip_hourly_metrics(base_df)
        location_hourly_df = build_location_hourly_metrics(base_df, zone_df)

        logger.info("Writing gold table=%s", trip_table)
        write_to_iceberg(trip_hourly_df, trip_table)

        logger.info("Writing gold table=%s", location_table)
        write_to_iceberg(location_hourly_df, location_table)

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