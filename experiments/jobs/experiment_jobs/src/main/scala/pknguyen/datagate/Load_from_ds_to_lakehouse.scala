package pknguyen.datagate

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.util

object Load_from_ds_to_lakehouse {

  def main(args: Array[String]): Unit = {

    val PG_JDBC = "jdbc:postgresql://data_source_postgres:5432/postgres"
    val PG_USER = "admin"
    val PG_PASS = "postgrespassword"
    val PG_DRIVER = "org.postgresql.Driver"

    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    val REST_URI = "http://iceberg-rest:8181"
    val WAREHOUSE = "s3://lakehouse/"

    val S3_ENDPOINT = "http://minio:9000"
    val S3_ACCESS_KEY = "admin"
    val S3_SECRET_KEY = "miniopassword"
    val AWS_REGION = "us-east-1"

    val PG_TABLE = if (args.length > 0) args(0) else "yellow_tripdata"
    val ICEBERG_TABLE = if (args.length > 1) args(1) else "yellow_tripdata"
    val DATE_HOUR = if (args.length > 2) args(2) else null

    val spark = SparkSession.builder()
      .appName("[DataGate] Iceberg Partition By Day (Official API)")
      .config("spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

      .config(s"spark.sql.catalog.$CATALOG", "org.apache.iceberg.spark.SparkCatalog")
      .config(s"spark.sql.catalog.$CATALOG.type", "rest")
      .config(s"spark.sql.catalog.$CATALOG.uri", REST_URI)
      .config(s"spark.sql.catalog.$CATALOG.warehouse", WAREHOUSE)
      .config(s"spark.sql.catalog.$CATALOG.io-impl",
        "org.apache.iceberg.aws.s3.S3FileIO")

      .config(s"spark.sql.catalog.$CATALOG.s3.endpoint", S3_ENDPOINT)
      .config(s"spark.sql.catalog.$CATALOG.s3.path-style-access", "true")
      .config(s"spark.sql.catalog.$CATALOG.s3.access-key-id", S3_ACCESS_KEY)
      .config(s"spark.sql.catalog.$CATALOG.s3.secret-access-key", S3_SECRET_KEY)
      .config(s"spark.sql.catalog.$CATALOG.s3.region", AWS_REGION)
      .config(s"spark.sql.catalog.$CATALOG.s3.ssl-enabled", "false")
      
      // Also set global Hadoop S3A properties as a fallback for some internal Spark/Iceberg calls
      .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT)
      .config("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY)
      .config("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY)
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

      .config("spark.sql.shuffle.partitions", "8")
      .config("spark.default.parallelism", "8")

      .getOrCreate()

    try {

      spark.sql(s"CREATE NAMESPACE IF NOT EXISTS $CATALOG.$NAMESPACE")

      val jdbcOptions = new util.HashMap[String, String]()
      jdbcOptions.put("url", PG_JDBC)
      jdbcOptions.put("dbtable", PG_TABLE)
      jdbcOptions.put("user", PG_USER)
      jdbcOptions.put("password", PG_PASS)
      jdbcOptions.put("driver", PG_DRIVER)
      jdbcOptions.put("fetchsize", "10000")

      var df = spark.read
        .format("jdbc")
        .options(jdbcOptions)
        .load()

      val dropoffDatetimeCol =
        if (PG_TABLE.toLowerCase.contains("green"))
          "lpep_dropoff_datetime"
        else
          "tpep_dropoff_datetime"

      // date_hour dạng TIMESTAMP
      df = df.withColumn(
        "date_hour",
        date_trunc("hour", col(dropoffDatetimeCol))
      )

      if (DATE_HOUR != null) {
        df = df.filter(col("date_hour") === DATE_HOUR)
      }

      val fullTableName = s"$CATALOG.$NAMESPACE.$ICEBERG_TABLE"

      val tableExists =
        try {
          spark.table(fullTableName)
          true
        } catch {
          case _: Exception => false
        }

      if (!tableExists) {

        println("Creating Iceberg table partitioned by DAY(date_hour)...")

        df.writeTo(fullTableName)
          .tableProperty("write.target-file-size-bytes", "33554432")
          .tableProperty("write.distribution-mode", "hash")
          .partitionedBy(days(col("date_hour")))   // ✅ Official Iceberg transform
          .create()

      } else {

        println("Appending to existing Iceberg table...")

        df.writeTo(fullTableName).append()
      }

    } finally {
      spark.stop()
    }
  }
}