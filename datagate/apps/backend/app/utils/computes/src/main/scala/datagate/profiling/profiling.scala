package datagate.profiling

import com.amazon.deequ.profiles.{ColumnProfilerRunner, NumericColumnProfile}
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule

import java.sql.{Connection, DriverManager}
import java.time.LocalDateTime

object profiling {

  def main(args: Array[String]): Unit = {

    val REST_URI   = args(0)
    val S3_ENDPOINT= args(1)
    val ACCESS_KEY = args(2)
    val SECRET_KEY = args(3)
    val REGION     = args(4)
    val TABLE      = args(5)
    val LAST_BATCH = args(6)
    val CUR_BATCH  = args(7)

    val PG_URL  = args(8)
    val PG_USER = args(9)
    val PG_PASS = args(10)

    val spark = SparkSession.builder()
      .appName("[DATAGATE] Profiling")

      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.rest.RESTCatalog")
      .config("spark.sql.catalog.iceberg.uri", REST_URI)

      .config("spark.sql.catalog.iceberg.s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog.iceberg.s3.access-key-id", ACCESS_KEY)
      .config("spark.sql.catalog.iceberg.s3.secret-access-key", SECRET_KEY)
      .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
      .config("spark.sql.catalog.iceberg.s3.region", REGION)

      .getOrCreate()

    try {

      val fullTable = s"iceberg.$TABLE"
      val partitionCol = "date_hour"

      // =========================
      // READ INCREMENTAL DATA
      // =========================
      val dfRaw = spark.table(fullTable)
        .where(
          col(partitionCol) > to_timestamp(lit(LAST_BATCH)) &&
            col(partitionCol) <= to_timestamp(lit(CUR_BATCH))
        )

      val count = dfRaw.count()

      if (count == 0) {
        println("⚠️ No new data")
        return
      }

      println(s"📊 Incremental rows: $count")

      // =========================
      // 🔥 FIX DEEQU TIMESTAMP
      // =========================
      val df: DataFrame = dfRaw.select(
        dfRaw.columns.map { c =>
          dfRaw.schema(c).dataType match {
            case TimestampNTZType => col(c).cast("timestamp").as(c)
            case _ => col(c)
          }
        }: _*
      )

      // =========================
      // PROFILING
      // =========================
      val result =
        ColumnProfilerRunner()
          .onData(df)
          .run()

      // =========================
      // FIX TIMESTAMP DB
      // =========================
      val batchTime = java.sql.Timestamp.valueOf(LocalDateTime.now())

      val mapper = new ObjectMapper()
      mapper.registerModule(DefaultScalaModule)
      val fullJson = mapper.writeValueAsString(result)

      // =========================
      // SAVE DB
      // =========================
      Class.forName("org.postgresql.Driver")
      val conn: Connection = DriverManager.getConnection(PG_URL, PG_USER, PG_PASS)
      conn.setAutoCommit(false)

      try {

        val runSql =
          """
          INSERT INTO profiling_runs
          (table_name, batch_time, partition_key, num_records, raw_json)
          VALUES (?, ?, ?, ?, ?::jsonb)
          """

        val runStmt = conn.prepareStatement(runSql, java.sql.Statement.RETURN_GENERATED_KEYS)

        runStmt.setString(1, TABLE)
        runStmt.setTimestamp(2, batchTime)
        runStmt.setString(3, CUR_BATCH)
        runStmt.setLong(4, result.numRecords)
        runStmt.setString(5, fullJson)

        runStmt.executeUpdate()

        val rs = runStmt.getGeneratedKeys
        rs.next()
        val runId = rs.getInt(1)
        runStmt.close()

        // =========================
        // COLUMN PROFILES
        // =========================
        val colSql =
          """
          INSERT INTO column_profiles
          (run_id, column_name, data_type, completeness, approx_distinct,
           mean, min, max, stddev)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          """

        val colStmt = conn.prepareStatement(colSql)

        result.profiles.foreach { case (name, profile) =>

          colStmt.setInt(1, runId)
          colStmt.setString(2, name)
          colStmt.setString(3, profile.dataType.toString)
          colStmt.setDouble(4, profile.completeness)
          colStmt.setLong(5, profile.approximateNumDistinctValues)

          profile match {
            case n: NumericColumnProfile =>
              colStmt.setObject(6, n.mean.orNull)
              colStmt.setObject(7, n.minimum.orNull)
              colStmt.setObject(8, n.maximum.orNull)
              colStmt.setObject(9, n.stdDev.orNull)
            case _ =>
              colStmt.setNull(6, java.sql.Types.DOUBLE)
              colStmt.setNull(7, java.sql.Types.DOUBLE)
              colStmt.setNull(8, java.sql.Types.DOUBLE)
              colStmt.setNull(9, java.sql.Types.DOUBLE)
          }

          colStmt.addBatch()
        }

        colStmt.executeBatch()
        colStmt.close()

        conn.commit()

        println(s"✅ Saved profiling run_id=$runId")

      } catch {
        case e: Exception =>
          conn.rollback()
          e.printStackTrace()
      } finally {
        conn.close()
      }

    } finally {
      spark.stop()
    }
  }
}