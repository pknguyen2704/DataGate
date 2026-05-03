import argparse
from dataclasses import dataclass
from time import perf_counter

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, to_timestamp, trim


JOB_NAME = "clean_data"


@dataclass
class JobConfig:
    source_table: str
    target_table: str
    processing_date_hour: str


def parse_args() -> JobConfig:
    parser = argparse.ArgumentParser(
        description="Clean one date_hour from bronze Iceberg table and write to silver Iceberg table"
    )

    parser.add_argument(
        "--source_table",
        required=False,
        default="bronze.yellow_tripdata",
    )

    parser.add_argument(
        "--target_table",
        required=False,
        default="silver.cleaned_yellow_tripdata",
    )

    parser.add_argument(
        "--processing_date_hour",
        required=True,
        help="Processing batch partition, format: yyyy-MM-dd HH:mm:ss",
    )

    args = parser.parse_args()

    return JobConfig(
        source_table=args.source_table,
        target_table=args.target_table,
        processing_date_hour=args.processing_date_hour,
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
    processing_date_hour: str,
) -> DataFrame:
    return (
        spark.read
        .format("iceberg")
        .load(f"iceberg.{source_table}")
        .filter(col("processing_date_hour") == to_timestamp(lit(processing_date_hour)))
    )


def write_to_iceberg(
    df: DataFrame,
    target_table: str,
) -> None:
    (
        df.writeTo(f"iceberg.{target_table}")
        .overwritePartitions()
    )


def clean_data(df: DataFrame) -> DataFrame:
    return (
        df
        # Required fields
        .filter(col("vendor_id").isNotNull())
        .filter(col("tpep_pickup_datetime").isNotNull())
        .filter(col("tpep_dropoff_datetime").isNotNull())
        .filter(col("trip_distance").isNotNull())
        .filter(col("fare_amount").isNotNull())
        .filter(col("total_amount").isNotNull())
        .filter(col("date_hour").isNotNull())

        # Trip time validation
        .filter(col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime"))

        # Passenger count validation
        .filter(col("passenger_count").isNull() | (col("passenger_count") >= 0))
        .filter(col("passenger_count").isNull() | (col("passenger_count") <= 8))

        # Trip distance validation
        .filter(col("trip_distance").isNull() | (col("trip_distance") > 0))

        # Location validation
        .filter(col("pulocationid").isNull() | (col("pulocationid") > 0))
        .filter(col("dolocationid").isNull() | (col("dolocationid") > 0))

        # Amount validation
        .filter(col("fare_amount").isNull() | (col("fare_amount") >= 0))
        
        .filter(col("extra").isNull() | (col("extra") >= 0))
        .filter(col("mta_tax").isNull() | (col("mta_tax") >= 0))
        .filter(col("tip_amount").isNull() | (col("tip_amount") >= 0))
        .filter(col("tolls_amount").isNull() | (col("tolls_amount") >= 0))
        .filter(col("improvement_surcharge").isNull() | (col("improvement_surcharge") >= 0))
        .filter(col("total_amount").isNull() | (col("total_amount") >= 0))
        .filter(col("congestion_surcharge").isNull() | (col("congestion_surcharge") >= 0))
        .filter(col("airport_fee").isNull() | (col("airport_fee") >= 0))
        .filter(col("cbd_congestion_fee").isNull() | (col("cbd_congestion_fee") >= 0))

        # Normalize string flag, keep the same schema
        .withColumn("store_and_fwd_flag", trim(col("store_and_fwd_flag")))
        .withColumn("passenger_count", col("passenger_count").cast("bigint"))
        .withColumn("ratecode_id", col("ratecode_id").cast("bigint"))

        # Remove fully duplicated rows
        .dropDuplicates()
    )


def attach_processing_date_hour(df: DataFrame, processing_date_hour: str) -> DataFrame:
    return df.withColumn(
        "processing_date_hour",
        to_timestamp(lit(processing_date_hour)),
    )


def main() -> None:
    job_start_time = perf_counter()

    job_config = parse_args()
    spark = build_spark_session()

    try:
        print(
            f"[{JOB_NAME}] Loading bronze partition "
            f"processing_date_hour={job_config.processing_date_hour}"
        )

        bronze_df = read_from_iceberg(
            spark=spark,
            source_table=job_config.source_table,
            processing_date_hour=job_config.processing_date_hour,
        )

        cleaned_df = attach_processing_date_hour(
            df=clean_data(bronze_df),
            processing_date_hour=job_config.processing_date_hour,
        )

        write_to_iceberg(
            df=cleaned_df,
            target_table=job_config.target_table,
        )

        total_seconds = perf_counter() - job_start_time
        print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
