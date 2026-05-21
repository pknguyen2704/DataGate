import logging
from collections import Counter, defaultdict
from contextlib import suppress
from datetime import datetime
from decimal import Decimal
from airflow.exceptions import AirflowException
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Validation
def validate_name(value, field_name):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} must not be None or empty.")
    value = str(value).strip()
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value


# Normalize processing date hour
def normalize_processing_date_hour(processing_date_hour):
    if processing_date_hour is None:
        raise ValueError("processing_date_hour must not be None or empty.")
    value = str(processing_date_hour).strip().replace("T", " ")
    if value == "":
        raise ValueError("processing_date_hour must not be empty.")
    dt = datetime.fromisoformat(value)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Format datetime for UI in slack
def format_datetime(value):
    if value is None:
        return "N/A"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    value = str(value).strip().replace("T", " ")
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def format_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, Decimal):
        value = float(value)
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


# Get connection_config from Datagate database
def get_connection_config(pg_hook, connection_name):
    if connection_name is None or str(connection_name).strip() == "":
        raise ValueError("connection_name must not be None or empty.")
    connection_name = str(connection_name).strip()
    row = pg_hook.get_first(
        """
        SELECT
            id,
            catalog_name
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,)
    )
    if row is None:
        raise ValueError(f"No active connection found with connection_name={connection_name}")
    connection_id = str(row[0])
    catalog_name = validate_name(row[1], "catalog_name")

    return {
        "connection_id": connection_id,
        "catalog_name": catalog_name
    }


def get_active_table_ids(pg_hook, connection_id, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT id
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        """,
        parameters=(connection_id, catalog_name, schema_name)
    )
    return [str(row[0]) for row in rows]


def severity_icon(severity):
    return ":red_circle:" if severity == "critical" else ":large_orange_circle:"


def table_full_name(row):
    parts = [
        row.get("catalog_name"),
        row.get("schema_name"),
        row.get("table_name"),
    ]
    return ".".join([str(x) for x in parts if x])


def threshold_text(row):
    check_type = row.get("check_type")
    min_v = row.get("min_threshold")
    max_v = row.get("max_threshold")

    if check_type == "anomaly":
        auc_threshold = max_v if max_v is not None else min_v
        if auc_threshold is None:
            return "Anomaly result threshold was not captured."
        return f"Require `anomaly_result < {format_value(auc_threshold)}`"
    rules = []
    if min_v is not None:
        rules.append(f"actual_value >= {format_value(min_v)}")
    if max_v is not None:
        rules.append(f"actual_value <= {format_value(max_v)}")
    if not rules:
        return "No min/max threshold was captured."
    return "Require `" + " and ".join(rules) + "`"


def fetch_quality_failure_details(
    pg_hook,
    table_ids,
    processing_date_hour,
    include_rule=False,
    include_auc=False,
):
    columns = [
        "check_type",
        "catalog_name",
        "schema_name",
        "table_name",
        "column_name",
        "fail_metric",
        "metric_description",
        "actual_value",
        "min_threshold",
        "max_threshold",
        "severity_level",
        "processing_date_hour",
        "created_at",
        "constraint_status",
        "constraint_value",
        "constraint_message",
    ]
    check_types = ["metadata", "profiling"]
    if include_rule:
        check_types.append("rule")
    if include_auc:
        check_types.append("anomaly")

    sql = """
        SELECT
            x.check_type,
            t.catalog_name,
            t.schema_name,
            t.table_name,
            x.column_name,
            COALESCE(
                x.metric_name,
                r.constraint_name,
                r.code_for_constraint,
                'quality_check'
            ) AS fail_metric,
            COALESCE(qt.description, r.description) AS metric_description,
            x.actual_value,
            x.min_threshold,
            x.max_threshold,
            x.severity_level::text,
            x.processing_date_hour,
            x.created_at,
            x.status AS constraint_status,
            COALESCE(
                x.metric_name,
                r.constraint_name,
                r.code_for_constraint
            ) AS constraint_value,
            x.message AS constraint_message
        FROM quality_check_results x
        JOIN tables t
            ON t.id = x.table_id
        LEFT JOIN quality_thresholds qt
            ON qt.id = x.threshold_id
        LEFT JOIN rules r
            ON r.id = x.rule_id
        WHERE x.table_id = ANY(%s::uuid[])
        AND x.processing_date_hour = %s::timestamp
        AND x.check_type = ANY(%s::text[])
        AND x.status = 'fail'
        AND x.is_resolved = FALSE
        ORDER BY
            CASE x.severity_level
                WHEN 'critical' THEN 1
                WHEN 'warning' THEN 2
                ELSE 3
            END,
            x.check_type,
            t.catalog_name,
            t.schema_name,
            t.table_name,
            x.column_name,
            fail_metric
    """
    params = [table_ids, processing_date_hour, check_types]
    records = pg_hook.get_records(sql, parameters=tuple(params))
    return [dict(zip(columns, row)) for row in records]


