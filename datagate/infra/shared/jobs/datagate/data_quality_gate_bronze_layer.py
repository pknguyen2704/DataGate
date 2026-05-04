from airflow.exceptions import AirflowException
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator


def check_data_quality_gate(
    datagate_db_conn_id,
    processing_date_hour,
    connection_name=None,
    schema_name=None,
):
    """
    Quality gate trước khi cho ETL chạy tiếp.

    Blocking conditions:
    - metric_results.status = 'fail'
    - rule_verification_result.constraint_status IN ('failed', 'error')

    Nếu có lỗi:
    - raise AirflowException
    - downstream tasks sẽ không chạy tiếp
    """

    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    filters = [
        "x.processing_date_hour = %s"
    ]

    params = [
        processing_date_hour,
    ]

    if connection_name:
        filters.append("c.connection_name = %s")
        params.append(connection_name)

    if schema_name:
        filters.append("t.schema_name = %s")
        params.append(schema_name)

    where_clause = " AND ".join(filters)

    sql = f"""
        WITH failed_checks AS (
            SELECT
                'metric' AS check_type,
                t.schema_name,
                t.table_name,
                x.column_name,
                x.metric_name AS check_name,
                x.status AS status,
                x.severity_level,
                x.message,
                x.processing_date_hour
            FROM metric_results x
            JOIN tables t
              ON t.id = x.table_id
            JOIN connections c
              ON c.id = t.connection_id
            WHERE {where_clause}
              AND x.status = 'fail'

            UNION ALL

            SELECT
                'rule' AS check_type,
                t.schema_name,
                t.table_name,
                x.column_name,
                COALESCE(x.constraint_name, x.code_for_constraint) AS check_name,
                x.constraint_status AS status,
                x.severity_level,
                x.constraint_message AS message,
                x.processing_date_hour
            FROM rule_verification_result x
            JOIN tables t
              ON t.id = x.table_id
            JOIN connections c
              ON c.id = t.connection_id
            WHERE {where_clause}
              AND x.constraint_status IN ('failed', 'error')
        )
        SELECT
            check_type,
            schema_name,
            table_name,
            column_name,
            check_name,
            status,
            severity_level,
            message,
            processing_date_hour
        FROM failed_checks
        ORDER BY
            severity_level DESC,
            check_type,
            schema_name,
            table_name,
            column_name
        LIMIT 50
    """

    # params cần nhân đôi vì where_clause dùng trong 2 SELECT của UNION ALL
    rows = pg_hook.get_records(
        sql,
        parameters=tuple(params + params),
    )

    if not rows:
        print(
            "[QUALITY GATE PASSED] "
            f"No failed checks found for processing_date_hour={processing_date_hour}"
        )
        return True

    print("\n========== QUALITY GATE FAILED ==========")
    print(f"processing_date_hour = {processing_date_hour}")

    for row in rows:
        (
            check_type,
            schema_name,
            table_name,
            column_name,
            check_name,
            status,
            severity_level,
            message,
            result_processing_date_hour,
        ) = row

        print(
            f"- [{severity_level}] {check_type} | "
            f"{schema_name}.{table_name} | "
            f"column={column_name} | "
            f"check={check_name} | "
            f"status={status} | "
            f"message={message}"
        )

    print("=========================================\n")

    raise AirflowException(
        f"Quality gate failed. Found {len(rows)} failed check(s). "
        "Stop ETL pipeline."
    )