package pknguyen.datagate

import org.apache.spark.sql.SparkSession

object data_profiling {
  def main(args: Array[String]): Unit = {
    val JOB_NAME = "[DataGate] Data Profiling"
    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    val TABLE = "green_tripdata"
    val REST_URI = "http://iceberg-rest:8181"
    val WAREHOUSE = "s3://lakehouse/"

    // ===== MinIO (S3 compatible) =====
    val S3_ENDPOINT = "http://minio:9000"
    val S3_ACCESS_KEY = "admin"
    val S3_SECRET_KEY = "miniopassword"
    val AWS_REGION = "us-east-1"

    // Profiling mode
    val PROFILING_MODE = "table_level"
    val spark = SparkSession.builder()
      .appName(JOB_NAME)
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog." + CATALOG, "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog." + CATALOG + ".type", "rest")
      .config("spark.sql.catalog." + CATALOG + ".uri", REST_URI)
      .config("spark.sql.catalog." + CATALOG + ".warehouse", WAREHOUSE)
      .config("spark.sql.catalog." + CATALOG + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
      .config("spark.sql.catalog." + CATALOG + ".s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog." + CATALOG + ".s3.path-style-access", "true")
      .config("spark.sql.catalog." + CATALOG + ".s3.access-key-id", S3_ACCESS_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.secret-access-key", S3_SECRET_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".client.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".s3.ssl-enabled", "false")
      .getOrCreate()
    try {
      val df = spark.table(s"$CATALOG.$NAMESPACE.$TABLE")
      df.show()
      // Choose profiling level (table/column)

      // Profiling
      val result = 
    } finally {
      spark.stop()
    }
  }
}
