package pknguyen.datagate

import org.apache.spark.sql.SparkSession
import com.amazon.deequ.suggestions.{ConstraintSuggestionRunner, Rules}
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule

import java.io.File
import java.sql.{Connection, DriverManager}
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import scala.collection.JavaConverters._

object constraints_suggestion {

  def main(args: Array[String]): Unit = {

    val JOB_NAME = "[DataGate] Constraints Suggestion"
    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    val TABLE = "yellow_tripdata"
    val REST_URI = "http://iceberg-rest:8181"
    val WAREHOUSE = "s3://lakehouse/"

    val S3_ENDPOINT = "http://minio:9000"
    val S3_ACCESS_KEY = "admin"
    val S3_SECRET_KEY = "miniopassword"
    val AWS_REGION = "us-east-1"

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

        val suggestionResult =
            ConstraintSuggestionRunner()
                .onData(df)
                .addConstraintRules(Rules.DEFAULT)
                .addConstraintRules(Rules.EXTENDED)
                .printStatusUpdates(true)
                .run()

        val suggestions =
            suggestionResult.constraintSuggestions.flatMap {
                case (column, suggestionSeq) =>
                suggestionSeq.map { suggestion =>
                    Map(
                    "column" -> column,
                    "description" -> suggestion.description,
                    "scalaCode" -> suggestion.codeForConstraint,
                    "constraintType" ->
                        suggestion.constraint.getClass.getSimpleName,
                    "constraint" ->
                        suggestion.constraint.toString
                    )
                }
            }.toSeq
      val resultJson =
        Map(
          "catalog" -> CATALOG,
          "namespace" -> NAMESPACE,
          "table" -> TABLE,
          "numRecords" -> df.count(),
          "constraints" -> suggestions
        )

      val mapper = new ObjectMapper()
      mapper.registerModule(DefaultScalaModule)

      val timestamp =
        LocalDateTime.now()
          .format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))

      val outputPath =
        s"/opt/spark/work-dir/functions/datagate_constraints_$timestamp.json"

      mapper.writerWithDefaultPrettyPrinter()
        .writeValue(new File(outputPath), resultJson)

      println(s"Constraint JSON saved to: $outputPath")

      // -----------------------------
      // Insert into Postgres
      // -----------------------------

      Class.forName("org.postgresql.Driver")
      val conn: Connection =
        DriverManager.getConnection(PG_URL, PG_USER, PG_PASS)

      val createTable =
        """
        CREATE TABLE IF NOT EXISTS constraint_suggestions (
            id BIGSERIAL PRIMARY KEY,
            catalog TEXT NOT NULL,
            namespace TEXT NOT NULL,
            table_name TEXT NOT NULL,
            suggestion_json JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """

      conn.createStatement().execute(createTable)

      val insertSql =
        """
        INSERT INTO constraint_suggestions
        (catalog, namespace, table_name, suggestion_json)
        VALUES (?, ?, ?, ?::jsonb)
        """

      val stmt = conn.prepareStatement(insertSql)
      stmt.setString(1, CATALOG)
      stmt.setString(2, NAMESPACE)
      stmt.setString(3, TABLE)
      stmt.setString(4,
        mapper.writeValueAsString(resultJson)
      )

      stmt.executeUpdate()
      stmt.close()
      conn.close()

      println("Constraint suggestions inserted into Postgres.")

    } finally {
      spark.stop()
    }
  }
}