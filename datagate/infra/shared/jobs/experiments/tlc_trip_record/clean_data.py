import argparse
import logging
from functools import reduce
from operator import or_
from datetime import datetime
from time import perf_counter

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "clean_bronze_to_silver"


TLC_COLUMNS = [
    "vendorid",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "ratecodeid",
    "store_and_fwd_flag",
    "pulocationid",
    "dolocationid",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee",
]

BATCH_COLUMNS = [
    "date_hour",
    "processing_date_hour",
]

EXPECTED_COLUMNS = TLC_COLUMNS + BATCH_COLUMNS

CRITICAL_NOT_NULL_COLUMNS = [
    "vendorid",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
    "pulocationid",
    "dolocationid",
    "fare_amount",
    "total_amount",
    "date_hour",
    "processing_date_hour",
]

BIGINT_COLUMNS = [
    "vendorid",
    "passenger_count",
    "ratecodeid",
    "pulocationid",
    "dolocationid",
    "payment_type",
]

DOUBLE_COLUMNS = [
    "trip_distance",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee",
]

DATETIME_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "date_hour",
    "processing_date_hour",
]

VALID_VENDOR_IDS = [1, 2, 6, 7]
VALID_RATECODE_IDS = [1, 2, 3, 4, 5, 6, 99]
VALID_PAYMENT_TYPES = [0, 1, 2, 3, 4, 5, 6]
VALID_STORE_AND_FWD_FLAGS = ["Y", "N"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Clean one processing_date_hour from bronze Iceberg table and write to silver Iceberg table"
    )

    parser.add_argument("--source_table", required=True)
    parser.add_argument("--target_table", required=True)
    parser.add_argument("--processing_date_hour", required=True)

    return parser.parse_args()


def build_spark_session():
    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .getOrCreate()
    )


def normalize_datetime_string(value):
    if value is None:
        raise ValueError("processing_date_hour must not be None.")

    value = str(value).strip().replace("T", " ")

    if value == "":
        raise ValueError("processing_date_hour must not be empty.")

    dt = datetime.fromisoformat(value)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_identifier_part(value, field_name):
    value = str(value).strip()

    if value == "":
        raise ValueError(f"{field_name} must not be empty.")

    for char in value:
        if not (char.isalnum() or char == "_"):
            raise ValueError(
                f"Invalid {field_name}: {value}. "
                "Only letters, numbers, and underscore (_) are allowed."
            )

    return value


def validate_table_identifier(table_name, field_name):
    table_name = str(table_name).strip()
    parts = table_name.split(".")

    if len(parts) not in (2, 3):
        raise ValueError(
            f"Invalid {field_name}: {table_name}. "
            "Expected format: schema.table or catalog.schema.table."
        )

    for part in parts:
        validate_identifier_part(part, field_name)

    return table_name


def get_spark_conf(spark, key, default_value=None):
    return spark.conf.get(key, default_value)


def resolve_table_name(table_name, iceberg_catalog):
    table_name = validate_table_identifier(table_name, "table_name")
    parts = table_name.split(".")

    if len(parts) == 3:
        return table_name

    return f"{iceberg_catalog}.{table_name}"


def normalize_column_names(df):
    renamed_df = df

    for old_col in df.columns:
        new_col = old_col.strip().lower()

        if old_col != new_col:
            renamed_df = renamed_df.withColumnRenamed(old_col, new_col)

    # Hỗ trợ nếu bronze đang dùng snake_case từ job cũ.
    rename_map = {
        "vendor_id": "vendorid",
        "ratecode_id": "ratecodeid",
    }

    for old_col, new_col in rename_map.items():
        if old_col in renamed_df.columns and new_col not in renamed_df.columns:
            renamed_df = renamed_df.withColumnRenamed(old_col, new_col)

    return renamed_df


def validate_expected_columns(df):
    missing_columns = [
        column_name
        for column_name in EXPECTED_COLUMNS
        if column_name not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing expected columns for Bronze -> Silver cleaning: {missing_columns}"
        )


