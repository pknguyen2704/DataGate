import sys
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


USAGE = """Usage:
 <REST_URI>
 <S3_ENDPOINT>
 <S3_ACCESS_KEY>
 <S3_SECRET_KEY>
 <AWS_REGION>
 <JDBC_URL>
 <DB_USER>
 <DB_PASSWORD>
 <SOURCE_TABLE>
 <TARGET_TABLE>
 <INGEST_TIME> (yyyy-MM-dd HH or NONE)
 <BATCH_INTERVAL_MINUTES>
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
        .config("spark.sql.catalog.iceberg.s3.endpoint", s3_endpoint)
        .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
        .config("spark.sql.catalog.iceberg.s3.access-key-id", s3_access_key)
        .config("spark.sql.catalog.iceberg.s3.secret-access-key", s3_secret_key)
        .config("spark.sql.catalog.iceberg.s3.region", aws_region)
        .config("spark.sql.catalog.iceberg.s3.client.factory", "org.apache.iceberg.aws.s3.S3ClientFactory")
        
        .config("spark.sql.catalog.iceberg.write.distribution-mode", "hash")
        .config("spark.sql.catalog.iceberg.write.format", "parquet")
        .config("spark.sql.catalog.iceberg.write.metadata.compression-codec", "zstd")
        .config("spark.sql.files.maxRecordsPerFile", 1000000)
        .config("spark.executor.memoryOverhead", "1g")
        .getOrCreate()
    )


def load_source_table(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    source_table: str,
):
    return (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", source_table)
        .option("user", db_user)
        .option("password", db_password)
        .option("driver", "org.postgresql.Driver")
        .load()
    )


def normalize_columns(df):
    return df.select([F.col(column_name).alias(column_name.lower()) for column_name in df.columns])


def filter_ingest_window(df, ingest_time: str):
    if ingest_time == "NONE":
        print("INFO: Performing full load (no filter)")
        return df

    start = datetime.strptime(ingest_time, "%Y-%m-%d %H")
    end = start + timedelta(hours=1)
    print(f"INFO: Filtering partition: {start} -> {end}")
    return df.filter(
        (F.col("tpep_dropoff_datetime") >= F.lit(start))
        & (F.col("tpep_dropoff_datetime") < F.lit(end))
    )


def prepare_output_df(df):
    return df.withColumn("date_hour", F.date_trunc("hour", F.col("tpep_dropoff_datetime")))


def main(argv: list[str]) -> int:
    if len(argv) < 12:
        print(USAGE, file=sys.stderr)
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
        ingest_time,
        batch_interval_minutes_raw,
    ) = argv[:12]

    batch_interval_minutes = int(batch_interval_minutes_raw)

    full_table_name = f"iceberg.{target_table}"
    spark = build_spark_session(
        app_name="Batch_Ingest_PS",
        rest_uri=rest_uri,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        aws_region=aws_region,
    )

    try:
        # 1. Register JDBC source as a temporary view (Lowercased to match Iceberg)
        raw_df = spark.read.format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", source_table) \
            .option("user", db_user) \
            .option("password", db_password) \
            .option("driver", "org.postgresql.Driver") \
            .option("fetchsize", "10000") \
            .load()
            
        raw_df.select([F.col(c).alias(c.lower()) for c in raw_df.columns]) \
            .createOrReplaceTempView("source_data")

        # 2. Perform transformation and write using SQL (Zero-copy to Python)
        sql_query = f"""
            INSERT INTO {full_table_name}
            SELECT 
                *,
                date_trunc('hour', tpep_dropoff_datetime) as date_hour
            FROM source_data
        """
        
        if ingest_time != "NONE":
            # Add filtering if needed
            start_ts = f"{ingest_time}:00:00"
            sql_query = f"""
                INSERT INTO {full_table_name}
                SELECT 
                    *,
                    date_trunc('hour', tpep_dropoff_datetime) as date_hour
                FROM source_data
                WHERE tpep_dropoff_datetime >= CAST('{start_ts}' AS TIMESTAMP)
                  AND tpep_dropoff_datetime < CAST('{start_ts}' AS TIMESTAMP) + INTERVAL 1 HOUR
            """

        print(f"INFO: Executing SQL Ingestion to {full_table_name}...")
        spark.sql(sql_query)
        print(f"SUCCESS: Data successfully written to {full_table_name}")
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
