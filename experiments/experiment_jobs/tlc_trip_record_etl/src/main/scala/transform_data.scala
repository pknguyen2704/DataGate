import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

import java.time.{Duration, Instant}

object transform_data {

  case class JobConfig(
                        source_table: String,
                        enriched_table: String,
                        trip_hourly_metrics_table: String,
                        location_hourly_metrics_table: String,
                        payment_hourly_metrics_table: String,
                        vendor_hourly_metrics_table: String
                      )

  private val job_name = "transform_data"

  def parse_args(args: Array[String]): JobConfig = {
    JobConfig(
      source_table = get_optional_arg(args, "source_table", "silver.cleaned_yellow_tripdata"),
      enriched_table = get_optional_arg(args, "enriched_table", "gold.yellow_tripdata_enriched"),
      trip_hourly_metrics_table = get_optional_arg(args, "trip_hourly_metrics_table", "gold.trip_hourly_metrics"),
      location_hourly_metrics_table = get_optional_arg(args, "location_hourly_metrics_table", "gold.location_hourly_metrics"),
      payment_hourly_metrics_table = get_optional_arg(args, "payment_hourly_metrics_table", "gold.payment_hourly_metrics"),
      vendor_hourly_metrics_table = get_optional_arg(args, "vendor_hourly_metrics_table", "gold.vendor_hourly_metrics")
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

  private def write_to_iceberg_partition_overwrite(df: DataFrame, target_table: String): Unit = {
    df.writeTo(s"iceberg.${target_table}")
      .overwritePartitions()
  }

  private def build_enriched_trip_data(df: DataFrame): DataFrame = {
    df
      .withColumn(
        "trip_duration_minutes",
        (
          unix_timestamp(col("tpep_dropoff_datetime")) -
            unix_timestamp(col("tpep_pickup_datetime"))
          ) / 60.0
      )
      .withColumn(
        "amount_per_mile",
        when(col("trip_distance") > 0, col("total_amount") / col("trip_distance"))
          .otherwise(lit(null).cast("double"))
      )
      .withColumn(
        "tip_rate",
        when(col("fare_amount") > 0, col("tip_amount") / col("fare_amount"))
          .otherwise(lit(null).cast("double"))
      )
      .select(
        col("vendorid"),
        col("tpep_pickup_datetime"),
        col("tpep_dropoff_datetime"),
        col("passenger_count"),
        col("trip_distance"),
        col("ratecodeid"),
        col("store_and_fwd_flag"),
        col("pulocationid"),
        col("dolocationid"),
        col("payment_type"),
        col("fare_amount"),
        col("extra"),
        col("mta_tax"),
        col("tip_amount"),
        col("tolls_amount"),
        col("improvement_surcharge"),
        col("total_amount"),
        col("congestion_surcharge"),
        col("airport_fee"),
        col("cbd_congestion_fee"),
        col("date_hour"),
        col("trip_duration_minutes"),
        col("amount_per_mile"),
        col("tip_rate")
      )
  }

  private def build_trip_hourly_metrics(enriched_df: DataFrame): DataFrame = {
    enriched_df
      .groupBy(col("date_hour"))
      .agg(
        count(lit(1)).cast("bigint").as("trip_count"),
        sum(col("passenger_count")).cast("bigint").as("total_passenger_count"),

        sum(col("trip_distance")).as("total_trip_distance"),
        avg(col("trip_distance")).as("avg_trip_distance"),

        sum(col("fare_amount")).as("total_fare_amount"),
        sum(col("tip_amount")).as("total_tip_amount"),
        sum(col("total_amount")).as("total_total_amount"),
        avg(col("total_amount")).as("avg_total_amount"),

        avg(col("trip_duration_minutes")).as("avg_trip_duration_minutes"),

        min(col("tpep_pickup_datetime")).as("min_pickup_datetime"),
        max(col("tpep_pickup_datetime")).as("max_pickup_datetime"),
        min(col("tpep_dropoff_datetime")).as("min_dropoff_datetime"),
        max(col("tpep_dropoff_datetime")).as("max_dropoff_datetime")
      )
  }

  private def build_location_hourly_metrics(enriched_df: DataFrame): DataFrame = {
    enriched_df
      .groupBy(
        col("date_hour"),
        col("pulocationid"),
        col("dolocationid")
      )
      .agg(
        count(lit(1)).cast("bigint").as("trip_count"),
        sum(col("passenger_count")).cast("bigint").as("total_passenger_count"),

        sum(col("trip_distance")).as("total_trip_distance"),
        avg(col("trip_distance")).as("avg_trip_distance"),

        sum(col("fare_amount")).as("total_fare_amount"),
        sum(col("tip_amount")).as("total_tip_amount"),
        sum(col("total_amount")).as("total_total_amount"),
        avg(col("total_amount")).as("avg_total_amount")
      )
  }

  private def build_payment_hourly_metrics(enriched_df: DataFrame): DataFrame = {
    enriched_df
      .groupBy(
        col("date_hour"),
        col("payment_type")
      )
      .agg(
        count(lit(1)).cast("bigint").as("trip_count"),
        sum(col("trip_distance")).as("total_trip_distance"),

        sum(col("fare_amount")).as("total_fare_amount"),
        sum(col("tip_amount")).as("total_tip_amount"),
        sum(col("total_amount")).as("total_total_amount"),
        avg(col("total_amount")).as("avg_total_amount"),

        avg(col("tip_rate")).as("avg_tip_rate")
      )
  }

  private def build_vendor_hourly_metrics(enriched_df: DataFrame): DataFrame = {
    enriched_df
      .groupBy(
        col("date_hour"),
        col("vendorid")
      )
      .agg(
        count(lit(1)).cast("bigint").as("trip_count"),
        sum(col("passenger_count")).cast("bigint").as("total_passenger_count"),

        sum(col("trip_distance")).as("total_trip_distance"),
        avg(col("trip_distance")).as("avg_trip_distance"),

        sum(col("fare_amount")).as("total_fare_amount"),
        sum(col("tip_amount")).as("total_tip_amount"),
        sum(col("total_amount")).as("total_total_amount"),
        avg(col("total_amount")).as("avg_total_amount")
      )
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
    println("[Transform Job] Starting transform data job")
    println(s"Source table: ${job_config.source_table}")
    println(s"Enriched table: ${job_config.enriched_table}")
    println(s"Trip hourly metrics table: ${job_config.trip_hourly_metrics_table}")
    println(s"Location hourly metrics table: ${job_config.location_hourly_metrics_table}")
    println(s"Payment hourly metrics table: ${job_config.payment_hourly_metrics_table}")
    println(s"Vendor hourly metrics table: ${job_config.vendor_hourly_metrics_table}")
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

      val read_start_time = start_timer("Read silver Iceberg table")
      val silver_df = read_from_iceberg(
        spark = spark,
        source_table = job_config.source_table
      )
      end_timer("Read silver Iceberg table", read_start_time)

      val enrich_start_time = start_timer("Build enriched trip data")
      val enriched_df = build_enriched_trip_data(silver_df)
      end_timer("Build enriched trip data", enrich_start_time)

      val trip_hourly_start_time = start_timer("Build trip hourly metrics")
      val trip_hourly_metrics_df = build_trip_hourly_metrics(enriched_df)
      end_timer("Build trip hourly metrics", trip_hourly_start_time)

      val location_start_time = start_timer("Build location hourly metrics")
      val location_hourly_metrics_df = build_location_hourly_metrics(enriched_df)
      end_timer("Build location hourly metrics", location_start_time)

      val payment_start_time = start_timer("Build payment hourly metrics")
      val payment_hourly_metrics_df = build_payment_hourly_metrics(enriched_df)
      end_timer("Build payment hourly metrics", payment_start_time)

      val vendor_start_time = start_timer("Build vendor hourly metrics")
      val vendor_hourly_metrics_df = build_vendor_hourly_metrics(enriched_df)
      end_timer("Build vendor hourly metrics", vendor_start_time)

      val write_enriched_start_time = start_timer("Write enriched trip data")
      write_to_iceberg_partition_overwrite(
        df = enriched_df,
        target_table = job_config.enriched_table
      )
      end_timer("Write enriched trip data", write_enriched_start_time)

      val write_trip_hourly_start_time = start_timer("Write trip hourly metrics")
      write_to_iceberg_partition_overwrite(
        df = trip_hourly_metrics_df,
        target_table = job_config.trip_hourly_metrics_table
      )
      end_timer("Write trip hourly metrics", write_trip_hourly_start_time)

      val write_location_start_time = start_timer("Write location hourly metrics")
      write_to_iceberg_partition_overwrite(
        df = location_hourly_metrics_df,
        target_table = job_config.location_hourly_metrics_table
      )
      end_timer("Write location hourly metrics", write_location_start_time)

      val write_payment_start_time = start_timer("Write payment hourly metrics")
      write_to_iceberg_partition_overwrite(
        df = payment_hourly_metrics_df,
        target_table = job_config.payment_hourly_metrics_table
      )
      end_timer("Write payment hourly metrics", write_payment_start_time)

      val write_vendor_start_time = start_timer("Write vendor hourly metrics")
      write_to_iceberg_partition_overwrite(
        df = vendor_hourly_metrics_df,
        target_table = job_config.vendor_hourly_metrics_table
      )
      end_timer("Write vendor hourly metrics", write_vendor_start_time)

      val job_end_time = Instant.now()
      val total_duration_ms = Duration.between(job_start_time, job_end_time).toMillis
      val total_duration_seconds = total_duration_ms / 1000.0

      println(s"[Performance] JOB END at ${job_end_time}")
      println(s"[Performance] TOTAL TIME: ${total_duration_ms} ms (${total_duration_seconds} seconds)")
      println("[Transform Job] Transform data job completed successfully")

    } finally {
      val stop_start_time = start_timer("Stop Spark session")
      spark.stop()
      end_timer("Stop Spark session", stop_start_time)
    }
  }
}