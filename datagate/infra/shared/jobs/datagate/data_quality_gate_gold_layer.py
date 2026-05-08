import logging

from data_quality_alert_utils import run_quality_gate


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_data_quality_gate_gold_layer(
    datagate_db_conn_id,
    processing_date_hour,
    connection_name,
    schema_name,
    slack_webhook_conn_id="slack_dq",
):
    return run_quality_gate(
        datagate_db_conn_id=datagate_db_conn_id,
        processing_date_hour=processing_date_hour,
        connection_name=connection_name,
        schema_name=schema_name,
        include_rule=True,
        include_auc=False,
        slack_webhook_conn_id=slack_webhook_conn_id,
    )