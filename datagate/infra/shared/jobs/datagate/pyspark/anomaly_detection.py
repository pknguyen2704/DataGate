import argparse
import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from time import perf_counter
from typing import Any, Dict, List

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import (
    DateType,
    StringType,
    TimestampType,
)

try:
    from prophet import Prophet
except ImportError:  # pragma: no cover - depends on runtime image
    Prophet = None

from analyzer import normalize_profile_metrics, run_analyzers

JOB_NAME = "prophet_anomaly_detection"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

METADATA_METRICS = [
    "batch_added_rows",
    "batch_added_files",
    "deleted_rows",
    "deleted_files",
    "table_total_rows",
    "table_total_files",
    "table_total_size_bytes",
    "changed_partition_count",
]
DEFAULT_HISTORY_POINTS = 12
DEFAULT_MIN_HISTORY_POINTS = 5
DEFAULT_INTERVAL_WIDTH = 0.95
ROOT_CAUSE_LIMIT = 15


@dataclass
class JobConfig:
    source_tables: List[str]
    table_date_columns: Dict[str, str]
    target_date: str
    batch_date_hour: str
    history_points: int
    min_history_points: int
    output_format: str
    iceberg_catalog: str
    datagate_db_conn_id: str
    datagate_jdbc_url: str | None
    datagate_db_user: str | None
    datagate_db_password: str | None


