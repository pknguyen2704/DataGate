package pknguyen.datagate

import org.apache.spark.sql.SparkSession

import java.util

object Load_from_ds_to_lakehouse {
  def main(args: Array[String]): Unit = {

    // Datasource connection
    val PG_JDBC = "jdbc:postgresql://data_source_postgres:5432/postgres"
    val PG_USER = "admin"
    val PG_PASS = "postgrespassword"
    val PG_TABLE = "yellow_tripdata"
    val PG_DRIVER = "org.postgresql.Driver"

    // Lakehouse connection
    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    val ICEBERG_TABLE = "yellow_tripdata"
    val REST_URI = "http://iceberg-rest:8181"
    val WAREHOUSE = "s3://lakehouse/"

    // ===== MinIO (S3 compatible) =====
    val S3_ENDPOINT = "http://minio:9000"
    val S3_ACCESS_KEY = "admin"
    val S3_SECRET_KEY = "miniopassword"
    val AWS_REGION = "us-east-1"

    // Job init
    val JOB_NAME = "[Experiment jobs] Load From DS to Lakehouse"
    val spark = SparkSession.builder()
      .appName(JOB_NAME)
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

      // Catalog REST
      .config("spark.sql.catalog." + CATALOG, "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog." + CATALOG + ".type", "rest")
      .config("spark.sql.catalog." + CATALOG + ".uri", REST_URI)
      .config("spark.sql.catalog." + CATALOG + ".warehouse", WAREHOUSE)

      // Iceberg S3FileIO
      .config("spark.sql.catalog." + CATALOG + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

      // Iceberg S3 settings (MinIO)
      .config("spark.sql.catalog." + CATALOG + ".s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog." + CATALOG + ".s3.path-style-access", "true")
      .config("spark.sql.catalog." + CATALOG + ".s3.access-key-id", S3_ACCESS_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.secret-access-key", S3_SECRET_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".client.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".s3.ssl-enabled", "false")
      .getOrCreate()

    try {
      println("[Experiment jobs] Start v2...")
      val jdbcOptions: util.Map[String, String] = new util.HashMap[String, String]
      jdbcOptions.put("url", PG_JDBC)
      jdbcOptions.put("dbtable", PG_TABLE)
      jdbcOptions.put("user", PG_USER)
      jdbcOptions.put("password", PG_PASS)
      jdbcOptions.put("driver", PG_DRIVER)
      val df = spark.read.format("jdbc").options(jdbcOptions).load()
      println("[Experiment jobs] Preview dataframe")
      df.show()
      val fullTableName = CATALOG + "." + NAMESPACE + "." + ICEBERG_TABLE
      df.writeTo(fullTableName).create()

    } finally {
      spark.stop()
    }
  }
}