def build_quality_alert_message(
    connection_name,
    schema_name,
    processing_date_hour,
    rows,
    max_detail_rows=30,
):
    severity_counts = Counter(row["severity_level"] for row in rows)
    type_counts = Counter(row["check_type"] for row in rows)
    lines = [
        ":rotating_light: *DataGate Data Quality Alert*",
        "",
        f"*Connection*: `{connection_name}`",
        f"*Schema*: `{schema_name}`",
        f"*Processing Date Hour*: `{processing_date_hour}`",
        f"*Detected At*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "*Summary*",
        f"• Total unresolved failures: `{len(rows)}`",
        f"• Critical: `{severity_counts.get('critical', 0)}`",
        f"• Warning: `{severity_counts.get('warning', 0)}`",
        f"• Metadata: `{type_counts.get('metadata', 0)}`",
        f"• Profiling: `{type_counts.get('profiling', 0)}`",
        f"• Rule: `{type_counts.get('rule', 0)}`",
        f"• AUC Result: `{type_counts.get('anomaly', 0)}`",
        "",
        "*Failure Details*",
    ]
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["check_type"]].append(row)
    section_titles = {
        "metadata": "Metadata Metrics",
        "profiling": "Profiling Metrics",
        "rule": "Rule Verification",
        "anomaly": "AUC Result",
    }
    shown = 0
    for check_type in ["metadata", "profiling", "rule", "anomaly"]:
        group_rows = grouped.get(check_type, [])

        if not group_rows:
            continue
        lines.append("")
        lines.append(f"*{section_titles[check_type]}*")

        for row in group_rows:
            if shown >= max_detail_rows:
                continue

            shown += 1

            table_name = table_full_name(row)
            column_name = row.get("column_name")

            target = f"`{table_name}`"
            if column_name:
                target += f".`{column_name}`"

            severity = row.get("severity_level") or "N/A"

            lines.append(f"{severity_icon(severity)} *{severity.upper()}* | {target}")
            lines.append(f"• Metric/Rule: `{format_value(row.get('fail_metric'))}`")

            if row.get("metric_description"):
                lines.append(f"• Description: {row['metric_description']}")

            if check_type == "rule":
                lines.append(
                    f"• Constraint Status: `{format_value(row.get('constraint_status'))}`"
                )
                lines.append(
                    f"• Constraint: `{format_value(row.get('constraint_value'))}`"
                )

                if row.get("constraint_message"):
                    lines.append(f"• Constraint Message: {row['constraint_message']}")
            else:
                lines.append(
                    f"• Actual Value: `{format_value(row.get('actual_value'))}`"
                )
                lines.append(f"• Threshold: {threshold_text(row)}")

            lines.append(
                f"• Result Created At: `{format_datetime(row.get('created_at'))}`"
            )
            lines.append("")

    if len(rows) > max_detail_rows:
        lines.append(
            f"...and `{len(rows) - max_detail_rows}` more unresolved failures. "
            "Please check Grafana/DataGate dashboard for the full list."
        )

    return "\n".join(lines)


def send_slack_message(slack_webhook_conn_id, message, timeout=30):
    SlackWebhookHook(
        slack_webhook_conn_id=slack_webhook_conn_id,
        timeout=timeout,
    ).send_text(message)


# Close hook connection
def close_hook_connection(hook):
    if hook is None:
        return
    for attr_name in ("conn", "_conn"):
        with suppress(Exception):
            conn = getattr(hook, attr_name, None)
            if conn is not None:
                conn.close()



def run_quality_gate(
    datagate_db_conn_id,
    processing_date_hour,
    connection_name,
    schema_name,
    include_rule=False,
    include_auc=False,
    slack_webhook_conn_id="slack_dq",
    max_alert_rows=30,
    slack_timeout=30,
):
    schema_name = validate_name(schema_name, "schema_name")
    connection_name = validate_name(connection_name, "connection_name")
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    try:
        connection_config = get_connection_config(pg_hook, connection_name)

        table_ids = get_active_table_ids(
            pg_hook,
            connection_config["connection_id"],
            connection_config["catalog_name"],
            schema_name,
        )

        if not table_ids:
            logger.info(
                "No active tables found | schema=%s",
                schema_name,
            )
            return True

        rows = fetch_quality_failure_details(
            pg_hook,
            table_ids,
            processing_date_hour,
            include_rule,
            include_auc,
        )

        severity_counts = Counter(row["severity_level"] for row in rows)
        type_counts = Counter(row["check_type"] for row in rows)

        critical_count = severity_counts.get("critical", 0)
        warning_count = severity_counts.get("warning", 0)

        logger.info(
            "Quality gate checked | schema=%s | processing_date_hour=%s | total_fail=%s | critical=%s | warning=%s | metadata=%s | profiling=%s | rule=%s | auc=%s",
            schema_name,
            processing_date_hour,
            len(rows),
            critical_count,
            warning_count,
            type_counts.get("metadata", 0),
            type_counts.get("profiling", 0),
            type_counts.get("rule", 0),
            type_counts.get("anomaly", 0),
        )

        if rows:
            message = build_quality_alert_message(
                connection_name,
                schema_name,
                processing_date_hour,
                rows,
                max_alert_rows,
            )
            send_slack_message(slack_webhook_conn_id, message, timeout=slack_timeout)

        if critical_count > 0:
            raise AirflowException(
                f"Quality gate failed. "
                f"schema={schema_name}, "
                f"processing_date_hour={processing_date_hour}, "
                f"unresolved_critical={critical_count}, "
                f"unresolved_warning={warning_count}, "
                f"metadata_fail={type_counts.get('metadata', 0)}, "
                f"profiling_fail={type_counts.get('profiling', 0)}, "
                f"rule_fail={type_counts.get('rule', 0)}, "
                f"auc_fail={type_counts.get('anomaly', 0)}"
            )

        return True

    finally:
        close_hook_connection(pg_hook)
