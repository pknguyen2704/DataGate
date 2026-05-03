import argparse
import hashlib
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List, Tuple

# PyDeequ requires SPARK_VERSION.
os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.suggestions import ConstraintSuggestionRunner, DEFAULT
from py4j.protocol import Py4JJavaError

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, count, lit, to_timestamp


JOB_NAME = "rule_suggestion"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SUGGESTION_TO_CONSTRAINT_TYPE = {
    "CompleteIfCompleteRule": "not_null",
    "RetainCompletenessRule": "not_null",
    "NonNegativeNumbersRule": "non_negative",
    "UniqueIfApproximatelyUniqueRule": "unique",
    "CategoricalRangeRule": "value_range",
    "FractionalCategoricalRangeRule": "value_range",
}


@dataclass
class JobConfig:
    source_tables: List[str]
    date_hour: str
    output_format: str
    iceberg_catalog: str
    datagate_db_conn_id: str
    datagate_jdbc_url: str | None
    datagate_db_user: str | None
    datagate_db_password: str | None


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
    parser.add_argument("--date_hour", required=True, help="Processing date_hour, format: yyyy-MM-dd HH:mm:ss")
    parser.add_argument("--output_format", required=False, default="json", choices=["json", "table"])
    parser.add_argument("--iceberg_catalog", required=False, default="iceberg")
    parser.add_argument("--datagate_db_conn_id", required=False, default="datagate_db_default")
    parser.add_argument("--datagate_jdbc_url", required=False, default=os.getenv("DATAGATE_JDBC_URL"))
    parser.add_argument("--datagate_db_user", required=False, default=os.getenv("DATAGATE_DB_USER"))
    parser.add_argument("--datagate_db_password", required=False, default=os.getenv("DATAGATE_DB_PASSWORD"))

    args = parser.parse_args()
    source_tables = parse_source_tables(args.source_tables)

    return JobConfig(
        source_tables=source_tables,
        date_hour=args.date_hour,
        output_format=args.output_format,
        iceberg_catalog=args.iceberg_catalog,
        datagate_db_conn_id=args.datagate_db_conn_id,
        datagate_jdbc_url=args.datagate_jdbc_url,
        datagate_db_user=args.datagate_db_user,
        datagate_db_password=args.datagate_db_password,
    )


def parse_source_tables(source_tables_value: str) -> List[str]:
    source_tables = [table.strip() for table in source_tables_value.split(",") if table.strip()]
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
    return parts[0], parts[1]


def validate_allowed_table(table_identifier: str) -> None:
    schema_name, _ = parse_table_identifier(table_identifier)
    if schema_name not in {"bronze", "silver", "gold"}:
        raise ValueError(
            f"Table {table_identifier} is not allowed. "
            "rule_suggestion only supports bronze, silver, and gold tables."
        )


def build_spark_session() -> SparkSession:
    return SparkSession.builder.appName(JOB_NAME).getOrCreate()


def read_from_iceberg(
    spark: SparkSession,
    iceberg_catalog: str,
    source_table: str,
    date_hour: str,
) -> DataFrame:
    df = spark.read.format("iceberg").load(f"{iceberg_catalog}.{source_table}")
    batch_column = resolve_batch_filter_column(df=df, source_table=source_table)
    return df.filter(col(batch_column) == to_timestamp(lit(date_hour)))


def resolve_batch_filter_column(df: DataFrame, source_table: str) -> str:
    if "processing_date_hour" in df.columns:
        return "processing_date_hour"
    if "date_hour" in df.columns:
        return "date_hour"
    raise ValueError(
        f"Table {source_table} does not contain processing_date_hour or date_hour column. "
        "This rule suggestion job expects a batch timestamp column."
    )


