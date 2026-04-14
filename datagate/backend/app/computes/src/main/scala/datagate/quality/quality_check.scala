package datagate.quality

import com.amazon.deequ.VerificationSuite
import com.amazon.deequ.checks.{Check, CheckLevel, CheckStatus}
import com.amazon.deequ.constraints.ConstraintStatus
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

import java.sql.{Connection, DriverManager, ResultSet}
import java.time.LocalDateTime
import scala.collection.mutable.ListBuffer

case class Rule(id: Int, columnName: String, ruleType: String, ruleExpression: String)

object quality_check {

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
      .appName(s"[DATAGATE] Quality Check - $TABLE")
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

      // 1. Read Data
      val dfRaw = spark.table(fullTable)
        .where(col(partitionCol) > to_timestamp(lit(LAST_BATCH)) && col(partitionCol) <= to_timestamp(lit(CUR_BATCH)))

      if (dfRaw.count() == 0) {
        println("⚠️ No new data for quality check")
        return
      }

      // Fix Deequ Timestamp issues
      val df: DataFrame = dfRaw.select(
        dfRaw.columns.map { c =>
          dfRaw.schema(c).dataType match {
            case TimestampNTZType => col(c).cast("timestamp").as(c)
            case _ => col(c)
          }
        }: _*
      )

      // 2. Fetch Rules from Postgres
      Class.forName("org.postgresql.Driver")
      val conn: Connection = DriverManager.getConnection(PG_URL, PG_USER, PG_PASS)
      
      val rules = new ListBuffer[Rule]()
      val stmt = conn.prepareStatement("SELECT id, column_name, rule_type, rule_expression FROM active_rules WHERE table_name = ? AND is_active = true")
      stmt.setString(1, TABLE)
      val rs: ResultSet = stmt.executeQuery()
      while (rs.next()) {
        rules += Rule(rs.getInt(1), rs.getString(2), rs.getString(3), rs.getString(4))
      }
      rs.close()
      stmt.close()

      if (rules.isEmpty) {
        println(s"ℹ️ No active rules found for $TABLE")
        return
      }

      // 3. Build Deequ Check Suite
      var check = Check(CheckLevel.Error, s"Quality Check for $TABLE")

      rules.foreach { r =>
        r.ruleType.toLowerCase match {
          case "completeness" => check = check.hasCompleteness(r.columnName, _ >= 0.95, Some(s"Completeness of ${r.columnName} should be >= 0.95"))
          case "uniqueness"   => check = check.hasUniqueness(r.columnName, _ == 1.0)
          case "non-negative" => check = check.isNonNegative(r.columnName)
          case "contains-email" => check = check.containsEmail(r.columnName)
          case "min" => check = check.hasMin(r.columnName, _ >= r.ruleExpression.toDouble)
          case "max" => check = check.hasMax(r.columnName, _ <= r.ruleExpression.toDouble)
          case _ => println(s"⚠️ Unknown rule type: ${r.ruleType}")
        }
      }

      val verificationResult = VerificationSuite()
        .onData(df)
        .addCheck(check)
        .run()

      // 4. Save Results to Postgres
      conn.setAutoCommit(false)
      try {
        val batchTime = java.sql.Timestamp.valueOf(LocalDateTime.now())
        val checkStatus = if (verificationResult.status == CheckStatus.Success) "SUCCESS" else "FAILURE"
        
        val runSql = "INSERT INTO quality_check_runs (table_name, batch_time, partition_key, total_checks, failed_checks, status) VALUES (?, ?, ?, ?, ?, ?)"
        val runStmt = conn.prepareStatement(runSql, java.sql.Statement.RETURN_GENERATED_KEYS)
        runStmt.setString(1, TABLE)
        runStmt.setTimestamp(2, batchTime)
        runStmt.setString(3, CUR_BATCH)
        runStmt.setInt(4, rules.size)
        
        val failedCount = verificationResult.checkResults.values.flatMap(_.constraintResults).count(_.status != ConstraintStatus.Success)
        runStmt.setInt(5, failedCount)
        runStmt.setString(6, checkStatus)
        runStmt.executeUpdate()

        val runIdRs = runStmt.getGeneratedKeys
        runIdRs.next()
        val runId = runIdRs.getInt(1)
        runStmt.close()

        val resultSql = "INSERT INTO quality_check_results (run_id, column_name, rule_type, constraint_status, constraint_message, severity) VALUES (?, ?, ?, ?, ?, ?)"
        val resStmt = conn.prepareStatement(resultSql)

        verificationResult.checkResults.foreach { case (_, checkResult) =>
          checkResult.constraintResults.foreach { cr =>
            resStmt.setInt(1, runId)
            resStmt.setString(2, cr.constraint.toString.split("\\(").headOption.getOrElse("unknown")) // Simplistic parsing
            resStmt.setString(3, "DeequConstraint")
            resStmt.setString(4, cr.status.toString)
            resStmt.setString(5, cr.message.getOrElse(""))
            resStmt.setString(6, "Error")
            resStmt.addBatch()
          }
        }
        resStmt.executeBatch()
        resStmt.close()

        conn.commit()
        println(s"✅ Quality check complete for $TABLE. run_id=$runId, status=$checkStatus")

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
