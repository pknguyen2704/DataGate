package pknguyen.datagate

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

import java.util

object Load_from_ds_to_lakehouse {
  def main(args: Array[String]): Unit = {

    // Datasource connection
    val PG_JDBC = "jdbc:postgresql://data_source_postgres:5432/postgres"
    val PG_USER = "admin"
    val PG_PASS = "postgrespassword"
    val PG_DRIVER = "org.postgresql.Driver"

    // Lakehouse connection
    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    
    // Get table names from command line args
    // Usage: spark-submit <jar> [table_name] [table_target] [date_hour]
    // Defaults: yellow_tripdata yellow_tripdata null
    val PG_TABLE = if (args.length > 0) args(0) else "yellow_tripdata"
    val ICEBERG_TABLE = if (args.length > 1) args(1) else "yellow_tripdata"
    val REST_URI = "http://iceberg-rest:8181"
    val WAREHOUSE = "s3://lakehouse/"

    // ===== MinIO (S3 compatible) =====
    val S3_ENDPOINT = "http://minio:9000"
    val S3_ACCESS_KEY = "admin"
    val S3_SECRET_KEY = "miniopassword"
    val AWS_REGION = "us-east-1"

    // Job init
    val JOB_NAME = "[Experiment jobs] Load From DS to Lakehouse"
    val spark = SparkSession.builder()
      .appName(JOB_NAME)
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

      // Catalog REST
      .config("spark.sql.catalog." + CATALOG, "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog." + CATALOG + ".type", "rest")
      .config("spark.sql.catalog." + CATALOG + ".uri", REST_URI)
      .config("spark.sql.catalog." + CATALOG + ".warehouse", WAREHOUSE)

      // Iceberg S3FileIO
      .config("spark.sql.catalog." + CATALOG + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

      // Iceberg S3 settings (MinIO)
      .config("spark.sql.catalog." + CATALOG + ".s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog." + CATALOG + ".s3.path-style-access", "true")
      .config("spark.sql.catalog." + CATALOG + ".s3.access-key-id", S3_ACCESS_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.secret-access-key", S3_SECRET_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".client.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".s3.ssl-enabled", "false")
      .getOrCreate()

    try {
      println("[Experiment jobs] Start v2...")
      
      // Get date_hour parameter from command line args (args(2)), default to null (load all)
      val dateHour = if (args.length > 2) args(2) else null
      val fullTableName = CATALOG + "." + NAMESPACE + "." + ICEBERG_TABLE
      println(s"[Experiment jobs] Loading from table: $PG_TABLE -> $fullTableName")
      if (dateHour != null) {
        println(s"[Experiment jobs] Filtering by date_hour: $dateHour")
      } else {
        println("[Experiment jobs] No date_hour filter specified. Loading all data.")
      }
      
      val jdbcOptions: util.Map[String, String] = new util.HashMap[String, String]
      jdbcOptions.put("url", PG_JDBC)
      jdbcOptions.put("dbtable", PG_TABLE)
      jdbcOptions.put("user", PG_USER)
      jdbcOptions.put("password", PG_PASS)
      jdbcOptions.put("driver", PG_DRIVER)
      var df = spark.read.format("jdbc").options(jdbcOptions).load()
      
      // Determine which datetime column to use based on table type
      val dropoffDatetimeCol = if (PG_TABLE.toLowerCase.contains("green")) "lpep_dropoff_datetime" else "tpep_dropoff_datetime"
      
      // Add date_hour column extracted from the appropriate datetime column
      println(s"[Experiment jobs] Adding date_hour column from $dropoffDatetimeCol...")
      df = df.withColumn("date_hour", date_format(col(dropoffDatetimeCol), "yyyy-MM-dd HH:00:00"))
      
      // Filter by date_hour if specified
      if (dateHour != null) {
        println(s"[Experiment jobs] Applying date_hour filter: $dateHour")
        df = df.filter(col("date_hour") === dateHour)
        val filteredRowCount = df.count()
        println(s"[Experiment jobs] Filtered to $filteredRowCount rows for date_hour=$dateHour")
      }
      
      println("[Experiment jobs] Preview dataframe")
      df.show()

      // Create the table if not exists, otherwise append to the existing table
      var tableExists = true
      try {
        spark.sql(s"DESCRIBE TABLE $fullTableName")
      } catch {
        case _: Exception => tableExists = false
      }

      if (!tableExists) {
        println(s"[Experiment jobs] Table $fullTableName does not exist. Ensuring namespace and creating table...")
        // make sure the namespace exists (catalog + namespace)
        spark.sql(s"CREATE NAMESPACE IF NOT EXISTS $CATALOG.$NAMESPACE")
        df.writeTo(fullTableName).create()
        println(s"[Experiment jobs] Table $fullTableName created and data written.")
      } else {
        println(s"[Experiment jobs] Table $fullTableName exists. Appending data...")
        df.writeTo(fullTableName).append()
        println(s"[Experiment jobs] Data appended to $fullTableName.")
      }

    } finally {
      spark.stop()
    }
  }
}