def sanitize_dataframe_for_rule_suggestion(df: DataFrame, source_table: str) -> DataFrame:
    excluded_columns = {"date_hour", "processing_date_hour"}
    candidate_columns = [column_name for column_name in df.columns if column_name not in excluded_columns]

    if not candidate_columns:
        logger.info("%s has no candidate columns for rule suggestion after excluding technical columns", source_table)
        return df.select()

    if not df.take(1):
        logger.info("%s has no rows for the requested date_hour", source_table)
        return df.select(*candidate_columns)

    non_null_counts = (
        df.agg(*[count(col(column_name)).alias(column_name) for column_name in candidate_columns])
        .collect()[0]
        .asDict()
    )
    retained_columns = [
        column_name
        for column_name in candidate_columns
        if (non_null_counts.get(column_name) or 0) > 0
    ]
    dropped_columns = [column_name for column_name in candidate_columns if column_name not in retained_columns]

    if dropped_columns:
        logger.info(
            "%s dropped all-null columns before rule suggestion: %s",
            source_table,
            ", ".join(dropped_columns),
        )

    if not retained_columns:
        logger.info("%s has no non-null business columns for rule suggestion", source_table)
        return df.select()

    return df.select(*retained_columns)


def run_rule_suggestion(spark: SparkSession, df: DataFrame) -> Dict[str, Any]:
    return ConstraintSuggestionRunner(spark).onData(df).addConstraintRule(DEFAULT()).run()


def truncate(value: Any, max_length: int) -> str | None:
    if value is None:
        return None
    text = str(value)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def extract_value_range_metadata(suggestion: Dict[str, Any]) -> tuple[str | None, float | None]:
    code = suggestion.get("code_for_constraint") or ""

    values_match = re.search(r"\[(.*?)\]", code)
    raw_values = values_match.group(1) if values_match else ""
    values = [value.strip().strip('"') for value in raw_values.split(",") if value.strip()]

    threshold_match = re.search(r"x\s*>=\s*([0-9.]+)", code)
    threshold_min = float(threshold_match.group(1)) if threshold_match else None

    return (json.dumps(values, ensure_ascii=False) if values else None, threshold_min)


def normalize_constraint_name(column_name: str, constraint_type: str) -> str:
    suffix = {
        "not_null": "not_null",
        "non_negative": "non_negative",
        "unique": "unique",
        "value_range": "value_range",
    }.get(constraint_type, "rule")
    return f"{column_name}_{suffix}"


