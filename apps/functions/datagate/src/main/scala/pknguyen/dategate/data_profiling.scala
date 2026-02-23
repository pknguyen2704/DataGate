package pknguyen.dategate

import org.apache.spark.sql.{Dataset, Row, SparkSession}
import org.apache.spark.storage.StorageLevel

import com.amazon.deequ.analyzers._
import com.amazon.deequ.analyzers.runners.{AnalysisRunner, AnomalyDetectionRunner} // (runner import optional)
import com.amazon.deequ.profiles.{ColumnProfilerRunner, ColumnProfiles}

object DataProfilingDeequ {

  // ===== Iceberg REST Catalog =====
  private val CATALOG   = "rest"
  private val REST_URI  = "http://iceberg-rest:8181"
  private val WAREHOUSE = "s3://lakehouse/"

  // ===== MinIO (S3 compatible) =====
  private val S3_ENDPOINT   = "http://minio:9000"
  private val S3_ACCESS_KEY = "admin"
  private val S3_SECRET_KEY = "miniopassword"
  private val AWS_REGION    = "us-east-1"

  def main(args: Array[String]): Unit = {
    val table =
      if (args != null && args.length > 0 && args(0).trim.nonEmpty) args(0).trim
      else "rest.bronze.yellow_tripdata"

    val spark = SparkSession.builder()
      .appName("[DataGate] Data profiling (Deequ)")

      // Iceberg extension
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

      // Catalog REST
      .config(s"spark.sql.catalog.$CATALOG", "org.apache.iceberg.spark.SparkCatalog")
      .config(s"spark.sql.catalog.$CATALOG.type", "rest")
      .config(s"spark.sql.catalog.$CATALOG.uri", REST_URI)
      .config(s"spark.sql.catalog.$CATALOG.warehouse", WAREHOUSE)

      // Iceberg S3FileIO
      .config(s"spark.sql.catalog.$CATALOG.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

      // MinIO S3 settings
      .config(s"spark.sql.catalog.$CATALOG.s3.endpoint", S3_ENDPOINT)
      .config(s"spark.sql.catalog.$CATALOG.s3.path-style-access", "true")
      .config(s"spark.sql.catalog.$CATALOG.s3.access-key-id", S3_ACCESS_KEY)
      .config(s"spark.sql.catalog.$CATALOG.s3.secret-access-key", S3_SECRET_KEY)
      .config(s"spark.sql.catalog.$CATALOG.s3.region", AWS_REGION)
      .config(s"spark.sql.catalog.$CATALOG.client.region", AWS_REGION)
      .config(s"spark.sql.catalog.$CATALOG.s3.ssl-enabled", "false")

      // optional perf
      .config(s"spark.sql.catalog.$CATALOG.s3.connection.maximum", "200")

      .getOrCreate()

    try {
      println(s"[INFO] Table: $table")

      // (optional) sanity
      spark.sql("SHOW CATALOGS").show(false)
      spark.sql(s"SHOW NAMESPACES IN $CATALOG").show(false)
      spark.sql(s"SHOW TABLES IN $CATALOG.bronze").show(false)

      // Load iceberg table
      val df: Dataset[Row] = spark.read.format("iceberg").load(table)

      // Cache to avoid recompute for multiple analyzers/profilers
      df.persist(StorageLevel.MEMORY_AND_DISK)

      df.printSchema()
      val rowCount = df.count()
      println(s"[INFO] Row count = $rowCount")

      // ==========================================================
      // A) Deequ Column Profiling (auto profile each column)
      // ==========================================================
      println("[INFO] Running Deequ ColumnProfilerRunner...")

      val profileResult = ColumnProfilerRunner()
        .onData(df)
        // .setRestrictToColumns(Seq("colA", "colB")) // nếu muốn giới hạn cột để nhanh hơn
        .run()

      // Print a readable summary
      // (profileResult.profiles là Seq[ColumnProfile]; toString khá dài, nhưng dùng được)
      profileResult.profiles.foreach { p =>
        println(s"[PROFILE] ${p.column} => ${p}")
      }

      // ==========================================================
      // B) Deequ Analyzer metrics (một số metrics phổ biến)
      // ==========================================================
      println("[INFO] Running Deequ AnalysisRunner (basic metrics)...")

      // Chọn 1 vài analyzers an toàn (không cần biết trước schema nhiều)
      val analysis = AnalysisRunner
        .onData(df)
        .addAnalyzer(Size())
        // Ví dụ: completeness cho TẤT CẢ columns (có thể hơi nặng nếu cột rất nhiều)
        .addAnalyzers(df.columns.toSeq.map(Completeness(_)))
        .run()

      // Convert metrics to Spark DF để show
      val metricsDf = AnalyzerContext.successMetricsAsDataFrame(spark, analysis)
      metricsDf.show(200, truncate = false)

      println("[INFO] Done profiling.")

      df.unpersist()

    } finally {
      spark.stop()
    }
  }
}