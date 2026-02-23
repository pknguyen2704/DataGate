package pknguyen.dategate

import org.apache.spark.sql.{Dataset, Row, SparkSession}
import org.apache.spark.storage.StorageLevel
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

import com.amazon.deequ.analyzers._
import com.amazon.deequ.analyzers.runners.{AnalysisRunner, AnalyzerContext}
import com.amazon.deequ.profiles.ColumnProfilerRunner
import com.amazon.deequ.metrics.Metric

object data_profiling {

  // ===== Iceberg REST Catalog =====
  private val CATALOG   = "rest"
  private val REST_URI  = "http://iceberg-rest:8181"
  private val WAREHOUSE = "s3://lakehouse/"

  // ===== MinIO (S3 compatible) =====
  private val S3_ENDPOINT   = "http://minio:9000"
  private val S3_ACCESS_KEY = "admin"
  private val S3_SECRET_KEY = "miniopassword"
  private val AWS_REGION    = "us-east-1"

  // ===== Deequ tuning knobs =====
  private val ENABLE_COLUMN_PROFILER = true
  private val ENABLE_HISTOGRAMS       = true
  private val HISTOGRAM_MAX_BINS      = 50

  private val ENABLE_PAIRWISE_CORR    = true
  private val MAX_CORR_PAIRS          = 10

  private val ENABLE_MUTUAL_INFO      = false
  private val MAX_MI_PAIRS            = 5

  private def timed[T](label: String)(f: => T): T = {
    val t0 = System.nanoTime()
    val out = f
    val ms = (System.nanoTime() - t0) / 1e6
    println(f"[TIME] $label: $ms%.0f ms")
    out
  }

