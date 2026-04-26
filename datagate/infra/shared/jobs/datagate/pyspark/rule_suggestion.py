import argparse
import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, List, Tuple

# PyDeequ requires SPARK_VERSION.
# Current Spark version: 3.5.x
os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.suggestions import ConstraintSuggestionRunner, DEFAULT

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, to_timestamp


JOB_NAME = "rule_suggestion"


@dataclass
class JobConfig:
    source_tables: List[str]
    date_hour: str
    output_format: str


def parse_args() -> JobConfig:
    parser = argparse.ArgumentParser(
        description="Run PyDeequ rule suggestions on silver/gold Iceberg tables by date_hour"
    )

    parser.add_argument(
        "--source_tables",
        required=True,
        help=(
            "Comma-separated Iceberg tables. "
            "Only silver and gold tables are allowed. "
            "Example: silver.cleaned_yellow_tripdata,gold.trip_hourly_metrics"
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

    for table in source_tables:
        validate_allowed_table(table)

    return source_tables


def parse_table_identifier(table_identifier: str) -> Tuple[str, str]:
    parts = table_identifier.split(".")

    if len(parts) != 2:
        raise ValueError(
            f"Invalid table identifier: {table_identifier}. "
            "Expected format: schema.table, for example silver.cleaned_yellow_tripdata"
        )

    schema_name = parts[0]
    table_name = parts[1]

    return schema_name, table_name


def validate_allowed_table(table_identifier: str) -> None:
    schema_name, _ = parse_table_identifier(table_identifier)

    allowed_schemas = {"silver", "gold"}

    if schema_name not in allowed_schemas:
        raise ValueError(
            f"Table {table_identifier} is not allowed. "
            "rule_suggestion only supports silver and gold tables."
        )


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

    validate_date_hour_column(
        df=df,
        source_table=source_table,
    )

    return df.filter(col("date_hour") == to_timestamp(lit(date_hour)))


def validate_date_hour_column(
    df: DataFrame,
    source_table: str,
) -> None:
    if "date_hour" not in df.columns:
        raise ValueError(
            f"Table {source_table} does not contain date_hour column. "
            "This rule suggestion job expects date_hour partition/filter column."
        )


def run_rule_suggestion(
    spark: SparkSession,
    df: DataFrame,
) -> Dict[str, Any]:
    return (
        ConstraintSuggestionRunner(spark)
        .onData(df)
        .addConstraintRule(DEFAULT())
        .run()
    )


def normalize_suggestions(
    suggestion_result: Dict[str, Any],
    source_table: str,
    date_hour: str,
) -> List[Dict[str, Any]]:
    suggestions = suggestion_result.get("constraint_suggestions", [])

    normalized_rows = []

    for suggestion in suggestions:
        normalized_rows.append(
            {
                "source_table": source_table,
                "date_hour": date_hour,
                "constraint_name": suggestion.get("constraint_name"),
                "column_name": suggestion.get("column_name"),
                "current_value": suggestion.get("current_value"),
                "description": suggestion.get("description"),
                "suggesting_rule": suggestion.get("suggesting_rule"),
                "rule_description": suggestion.get("rule_description"),
                "code_for_constraint": suggestion.get("code_for_constraint"),
            }
        )

    return normalized_rows


def print_json_result(
    source_table: str,
    rows: List[Dict[str, Any]],
) -> None:
    print("")
    print("=" * 100)
    print(f"[PyDeequ Rule Suggestion Result] {source_table}")
    print("=" * 100)
    print(json.dumps(rows, indent=2, ensure_ascii=False, default=str))


def print_table_result(
    spark: SparkSession,
    source_table: str,
    rows: List[Dict[str, Any]],
) -> None:
    print("")
    print("=" * 100)
    print(f"[PyDeequ Rule Suggestion Result] {source_table}")
    print("=" * 100)

    if not rows:
        print("No rule suggestions generated.")
        return

    result_df = spark.createDataFrame(rows)

    (
        result_df
        .select(
            "source_table",
            "date_hour",
            "column_name",
            "constraint_name",
            "current_value",
            "description",
            "suggesting_rule",
            "rule_description",
            "code_for_constraint",
        )
        .orderBy("source_table", "column_name", "constraint_name")
        .show(500, truncate=False)
    )


def suggest_rules_for_table(
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

    suggestion_result = run_rule_suggestion(
        spark=spark,
        df=df,
    )

    normalized_rows = normalize_suggestions(
        suggestion_result=suggestion_result,
        source_table=source_table,
        date_hour=date_hour,
    )

    if output_format == "table":
        print_table_result(
            spark=spark,
            source_table=source_table,
            rows=normalized_rows,
        )
        return

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
            suggest_rules_for_table(
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