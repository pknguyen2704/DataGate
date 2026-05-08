import logging
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal

from airflow.exceptions import AirflowException
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def validate_name(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value

def normalize_processing_date_hour(value):
    value = str(value or "").strip().replace("T", " ")
    if not value:
        raise ValueError("processing_date_hour must not be empty.")
    return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")

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

def get_connection_config(pg_hook, connection_name):
    connection_name = validate_name(connection_name, "connection_name")
    row = pg_hook.get_first(
        """
        SELECT id, connection_name, iceberg_catalog_name
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,),
    )
    if row is None:
        raise ValueError(f"No active connection found: {connection_name}")
    return {
        "connection_id": str(row[0]),
        "connection_name": row[1],
        "catalog_name": validate_name(row[2], "iceberg_catalog_name"),
    }

def get_active_tables(pg_hook, catalog_name, schema_name):
    schema_name = validate_name(schema_name, "schema_name")
    rows = pg_hook.get_records(
        """
        SELECT id
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        """,
        parameters=(catalog_name, schema_name),
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

    if check_type == "lightgbm_auc":
        if max_v is None:
            return "AUC threshold was not captured."
        return f"Require `auc_score < {format_value(max_v)}`"
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
    selects = []
    params = []
    selects.append(
        """
        SELECT
            'metadata' AS check_type,
            t.catalog_name,
            t.schema_name,
            t.table_name,
            NULL::text AS column_name,
            COALESCE(
                to_jsonb(m)->>'metric_name',
                to_jsonb(m)->>'metric_code',
                to_jsonb(m)->>'metric_type',
                to_jsonb(m)->>'metadata_metric_name',
                'metadata_metric'
            ) AS fail_metric,
            COALESCE(
                to_jsonb(m)->>'description',
                to_jsonb(m)->>'metric_description',
                to_jsonb(m)->>'rule_description'
            ) AS metric_description,
            x.actual_value,
            x.min_threshold,
            x.max_threshold,
            x.severity_level::text,
            x.processing_date_hour,
            x.created_at,
            NULL::text AS constraint_status,
            NULL::text AS constraint_value,
            NULL::text AS constraint_message
        FROM batch_table_metadata_metrics_verify x
        JOIN batch_table_metadata_manual_thresholds m
            ON m.id = x.metadata_manual_threshold_id
        JOIN tables t
            ON t.id = m.table_id
        WHERE m.table_id = ANY(%s::uuid[])
          AND x.processing_date_hour = %s::timestamp
          AND x.status = 'fail'
          AND x.is_resolved = FALSE
        """
    )
    params.extend([table_ids, processing_date_hour])
    selects.append(
        """
        SELECT
            'profiling' AS check_type,
            t.catalog_name,
            t.schema_name,
            t.table_name,
            COALESCE(
                to_jsonb(p)->>'column_name',
                to_jsonb(m)->>'column_name'
            ) AS column_name,
            COALESCE(
                to_jsonb(m)->>'metric_name',
                to_jsonb(m)->>'metric_code',
                to_jsonb(m)->>'metric_type',
                to_jsonb(m)->>'profiling_metric_name',
                'profiling_metric'
            ) AS fail_metric,
            COALESCE(
                to_jsonb(m)->>'description',
                to_jsonb(m)->>'metric_description',
                to_jsonb(m)->>'rule_description'
            ) AS metric_description,
            x.actual_value,
            x.min_threshold,
            x.max_threshold,
            x.severity_level::text,
            x.processing_date_hour,
            x.created_at,
            NULL::text AS constraint_status,
            NULL::text AS constraint_value,
            NULL::text AS constraint_message
        FROM batch_table_profiling_metrics_verify x
        JOIN batch_table_profiling_manual_thresholds m
            ON m.id = x.profiling_manual_threshold_id
        JOIN batch_table_profiling p
            ON p.id = x.batch_table_profiling_id
        JOIN tables t
            ON t.id = m.table_id
        WHERE m.table_id = ANY(%s::uuid[])
          AND x.processing_date_hour = %s::timestamp
          AND x.status = 'fail'
          AND x.is_resolved = FALSE
        """
    )
    params.extend([table_ids, processing_date_hour])
    if include_rule:
        selects.append(
            """
            SELECT
                'rule' AS check_type,
                t.catalog_name,
                t.schema_name,
                t.table_name,
                r.column_name,
                COALESCE(
                    r.constraint_name,
                    r.code_for_constraint,
                    'rule_constraint'
                ) AS fail_metric,
                COALESCE(
                    r.rule_description,
                    r.description
                ) AS metric_description,
                NULL::float AS actual_value,
                NULL::float AS min_threshold,
                NULL::float AS max_threshold,
                x.severity_level::text,
                x.processing_date_hour,
                x.created_at,
                x.constraint_status,
                COALESCE(
                    x.constraint,
                    r.constraint_name,
                    r.code_for_constraint
                ) AS constraint_value,
                x.constraint_message
            FROM rule_verify x
            JOIN rules r
                ON r.id = x.rule_id
            JOIN tables t
                ON t.id = r.table_id
            WHERE r.table_id = ANY(%s::uuid[])
              AND x.processing_date_hour = %s::timestamp
              AND LOWER(x.constraint_status) IN ('fail', 'failed', 'failure', 'error')
              AND x.is_resolved = FALSE
            """
        )
        params.extend([table_ids, processing_date_hour])

    if include_auc:
        selects.append(
            """
            SELECT
                'lightgbm_auc' AS check_type,
                t.catalog_name,
                t.schema_name,
                t.table_name,
                NULL::text AS column_name,
                'lightgbm_auc' AS fail_metric,
                'AUC score indicates that the target batch distribution is significantly different from historical reference data.' AS metric_description,
                x.auc_score AS actual_value,
                NULL::float AS min_threshold,
                x.auc_threshold AS max_threshold,
                x.severity_level::text,
                x.processing_date_hour,
                x.created_at,
                NULL::text AS constraint_status,
                NULL::text AS constraint_value,
                NULL::text AS constraint_message
            FROM lightgbm_auc_verify x
            JOIN lightgbm_auc a
                ON a.id = x.lightgbm_result_id
            JOIN tables t
                ON t.id = a.table_id
            WHERE a.table_id = ANY(%s::uuid[])
              AND x.processing_date_hour = %s::timestamp
              AND x.status = 'fail'
              AND x.is_resolved = FALSE
            """
        )
        params.extend([table_ids, processing_date_hour])

    sql = f"""
        SELECT *
        FROM (
            {" UNION ALL ".join(selects)}
        ) q
        ORDER BY
            CASE severity_level
                WHEN 'critical' THEN 1
                WHEN 'warning' THEN 2
                ELSE 3
            END,
            check_type,
            catalog_name,
            schema_name,
            table_name,
            column_name,
            fail_metric
    """

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
        f"• LightGBM AUC: `{type_counts.get('lightgbm_auc', 0)}`",
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
        "lightgbm_auc": "LightGBM AUC",
    }

    shown = 0

    for check_type in ["metadata", "profiling", "rule", "lightgbm_auc"]:
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
                lines.append(f"• Constraint Status: `{format_value(row.get('constraint_status'))}`")
                lines.append(f"• Constraint: `{format_value(row.get('constraint_value'))}`")

                if row.get("constraint_message"):
                    lines.append(f"• Constraint Message: {row['constraint_message']}")
            else:
                lines.append(f"• Actual Value: `{format_value(row.get('actual_value'))}`")
                lines.append(f"• Threshold: {threshold_text(row)}")

            lines.append(f"• Result Created At: `{format_datetime(row.get('created_at'))}`")
            lines.append("")

    if len(rows) > max_detail_rows:
        lines.append(
            f"...and `{len(rows) - max_detail_rows}` more unresolved failures. "
            "Please check Grafana/DataGate dashboard for the full list."
        )

    return "\n".join(lines)


def send_slack_message(slack_webhook_conn_id, message):
    SlackWebhookHook(
        slack_webhook_conn_id=slack_webhook_conn_id,
    ).send_text(message)


def run_quality_gate(
    datagate_db_conn_id,
    processing_date_hour,
    connection_name,
    schema_name,
    include_rule=False,
    include_auc=False,
    slack_webhook_conn_id="slack_dq",
    max_alert_rows=30,
):
    schema_name = validate_name(schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    connection_config = get_connection_config(pg_hook, connection_name)

    table_ids = get_active_tables(
        pg_hook,
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
        pg_hook=pg_hook,
        table_ids=table_ids,
        processing_date_hour=processing_date_hour,
        include_rule=include_rule,
        include_auc=include_auc,
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
        type_counts.get("lightgbm_auc", 0),
    )

    if rows:
        message = build_quality_alert_message(
            connection_name=connection_name,
            schema_name=schema_name,
            processing_date_hour=processing_date_hour,
            rows=rows,
            max_detail_rows=max_alert_rows,
        )
        send_slack_message(slack_webhook_conn_id, message)

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
            f"auc_fail={type_counts.get('lightgbm_auc', 0)}"
        )

    return True