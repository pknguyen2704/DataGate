import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


USAGE = """Usage:
 <REST_URI>
 <S3_ENDPOINT>
 <S3_ACCESS_KEY>
 <S3_SECRET_KEY>
 <AWS_REGION>
 <SOURCE_TABLE>
 <SILVER_TABLE>
 <GOLD_TABLE>
"""


def build_spark_session(
    app_name: str,
    rest_uri: str,
    s3_endpoint: str,
    s3_access_key: str,
    s3_secret_key: str,
    aws_region: str,
) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
        .config(
            "spark.sql.catalog.iceberg.catalog-impl",
            "org.apache.iceberg.rest.RESTCatalog",
        )
        .config("spark.sql.catalog.iceberg.uri", rest_uri)
        .config("spark.sql.catalog.iceberg.warehouse", "s3://lakehouse/")
        .config("spark.sql.catalog.iceberg.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .config("spark.sql.catalog.iceberg.s3.endpoint", s3_endpoint)
        .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
        .config("spark.sql.catalog.iceberg.s3.access-key-id", s3_access_key)
        .config("spark.sql.catalog.iceberg.s3.secret-access-key", s3_secret_key)
        .config("spark.sql.catalog.iceberg.s3.region", aws_region)
        .getOrCreate()
    )


def main(argv: list[str]) -> int:
    if len(argv) < 8:
        print(USAGE, file=sys.stderr)
        return 1

    (
        rest_uri,
        s3_endpoint,
        s3_access_key,
        s3_secret_key,
        aws_region,
        source_table,
        silver_table,
        gold_table,
    ) = argv[:8]

    spark = build_spark_session(
        app_name="Transform_Silver_Gold",
        rest_uri=rest_uri,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        aws_region=aws_region,
    )

    try:
        bronze_df = spark.table(f"iceberg.{source_table}")

        silver_df = (
            bronze_df.withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))
            .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
            .withColumn(
                "trip_duration_minutes",
                (F.col("tpep_dropoff_datetime").cast("long") - F.col("tpep_pickup_datetime").cast("long")) / 60.0,
            )
            .filter(F.col("trip_duration_minutes").isNull() | (F.col("trip_duration_minutes") >= 0))
        )

        (
            silver_df.writeTo(f"iceberg.{silver_table}")
            .using("iceberg")
            .createOrReplace()
        )

        gold_df = (
            silver_df.groupBy("pickup_date", "pickup_hour")
            .agg(
                F.count("*").alias("trip_count"),
                F.sum(F.coalesce(F.col("fare_amount"), F.lit(0.0))).alias("total_fare_amount"),
                F.avg(F.col("trip_distance")).alias("avg_trip_distance"),
                F.avg(F.col("trip_duration_minutes")).alias("avg_trip_duration_minutes"),
            )
            .withColumn("processed_at", F.current_timestamp())
        )

        (
            gold_df.writeTo(f"iceberg.{gold_table}")
            .using("iceberg")
            .createOrReplace()
        )
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