def cast_columns(df):
    result_df = df

    for column_name in DATETIME_COLUMNS:
        result_df = result_df.withColumn(
            column_name,
            F.to_timestamp(F.col(column_name)),
        )

    for column_name in BIGINT_COLUMNS:
        result_df = result_df.withColumn(
            column_name,
            F.col(column_name).cast("bigint"),
        )

    for column_name in DOUBLE_COLUMNS:
        result_df = result_df.withColumn(
            column_name,
            F.col(column_name).cast("double"),
        )

    result_df = result_df.withColumn(
        "store_and_fwd_flag",
        F.upper(F.trim(F.col("store_and_fwd_flag").cast("string"))),
    )

    result_df = result_df.withColumn(
        "store_and_fwd_flag",
        F.when(
            F.col("store_and_fwd_flag").isin("", "<NA>", "NAN", "NONE", "NULL"),
            F.lit(None).cast("string"),
        ).otherwise(F.col("store_and_fwd_flag")),
    )

    result_df = result_df.withColumn(
        "ratecodeid",
        F.when(F.col("ratecodeid").isNull(), F.lit(99))
        .otherwise(F.col("ratecodeid")),
    )

    result_df = result_df.withColumn(
        "payment_type",
        F.when(F.col("payment_type").isNull(), F.lit(5))
        .otherwise(F.col("payment_type")),
    )

    return result_df


def build_invalid_condition(df):
    null_critical_condition = reduce(
        or_,
        [F.col(column_name).isNull() for column_name in CRITICAL_NOT_NULL_COLUMNS],
    )

    invalid_conditions = [
        null_critical_condition,

        F.col("tpep_dropoff_datetime") < F.col("tpep_pickup_datetime"),

        F.col("vendorid").isNotNull()
        & (~F.col("vendorid").isin(VALID_VENDOR_IDS)),

        F.col("ratecodeid").isNotNull()
        & (~F.col("ratecodeid").isin(VALID_RATECODE_IDS)),

        F.col("payment_type").isNotNull()
        & (~F.col("payment_type").isin(VALID_PAYMENT_TYPES)),

        F.col("store_and_fwd_flag").isNotNull()
        & (~F.col("store_and_fwd_flag").isin(VALID_STORE_AND_FWD_FLAGS)),

        F.col("trip_distance").isNotNull()
        & (F.col("trip_distance") < 0),

        F.col("passenger_count").isNotNull()
        & (F.col("passenger_count") < 0),

        F.col("pulocationid").isNotNull()
        & F.col("dolocationid").isNotNull()
        & (
            (F.col("pulocationid") <= 0)
            | (F.col("dolocationid") <= 0)
        ),

        F.col("fare_amount").isNotNull()
        & (F.col("fare_amount") < 0),

        F.col("total_amount").isNotNull()
        & (F.col("total_amount") < 0),
    ]

    return reduce(or_, invalid_conditions)


def clean_data(df):
    df = normalize_column_names(df)
    validate_expected_columns(df)

    df = cast_columns(df)

    invalid_condition = build_invalid_condition(df)

    cleaned_df = (
        df
        .filter(~invalid_condition)
        .dropDuplicates(EXPECTED_COLUMNS)
    )

    extra_columns = [
        column_name
        for column_name in cleaned_df.columns
        if column_name not in EXPECTED_COLUMNS
    ]

    return cleaned_df.select(EXPECTED_COLUMNS + extra_columns)


def read_bronze_batch(spark, source_table, processing_date_hour):
    sql = f"""
        SELECT *
        FROM {source_table}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """

    return spark.sql(sql)


def write_to_silver(df, target_table):
    (
        df.writeTo(target_table)
        .overwritePartitions()
    )


def main():
    start_time = perf_counter()

    args = parse_args()
    args.processing_date_hour = normalize_datetime_string(
        args.processing_date_hour
    )

    spark = build_spark_session()

    try:
        iceberg_catalog = get_spark_conf(
            spark=spark,
            key="datagate.iceberg.catalog",
            default_value="iceberg",
        )

        source_table = resolve_table_name(
            table_name=args.source_table,
            iceberg_catalog=iceberg_catalog,
        )

        target_table = resolve_table_name(
            table_name=args.target_table,
            iceberg_catalog=iceberg_catalog,
        )

        logger.info(
            "Reading bronze table=%s | processing_date_hour=%s",
            source_table,
            args.processing_date_hour,
        )

        bronze_df = read_bronze_batch(
            spark=spark,
            source_table=source_table,
            processing_date_hour=args.processing_date_hour,
        )

        before_count = bronze_df.count()

        silver_df = clean_data(bronze_df)

        after_count = silver_df.count()

        logger.info(
            "Clean result | before=%s | after=%s | removed=%s",
            before_count,
            after_count,
            before_count - after_count,
        )

        logger.info(
            "Writing silver table=%s | processing_date_hour=%s",
            target_table,
            args.processing_date_hour,
        )

        write_to_silver(
            df=silver_df,
            target_table=target_table,
        )

        total_seconds = perf_counter() - start_time

        logger.info(
            "[Job Completed] %s finished in %.3f seconds",
            JOB_NAME,
            total_seconds,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()