def build_rule_signature(
    column_name: str,
    constraint_type: str,
    value_set: str | None,
    regex_pattern: str | None,
    threshold_min: float | None,
    threshold_max: float | None,
) -> str:
    payload = {
        "column_name": column_name,
        "constraint_type": constraint_type,
        "value_set": value_set or "",
        "regex_pattern": regex_pattern or "",
        "threshold_min": threshold_min,
        "threshold_max": threshold_max,
    }
    return hashlib.md5(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def normalize_suggestions(
    suggestion_result: Dict[str, Any],
    source_table: str,
    date_hour: str,
) -> List[Dict[str, Any]]:
    suggestions = suggestion_result.get("constraint_suggestions", [])
    normalized_rows = []

    for suggestion in suggestions:
        suggesting_rule = suggestion.get("suggesting_rule") or ""
        rule_name = suggesting_rule.split("(")[0]
        constraint_type = SUGGESTION_TO_CONSTRAINT_TYPE.get(rule_name)
        if not constraint_type:
            continue

        column_name = suggestion.get("column_name")
        value_set = None
        threshold_min = None
        if constraint_type == "value_range":
            value_set, threshold_min = extract_value_range_metadata(suggestion)

        normalized_rows.append(
            {
                "source_table": source_table,
                "date_hour": date_hour,
                "constraint_name": normalize_constraint_name(column_name, constraint_type),
                "column_name": column_name,
                "constraint_type": constraint_type,
                "current_value": truncate(suggestion.get("current_value"), 255),
                "description": suggestion.get("description") or suggestion.get("rule_description"),
                "suggesting_rule": truncate(suggesting_rule, 255),
                "rule_description": suggestion.get("rule_description"),
                "code_for_constraint": truncate(suggestion.get("code_for_constraint"), 512),
                "threshold_min": threshold_min,
                "threshold_max": None,
                "value_set": value_set,
                "regex_pattern": None,
            }
        )

        normalized_rows[-1]["rule_signature"] = build_rule_signature(
            column_name=column_name,
            constraint_type=constraint_type,
            value_set=value_set,
            regex_pattern=None,
            threshold_min=threshold_min,
            threshold_max=None,
        )

    return normalized_rows


def print_json_result(source_table: str, rows: List[Dict[str, Any]]) -> None:
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
        result_df.select(
            "source_table",
            "date_hour",
            "column_name",
            "constraint_type",
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


def resolve_datagate_db_config(config: JobConfig) -> tuple[str, str, str]:
    if config.datagate_jdbc_url and config.datagate_db_user and config.datagate_db_password:
        return config.datagate_jdbc_url, config.datagate_db_user, config.datagate_db_password

    try:
        from airflow.hooks.base import BaseHook

        conn = BaseHook.get_connection(config.datagate_db_conn_id)
        schema = conn.schema or "datagate"
        port = conn.port or 5432
        jdbc_url = f"jdbc:postgresql://{conn.host}:{port}/{schema}"
        return jdbc_url, conn.login, conn.password
    except Exception as exc:
        raise RuntimeError(
            "Missing DataGate database connection. Provide Airflow connection "
            f"{config.datagate_db_conn_id!r} or --datagate_jdbc_url, "
            "--datagate_db_user, and --datagate_db_password."
        ) from exc


def split_source_table(source_table: str) -> tuple[str, str]:
    parts = source_table.split(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid source table {source_table}. Expected <schema>.<table>")
    return parts[0], parts[1]


def get_table_id(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    iceberg_catalog: str,
    source_table: str,
) -> str:
    schema_name, table_name = split_source_table(source_table)
    query = (
        "(SELECT id FROM tables "
        f"WHERE catalog_name = '{iceberg_catalog}' "
        f"AND schema_name = '{schema_name}' "
        f"AND table_name = '{table_name}' "
        "AND is_active = TRUE "
        "LIMIT 1) AS table_lookup"
    )
    rows = (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", query)
        .option("user", db_user)
        .option("password", db_password)
        .option("driver", "org.postgresql.Driver")
        .load()
        .collect()
    )
    if not rows:
        raise ValueError(f"Table {iceberg_catalog}.{source_table} is not registered in DataGate.")
    return rows[0]["id"]


def execute_jdbc_batch(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    sql: str,
    rows: List[tuple],
) -> None:
    if not rows:
        return

    jvm = spark.sparkContext._gateway.jvm
    jvm.java.lang.Class.forName("org.postgresql.Driver")
    connection = jvm.java.sql.DriverManager.getConnection(jdbc_url, db_user, db_password)
    try:
        connection.setAutoCommit(False)
        statement = connection.prepareStatement(sql)
        try:
            for row in rows:
                for index, value in enumerate(row, start=1):
                    statement.setObject(index, value)
                statement.addBatch()
            statement.executeBatch()
            connection.commit()
        finally:
            statement.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def write_suggested_rules(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    rows: List[Dict[str, Any]],
) -> None:
    sql = """
        INSERT INTO rules (
            id,
            table_id,
            source,
            status,
            column_name,
            constraint_type,
            description,
            threshold_min,
            threshold_max,
            value_set,
            regex_pattern,
            rule_signature,
            frequency,
            first_seen_at_date_hour,
            last_seen_at_date_hour,
            constraint_name,
            current_value,
            suggesting_rule,
            code_for_constraint,
            suggested_at_date_hour,
            is_active,
            created_at,
            updated_at
        )
        VALUES (
            ?::uuid,
            ?::uuid,
            ?::rule_source,
            ?::rule_status,
            ?,
            ?::constraint_type,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?::timestamp,
            ?::timestamp
        )
        ON CONFLICT (table_id, source, rule_signature)
        WHERE rule_signature IS NOT NULL
        DO UPDATE SET
            description = EXCLUDED.description,
            threshold_min = EXCLUDED.threshold_min,
            threshold_max = EXCLUDED.threshold_max,
            value_set = EXCLUDED.value_set,
            regex_pattern = EXCLUDED.regex_pattern,
            constraint_name = EXCLUDED.constraint_name,
            current_value = EXCLUDED.current_value,
            suggesting_rule = EXCLUDED.suggesting_rule,
            code_for_constraint = EXCLUDED.code_for_constraint,
            suggested_at_date_hour = EXCLUDED.suggested_at_date_hour,
            last_seen_at_date_hour = EXCLUDED.last_seen_at_date_hour,
            frequency = rules.frequency + 1,
            updated_at = EXCLUDED.updated_at,
            status = rules.status
    """
    params = [
        (
            str(uuid.uuid4()),
            row["table_id"],
            "system",
            "pending",
            row["column_name"],
            row["constraint_type"],
            row["description"],
            row.get("threshold_min"),
            row.get("threshold_max"),
            row.get("value_set"),
            row.get("regex_pattern"),
            row["rule_signature"],
            1,
            row["date_hour"],
            row["date_hour"],
            truncate(row["constraint_name"], 512),
            str(row["current_value"]) if row["current_value"] is not None else None,
            truncate(row["suggesting_rule"], 255),
            truncate(row["code_for_constraint"], 512),
            row["date_hour"],
            True,
            row["created_at"],
            row["updated_at"],
        )
        for row in rows
    ]
    execute_jdbc_batch(spark, jdbc_url, db_user, db_password, sql, params)


def persist_suggestions(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    table_id: str,
    date_hour: str,
    source_rows: List[Dict[str, Any]],
) -> int:
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    normalized_rows = [
        {
            **row,
            "table_id": table_id,
            "date_hour": date_hour,
            "created_at": created_at,
            "updated_at": created_at,
        }
        for row in source_rows
    ]
    write_suggested_rules(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        rows=normalized_rows,
    )
    return len(normalized_rows)


def suggest_rules_for_table(
    spark: SparkSession,
    source_table: str,
    date_hour: str,
    output_format: str,
    iceberg_catalog: str,
    jdbc_url: str,
    db_user: str,
    db_password: str,
) -> int:
    table_id = get_table_id(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        iceberg_catalog=iceberg_catalog,
        source_table=source_table,
    )
    df = read_from_iceberg(
        spark=spark,
        iceberg_catalog=iceberg_catalog,
        source_table=source_table,
        date_hour=date_hour,
    )
    sanitized_df = sanitize_dataframe_for_rule_suggestion(df=df, source_table=source_table)

    if not sanitized_df.columns:
        logger.info("%s produced no analyzable columns for %s; skipping", source_table, date_hour)
        return 0

    try:
        suggestion_result = run_rule_suggestion(spark=spark, df=sanitized_df)
    except Py4JJavaError as exc:
        if "EmptyStateException" in str(exc):
            logger.warning(
                "%s hit EmptyStateException during rule suggestion for %s; skipping this batch",
                source_table,
                date_hour,
            )
            return 0
        raise

    normalized_rows = normalize_suggestions(
        suggestion_result=suggestion_result,
        source_table=source_table,
        date_hour=date_hour,
    )

    if output_format == "table":
        print_table_result(spark=spark, source_table=source_table, rows=normalized_rows)
    else:
        print_json_result(source_table=source_table, rows=normalized_rows)

    return persist_suggestions(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        table_id=table_id,
        date_hour=date_hour,
        source_rows=normalized_rows,
    )


def main() -> None:
    job_start_time = perf_counter()
    job_config = parse_args()
    spark = build_spark_session()
    jdbc_url, db_user, db_password = resolve_datagate_db_config(job_config)

    try:
        total_written = 0
        for source_table in job_config.source_tables:
            total_written += suggest_rules_for_table(
                spark=spark,
                source_table=source_table,
                date_hour=job_config.date_hour,
                output_format=job_config.output_format,
                iceberg_catalog=job_config.iceberg_catalog,
                jdbc_url=jdbc_url,
                db_user=db_user,
                db_password=db_password,
            )

        total_seconds = perf_counter() - job_start_time
        logger.info("%s wrote %s suggested rules in %.3f seconds", JOB_NAME, total_written, total_seconds)
        print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
