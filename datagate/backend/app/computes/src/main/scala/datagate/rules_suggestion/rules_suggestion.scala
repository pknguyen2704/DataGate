package datagate.rules_suggestion

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

import com.amazon.deequ.suggestions.{ConstraintSuggestionRunner, Rules}

import java.sql.{Connection, DriverManager}

object rules_suggestion {

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
      .appName("[DATAGATE] Rule Suggestion FINAL CLEAN")

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

      // =========================
      // AUTO DETECT PARTITION
      // =========================
      val dfAll = spark.table(fullTable)

      val partitionCol = Seq("date_hour", "pickup_date_hour")
        .find(dfAll.columns.contains)
        .getOrElse(
          throw new RuntimeException(
            s"❌ No partition column found: ${dfAll.columns.mkString(",")}"
          )
        )

      println(s"✅ Using partition column: $partitionCol")

      // =========================
      // INCREMENTAL DATA
      // =========================
      val dfRaw = dfAll.where(
        col(partitionCol) > to_timestamp(lit(LAST_BATCH)) &&
          col(partitionCol) <= to_timestamp(lit(CUR_BATCH))
      )

      val count = dfRaw.count()

      if (count == 0) {
        println("⚠️ No new data")
        return
      }

      println(s"📊 Rows for rule suggestion: $count")

      // =========================
      // FIX TimestampNTZ
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
      // SAMPLING
      // =========================
      val dfSample =
        if (count > 1000000) df.sample(0.2)
        else df

      // =========================
      // DEEQU SUGGESTION
      // =========================
      val suggestionResult =
        ConstraintSuggestionRunner()
          .onData(dfSample)
          .addConstraintRules(Rules.EXTENDED)
          .run()

      // =========================
      // SAVE DB
      // =========================
      Class.forName("org.postgresql.Driver")
      val conn: Connection = DriverManager.getConnection(PG_URL, PG_USER, PG_PASS)
      conn.setAutoCommit(false)

      try {

        // ===== INSERT INTO rule_suggestions =====
        val suggestionSql =
          """
          INSERT INTO rule_suggestions
          (table_name, column_name, rule_type, rule_expression)
          VALUES (?, ?, ?, ?)
          """

        val suggestionStmt = conn.prepareStatement(suggestionSql)

        // ===== UPSERT INTO active_rules =====
        val activeSql =
          """
          INSERT INTO active_rules
          (table_name, column_name, rule_type, rule_expression, frequency, last_seen)
          VALUES (?, ?, ?, ?, 1, now())
          ON CONFLICT (rule_expression)
          DO UPDATE SET
              frequency = active_rules.frequency + 1,
              last_seen = now();
          """

        val activeStmt = conn.prepareStatement(activeSql)

        // ===== LOOP RULES =====
        suggestionResult.constraintSuggestions.foreach {
          case (column, suggestions) =>

            suggestions.foreach { suggestion =>

              val ruleType = suggestion.constraint.getClass.getSimpleName
              val ruleExpr = suggestion.codeForConstraint

              // ---- INSERT suggestion ----
              suggestionStmt.setString(1, TABLE)
              suggestionStmt.setString(2, column)
              suggestionStmt.setString(3, ruleType)
              suggestionStmt.setString(4, ruleExpr)
              suggestionStmt.addBatch()

              // ---- UPSERT active ----
              activeStmt.setString(1, TABLE)
              activeStmt.setString(2, column)
              activeStmt.setString(3, ruleType)
              activeStmt.setString(4, ruleExpr)
              activeStmt.addBatch()
            }
        }

        suggestionStmt.executeBatch()
        activeStmt.executeBatch()

        conn.commit()

        println("✅ Rules saved + merged (clean version)")

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