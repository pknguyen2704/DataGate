import argparse
from datetime import datetime, timedelta

from pyspark.sql import functions as F
from pyspark.sql import SparkSession

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--rest_uri", required=True)
    parser.add_argument("--s3_endpoint", required=True)
    parser.add_argument("--s3_access_key", required=True)
    parser.add_argument("--s3_secret_key", required=True)
    parser.add_argument("--aws_region", required=True)
    parser.add_argument("--jdbc_url", required=True)
    parser.add_argument("--db_user", required=True)
    parser.add_argument("--db_password", required=True)
    parser.add_argument("--source_table", required=True)
    parser.add_argument("--target_table", required=True)
    parser.add_argument("--ingest_time", default="NONE")

    return parser.parse_args()



def build_spark(args):
    return (
        SparkSession.builder.appName("Batch_Ingest_PS")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.rest.RESTCatalog")
        .config("spark.sql.catalog.iceberg.uri", args.rest_uri)
        .config("spark.sql.catalog.iceberg.s3.endpoint", args.s3_endpoint)
        .config("spark.sql.catalog.iceberg.s3.access-key-id", args.s3_access_key)
        .config("spark.sql.catalog.iceberg.s3.secret-access-key", args.s3_secret_key)
        .config("spark.sql.catalog.iceberg.s3.region", args.aws_region)
        .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
        .config("spark.sql.shuffle.partitions", "20")
        .config("spark.default.parallelism", "20")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.catalog.iceberg.write.distribution-mode", "hash")
        .config("spark.sql.files.maxRecordsPerFile", "1000000")
        .config("spark.sql.catalog.iceberg.write.target-file-size-bytes", "134217728")  # 128MB
        .getOrCreate()
    )


# =========================
# JDBC read (parallel)
# =========================
def read_source(spark, jdbc_url, db_user, db_password, source_table):
    return (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", source_table)
        .option("user", db_user)
        .option("password", db_password)
        .option("driver", "org.postgresql.Driver")
        .option("fetchsize", "20000")
        .load()
    )
def transform(df, ingest_time):
    df = df.select([F.col(c).alias(c.lower()) for c in df.columns])

    if ingest_time != "NONE":
        start = datetime.strptime(ingest_time, "%Y-%m-%d %H")
        end = start + timedelta(hours=1)

        df = df.filter(
            (F.col("date_hour") >= F.lit(start)) &
            (F.col("date_hour") < F.lit(end))
        )

    return df

def main():
    args = parse_args()
    spark = build_spark(args)

    try:
        df = read_source(
            spark,
            args.jdbc_url,
            args.db_user,
            args.db_password,
            args.source_table,
        )

        df = transform(df, args.ingest_time)

        print(f"Writing to iceberg.{args.target_table}")

        (
            df.write
            .format("iceberg")
            .mode("append")
            .save(f"iceberg.{args.target_table}")
        )

        print("SUCCESS")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()