package datagate.experiment.streaming

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object streaming_ingestion_ps_to_bronze_layer {

  def main(args: Array[String]): Unit = {

    if (args.length < 10) {
      System.err.println("Missing args")
      System.exit(1)
    }

    val REST_URI       = args(0)
    val S3_ENDPOINT    = args(1)
    val S3_ACCESS_KEY  = args(2)
    val S3_SECRET_KEY  = args(3)
    val AWS_REGION     = args(4)
    val JDBC_URL       = args(5)
    val DB_USER        = args(6)
    val DB_PASSWORD    = args(7)
    val SOURCE_TABLE   = args(8)
    val TARGET_TABLE   = args(9)

    val fullTableName = s"iceberg.$TARGET_TABLE"

    val spark = SparkSession.builder()
      .appName("Streaming_Ingest_PS")

      // Iceberg
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.rest.RESTCatalog")
      .config("spark.sql.catalog.iceberg.uri", REST_URI)

      // Iceberg S3
      .config("spark.sql.catalog.iceberg.s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
      .config("spark.sql.catalog.iceberg.s3.access-key-id", S3_ACCESS_KEY)
      .config("spark.sql.catalog.iceberg.s3.secret-access-key", S3_SECRET_KEY)
      .config("spark.sql.catalog.iceberg.s3.region", AWS_REGION)

      // Spark S3A
      .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT)
      .config("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY)
      .config("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY)
      .config("spark.hadoop.fs.s3a.path.style.access", "true")

      // optimize
      .config("spark.sql.catalog.iceberg.write.distribution-mode", "hash")
      .config("spark.sql.files.maxRecordsPerFile", 500000)

      .getOrCreate()

    import spark.implicits._

    println("🚀 Streaming started...")

    while (true) {

      val df = spark.read
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", SOURCE_TABLE)
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .load()

      val dfWithDateHour = df.withColumn(
        "date_hour",
        date_trunc("hour", col("tpep_dropoff_datetime"))
      )

      val dfFinal = dfWithDateHour
        .repartition(col("date_hour"))
        .sortWithinPartitions("date_hour")

      val count = dfFinal.count()
      println(s"Fetched $count rows")

      if (count > 0) {
        dfFinal.writeTo(fullTableName).append()
        println(s"Written $count rows")
      }

      Thread.sleep(60000)
    }
  }
}