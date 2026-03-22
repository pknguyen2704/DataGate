package pknguyen.datagate

import com.amazon.deequ.profiles.ColumnProfilerRunner
import org.apache.spark.sql.SparkSession
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule

import java.io.File
import java.sql.{Connection, DriverManager, PreparedStatement}
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object data_profiling {

    def main(args: Array[String]): Unit = {

      val JOB_NAME = "[DataGate] Profiling"
      val CATALOG = "rest"
      val NAMESPACE = "bronze"
      val TABLE = "yellow_tripdata"
      val REST_URI = "http://iceberg-rest:8181"
      val WAREHOUSE = "s3://lakehouse/"

      val S3_ENDPOINT = "http://minio:9000"
      val S3_ACCESS_KEY = "admin"
      val S3_SECRET_KEY = "miniopassword"
      val AWS_REGION = "us-east-1"

      // Postgres config (bạn có thể chuyển sang env sau)
      val PG_URL = "jdbc:postgresql://datagate_database:5432/datagate"
      val PG_USER = "admin"
      val PG_PASS = "datagatepassword"

      val spark = SparkSession.builder()
        .appName(JOB_NAME)
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
        .config(s"spark.sql.catalog.$CATALOG.s3.ssl-enabled", "false")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()

      try {

        val df = spark.table(s"$CATALOG.$NAMESPACE.$TABLE")

        val result =
          ColumnProfilerRunner()
            .onData(df)
            .printStatusUpdates(true)
            .run()

        println(result)
        // ----------------------------
        // Convert to JSON
        // ----------------------------

        val mapper = new ObjectMapper()
        mapper.registerModule(DefaultScalaModule)

        val prettyJson =
          mapper.writerWithDefaultPrettyPrinter().writeValueAsString(result)

        // ----------------------------
        // Save JSON file
        // ----------------------------

        val timestamp = LocalDateTime.now()
          .format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))

        val outputPath =
          s"/opt/spark/work-dir/functions/datagate_profile_$timestamp.json"

        mapper.writeValue(new File(outputPath), result)

        println(s"\nJSON saved to: $outputPath\n")

        // ----------------------------
        // Insert into Postgres (Structured)
        // ----------------------------
        Class.forName("org.postgresql.Driver")
        val conn: Connection = DriverManager.getConnection(PG_URL, PG_USER, PG_PASS)
        conn.setAutoCommit(false) // Use transaction

        try {
          // 2. Insert Run Metadata
          val runSql = "INSERT INTO profile_runs (catalog, namespace, table_name, num_records, raw_json) VALUES (?, ?, ?, ?, ?::jsonb)"
          val runStmt = conn.prepareStatement(runSql, java.sql.Statement.RETURN_GENERATED_KEYS)
          runStmt.setString(1, CATALOG)
          runStmt.setString(2, NAMESPACE)
          runStmt.setString(3, TABLE)
          runStmt.setLong(4, result.numRecords)
          runStmt.setString(5, prettyJson)
          runStmt.executeUpdate()

          val rsRun = runStmt.getGeneratedKeys
          rsRun.next()
          val runPk = rsRun.getInt(1)
          runStmt.close()

          // 3. Insert Column Profiles
          result.profiles.foreach { case (colName, profile) =>
            val colSql =
              """
                INSERT INTO column_profiles
                (run_id, column_name, data_type, completeness, approx_distinct_values, mean, maximum, minimum, sum, std_dev)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              """
            val colStmt = conn.prepareStatement(colSql, java.sql.Statement.RETURN_GENERATED_KEYS)
            colStmt.setInt(1, runPk)
            colStmt.setString(2, colName)
            colStmt.setString(3, profile.dataType.toString)
            colStmt.setDouble(4, profile.completeness)
            colStmt.setLong(5, profile.approximateNumDistinctValues)

            // Extract numeric metrics if available
            import com.amazon.deequ.profiles.NumericColumnProfile
            profile match {
              case n: NumericColumnProfile =>
                colStmt.setObject(6, n.mean.getOrElse(null))
                colStmt.setObject(7, n.maximum.getOrElse(null))
                colStmt.setObject(8, n.minimum.getOrElse(null))
                colStmt.setObject(9, n.sum.getOrElse(null))
                colStmt.setObject(10, n.stdDev.getOrElse(null))
              case _ =>
                colStmt.setNull(6, java.sql.Types.DOUBLE)
                colStmt.setNull(7, java.sql.Types.DOUBLE)
                colStmt.setNull(8, java.sql.Types.DOUBLE)
                colStmt.setNull(9, java.sql.Types.DOUBLE)
                colStmt.setNull(10, java.sql.Types.DOUBLE)
            }
            colStmt.executeUpdate()

            val rsCol = colStmt.getGeneratedKeys
            rsCol.next()
            val colPk = rsCol.getInt(1)
            colStmt.close()

            // 4. Insert Histograms (if present)
            profile.histogram.foreach { hist =>
              val histSql = "INSERT INTO column_histograms (column_profile_id, bin_value, absolute_count, ratio) VALUES (?, ?, ?, ?)"
              val histStmt = conn.prepareStatement(histSql)
              hist.values.foreach { case (value, distValue) =>
                histStmt.setInt(1, colPk)
                histStmt.setString(2, value)
                histStmt.setLong(3, distValue.absolute)
                histStmt.setDouble(4, distValue.ratio)
                histStmt.addBatch()
              }
              histStmt.executeBatch()
              histStmt.close()
            }
          }

          conn.commit()
          println(s"Profile structured data saved to Postgres successfully (Run ID: $runPk)")

        } catch {
          case e: Exception =>
            conn.rollback()
            println(s"Error saving to Postgres: ${e.getMessage}")
            e.printStackTrace()
        } finally {
          conn.close()
        }

      } finally {
        spark.stop()
      }
    }
}