def parse_args() -> JobConfig:
    parser = argparse.ArgumentParser(
        description=(
            "Run Prophet-based time-series anomaly detection against DataGate table metadata "
            "and historical profiling metrics."
        )
    )
    parser.add_argument("--source_tables", required=True, help="Comma-separated Iceberg tables")
    parser.add_argument(
        "--table_date_columns",
        required=True,
        help="Comma-separated table=date_column mappings",
    )
    parser.add_argument(
        "--date_hour",
        required=True,
        help="Processing date_hour in YYYY-MM-DD HH:mm:ss format; date portion is used as the target date",
    )
    parser.add_argument(
        "--history_points",
        required=False,
        type=int,
        default=DEFAULT_HISTORY_POINTS,
        help="Maximum number of historical observations used per metric",
    )
    parser.add_argument(
        "--min_history_points",
        required=False,
        type=int,
        default=DEFAULT_MIN_HISTORY_POINTS,
        help="Minimum number of historical observations required before fitting Prophet",
    )
    parser.add_argument("--output_format", required=False, default="json", choices=["json", "table"])
    parser.add_argument("--iceberg_catalog", required=False, default="iceberg")
    parser.add_argument("--datagate_db_conn_id", required=False, default="datagate_db_default")
    parser.add_argument("--datagate_jdbc_url", required=False, default=os.getenv("DATAGATE_JDBC_URL"))
    parser.add_argument("--datagate_db_user", required=False, default=os.getenv("DATAGATE_DB_USER"))
    parser.add_argument("--datagate_db_password", required=False, default=os.getenv("DATAGATE_DB_PASSWORD"))
    args = parser.parse_args()

    source_tables = [table.strip() for table in args.source_tables.split(",") if table.strip()]
    if not source_tables:
        raise ValueError("Missing source tables. Please provide at least one table.")

    table_date_columns: Dict[str, str] = {}
    for mapping in args.table_date_columns.split(","):
        item = mapping.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("Invalid --table_date_columns mapping. Expected <table>=<date_column>.")
        table_name, column_name = item.split("=", 1)
        table_date_columns[table_name.strip()] = column_name.strip()

    missing_date_columns = [table_name for table_name in source_tables if table_name not in table_date_columns]
    if missing_date_columns:
        raise ValueError("Missing date column mapping for tables: " + ", ".join(missing_date_columns))

    target_date = args.date_hour.split(" ")[0]
    datetime.strptime(target_date, "%Y-%m-%d")

    return JobConfig(
        source_tables=source_tables,
        table_date_columns=table_date_columns,
        target_date=target_date,
        batch_date_hour=args.date_hour,
        history_points=max(args.history_points, 1),
        min_history_points=max(args.min_history_points, 2),
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


def read_from_iceberg(spark: SparkSession, iceberg_catalog: str, source_table: str) -> DataFrame:
    return spark.read.format("iceberg").load(f"{iceberg_catalog}.{source_table}")


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


def validate_date_column(df: DataFrame, source_table: str, date_column: str) -> None:
    if date_column not in df.columns:
        raise ValueError(f"Table {source_table} does not contain date column {date_column}.")


def build_day_filter(df: DataFrame, date_column: str, target_date: str):
    field = next(field for field in df.schema.fields if field.name == date_column)
    start_dt = datetime.strptime(target_date, "%Y-%m-%d")
    next_dt = start_dt + timedelta(days=1)
    type_name = field.dataType.simpleString()

    if isinstance(field.dataType, DateType):
        return F.col(date_column) == F.lit(target_date)

    if isinstance(field.dataType, TimestampType) or type_name.startswith("timestamp"):
        return (
            (F.col(date_column) >= F.lit(start_dt.strftime("%Y-%m-%d %H:%M:%S")).cast("timestamp"))
            & (F.col(date_column) < F.lit(next_dt.strftime("%Y-%m-%d %H:%M:%S")).cast("timestamp"))
        )

    if isinstance(field.dataType, StringType):
        return (F.col(date_column) >= F.lit(target_date)) & (F.col(date_column) < F.lit(next_dt.strftime("%Y-%m-%d")))

    raise ValueError(
        f"Unsupported date column type for {date_column}: {type_name}. "
        "Expected date, timestamp, or string."
    )


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_obs_date(row: Dict[str, Any]) -> date | None:
    for key in ("last_updated_time", "collected_at"):
        value = row.get(key)
        if isinstance(value, datetime):
            return value.date()
    return None


def fetch_table_metadata_history(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    table_id: str,
    history_points: int,
) -> List[Dict[str, Any]]:
    query = (
        "(SELECT "
        "snapshot_id, "
        "parent_snapshot_id, "
        "operation, "
        "last_updated_time, "
        "collected_at, "
        "batch_added_rows, "
        "batch_added_files, "
        "deleted_rows, "
        "deleted_files, "
        "table_total_rows, "
        "table_total_files, "
        "table_total_size_bytes, "
        "changed_partition_count "
        "FROM table_batch_metadata "
        f"WHERE table_id = '{table_id}' "
        "ORDER BY COALESCE(last_updated_time, collected_at) DESC "
        f"LIMIT {history_points + 5}) AS metadata_history"
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
    return [row.asDict() for row in rows]


def split_current_and_history_rows(
    rows: List[Dict[str, Any]],
    target_date: str,
    history_points: int,
) -> tuple[Dict[str, Any] | None, List[Dict[str, Any]]]:
    if not rows:
        return None, []

    rows_sorted = sorted(
        rows,
        key=lambda row: row.get("last_updated_time") or row.get("collected_at") or datetime.min,
    )
    current_row = None
    target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()

    for row in reversed(rows_sorted):
        if to_obs_date(row) == target_dt:
            current_row = row
            break

    if current_row is None:
        current_row = rows_sorted[-1]

    current_obs_date = to_obs_date(current_row)
    history_rows: List[Dict[str, Any]] = []
    seen_dates: set[date] = set()
    for row in reversed(rows_sorted[:-1] if current_row is rows_sorted[-1] else rows_sorted):
        obs_date = to_obs_date(row)
        if obs_date is None or obs_date == current_obs_date or obs_date in seen_dates:
            continue
        history_rows.append(row)
        seen_dates.add(obs_date)
        if len(history_rows) >= history_points:
            break

    history_rows.reverse()
    return current_row, history_rows


def run_profile_metrics_for_day(
    spark: SparkSession,
    df_source: DataFrame,
    source_table: str,
    date_column: str,
    target_date: str,
) -> Dict[tuple[str, str], float]:
    filtered_df = df_source.filter(build_day_filter(df_source, date_column, target_date))
    if filtered_df.limit(1).count() == 0:
        logger.info("%s has no rows for historical profiling date %s", source_table, target_date)
        return {}

    metric_rows = [row.asDict() for row in run_analyzers(spark=spark, df=filtered_df).collect()]
    return normalize_profile_metrics(metric_rows)


def build_history_frame(history_values: List[tuple[date, float]]) -> pd.DataFrame:
    unique_points: Dict[pd.Timestamp, float] = {}
    for obs_date, metric_value in history_values:
        unique_points[pd.Timestamp(obs_date)] = metric_value

    return pd.DataFrame(
        {
            "ds": list(sorted(unique_points.keys())),
            "y": [unique_points[key] for key in sorted(unique_points.keys())],
        }
    )


def classify_severity(normalized_deviation: float) -> str:
    if normalized_deviation >= 0.60:
        return "Extreme"
    if normalized_deviation >= 0.35:
        return "Severe"
    if normalized_deviation >= 0.20:
        return "Strong"
    if normalized_deviation >= 0.10:
        return "Moderate"
    if normalized_deviation >= 0.05:
        return "Weak"
    return "Minimal"


def compute_anomaly_score(normalized_deviation: float) -> float:
    if normalized_deviation <= 0:
        return 0.0
    return min(1.0, normalized_deviation / 0.60)


def fit_and_score_series(
    history_values: List[tuple[date, float]],
    current_date: str,
    current_value: float,
    metric_category: str,
    metric_name: str,
    column_name: str | None,
    interval_width: float,
) -> Dict[str, Any] | None:
    if Prophet is None:
        raise RuntimeError(
            "Prophet is not installed in the runtime. Install the `prophet` package "
            "for the job environment before running prophet.py."
        )

    history_df = build_history_frame(history_values)
    if history_df.empty:
        return None

    model = Prophet(
        interval_width=interval_width,
        daily_seasonality=False,
        weekly_seasonality=len(history_df) >= 14,
        yearly_seasonality=False,
    )
    model.fit(history_df)

    forecast_input = pd.DataFrame({"ds": [pd.Timestamp(current_date)]})
    forecast_row = model.predict(forecast_input).iloc[0]

    expected = float(forecast_row["yhat"])
    lower = float(forecast_row["yhat_lower"])
    upper = float(forecast_row["yhat_upper"])
    distance = 0.0
    if current_value < lower:
        distance = lower - current_value
    elif current_value > upper:
        distance = current_value - upper

    scale = max(abs(expected), abs(upper - lower), 1.0)
    normalized_deviation = distance / scale
    anomaly_score = compute_anomaly_score(normalized_deviation)

    return {
        "category": metric_category,
        "metric_name": metric_name,
        "column_name": column_name,
        "actual": round(current_value, 6),
        "expected": round(expected, 6),
        "lower_bound": round(lower, 6),
        "upper_bound": round(upper, 6),
        "normalized_deviation": round(normalized_deviation, 6),
        "anomaly_score": round(anomaly_score, 6),
        "severity": classify_severity(normalized_deviation) if anomaly_score > 0 else "None",
        "is_anomaly": anomaly_score > 0,
        "history_points": len(history_df),
    }


def evaluate_metadata_metrics(
    current_row: Dict[str, Any],
    history_rows: List[Dict[str, Any]],
    target_date: str,
    min_history_points: int,
) -> tuple[List[Dict[str, Any]], int, int]:
    findings: List[Dict[str, Any]] = []
    evaluated_series = 0
    historical_points = 0

    for metric_name in METADATA_METRICS:
        current_value = safe_float(current_row.get(metric_name))
        if current_value is None:
            continue

        history_values: List[tuple[date, float]] = []
        for row in history_rows:
            obs_date = to_obs_date(row)
            metric_value = safe_float(row.get(metric_name))
            if obs_date is None or metric_value is None:
                continue
            history_values.append((obs_date, metric_value))

        if len(history_values) < min_history_points:
            continue

        evaluated_series += 1
        historical_points += len(history_values)
        finding = fit_and_score_series(
            history_values=history_values,
            current_date=target_date,
            current_value=current_value,
            metric_category="metadata",
            metric_name=metric_name,
            column_name=None,
            interval_width=DEFAULT_INTERVAL_WIDTH,
        )
        if finding and finding["is_anomaly"]:
            findings.append(finding)

    return findings, evaluated_series, historical_points


def evaluate_profile_metrics(
    spark: SparkSession,
    df_source: DataFrame,
    source_table: str,
    date_column: str,
    target_date: str,
    history_rows: List[Dict[str, Any]],
    min_history_points: int,
) -> tuple[List[Dict[str, Any]], int, int]:
    current_metrics = run_profile_metrics_for_day(
        spark=spark,
        df_source=df_source,
        source_table=source_table,
        date_column=date_column,
        target_date=target_date,
    )
    if not current_metrics:
        return [], 0, 0

    historical_profiles: Dict[str, Dict[tuple[str, str], float]] = {}
    for row in history_rows:
        obs_date = to_obs_date(row)
        if obs_date is None:
            continue

        obs_date_str = obs_date.isoformat()
        historical_profiles[obs_date_str] = run_profile_metrics_for_day(
            spark=spark,
            df_source=df_source,
            source_table=source_table,
            date_column=date_column,
            target_date=obs_date_str,
        )

    findings: List[Dict[str, Any]] = []
    evaluated_series = 0
    historical_points = 0

    for (column_name, metric_name), current_value in current_metrics.items():
        history_values: List[tuple[date, float]] = []
        for obs_date_str, profile_map in historical_profiles.items():
            historical_value = profile_map.get((column_name, metric_name))
            if historical_value is None:
                continue
            history_values.append((datetime.strptime(obs_date_str, "%Y-%m-%d").date(), historical_value))

        if len(history_values) < min_history_points:
            continue

        evaluated_series += 1
        historical_points += len(history_values)
        try:
            finding = fit_and_score_series(
                history_values=history_values,
                current_date=target_date,
                current_value=current_value,
                metric_category="profiling",
                metric_name=metric_name,
                column_name=column_name,
                interval_width=DEFAULT_INTERVAL_WIDTH,
            )
        except Exception as exc:
            logger.warning(
                "Skipping Prophet fit for %s.%s (%s): %s",
                source_table,
                column_name,
                metric_name,
                exc,
            )
            continue

        if finding and finding["is_anomaly"]:
            findings.append(finding)

    return findings, evaluated_series, historical_points


def build_non_success_result(
    source_table: str,
    date_column: str,
    target_date: str,
    status: str,
    message: str,
) -> Dict[str, Any]:
    return {
        "source_table": source_table,
        "date_column": date_column,
        "target_date": target_date,
        "sample_counts": {"today": 0, "comparison": 0, "total": 0},
        "auc": 0.0,
        "status": status,
        "anomaly_count": 0,
        "severity_counts": {},
        "root_causes": [],
        "examples": [],
        "message": message,
    }


def build_result(
    source_table: str,
    date_column: str,
    target_date: str,
    findings: List[Dict[str, Any]],
    evaluated_series: int,
    historical_points: int,
) -> Dict[str, Any]:
    findings_sorted = sorted(findings, key=lambda item: item["anomaly_score"], reverse=True)
    severity_counts: Dict[str, int] = {}
    for finding in findings_sorted:
        severity = finding["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    anomaly_score = max((item["anomaly_score"] for item in findings_sorted), default=0.0)
    status = "anomaly_detected" if findings_sorted else "normal"
    message = None
    if findings_sorted:
        message = f"Detected {len(findings_sorted)} time-series anomalies from metadata/profiling history."

    return {
        "source_table": source_table,
        "date_column": date_column,
        "target_date": target_date,
        "sample_counts": {
            "today": evaluated_series,
            "comparison": historical_points,
            "total": evaluated_series + historical_points,
        },
        "auc": round(anomaly_score, 4),
        "status": status,
        "anomaly_count": len(findings_sorted),
        "severity_counts": severity_counts,
        "root_causes": findings_sorted[:ROOT_CAUSE_LIMIT],
        "examples": findings_sorted[:10],
        "message": message,
    }


def print_json_result(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print(f"[Prophet Result] {result['source_table']}")
    print("=" * 100)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def print_table_result(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print(f"[Prophet Result] {result['source_table']}")
    print("=" * 100)
    print(f"Target date: {result['target_date']}")
    print(f"Status: {result['status']}")
    print(f"Anomaly score: {result['auc']}")
    print(f"Anomaly count: {result['anomaly_count']}")
    if result["severity_counts"]:
        print("Severity counts:")
        for severity, count in result["severity_counts"].items():
            print(f"  - {severity}: {count}")
    if result["root_causes"]:
        print("Top root causes:")
        for item in result["root_causes"][:10]:
            identifier = f"{item['metric_name']}"
            if item.get("column_name"):
                identifier = f"{item['column_name']}.{identifier}"
            print(
                f"  - [{item['category']}] {identifier}: "
                f"actual={item['actual']} expected={item['expected']} "
                f"interval=({item['lower_bound']}, {item['upper_bound']}) "
                f"severity={item['severity']}"
            )


def write_anomaly_results(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    rows: List[Dict[str, Any]],
) -> None:
    sql = """
        INSERT INTO anomaly_results (
            id,
            table_id,
            date_column,
            batch_date_hour,
            target_date,
            status,
            auc,
            sample_today_count,
            sample_comparison_count,
            sample_total_count,
            anomaly_count,
            severity_counts,
            root_causes,
            examples,
            message,
            detected_at
        )
        VALUES (
            ?::uuid,
            ?::uuid,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?::jsonb,
            ?::jsonb,
            ?::jsonb,
            ?,
            ?::timestamp
        )
        ON CONFLICT (table_id, date_column, batch_date_hour)
        DO UPDATE SET
            target_date = EXCLUDED.target_date,
            status = EXCLUDED.status,
            auc = EXCLUDED.auc,
            sample_today_count = EXCLUDED.sample_today_count,
            sample_comparison_count = EXCLUDED.sample_comparison_count,
            sample_total_count = EXCLUDED.sample_total_count,
            anomaly_count = EXCLUDED.anomaly_count,
            severity_counts = EXCLUDED.severity_counts,
            root_causes = EXCLUDED.root_causes,
            examples = EXCLUDED.examples,
            message = EXCLUDED.message,
            detected_at = EXCLUDED.detected_at
    """
    params = [
        (
            str(uuid.uuid4()),
            row["table_id"],
            row["date_column"],
            row["batch_date_hour"],
            row["target_date"],
            row["status"],
            row["auc"],
            row["sample_today_count"],
            row["sample_comparison_count"],
            row["sample_total_count"],
            row["anomaly_count"],
            json.dumps(row["severity_counts"]),
            json.dumps(row["root_causes"]),
            json.dumps(row["examples"]),
            row.get("message"),
            row["detected_at"],
        )
        for row in rows
    ]
    execute_jdbc_batch(spark, jdbc_url, db_user, db_password, sql, params)


def persist_result(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    iceberg_catalog: str,
    source_table: str,
    date_column: str,
    batch_date_hour: str,
    result: Dict[str, Any],
) -> None:
    table_id = get_table_id(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        iceberg_catalog=iceberg_catalog,
        source_table=source_table,
    )
    write_anomaly_results(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        rows=[
            {
                "table_id": table_id,
                "date_column": date_column,
                "batch_date_hour": batch_date_hour,
                "target_date": result["target_date"],
                "status": result["status"],
                "auc": result["auc"],
                "sample_today_count": result["sample_counts"]["today"],
                "sample_comparison_count": result["sample_counts"]["comparison"],
                "sample_total_count": result["sample_counts"]["total"],
                "anomaly_count": result["anomaly_count"],
                "severity_counts": result["severity_counts"],
                "root_causes": result["root_causes"],
                "examples": result["examples"],
                "message": result.get("message"),
                "detected_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            }
        ],
    )


def run_prophet_for_table(
    spark: SparkSession,
    jdbc_url: str,
    db_user: str,
    db_password: str,
    iceberg_catalog: str,
    source_table: str,
    date_column: str,
    target_date: str,
    history_points: int,
    min_history_points: int,
    output_format: str,
) -> Dict[str, Any]:
    table_id = get_table_id(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        iceberg_catalog=iceberg_catalog,
        source_table=source_table,
    )
    metadata_rows = fetch_table_metadata_history(
        spark=spark,
        jdbc_url=jdbc_url,
        db_user=db_user,
        db_password=db_password,
        table_id=table_id,
        history_points=history_points,
    )
    current_metadata_row, history_metadata_rows = split_current_and_history_rows(
        rows=metadata_rows,
        target_date=target_date,
        history_points=history_points,
    )
    if current_metadata_row is None:
        raise ValueError(f"No table metadata history found for {source_table}.")

    df_source = read_from_iceberg(spark=spark, iceberg_catalog=iceberg_catalog, source_table=source_table)
    validate_date_column(df_source, source_table, date_column)

    metadata_findings, metadata_series, metadata_history_count = evaluate_metadata_metrics(
        current_row=current_metadata_row,
        history_rows=history_metadata_rows,
        target_date=target_date,
        min_history_points=min_history_points,
    )
    profile_findings, profile_series, profile_history_count = evaluate_profile_metrics(
        spark=spark,
        df_source=df_source,
        source_table=source_table,
        date_column=date_column,
        target_date=target_date,
        history_rows=history_metadata_rows,
        min_history_points=min_history_points,
    )

    total_series = metadata_series + profile_series
    total_history_points = metadata_history_count + profile_history_count
    if total_series == 0:
        result = build_non_success_result(
            source_table=source_table,
            date_column=date_column,
            target_date=target_date,
            status="skipped",
            message=(
                "Insufficient historical observations to fit Prophet. "
                f"Need at least {min_history_points} points per metric."
            ),
        )
    else:
        result = build_result(
            source_table=source_table,
            date_column=date_column,
            target_date=target_date,
            findings=metadata_findings + profile_findings,
            evaluated_series=total_series,
            historical_points=total_history_points,
        )

    if output_format == "table":
        print_table_result(result)
    else:
        print_json_result(result)
    return result


def main() -> None:
    job_start_time = perf_counter()
    config = parse_args()
    spark = build_spark_session()
    jdbc_url, db_user, db_password = resolve_datagate_db_config(config)

    try:
        completed_tables = 0
        skipped_tables = 0
        for source_table in config.source_tables:
            date_column = config.table_date_columns[source_table]
            try:
                result = run_prophet_for_table(
                    spark=spark,
                    jdbc_url=jdbc_url,
                    db_user=db_user,
                    db_password=db_password,
                    iceberg_catalog=config.iceberg_catalog,
                    source_table=source_table,
                    date_column=date_column,
                    target_date=config.target_date,
                    history_points=config.history_points,
                    min_history_points=config.min_history_points,
                    output_format=config.output_format,
                )
                persist_result(
                    spark=spark,
                    jdbc_url=jdbc_url,
                    db_user=db_user,
                    db_password=db_password,
                    iceberg_catalog=config.iceberg_catalog,
                    source_table=source_table,
                    date_column=date_column,
                    batch_date_hour=config.batch_date_hour,
                    result=result,
                )
                if result["status"] == "skipped":
                    skipped_tables += 1
                else:
                    completed_tables += 1
            except ValueError as exc:
                logger.warning("Prophet anomaly detection skipped for %s: %s", source_table, exc)
                persist_result(
                    spark=spark,
                    jdbc_url=jdbc_url,
                    db_user=db_user,
                    db_password=db_password,
                    iceberg_catalog=config.iceberg_catalog,
                    source_table=source_table,
                    date_column=date_column,
                    batch_date_hour=config.batch_date_hour,
                    result=build_non_success_result(
                        source_table=source_table,
                        date_column=date_column,
                        target_date=config.target_date,
                        status="skipped",
                        message=str(exc),
                    ),
                )
                skipped_tables += 1
            except Exception as exc:
                logger.exception("Prophet anomaly detection failed for %s: %s", source_table, exc)
                raise

        total_seconds = perf_counter() - job_start_time
        logger.info(
            "%s processed %s table(s), skipped %s table(s) in %.3f seconds",
            JOB_NAME,
            completed_tables,
            skipped_tables,
            total_seconds,
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
