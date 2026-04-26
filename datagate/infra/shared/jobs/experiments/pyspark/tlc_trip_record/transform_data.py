import argparse
from dataclasses import dataclass
from time import perf_counter

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    lit,
    max as spark_max,
    min as spark_min,
    sum as spark_sum,
    unix_timestamp,
    when,
)


JOB_NAME = "transform_data"


@dataclass
class JobConfig:
    source_table: str
    enriched_table: str
    trip_hourly_metrics_table: str
    location_hourly_metrics_table: str
    payment_hourly_metrics_table: str
    vendor_hourly_metrics_table: str
    date_hour: str


def parse_args() -> JobConfig:
    parser = argparse.ArgumentParser(
        description="Transform one date_hour from silver Iceberg table into gold layer tables"
    )

    parser.add_argument(
        "--source_table",
        required=False,
        default="silver.cleaned_yellow_tripdata",
    )

    parser.add_argument(
        "--enriched_table",
        required=False,
        default="gold.yellow_tripdata_enriched",
    )

    parser.add_argument(
        "--trip_hourly_metrics_table",
        required=False,
        default="gold.trip_hourly_metrics",
    )

    parser.add_argument(
        "--location_hourly_metrics_table",
        required=False,
        default="gold.location_hourly_metrics",
    )

    parser.add_argument(
        "--payment_hourly_metrics_table",
        required=False,
        default="gold.payment_hourly_metrics",
    )

    parser.add_argument(
        "--vendor_hourly_metrics_table",
        required=False,
        default="gold.vendor_hourly_metrics",
    )

    parser.add_argument(
        "--date_hour",
        required=True,
        help="Processing date_hour, format: yyyy-MM-dd HH:mm:ss",
    )

    args = parser.parse_args()

    return JobConfig(
        source_table=args.source_table,
        enriched_table=args.enriched_table,
        trip_hourly_metrics_table=args.trip_hourly_metrics_table,
        location_hourly_metrics_table=args.location_hourly_metrics_table,
        payment_hourly_metrics_table=args.payment_hourly_metrics_table,
        vendor_hourly_metrics_table=args.vendor_hourly_metrics_table,
        date_hour=args.date_hour,
    )


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .getOrCreate()
    )


def read_from_iceberg(
    spark: SparkSession,
    source_table: str,
    date_hour: str,
) -> DataFrame:
    return (
        spark.read
        .format("iceberg")
        .load(f"iceberg.{source_table}")
        .filter(col("date_hour") == date_hour)
    )


def write_to_iceberg_partition_overwrite(
    df: DataFrame,
    target_table: str,
) -> None:
    (
        df.writeTo(f"iceberg.{target_table}")
        .overwritePartitions()
    )


def build_enriched_trip_data(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn(
            "trip_duration_minutes",
            (
                unix_timestamp(col("tpep_dropoff_datetime"))
                - unix_timestamp(col("tpep_pickup_datetime"))
            ) / lit(60.0),
        )
        .withColumn(
            "amount_per_mile",
            when(
                col("trip_distance") > 0,
                col("total_amount") / col("trip_distance"),
            ).otherwise(lit(None).cast("double")),
        )
        .withColumn(
            "tip_rate",
            when(
                col("fare_amount") > 0,
                col("tip_amount") / col("fare_amount"),
            ).otherwise(lit(None).cast("double")),
        )
        .select(
            col("vendorid"),
            col("tpep_pickup_datetime"),
            col("tpep_dropoff_datetime"),
            col("passenger_count"),
            col("trip_distance"),
            col("ratecodeid"),
            col("store_and_fwd_flag"),
            col("pulocationid"),
            col("dolocationid"),
            col("payment_type"),
            col("fare_amount"),
            col("extra"),
            col("mta_tax"),
            col("tip_amount"),
            col("tolls_amount"),
            col("improvement_surcharge"),
            col("total_amount"),
            col("congestion_surcharge"),
            col("airport_fee"),
            col("cbd_congestion_fee"),
            col("date_hour"),
            col("trip_duration_minutes"),
            col("amount_per_mile"),
            col("tip_rate"),
        )
    )


