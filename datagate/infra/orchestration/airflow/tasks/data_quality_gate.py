try:
    from .data_quality_alert_utils import run_quality_gate
except ImportError:
    from data_quality_alert_utils import run_quality_gate


def data_quality_gate(
    datagate_db_conn_id,
    processing_date_hour,
    connection_name,
    schema_name,
    slack_webhook_conn_id="slack_dq",
):
    schema = str(schema_name).strip().lower()
    return run_quality_gate(datagate_db_conn_id,processing_date_hour,connection_name,schema_name,schema in {"silver", "gold"},schema == "silver",slack_webhook_conn_id)
