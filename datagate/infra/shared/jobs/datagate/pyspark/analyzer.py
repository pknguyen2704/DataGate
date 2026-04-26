import argparse
import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, List

# PyDeequ requires SPARK_VERSION.
# Current Spark version: 3.5.x
os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.analyzers import (
    AnalysisRunner,
    AnalyzerContext,
    Completeness,
    ApproxCountDistinct,
    Distinctness,
    Minimum,
    Maximum,
    Mean,
    StandardDeviation,
    MinLength,
    MaxLength,
)

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, to_timestamp
from pyspark.sql.types import (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
    StringType,
)


JOB_NAME = "data_analyzer"


@dataclass
class JobConfig:
    source_tables: List[str]
    date_hour: str
    output_format: str


def parse_args() -> JobConfig:
    parser = argparse.ArgumentParser(
        description="Run PyDeequ analyzers on multiple Iceberg tables by date_hour"
    )

    parser.add_argument(
        "--source_tables",
        required=True,
        help=(
            "Comma-separated Iceberg tables. "
            "Example: bronze.yellow_tripdata,silver.cleaned_yellow_tripdata,gold.trip_hourly_metrics"
        ),
    )

    parser.add_argument(
        "--date_hour",
        required=True,
        help="Processing date_hour, format: yyyy-MM-dd HH:mm:ss",
    )

    parser.add_argument(
        "--output_format",
        required=False,
        default="json",
        choices=["json", "table"],
    )

    args = parser.parse_args()

    source_tables = parse_source_tables(args.source_tables)

    return JobConfig(
        source_tables=source_tables,
        date_hour=args.date_hour,
        output_format=args.output_format,
    )


def parse_source_tables(source_tables_value: str) -> List[str]:
    source_tables = [
        table.strip()
        for table in source_tables_value.split(",")
        if table.strip()
    ]

    if not source_tables:
        raise ValueError("Missing source tables. Please provide --source_tables")

    return source_tables


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName(JOB_NAME)
        .getOrCreate()
    )


def read_from_iceberg(
    spark: SparkSession,
    source_table: str,
    date_hour: str,
) -> DataFrame:
    df = (
        spark.read
        .format("iceberg")
        .load(f"iceberg.{source_table}")
    )

    validate_date_hour_column(df=df, source_table=source_table)

    return df.filter(col("date_hour") == to_timestamp(lit(date_hour)))


def validate_date_hour_column(df: DataFrame, source_table: str) -> None:
    if "date_hour" not in df.columns:
        raise ValueError(
            f"Table {source_table} does not contain date_hour column. "
            "This analyzer job expects date_hour partition/filter column."
        )


def is_numeric_type(data_type: Any) -> bool:
    return isinstance(
        data_type,
        (
            ByteType,
            ShortType,
            IntegerType,
            LongType,
            FloatType,
            DoubleType,
            DecimalType,
        ),
    )


def is_string_type(data_type: Any) -> bool:
    return isinstance(data_type, StringType)


def build_analysis_runner(
    spark: SparkSession,
    df: DataFrame,
):
    analysis_runner = AnalysisRunner(spark).onData(df)

    for field in df.schema.fields:
        column_name = field.name
        data_type = field.dataType

        analysis_runner = add_common_column_analyzers(
            analysis_runner=analysis_runner,
            column_name=column_name,
        )

        if is_numeric_type(data_type):
            analysis_runner = add_numeric_column_analyzers(
                analysis_runner=analysis_runner,
                column_name=column_name,
            )

        if is_string_type(data_type):
            analysis_runner = add_string_column_analyzers(
                analysis_runner=analysis_runner,
                column_name=column_name,
            )

    return analysis_runner


def add_common_column_analyzers(
    analysis_runner,
    column_name: str,
):
    return (
        analysis_runner
        .addAnalyzer(Completeness(column_name))
        .addAnalyzer(ApproxCountDistinct(column_name))
        .addAnalyzer(Distinctness(column_name))
    )


def add_numeric_column_analyzers(
    analysis_runner,
    column_name: str,
):
    return (
        analysis_runner
        .addAnalyzer(Minimum(column_name))
        .addAnalyzer(Maximum(column_name))
        .addAnalyzer(Mean(column_name))
        .addAnalyzer(StandardDeviation(column_name))
    )


def add_string_column_analyzers(
    analysis_runner,
    column_name: str,
):
    return (
        analysis_runner
        .addAnalyzer(MinLength(column_name))
        .addAnalyzer(MaxLength(column_name))
    )


def run_analyzers(
    spark: SparkSession,
    df: DataFrame,
) -> DataFrame:
    analysis_runner = build_analysis_runner(
        spark=spark,
        df=df,
    )

    analysis_result = analysis_runner.run()

    return AnalyzerContext.successMetricsAsDataFrame(
        spark,
        analysis_result,
    )


def normalize_metric_rows(
    metric_rows: List[Dict[str, Any]],
    source_table: str,
    date_hour: str,
) -> List[Dict[str, Any]]:
    normalized_rows = []

    for row in metric_rows:
        normalized_rows.append(
            {
                "source_table": source_table,
                "date_hour": date_hour,
                "entity": row.get("entity"),
                "column_name": row.get("instance"),
                "metric_name": row.get("name"),
                "metric_value": row.get("value"),
            }
        )

    return normalized_rows


def print_json_result(
    source_table: str,
    rows: List[Dict[str, Any]],
) -> None:
    print("")
    print("=" * 100)
    print(f"[PyDeequ Analyzer Result] {source_table}")
    print("=" * 100)
    print(json.dumps(rows, indent=2, ensure_ascii=False, default=str))


def print_table_result(
    source_table: str,
    result_df: DataFrame,
) -> None:
    print("")
    print("=" * 100)
    print(f"[PyDeequ Analyzer Result] {source_table}")
    print("=" * 100)

    (
        result_df
        .orderBy("entity", "instance", "name")
        .show(500, truncate=False)
    )


def analyze_table(
    spark: SparkSession,
    source_table: str,
    date_hour: str,
    output_format: str,
) -> None:
    df = read_from_iceberg(
        spark=spark,
        source_table=source_table,
        date_hour=date_hour,
    )

    result_df = run_analyzers(
        spark=spark,
        df=df,
    )

    if output_format == "table":
        print_table_result(
            source_table=source_table,
            result_df=result_df,
        )
        return

    result_rows = [
        row.asDict()
        for row in result_df.collect()
    ]

    normalized_rows = normalize_metric_rows(
        metric_rows=result_rows,
        source_table=source_table,
        date_hour=date_hour,
    )

    print_json_result(
        source_table=source_table,
        rows=normalized_rows,
    )


def main() -> None:
    job_start_time = perf_counter()

    job_config = parse_args()
    spark = build_spark_session()

    try:
        for source_table in job_config.source_tables:
            analyze_table(
                spark=spark,
                source_table=source_table,
                date_hour=job_config.date_hour,
                output_format=job_config.output_format,
            )

        total_seconds = perf_counter() - job_start_time
        print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()