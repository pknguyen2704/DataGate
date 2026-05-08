from data_quality_alert_utils import run_quality_gate


def check_data_quality_gate(
    datagate_db_conn_id,
    processing_date_hour,
    connection_name,
    schema_name,
    slack_webhook_conn_id="slack_dq",
):
    schema = str(schema_name).strip().lower()

    return run_quality_gate(
        datagate_db_conn_id=datagate_db_conn_id,
        processing_date_hour=processing_date_hour,
        connection_name=connection_name,
        schema_name=schema_name,
        include_rule=schema in {"silver", "gold"},
        include_auc=schema == "silver",
        slack_webhook_conn_id=slack_webhook_conn_id,
    )