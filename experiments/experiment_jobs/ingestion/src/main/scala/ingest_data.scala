import org.apache.spark.sql.SparkSession

object ingest_data {

  def main(args: Array[String]): Unit = {
    val job_name = "ingest_data"

    val spark = SparkSession.builder()
      .config()
  }
}
