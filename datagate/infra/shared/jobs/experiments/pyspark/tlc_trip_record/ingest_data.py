import argparse
from datetime import datetime, timedelta
from time import perf_counter

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, to_timestamp

JOB_NAME = "ingest_data"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest one processing batch from PostgreSQL to Iceberg bronze table"
    )

    parser.add_argument("--jdbc_url", required=True)
    parser.add_argument("--source_db_user", required=True)
    parser.add_argument("--source_db_password", required=True)
    parser.add_argument("--source_table", required=True)
    parser.add_argument("--target_table", required=True)
    parser.add_argument("--processing_date_hour", required=True)
    parser.add_argument("--spark_master", default="spark://spark-master:7077")
    parser.add_argument("--spark_driver_cores", type=int, default=2)
    parser.add_argument("--spark_driver_memory", default="4g")
    parser.add_argument("--spark_executor_instances", type=int, default=2)
    parser.add_argument("--spark_executor_cores", type=int, default=6)
    parser.add_argument("--spark_executor_memory", default="7g")
    parser.add_argument("--spark_sql_shuffle_partitions", type=int, default=32)
    parser.add_argument("--spark_default_parallelism", type=int, default=32)

    return parser.parse_args()


def build_spark_session(args) -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(JOB_NAME)
        .master(args.spark_master)
        .config("spark.driver.cores", str(args.spark_driver_cores))
        .config("spark.driver.memory", args.spark_driver_memory)
        .config("spark.executor.instances", str(args.spark_executor_instances))
        .config("spark.executor.cores", str(args.spark_executor_cores))
        .config("spark.executor.memory", args.spark_executor_memory)
        .config("spark.sql.shuffle.partitions", str(args.spark_sql_shuffle_partitions))
        .config("spark.default.parallelism", str(args.spark_default_parallelism))
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )

    return spark


def resolve_batch_window(processing_date_hour: str) -> tuple[str, str]:
    batch_end = datetime.strptime(processing_date_hour, "%Y-%m-%d %H:%M:%S")

    if batch_end.hour not in {0, 12} or batch_end.minute != 0 or batch_end.second != 0:
        raise ValueError(
            "processing_date_hour must be in format YYYY-MM-DD HH:MM:SS "
            "and the hour must be 00:00:00 or 12:00:00"
        )

    batch_start = batch_end - timedelta(hours=12)

    batch_start_str = batch_start.strftime("%Y-%m-%d %H:%M:%S")
    batch_end_str = batch_end.strftime("%Y-%m-%d %H:%M:%S")

    return batch_start_str, batch_end_str


def build_source_query(source_table: str, processing_date_hour: str) -> str:
    batch_start, batch_end = resolve_batch_window(processing_date_hour)

    query = f"""
    (
        SELECT *
        FROM {source_table}
        WHERE date_hour >= TIMESTAMP '{batch_start}'
          AND date_hour < TIMESTAMP '{batch_end}'
    ) AS source_data
    """

    return query


def read_table_from_data_source(
    spark: SparkSession,
    jdbc_url: str,
    source_db_user: str,
    source_db_password: str,
    source_table: str,
    processing_date_hour: str,
) -> DataFrame:
    dbtable = build_source_query(
        source_table=source_table,
        processing_date_hour=processing_date_hour,
    )

    df = (
        spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", dbtable)
        .option("user", source_db_user)
        .option("password", source_db_password)
        .option("driver", "org.postgresql.Driver")
        .option("fetchsize", "20000")
        .load()
    )

    return df


def convert_column_names_to_lower_case(df: DataFrame) -> DataFrame:
    lower_case_df = df.select(
        *[
            col(column_name).alias(column_name.lower())
            for column_name in df.columns
        ]
    )

    return lower_case_df


def transform_data(df: DataFrame, processing_date_hour: str) -> DataFrame:
    transformed_df = (
        convert_column_names_to_lower_case(df)
        .withColumn(
            "processing_date_hour",
            to_timestamp(lit(processing_date_hour)),
        )
    )

    return transformed_df


def write_to_iceberg(df: DataFrame, target_table: str) -> None:
    (
        df.writeTo(f"iceberg.{target_table}")
        .overwritePartitions()
    )


def main() -> None:
    job_start_time = perf_counter()
    args = parse_args()
    spark = build_spark_session(args)

    try:
        batch_start, batch_end = resolve_batch_window(args.processing_date_hour)

        print(
            f"[{JOB_NAME}] Processing source date_hour window "
            f"[{batch_start}, {batch_end})"
        )

        source_df = read_table_from_data_source(
            spark=spark,
            jdbc_url=args.jdbc_url,
            source_db_user=args.source_db_user,
            source_db_password=args.source_db_password,
            source_table=args.source_table,
            processing_date_hour=args.processing_date_hour,
        )

        transformed_df = transform_data(
            df=source_df,
            processing_date_hour=args.processing_date_hour,
        )

        write_to_iceberg(
            df=transformed_df,
            target_table=args.target_table,
        )

        total_seconds = perf_counter() - job_start_time

        print(
            f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds"
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()