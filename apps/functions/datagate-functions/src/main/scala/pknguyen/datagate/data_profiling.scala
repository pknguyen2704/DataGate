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
        // Insert into Postgres
        // ----------------------------

        Class.forName("org.postgresql.Driver")
        val conn: Connection = DriverManager.getConnection(PG_URL, PG_USER, PG_PASS)

        val sql =
          """
            INSERT INTO profile_runs
            (catalog, namespace, table_name, num_records, profile_json)
            VALUES (?, ?, ?, ?, ?::jsonb)
          """

        val stmt: PreparedStatement = conn.prepareStatement(sql)

        stmt.setString(1, CATALOG)
        stmt.setString(2, NAMESPACE)
        stmt.setString(3, TABLE)
        stmt.setLong(4, result.numRecords)
        stmt.setString(5, prettyJson)

        stmt.executeUpdate()

        stmt.close()
        conn.close()

        println("Profile inserted into Postgres successfully.")

      } finally {
        spark.stop()
      }
    }
}