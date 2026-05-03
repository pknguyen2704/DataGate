import argparse
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, to_timestamp


JOB_NAME = "rule_verification"
logger = logging.getLogger(__name__)


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
        description="Verify active DataGate rules against Iceberg tables by date_hour"
    )
    parser.add_argument("--source_tables", required=True, help="Comma-separated Iceberg tables")
    parser.add_argument("--date_hour", required=True, help="Processing date_hour, format: yyyy-MM-dd HH:mm:ss")
    parser.add_argument("--output_format", required=False, default="json", choices=["json", "table"])
    parser.add_argument("--iceberg_catalog", required=False, default="iceberg")
    parser.add_argument("--datagate_db_conn_id", required=False, default="datagate_db_default")
    parser.add_argument("--datagate_jdbc_url", required=False, default=os.getenv("DATAGATE_JDBC_URL"))
    parser.add_argument("--datagate_db_user", required=False, default=os.getenv("DATAGATE_DB_USER"))
    parser.add_argument("--datagate_db_password", required=False, default=os.getenv("DATAGATE_DB_PASSWORD"))

    args = parser.parse_args()
    source_tables = [table.strip() for table in args.source_tables.split(",") if table.strip()]
    if not source_tables:
        raise ValueError("Missing source tables. Please provide --source_tables")

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


def build_spark_session() -> SparkSession:
    return SparkSession.builder.appName(JOB_NAME).getOrCreate()


