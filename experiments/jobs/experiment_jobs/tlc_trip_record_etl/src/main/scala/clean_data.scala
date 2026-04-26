import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

import java.time.{Duration, Instant}

object clean_data {

  case class JobConfig(
                        source_table: String,
                        target_table: String
                      )

  private val job_name = "clean_data"

  def parse_args(args: Array[String]): JobConfig = {
    JobConfig(
      source_table = get_optional_arg(args, "source_table", "bronze.yellow_tripdata"),
      target_table = get_optional_arg(args, "target_table", "silver.cleaned_yellow_tripdata")
    )
  }

  private def get_optional_arg(args: Array[String], name: String, default_value: String): String = {
    val index = args.indexOf(s"--${name}")

    if (index == -1 || index + 1 >= args.length) {
      default_value
    } else {
      args(index + 1)
    }
  }

  private def build_spark_session(): SparkSession = {
    SparkSession.builder()
      .appName(job_name)
      .getOrCreate()
  }

  private def read_from_iceberg(spark: SparkSession, source_table: String): DataFrame = {
    spark.read
      .format("iceberg")
      .load(s"iceberg.${source_table}")
  }

  private def write_to_iceberg(df: DataFrame, target_table: String): Unit = {
    df.write
      .format("iceberg")
      .mode("append")
      .save(s"iceberg.${target_table}")
  }

  private def clean_data(df: DataFrame): DataFrame = {
    df
      // Loại bỏ các dòng thiếu dữ liệu bắt buộc
      .filter(col("vendorid").isNotNull)
      .filter(col("tpep_pickup_datetime").isNotNull)
      .filter(col("tpep_dropoff_datetime").isNotNull)
      .filter(col("trip_distance").isNotNull)
      .filter(col("fare_amount").isNotNull)
      .filter(col("total_amount").isNotNull)
      .filter(col("date_hour").isNotNull)

      // Làm sạch thời gian chuyến đi
      .filter(col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime"))

      // Làm sạch số lượng hành khách
      .filter(col("passenger_count").isNull || col("passenger_count") >= 0)
      .filter(col("passenger_count").isNull || col("passenger_count") <= 8)

      // Làm sạch khoảng cách chuyến đi
      .filter(col("trip_distance") > 0)

      // Làm sạch mã location
      .filter(col("pulocationid").isNull || col("pulocationid") > 0)
      .filter(col("dolocationid").isNull || col("dolocationid") > 0)

      // Làm sạch các trường tiền
      .filter(col("fare_amount") >= 0)
      .filter(col("extra").isNull || col("extra") >= 0)
      .filter(col("mta_tax").isNull || col("mta_tax") >= 0)
      .filter(col("tip_amount").isNull || col("tip_amount") >= 0)
      .filter(col("tolls_amount").isNull || col("tolls_amount") >= 0)
      .filter(col("improvement_surcharge").isNull || col("improvement_surcharge") >= 0)
      .filter(col("total_amount") >= 0)
      .filter(col("congestion_surcharge").isNull || col("congestion_surcharge") >= 0)
      .filter(col("airport_fee").isNull || col("airport_fee") >= 0)
      .filter(col("cbd_congestion_fee").isNull || col("cbd_congestion_fee") >= 0)

      // Chuẩn hóa string flag nhưng vẫn giữ nguyên cột cũ
      .withColumn("store_and_fwd_flag", trim(col("store_and_fwd_flag")))

      // Loại bỏ dòng trùng hoàn toàn
      .dropDuplicates()
  }

  private def start_timer(step_name: String): Instant = {
    val start_time = Instant.now()
    println(s"[Performance] START - ${step_name} at ${start_time}")
    start_time
  }

  private def end_timer(step_name: String, start_time: Instant): Unit = {
    val end_time = Instant.now()
    val duration_ms = Duration.between(start_time, end_time).toMillis
    val duration_seconds = duration_ms / 1000.0

    println(s"[Performance] END   - ${step_name} at ${end_time}")
    println(s"[Performance] TIME  - ${step_name}: ${duration_ms} ms (${duration_seconds} seconds)")
  }

  private def log_job_config(job_config: JobConfig): Unit = {
    println("[Clean Job] Starting clean data job")
    println(s"Source table: ${job_config.source_table}")
    println(s"Target table: ${job_config.target_table}")
  }

  def main(args: Array[String]): Unit = {
    val job_start_time = Instant.now()
    println(s"[Performance] JOB START at ${job_start_time}")

    val parse_start_time = start_timer("Parse arguments")
    val job_config = parse_args(args)
    end_timer("Parse arguments", parse_start_time)

    val spark_start_time = start_timer("Build Spark session")
    val spark = build_spark_session()
    end_timer("Build Spark session", spark_start_time)

    try {
      log_job_config(job_config)

      val read_start_time = start_timer("Read bronze Iceberg table")
      val bronze_df = read_from_iceberg(
        spark = spark,
        source_table = job_config.source_table
      )
      end_timer("Read bronze Iceberg table", read_start_time)

      val clean_start_time = start_timer("Clean bronze data")
      val cleaned_df = clean_data(bronze_df)
      end_timer("Clean bronze data", clean_start_time)

      val write_start_time = start_timer("Write cleaned data to silver Iceberg table")
      write_to_iceberg(
        df = cleaned_df,
        target_table = job_config.target_table
      )
      end_timer("Write cleaned data to silver Iceberg table", write_start_time)

      val job_end_time = Instant.now()
      val total_duration_ms = Duration.between(job_start_time, job_end_time).toMillis
      val total_duration_seconds = total_duration_ms / 1000.0

      println(s"[Performance] JOB END at ${job_end_time}")
      println(s"[Performance] TOTAL TIME: ${total_duration_ms} ms (${total_duration_seconds} seconds)")
      println("[Clean Job] Clean data job completed successfully")

    } finally {
      val stop_start_time = start_timer("Stop Spark session")
      spark.stop()
      end_timer("Stop Spark session", stop_start_time)
    }
  }
}