def build_trip_hourly_metrics(enriched_df: DataFrame) -> DataFrame:
    return (
        enriched_df
        .groupBy(col("date_hour"))
        .agg(
            count(lit(1)).cast("bigint").alias("trip_count"),
            spark_sum(col("passenger_count")).cast("bigint").alias("total_passenger_count"),

            spark_sum(col("trip_distance")).alias("total_trip_distance"),
            avg(col("trip_distance")).alias("avg_trip_distance"),

            spark_sum(col("fare_amount")).alias("total_fare_amount"),
            spark_sum(col("tip_amount")).alias("total_tip_amount"),
            spark_sum(col("total_amount")).alias("total_total_amount"),
            avg(col("total_amount")).alias("avg_total_amount"),

            avg(col("trip_duration_minutes")).alias("avg_trip_duration_minutes"),

            spark_min(col("tpep_pickup_datetime")).alias("min_pickup_datetime"),
            spark_max(col("tpep_pickup_datetime")).alias("max_pickup_datetime"),
            spark_min(col("tpep_dropoff_datetime")).alias("min_dropoff_datetime"),
            spark_max(col("tpep_dropoff_datetime")).alias("max_dropoff_datetime"),
        )
    )


def build_location_hourly_metrics(enriched_df: DataFrame) -> DataFrame:
    return (
        enriched_df
        .groupBy(
            col("date_hour"),
            col("pulocationid"),
            col("dolocationid"),
        )
        .agg(
            count(lit(1)).cast("bigint").alias("trip_count"),
            spark_sum(col("passenger_count")).cast("bigint").alias("total_passenger_count"),

            spark_sum(col("trip_distance")).alias("total_trip_distance"),
            avg(col("trip_distance")).alias("avg_trip_distance"),

            spark_sum(col("fare_amount")).alias("total_fare_amount"),
            spark_sum(col("tip_amount")).alias("total_tip_amount"),
            spark_sum(col("total_amount")).alias("total_total_amount"),
            avg(col("total_amount")).alias("avg_total_amount"),
        )
    )


def build_payment_hourly_metrics(enriched_df: DataFrame) -> DataFrame:
    return (
        enriched_df
        .groupBy(
            col("date_hour"),
            col("payment_type"),
        )
        .agg(
            count(lit(1)).cast("bigint").alias("trip_count"),
            spark_sum(col("trip_distance")).alias("total_trip_distance"),

            spark_sum(col("fare_amount")).alias("total_fare_amount"),
            spark_sum(col("tip_amount")).alias("total_tip_amount"),
            spark_sum(col("total_amount")).alias("total_total_amount"),
            avg(col("total_amount")).alias("avg_total_amount"),

            avg(col("tip_rate")).alias("avg_tip_rate"),
        )
    )


def build_vendor_hourly_metrics(enriched_df: DataFrame) -> DataFrame:
    return (
        enriched_df
        .groupBy(
            col("date_hour"),
            col("vendorid"),
        )
        .agg(
            count(lit(1)).cast("bigint").alias("trip_count"),
            spark_sum(col("passenger_count")).cast("bigint").alias("total_passenger_count"),

            spark_sum(col("trip_distance")).alias("total_trip_distance"),
            avg(col("trip_distance")).alias("avg_trip_distance"),

            spark_sum(col("fare_amount")).alias("total_fare_amount"),
            spark_sum(col("tip_amount")).alias("total_tip_amount"),
            spark_sum(col("total_amount")).alias("total_total_amount"),
            avg(col("total_amount")).alias("avg_total_amount"),
        )
    )


def main() -> None:
    job_start_time = perf_counter()

    job_config = parse_args()
    spark = build_spark_session()

    try:
        silver_df = read_from_iceberg(
            spark=spark,
            source_table=job_config.source_table,
            date_hour=job_config.date_hour,
        )

        enriched_df = build_enriched_trip_data(silver_df)

        trip_hourly_metrics_df = build_trip_hourly_metrics(enriched_df)
        location_hourly_metrics_df = build_location_hourly_metrics(enriched_df)
        payment_hourly_metrics_df = build_payment_hourly_metrics(enriched_df)
        vendor_hourly_metrics_df = build_vendor_hourly_metrics(enriched_df)

        write_to_iceberg_partition_overwrite(
            df=enriched_df,
            target_table=job_config.enriched_table,
        )

        write_to_iceberg_partition_overwrite(
            df=trip_hourly_metrics_df,
            target_table=job_config.trip_hourly_metrics_table,
        )

        write_to_iceberg_partition_overwrite(
            df=location_hourly_metrics_df,
            target_table=job_config.location_hourly_metrics_table,
        )

        write_to_iceberg_partition_overwrite(
            df=payment_hourly_metrics_df,
            target_table=job_config.payment_hourly_metrics_table,
        )

        write_to_iceberg_partition_overwrite(
            df=vendor_hourly_metrics_df,
            target_table=job_config.vendor_hourly_metrics_table,
        )

        total_seconds = perf_counter() - job_start_time
        print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()