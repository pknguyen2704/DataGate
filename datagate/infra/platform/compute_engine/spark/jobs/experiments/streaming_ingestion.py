import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


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
        .config("spark.sql.catalog.iceberg.s3.endpoint", s3_endpoint)
        .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
        .config("spark.sql.catalog.iceberg.s3.access-key-id", s3_access_key)
        .config("spark.sql.catalog.iceberg.s3.secret-access-key", s3_secret_key)
        .config("spark.sql.catalog.iceberg.s3.region", aws_region)
        .config("spark.hadoop.fs.s3a.endpoint", s3_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", s3_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", s3_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.sql.catalog.iceberg.write.distribution-mode", "hash")
        .config("spark.sql.files.maxRecordsPerFile", 500000)
        .getOrCreate()
    )


def main(argv: list[str]) -> int:
    if len(argv) < 10:
        print("Missing args", file=sys.stderr)
        return 1

    (
        rest_uri,
        s3_endpoint,
        s3_access_key,
        s3_secret_key,
        aws_region,
        jdbc_url,
        db_user,
        db_password,
        source_table,
        target_table,
    ) = argv[:10]

    full_table_name = f"iceberg.{target_table}"
    spark = build_spark_session(
        app_name="Streaming_Ingest_PS",
        rest_uri=rest_uri,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        aws_region=aws_region,
    )

    try:
        print("Streaming started...")
        while True:
            df = (
                spark.read.format("jdbc")
                .option("url", jdbc_url)
                .option("dbtable", source_table)
                .option("user", db_user)
                .option("password", db_password)
                .load()
            )

            df_final = (
                df.withColumn(
                    "date_hour", F.date_trunc("hour", F.col("tpep_dropoff_datetime"))
                )
                .repartition(F.col("date_hour"))
                .sortWithinPartitions("date_hour")
            )

            count = df_final.count()
            print(f"Fetched {count} rows")

            if count > 0:
                df_final.writeTo(full_table_name).append()
                print(f"Written {count} rows")

            time.sleep(60)
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
