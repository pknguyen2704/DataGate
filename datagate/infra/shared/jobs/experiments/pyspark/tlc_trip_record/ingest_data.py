import argparse
from dataclasses import dataclass
from time import perf_counter

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col


JOB_NAME = "ingest_data"


@dataclass
class JobConfig:
    jdbc_url: str
    source_db_user: str
    source_db_password: str
    source_table: str
    target_table: str
    date_hour: str


def parse_args() -> JobConfig:
    parser = argparse.ArgumentParser(
        description="Ingest one date_hour from PostgreSQL to Iceberg bronze table"
    )

    parser.add_argument("--jdbc_url", required=True)
    parser.add_argument("--source_db_user", required=True)
    parser.add_argument("--source_db_password", required=True)
    parser.add_argument("--source_table", required=True)
    parser.add_argument("--target_table", required=True)
    parser.add_argument("--date_hour",required=True)

    args = parser.parse_args()

    return JobConfig(
        jdbc_url=args.jdbc_url,
        source_db_user=args.source_db_user,
        source_db_password=args.source_db_password,
        source_table=args.source_table,
        target_table=args.target_table,
        date_hour=args.date_hour,
    )


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .getOrCreate()
    )


def build_source_query(job_config: JobConfig) -> str:
    return f"""
    (
        SELECT *
        FROM {job_config.source_table}
        WHERE date_hour = TIMESTAMP '{job_config.date_hour}'
    ) AS source_data
    """


def read_table_from_data_source(
    spark: SparkSession,
    job_config: JobConfig,
) -> DataFrame:
    dbtable = build_source_query(job_config)

    return (
        spark.read
        .format("jdbc")
        .option("url", job_config.jdbc_url)
        .option("dbtable", dbtable)
        .option("user", job_config.source_db_user)
        .option("password", job_config.source_db_password)
        .option("driver", "org.postgresql.Driver")
        .option("fetchsize", "20000")
        .load()
    )


def convert_column_names_to_lower_case(df: DataFrame) -> DataFrame:
    return df.select(
        *[
            col(column_name).alias(column_name.lower())
            for column_name in df.columns
        ]
    )


def transform_data(df: DataFrame) -> DataFrame:
    return convert_column_names_to_lower_case(df)


def write_to_iceberg(df: DataFrame, target_table: str) -> None:
    (
        df.writeTo(f"iceberg.{target_table}")
        .overwritePartitions()
    )


def main() -> None:
    job_start_time = perf_counter()

    job_config = parse_args()
    spark = build_spark_session()

    try:
        source_df = read_table_from_data_source(
            spark=spark,
            job_config=job_config,
        )

        transformed_df = transform_data(source_df)

        write_to_iceberg(
            df=transformed_df,
            target_table=job_config.target_table,
        )

        total_seconds = perf_counter() - job_start_time
        print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()