def split_source_table(source_table: str) -> tuple[str, str]:
    parts = source_table.split(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid source table {source_table}. Expected <schema>.<table>")
    return parts[0], parts[1]


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
        f"Table {source_table} does not contain processing_date_hour or date_hour column."
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


def load_active_rules(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    iceberg_catalog: str,
    source_tables: List[str],
) -> List[Dict[str, Any]]:
    filters = []
    for source_table in source_tables:
        schema_name, table_name = split_source_table(source_table)
        filters.append(
            f"(t.catalog_name = '{iceberg_catalog}' AND t.schema_name = '{schema_name}' AND t.table_name = '{table_name}')"
        )

    where_clause = " OR ".join(filters) if filters else "1=0"
    query = f"""
        (
            SELECT
                r.id,
                r.table_id,
                r.column_name,
                r.constraint_type,
                r.threshold_min,
                r.threshold_max,
                r.value_set,
                r.regex_pattern,
                r.description,
                t.catalog_name,
                t.schema_name,
                t.table_name
            FROM rules r
            JOIN tables t ON t.id = r.table_id
            WHERE r.status = 'active'
              AND r.is_active = TRUE
              AND ({where_clause})
        ) AS active_rules
    """
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
    return [row.asDict(recursive=True) for row in rows]


def parse_json_list(value: str | None) -> List[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return [str(item) for item in parsed] if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def verify_rule(rule: Dict[str, Any], df: DataFrame, total_count: int, date_hour: str) -> Dict[str, Any]:
    column_name = rule["column_name"]
    constraint_type = rule["constraint_type"]

    if column_name not in df.columns:
        return {
            "id": str(uuid.uuid4()),
            "rule_id": rule["id"],
            "table_id": rule["table_id"],
            "batch_date_hour": date_hour,
            "verification_status": "error",
            "actual_value": None,
            "expected_value": constraint_type,
            "failure_count": None,
            "total_count": total_count,
            "message": f"Column {column_name} not found in source table",
            "verified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

    failure_count = 0
    actual_value = None
    expected_value = None
    message = rule.get("description")
    verification_status = "passed"

    if constraint_type == "not_null":
        failure_count = df.filter(col(column_name).isNull()).count()
        completeness = 1.0 if total_count == 0 else (total_count - failure_count) / total_count
        actual_value = f"completeness={completeness:.4f}"
        expected_value = "completeness=1.0000"
    elif constraint_type == "non_negative":
        failure_count = df.filter(col(column_name) < 0).count()
        actual_value = f"negative_rows={failure_count}"
        expected_value = "negative_rows=0"
    elif constraint_type == "unique":
        distinct_count = df.select(column_name).distinct().count()
        failure_count = max(total_count - distinct_count, 0)
        actual_value = f"distinct={distinct_count}"
        expected_value = f"distinct={total_count}"
    elif constraint_type == "value_range":
        allowed_values = parse_json_list(rule.get("value_set"))
        threshold_min = rule.get("threshold_min")
        if not allowed_values:
            return {
                "id": str(uuid.uuid4()),
                "rule_id": rule["id"],
                "table_id": rule["table_id"],
                "batch_date_hour": date_hour,
                "verification_status": "error",
                "actual_value": None,
                "expected_value": "value_set required",
                "failure_count": None,
                "total_count": total_count,
                "message": "Value range rule does not have an allowed value set",
                "verified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            }
        matching_count = df.filter(col(column_name).cast("string").isin(allowed_values)).count()
        compliance = 1.0 if total_count == 0 else matching_count / total_count
        failure_count = max(total_count - matching_count, 0)
        target = threshold_min if threshold_min is not None else 1.0
        actual_value = f"compliance={compliance:.4f}"
        expected_value = f"compliance>={target:.4f}"
        if compliance < target:
            verification_status = "failed"
    elif constraint_type == "range_check":
        threshold_min = rule.get("threshold_min")
        threshold_max = rule.get("threshold_max")
        predicate = None
        if threshold_min is not None:
            predicate = col(column_name) < float(threshold_min)
        if threshold_max is not None:
            upper_predicate = col(column_name) > float(threshold_max)
            predicate = upper_predicate if predicate is None else (predicate | upper_predicate)
        failure_count = df.filter(predicate).count() if predicate is not None else 0
        actual_value = f"out_of_range={failure_count}"
        expected_value = f"range=[{threshold_min},{threshold_max}]"
    elif constraint_type == "regex":
        regex_pattern = rule.get("regex_pattern")
        if not regex_pattern:
            verification_status = "error"
            actual_value = None
            expected_value = "regex pattern required"
            failure_count = None
            message = "Regex rule does not have a pattern"
        else:
            failure_count = df.filter(~col(column_name).cast("string").rlike(regex_pattern)).count()
            actual_value = f"non_matching_rows={failure_count}"
            expected_value = f"regex={regex_pattern}"
    else:
        verification_status = "error"
        message = f"Unsupported constraint type: {constraint_type}"

    if verification_status != "error" and failure_count and failure_count > 0:
        verification_status = "failed"

    return {
        "id": str(uuid.uuid4()),
        "rule_id": rule["id"],
        "table_id": rule["table_id"],
        "batch_date_hour": date_hour,
        "verification_status": verification_status,
        "actual_value": actual_value,
        "expected_value": expected_value,
        "failure_count": failure_count,
        "total_count": total_count,
        "message": message,
        "verified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


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


def write_verification_results(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    rows: List[Dict[str, Any]],
) -> None:
    sql = """
        INSERT INTO rule_verification_results (
            id,
            rule_id,
            table_id,
            batch_date_hour,
            verification_status,
            actual_value,
            expected_value,
            failure_count,
            total_count,
            message,
            verified_at
        )
        VALUES (
            ?::uuid,
            ?::uuid,
            ?::uuid,
            ?,
            ?::rule_verification_status,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?::timestamp
        )
        ON CONFLICT (rule_id, batch_date_hour)
        DO UPDATE SET
            verification_status = EXCLUDED.verification_status,
            actual_value = EXCLUDED.actual_value,
            expected_value = EXCLUDED.expected_value,
            failure_count = EXCLUDED.failure_count,
            total_count = EXCLUDED.total_count,
            message = EXCLUDED.message,
            verified_at = EXCLUDED.verified_at
    """
    params = [
        (
            row["id"],
            row["rule_id"],
            row["table_id"],
            row["batch_date_hour"],
            row["verification_status"],
            row["actual_value"],
            row["expected_value"],
            row["failure_count"],
            row["total_count"],
            row["message"],
            row["verified_at"],
        )
        for row in rows
    ]
    execute_jdbc_batch(spark, jdbc_url, db_user, db_password, sql, params)


def print_results(output_format: str, rows: List[Dict[str, Any]]) -> None:
    if output_format == "table":
        for row in rows:
            print(
                f"{row['rule_id']} | {row['verification_status']} | "
                f"{row['actual_value']} | {row['expected_value']}"
            )
        return
    print(json.dumps(rows, indent=2, ensure_ascii=False, default=str))


def main() -> None:
    job_start_time = perf_counter()
    config = parse_args()
    spark = build_spark_session()
    jdbc_url, db_user, db_password = resolve_datagate_db_config(config)

    try:
        active_rules = load_active_rules(
            spark=spark,
            jdbc_url=jdbc_url,
            db_user=db_user,
            db_password=db_password,
            iceberg_catalog=config.iceberg_catalog,
            source_tables=config.source_tables,
        )

        grouped_rules: Dict[str, List[Dict[str, Any]]] = {}
        for rule in active_rules:
            source_table = f"{rule['schema_name']}.{rule['table_name']}"
            grouped_rules.setdefault(source_table, []).append(rule)

        verification_rows: List[Dict[str, Any]] = []
        for source_table, rules in grouped_rules.items():
            df = read_from_iceberg(
                spark=spark,
                iceberg_catalog=config.iceberg_catalog,
                source_table=source_table,
                date_hour=config.date_hour,
            )
            total_count = df.count()
            for rule in rules:
                verification_rows.append(
                    verify_rule(rule=rule, df=df, total_count=total_count, date_hour=config.date_hour)
                )

        write_verification_results(
            spark=spark,
            jdbc_url=jdbc_url,
            db_user=db_user,
            db_password=db_password,
            rows=verification_rows,
        )
        print_results(config.output_format, verification_rows)

        total_seconds = perf_counter() - job_start_time
        logger.info("%s wrote %s verification rows in %.3f seconds", JOB_NAME, len(verification_rows), total_seconds)
        print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
