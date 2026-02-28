package pknguyen.datagate

import com.amazon.deequ.profiles.{ColumnProfilerRunner, NumericColumnProfile}
import org.apache.spark.sql.SparkSession

object data_profiling {
  def main(args: Array[String]): Unit = {
    val JOB_NAME = "[DataGate] Data Profiling"
    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    val TABLE = "green_tripdata"
    val REST_URI = "http://iceberg-rest:8181"
    val WAREHOUSE = "s3://lakehouse/"

    // ===== MinIO (S3 compatible) =====
    val S3_ENDPOINT = "http://minio:9000"
    val S3_ACCESS_KEY = "admin"
    val S3_SECRET_KEY = "miniopassword"
    val AWS_REGION = "us-east-1"

    // Profiling mode
    val PROFILING_MODE = "table_level"
    val spark = SparkSession.builder()
      .appName(JOB_NAME)
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog." + CATALOG, "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog." + CATALOG + ".type", "rest")
      .config("spark.sql.catalog." + CATALOG + ".uri", REST_URI)
      .config("spark.sql.catalog." + CATALOG + ".warehouse", WAREHOUSE)
      .config("spark.sql.catalog." + CATALOG + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
      .config("spark.sql.catalog." + CATALOG + ".s3.endpoint", S3_ENDPOINT)
      .config("spark.sql.catalog." + CATALOG + ".s3.path-style-access", "true")
      .config("spark.sql.catalog." + CATALOG + ".s3.access-key-id", S3_ACCESS_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.secret-access-key", S3_SECRET_KEY)
      .config("spark.sql.catalog." + CATALOG + ".s3.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".client.region", AWS_REGION)
      .config("spark.sql.catalog." + CATALOG + ".s3.ssl-enabled", "false")
      .getOrCreate()
    try {
      val df = spark.table(s"$CATALOG.$NAMESPACE.$TABLE")
      df.show()

      // Profiling column level
      val result = ColumnProfilerRunner()
        .onData(df)
        .run()

      result.profiles.foreach { case (productName, profile) =>

        println(s"Column '$productName':\n " +
          s"\tcompleteness: ${profile.completeness}\n" +
          s"\tapproximate number of distinct values: ${profile.approximateNumDistinctValues}\n" +
          s"\tdatatype: ${profile.dataType}\n")
      }

      /* For numeric columns, we get descriptive statistics */
      val totalNumberProfile = result.profiles("totalNumber").asInstanceOf[NumericColumnProfile]

      println(s"Statistics of 'totalNumber':\n" +
        s"\tminimum: ${totalNumberProfile.minimum.get}\n" +
        s"\tmaximum: ${totalNumberProfile.maximum.get}\n" +
        s"\tmean: ${totalNumberProfile.mean.get}\n" +
        s"\tstandard deviation: ${totalNumberProfile.stdDev.get}\n")

      val statusProfile = result.profiles("status")

      /* For columns with a low number of distinct values, we get the full value distribution. */
      println("Value distribution in 'stats':")
      statusProfile.histogram.foreach {
        _.values.foreach { case (key, entry) =>
          println(s"\t$key occurred ${entry.absolute} times (ratio is ${entry.ratio})")
        }
      }
    } finally {
      spark.stop()
    }
  }
}
