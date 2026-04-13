package datagate.experiment.batch

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.sql.Timestamp

object batch_ingestion_from_ps_to_bronze_layer {

  def main(args: Array[String]): Unit = {

    if (args.length < 11) {
      System.err.println(
        """
          |Usage:
          | <REST_URI>
          | <S3_ENDPOINT>
          | <S3_ACCESS_KEY>
          | <S3_SECRET_KEY>
          | <AWS_REGION>
          | <JDBC_URL>
          | <DB_USER>
          | <DB_PASSWORD>
          | <SOURCE_TABLE>
          | <TARGET_TABLE>
          | <INGEST_TIME> (yyyy-MM-dd HH or NONE)
        """.stripMargin)
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
    val INGEST_TIME    = args(10)

    val fullTableName = s"iceberg.$TARGET_TABLE"

    val spark = SparkSession.builder()
      .appName("Batch_Ingest_PS")

      // Iceberg Catalog configuration
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.rest.RESTCatalog")
      .config("spark.sql.catalog.iceberg.uri", REST_URI)

      // Storage (S3/MinIO) configuration
      .config("spark.sql.catalog.iceberg.s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
      .config("spark.sql.catalog.iceberg.s3.access-key-id", S3_ACCESS_KEY)
      .config("spark.sql.catalog.iceberg.s3.secret-access-key", S3_SECRET_KEY)
      .config("spark.sql.catalog.iceberg.s3.region", AWS_REGION)
      .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT)
      .config("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY)
      .config("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY)
      .config("spark.hadoop.fs.s3a.path.style.access", "true")

      // 🔥 OPTIMIZATION: distribution and file sizing
      .config("spark.sql.catalog.iceberg.write.distribution-mode", "hash")
      .config("spark.sql.files.maxRecordsPerFile", 1000000)

      .getOrCreate()

    import spark.implicits._

    // ==========================================
    // 1. Read source & Standardize (Lowercase)
    // ==========================================
    val rawDF = spark.read
      .format("jdbc")
      .option("url", JDBC_URL)
      .option("dbtable", SOURCE_TABLE)
      .option("user", DB_USER)
      .option("password", DB_PASSWORD)
      .load()

    val baseDF = rawDF.select(rawDF.columns.map(c => col(c).as(c.toLowerCase)): _*)

    val filteredDF =
      if (INGEST_TIME != "NONE") {
        val start = Timestamp.valueOf(INGEST_TIME + ":00:00")
        val end   = new Timestamp(start.getTime + 3600 * 1000)
        println(s"INFO: Filtering partition: $start → $end")
        baseDF.filter(col("tpep_dropoff_datetime") >= lit(start) && col("tpep_dropoff_datetime") < lit(end))
      } else {
        println("INFO: Performing full load (no filter)")
        baseDF
      }

    // We compute date_hour to align with Iceberg partitioning strategy
    val dfFinal = filteredDF
      .withColumn("date_hour", date_trunc("hour", col("tpep_dropoff_datetime")))
      .repartition(col("date_hour"))
      .sortWithinPartitions("date_hour")

    val rowCount = dfFinal.count()
    println(s"INFO: Records to write: $rowCount")
    
    if (rowCount > 0) {
      dfFinal.writeTo(fullTableName).append()
      println(s"SUCCESS: Data successfully written to $fullTableName")
    } else {
      println("WARN: No data found to ingest.")
    }

    spark.stop()
  }
}