  def main(args: Array[String]): Unit = {
    val jobT0 = System.nanoTime()

    val table =
      if (args != null && args.length > 0 && args(0).trim.nonEmpty) args(0).trim
      else "rest.bronze.yellow_tripdata"

    val spark = SparkSession.builder()
      .appName("[DataGate] Data profiling (Deequ)")
      .config("spark.sql.shuffle.partitions", "8")
      .config("spark.default.parallelism", "8")

      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

      .config(s"spark.sql.catalog.$CATALOG", "org.apache.iceberg.spark.SparkCatalog")
      .config(s"spark.sql.catalog.$CATALOG.type", "rest")
      .config(s"spark.sql.catalog.$CATALOG.uri", REST_URI)
      .config(s"spark.sql.catalog.$CATALOG.warehouse", WAREHOUSE)

      .config(s"spark.sql.catalog.$CATALOG.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

      .config(s"spark.sql.catalog.$CATALOG.s3.endpoint", S3_ENDPOINT)
      .config(s"spark.sql.catalog.$CATALOG.s3.path-style-access", "true")
      .config(s"spark.sql.catalog.$CATALOG.s3.access-key-id", S3_ACCESS_KEY)
      .config(s"spark.sql.catalog.$CATALOG.s3.secret-access-key", S3_SECRET_KEY)
      .config(s"spark.sql.catalog.$CATALOG.s3.region", AWS_REGION)
      .config(s"spark.sql.catalog.$CATALOG.client.region", AWS_REGION)
      .config(s"spark.sql.catalog.$CATALOG.s3.ssl-enabled", "false")

      .config(s"spark.sql.catalog.$CATALOG.s3.connection.maximum", "200")
      .getOrCreate()

    try {
      println(s"[INFO] Table: $table")

      timed("SHOW CATALOGS / NAMESPACES / TABLES") {
        spark.sql("SHOW CATALOGS").show(false)
        spark.sql(s"SHOW NAMESPACES IN $CATALOG").show(false)
        spark.sql(s"SHOW TABLES IN $CATALOG.bronze").show(false)
      }

      val rawDf: Dataset[Row] = timed("Load Iceberg table") {
        spark.read.format("iceberg").load(table)
      }

      rawDf.printSchema()

      timed("Persist DF") {
        rawDf.persist(StorageLevel.MEMORY_AND_DISK)
        rawDf.take(1)
      }

      val fields = rawDf.schema.fields.toSeq
      val allCols = fields.map(_.name)

      val numericCols = fields.collect { case StructField(name, _: NumericType, _, _) => name }
      val stringCols  = fields.collect { case StructField(name, StringType, _, _) => name }
      val dateTimeCols = fields.collect {
        case StructField(name, DateType, _, _) => name
        case StructField(name, TimestampType, _, _) => name
      }

      println(s"[INFO] Columns: total=${allCols.size}, numeric=${numericCols.size}, string=${stringCols.size}, datetime=${dateTimeCols.size}")

      // ==========================================================
      // A) ColumnProfilerRunner
      // ==========================================================
      if (ENABLE_COLUMN_PROFILER) {
        val profileResult = timed("Deequ ColumnProfilerRunner") {
          ColumnProfilerRunner().onData(rawDf).run()
        }
        profileResult.profiles.foreach { case (col, prof) =>
          println(s"[PROFILE] $col => $prof")
        }
      } else {
        println("[INFO] ColumnProfilerRunner disabled.")
      }

      // ==========================================================
      // B) Analyzer set (compatible Deequ 2.0.13)
      // ==========================================================

      // Tạo thêm length columns cho string để tính mean/min/max length (thay AverageLength)
      val lenCols: Seq[(String, String)] = stringCols.map { c =>
        val lenName = s"__len__$c"
        (c, lenName)
      }

      val df = lenCols.foldLeft(rawDf) { case (acc, (c, lenName)) =>
        acc.withColumn(lenName, length(col(c)).cast("double"))
      }

      val analyzers = scala.collection.mutable.ArrayBuffer.empty[Analyzer[_, Metric[_]]]

      // Dataset-level
      analyzers += Size()

      // Generic per-column
      allCols.foreach { c =>
        analyzers += Completeness(c)
        analyzers += ApproxCountDistinct(c)
        analyzers += Distinctness(c)
        analyzers += Uniqueness(Seq(c))
        analyzers += Entropy(c)
      }

      // String-only metrics
      stringCols.foreach { c =>
        analyzers += MinLength(c)
        analyzers += MaxLength(c)

        // Mean length via helper column
        val lenName = s"__len__$c"
        analyzers += Mean(lenName)
        analyzers += StandardDeviation(lenName)

        if (ENABLE_HISTOGRAMS) {
          // ✅ đúng signature: Histogram(col, binningUdfOpt, maxBins)
          analyzers += Histogram(c, None, HISTOGRAM_MAX_BINS)
        }
      }

      // Numeric-only
      numericCols.foreach { c =>
        analyzers += Minimum(c)
        analyzers += Maximum(c)
        analyzers += Mean(c)
        analyzers += Sum(c)
        analyzers += StandardDeviation(c)
        analyzers += ApproxQuantile(c, 0.5)
        analyzers += ApproxQuantile(c, 0.95)

        if (ENABLE_HISTOGRAMS) {
          analyzers += Histogram(c, None, HISTOGRAM_MAX_BINS)
        }
      }

      // Pairwise correlation (giới hạn)
      if (ENABLE_PAIRWISE_CORR && numericCols.size >= 2) {
        val pairs = numericCols.combinations(2).take(MAX_CORR_PAIRS).toSeq
        pairs.foreach { case Seq(a, b) => analyzers += Correlation(a, b) }
        println(s"[INFO] Correlation pairs added: ${pairs.size}")
      }

      if (ENABLE_MUTUAL_INFO && allCols.size >= 2) {
        val pairs = allCols.combinations(2).take(MAX_MI_PAIRS).toSeq
        pairs.foreach { case Seq(a, b) => analyzers += MutualInformation(a, b) }
        println(s"[INFO] MutualInformation pairs added: ${pairs.size}")
      }

      println(s"[INFO] Total analyzers = ${analyzers.size}")

      val analysisContext = timed("Deequ AnalysisRunner (all analyzers)") {
        AnalysisRunner.onData(df).addAnalyzers(analyzers.toSeq).run()
      }

      timed("AnalyzerContext.successMetricsAsDataFrame + show") {
        val mdf = AnalyzerContext.successMetricsAsDataFrame(spark, analysisContext)
        mdf.show(500, truncate = false)
      }

      timed("Unpersist DF") {
        rawDf.unpersist()
      }

      val totalMs = (System.nanoTime() - jobT0) / 1e6
      println(f"[TIME] TOTAL JOB: $totalMs%.0f ms")

    } finally {
      spark.stop()
    }
  }
}