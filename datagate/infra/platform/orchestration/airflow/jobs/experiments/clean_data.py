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
 <TARGET_TABLE>
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
    if len(argv) < 7:
        print(USAGE, file=sys.stderr)
        return 1

    (
        rest_uri,
        s3_endpoint,
        s3_access_key,
        s3_secret_key,
        aws_region,
        source_table,
        target_table,
    ) = argv[:7]

    spark = build_spark_session(
        app_name="Clean_Data_To_Bronze",
        rest_uri=rest_uri,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        aws_region=aws_region,
    )

    try:
        source_df = spark.table(f"iceberg.{source_table}")

        cleaned_df = (
            source_df.dropDuplicates()
            .dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])
            .filter(F.col("trip_distance").isNull() | (F.col("trip_distance") >= 0))
            .filter(F.col("fare_amount").isNull() | (F.col("fare_amount") >= 0))
            .withColumn("processed_at", F.current_timestamp())
        )

        (
            cleaned_df.writeTo(f"iceberg.{target_table}")
            .using("iceberg")
            .createOrReplace()
        )
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
