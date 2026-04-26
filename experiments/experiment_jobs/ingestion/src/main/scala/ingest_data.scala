import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

import java.time.{Duration, Instant, LocalDate, LocalDateTime}
import java.time.format.DateTimeFormatter

object ingest_data {

  case class JobConfig(
                        jdbc_url: String,
                        source_db_user: String,
                        source_db_password: String,
                        source_table: String,
                        target_table: String,
                        ingestion_time: String
                      )

  private val job_name = "ingest_data"

  def parse_args(args: Array[String]): JobConfig = {
    JobConfig(
      jdbc_url = get_required_arg(args, "jdbc_url"),
      source_db_user = get_required_arg(args, "source_db_user"),
      source_db_password = get_required_arg(args, "source_db_password"),
      source_table = get_required_arg(args, "source_table"),
      target_table = get_required_arg(args, "target_table"),
      ingestion_time = get_optional_arg(args, "ingestion_time", "NONE")
    )
  }

  private def get_required_arg(args: Array[String], name: String): String = {
    val index = args.indexOf(s"--${name}")

    if (index == -1 || index + 1 >= args.length) {
      throw new IllegalArgumentException(s"Missing required argument: --${name}")
    }

    args(index + 1)
  }

  private def get_optional_arg(args: Array[String], name: String, default_value: String): String = {
    val index = args.indexOf(s"--${name}")

    if (index == -1 || index + 1 >= args.length) {
      default_value
    } else {
      args(index + 1)
    }
  }

  private def build_spark_session(config: JobConfig): SparkSession = {
    SparkSession.builder()
      .appName(job_name)
      .getOrCreate()
  }

  private def read_table_from_data_source(
                                           spark: SparkSession,
                                           job_config: JobConfig
                                         ): DataFrame = {
    val dbtable = build_source_query(job_config)

    spark.read
      .format("jdbc")
      .option("url", job_config.jdbc_url)
      .option("dbtable", dbtable)
      .option("user", job_config.source_db_user)
      .option("password", job_config.source_db_password)
      .option("driver", "org.postgresql.Driver")
      .option("fetchsize", "20000")
      .load()
  }

  private def build_source_query(job_config: JobConfig): String = {
    if (job_config.ingestion_time == "NONE") {
      return job_config.source_table
    }

    val start_time = get_start_time(job_config.ingestion_time)
    val end_time = get_end_time(job_config.ingestion_time, start_time)

    val start_time_sql = start_time.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
    val end_time_sql = end_time.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))

    s"""
       |(
       |  SELECT *
       |  FROM ${job_config.source_table}
       |  WHERE date_hour >= TIMESTAMP '${start_time_sql}'
       |    AND date_hour <  TIMESTAMP '${end_time_sql}'
       |) AS source_data
       |""".stripMargin
  }

  private def get_start_time(ingestion_time: String): LocalDateTime = {
    if (is_date_only(ingestion_time)) {
      val date = LocalDate.parse(
        ingestion_time,
        DateTimeFormatter.ofPattern("yyyy-MM-dd")
      )

      return date.atStartOfDay()
    }

    LocalDateTime.parse(
      ingestion_time,
      DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
    )
  }

  private def get_end_time(
                            ingestion_time: String,
                            start_time: LocalDateTime
                          ): LocalDateTime = {
    if (is_date_only(ingestion_time)) {
      return start_time.plusDays(1)
    }

    start_time.plusHours(1)
  }

  private def is_date_only(value: String): Boolean = {
    value.matches("\\d{4}-\\d{2}-\\d{2}")
  }

  private def convert_column_names_to_lower_case(df: DataFrame): DataFrame = {
    val new_columns = df.columns.map { column_name =>
      col(column_name).as(column_name.toLowerCase)
    }

    df.select(new_columns: _*)
  }

  private def transform_data(df: DataFrame): DataFrame = {
    convert_column_names_to_lower_case(df)
  }

  private def write_to_iceberg(df: DataFrame, target_table: String): Unit = {
    df.write
      .format("iceberg")
      .mode("append")
      .save(s"iceberg.${target_table}")
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
    println("[Experiment] Starting batch ingest job")
    println(s"Source table: ${job_config.source_table}")
    println(s"Target table: ${job_config.target_table}")
    println(s"Ingestion time: ${job_config.ingestion_time}")
  }

  def main(args: Array[String]): Unit = {
    val job_start_time = Instant.now()
    println(s"[Performance] JOB START at ${job_start_time}")

    val parse_start_time = start_timer("Parse arguments")
    val job_config = parse_args(args)
    end_timer("Parse arguments", parse_start_time)

    val spark_start_time = start_timer("Build Spark session")
    val spark = build_spark_session(job_config)
    end_timer("Build Spark session", spark_start_time)

    try {
      log_job_config(job_config)

      val read_plan_start_time = start_timer("Create PostgreSQL DataFrame")
      val source_df = read_table_from_data_source(
        spark = spark,
        job_config = job_config
      )
      end_timer("Create PostgreSQL DataFrame", read_plan_start_time)

      val transform_plan_start_time = start_timer("Create transform DataFrame")
      val transformed_df = transform_data(source_df)
      end_timer("Create transform DataFrame", transform_plan_start_time)

      val write_start_time = start_timer("Write data to Iceberg")
      write_to_iceberg(
        df = transformed_df,
        target_table = job_config.target_table
      )
      end_timer("Write data to Iceberg", write_start_time)

      val job_end_time = Instant.now()
      val total_duration_ms = Duration.between(job_start_time, job_end_time).toMillis
      val total_duration_seconds = total_duration_ms / 1000.0

      println(s"[Performance] JOB END at ${job_end_time}")
      println(s"[Performance] TOTAL TIME: ${total_duration_ms} ms (${total_duration_seconds} seconds)")
      println("Batch ingestion job completed successfully")

    } finally {
      val stop_start_time = start_timer("Stop Spark session")
      spark.stop()
      end_timer("Stop Spark session", stop_start_time)
    }
  }
}