rule_verification_task = SparkSubmitOperator(
    task_id="verify_active_rules",
    conn_id="spark_default",
    application="/opt/airflow/dags/jobs/batch_rule_verification_job.py",
    name="batch_rule_verification",
    master="spark://spark-master:7077",
    deploy_mode="client",

    driver_cores=2,
    driver_memory="4g",
    executor_cores=6,
    executor_memory="10g",
    num_executors=2,

    conf={
        "spark.sql.shuffle.partitions": "24",
        "spark.sql.session.timeZone": "Asia/Ho_Chi_Minh",
        "spark.standalone.submit.waitAppCompletion": "true",
        "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    },

    application_args=[
        "--datagate_db_conn_id", "datagate_db_default",
        "--connection_name", "local_iceberg",
        "--schema_name", "silver",
        "--processing_date_hour", "{{ dag_run.conf.get('processing_date_hour', params.processing_date_hour) }}",
    ],

    verbose=True,
import argparse

import logging
import os
import uuid
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.checks import Check, CheckLevel
from pydeequ.verification import VerificationSuite, VerificationResult

from pyspark.sql import SparkSession


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SPARK_APP_NAME = "batch_rule_verification"


# ============================================================
# 1. Input arguments
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify active rules on Iceberg batch data and save results to DataGate DB"
    )

    parser.add_argument(
        "--datagate_db_conn_id",
        default="datagate_db_default",
        help="Airflow Postgres connection id for DataGate DB",
    )

    parser.add_argument("--connection_name", required=True)
    parser.add_argument("--schema_name", required=True)
    parser.add_argument("--processing_date_hour", required=True)

    return parser.parse_args()


# ============================================================
# 2. Validate input
# ============================================================

def validate_name(value, field_name):
    if value is None:
        raise ValueError(f"{field_name} must not be None.")

    value = str(value).strip()

    if value == "":
        raise ValueError(f"{field_name} must not be empty.")

    for char in value:
        if not (char.isalnum() or char == "_"):
            raise ValueError(
                f"Invalid {field_name}: {value}. "
                "Only letters, numbers, and underscore (_) are allowed."
            )

    return value


def normalize_processing_date_hour(processing_date_hour):
    if processing_date_hour is None:
        raise ValueError("processing_date_hour must not be None.")

    value = str(processing_date_hour).strip().replace("T", " ")

    if value == "":
        raise ValueError("processing_date_hour must not be empty.")

    dt = datetime.fromisoformat(value)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 3. Read DataGate metadata from PostgreSQL
# ============================================================

def get_connection_config(pg_hook, connection_name):
    connection_name = str(connection_name).strip()

    if connection_name == "":
        raise ValueError("connection_name must not be empty.")

    row = pg_hook.get_first(
        """
        SELECT
            id,
            name,
            iceberg_rest_url,
            iceberg_catalog_name,
            minio_endpoint_url,
            minio_access_key,
            minio_secret_key
        FROM connections
        WHERE name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,),
    )

    if row is None:
        raise ValueError(
            f"No active connection found with name={connection_name}"
        )

    return {
        "connection_id": str(row[0]),
        "connection_name": str(row[1]),
        "iceberg_rest_url": row[2],
        "iceberg_catalog_name": validate_name(row[3], "iceberg_catalog_name"),
        "minio_endpoint_url": row[4],
        "minio_access_key": row[5],
        "minio_secret_key": row[6],
    }


def get_active_tables(pg_hook, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT
            id,
            table_name
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(catalog_name, schema_name),
    )

    tables = []

    for table_id, table_name in rows:
        table_name = validate_name(table_name, "table_name")

        tables.append(
            {
                "table_id": str(table_id),
                "table_name": table_name,
                "full_table_name": f"{catalog_name}.{schema_name}.{table_name}",
            }
        )

    return tables


def get_active_rules(pg_hook, table_id):
    rows = pg_hook.get_records(
        """
        SELECT
            id,
            table_id,
            source,
            importance_level,
            column_name,
            constraint_name,
            description,
            current_value,
            suggesting_rule,
            code_for_constraint,
            rule_description
        FROM rules
        WHERE table_id = %s
          AND status = 'active'
        ORDER BY column_name, code_for_constraint
        """,
        parameters=(table_id,),
    )

    rules = []

    for row in rows:
        rules.append(
            {
                "rule_id": str(row[0]),
                "table_id": str(row[1]),
                "source": row[2],
                "importance_level": row[3],
                "column_name": row[4],
                "constraint_name": row[5],
                "description": row[6],
                "current_value": row[7],
                "suggesting_rule": row[8],
                "code_for_constraint": row[9],
                "rule_description": row[10],
            }
        )

    return rules


# ============================================================
# 4. Save verification results
# ============================================================

def save_rule_verification_results(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO rule_verification_result (
            id,
            table_id,
            rule_id,
            source,
            importance_level,
            column_name,
            constraint_name,
            description,
            current_value,
            suggesting_rule,
            code_for_constraint,
            rule_description,
            constraint_status,
            constraint_message,
            checked_rows,
            processing_date_hour,
            created_at
        )
        VALUES %s
        ON CONFLICT (table_id, rule_id, processing_date_hour)
        DO UPDATE SET
            source = EXCLUDED.source,
            importance_level = EXCLUDED.importance_level,
            column_name = EXCLUDED.column_name,
            constraint_name = EXCLUDED.constraint_name,
            description = EXCLUDED.description,
            current_value = EXCLUDED.current_value,
            suggesting_rule = EXCLUDED.suggesting_rule,
            code_for_constraint = EXCLUDED.code_for_constraint,
            rule_description = EXCLUDED.rule_description,
            constraint_status = EXCLUDED.constraint_status,
            constraint_message = EXCLUDED.constraint_message,
            checked_rows = EXCLUDED.checked_rows,
            created_at = EXCLUDED.created_at
    """

    now = datetime.utcnow()
    values = []

    for row in rows:
        values.append(
            (
                str(uuid.uuid4()),
                row["table_id"],
                row["rule_id"],
                row["source"],
                row["importance_level"],
                row["column_name"],
                row["constraint_name"],
                row["description"],
                row["current_value"],
                row["suggesting_rule"],
                row["code_for_constraint"],
                row["rule_description"],
                row["constraint_status"],
                row["constraint_message"],
                row["checked_rows"],
                row["processing_date_hour"],
                now,
            )
        )

    conn = pg_hook.get_conn()

    with conn.cursor() as cursor:
        execute_values(cursor, sql, values)

    conn.commit()


# ============================================================
# 5. Spark session
# ============================================================

def create_spark_session(connection_config):
    catalog_name = connection_config["iceberg_catalog_name"]

    return (
        SparkSession.builder
        .appName(SPARK_APP_NAME)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            f"spark.sql.catalog.{catalog_name}",
            "org.apache.iceberg.spark.SparkCatalog",
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.type",
            "rest",
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.uri",
            connection_config["iceberg_rest_url"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.io-impl",
            "org.apache.iceberg.aws.s3.S3FileIO",
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.warehouse",
            "s3://lakehouse/",
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.endpoint",
            connection_config["minio_endpoint_url"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.access-key-id",
            connection_config["minio_access_key"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.secret-access-key",
            connection_config["minio_secret_key"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.path-style-access",
            "true",
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.region",
            "us-east-1",
        )
        .getOrCreate()
    )


# ============================================================
# 6. Read only target batch
# ============================================================

def read_batch_table(spark, full_table_name, processing_date_hour):
    table_df = spark.table(full_table_name)

    if "processing_date_hour" not in table_df.columns:
        raise ValueError(
            f"Table {full_table_name} does not have processing_date_hour column."
        )

    sql = f"""
        SELECT *
        FROM {full_table_name}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """

    return spark.sql(sql)


# ============================================================
# 7. Convert active rule to PyDeequ Check
# ============================================================

def add_rule_code_to_check(check, rule):
    code_for_constraint = rule.get("code_for_constraint")

    if code_for_constraint is None:
        raise ValueError("code_for_constraint must not be None.")

    code_for_constraint = str(code_for_constraint).strip()

    if code_for_constraint == "":
        raise ValueError("code_for_constraint must not be empty.")

    expression = "check" + code_for_constraint

    return eval(
        expression,
        {"__builtins__": {}},
        {
            "check": check,
        },
    )


# ============================================================
# 8. Build result rows
# ============================================================

def map_constraint_status(pydeequ_status):
    value = str(pydeequ_status or "").strip().lower()

    if value == "success":
        return "success"

    if value == "failure":
        return "failed"

    if value == "error":
        return "error"

    return "error"


def build_result_row(
    rule,
    constraint_status,
    constraint_message,
    checked_rows,
    processing_date_hour,
):
    return {
        "table_id": rule["table_id"],
        "rule_id": rule["rule_id"],
        "source": rule["source"],
        "importance_level": rule["importance_level"],
        "column_name": rule["column_name"],
        "constraint_name": rule["constraint_name"],
        "description": rule["description"],
        "current_value": rule["current_value"],
        "suggesting_rule": rule["suggesting_rule"],
        "code_for_constraint": rule["code_for_constraint"],
        "rule_description": rule["rule_description"],
        "constraint_status": constraint_status,
        "constraint_message": constraint_message,
        "checked_rows": checked_rows,
        "processing_date_hour": processing_date_hour,
    }


def build_error_result(rule, message, processing_date_hour):
    return build_result_row(
        rule=rule,
        constraint_status="error",
        constraint_message=message,
        checked_rows=None,
        processing_date_hour=processing_date_hour,
    )


# ============================================================
# 9. Verify rules for one table
# ============================================================

def verify_rules_for_table(spark, table_info, rules, processing_date_hour):
    full_table_name = table_info["full_table_name"]

    logger.info(
        "Verifying rules | table=%s | rules=%s | processing_date_hour=%s",
        full_table_name,
        len(rules),
        processing_date_hour,
    )

    try:
        batch_df = read_batch_table(
            spark=spark,
            full_table_name=full_table_name,
            processing_date_hour=processing_date_hour,
        )
    except Exception as exc:
        return [
            build_error_result(
                rule=rule,
                message=str(exc),
                processing_date_hour=processing_date_hour,
            )
            for rule in rules
        ]

    check = Check(
        spark,
        CheckLevel.Warning,
        f"DataGate rules for {full_table_name}",
    )

    runnable_rules = []
    error_rows = []

    for rule in rules:
        try:
            check = add_rule_code_to_check(
                check=check,
                rule=rule,
            )
            runnable_rules.append(rule)

        except Exception as exc:
            error_rows.append(
                build_error_result(
                    rule=rule,
                    message=str(exc),
                    processing_date_hour=processing_date_hour,
                )
            )

    if not runnable_rules:
        return error_rows

    try:
        check_result = (
            VerificationSuite(spark)
            .onData(batch_df)
            .addCheck(check)
            .run()
        )

        check_result_df = VerificationResult.checkResultsAsDataFrame(
            spark,
            check_result,
        )

        pydeequ_rows = check_result_df.collect()

    except Exception as exc:
        return error_rows + [
            build_error_result(
                rule=rule,
                message=str(exc),
                processing_date_hour=processing_date_hour,
            )
            for rule in runnable_rules
        ]

    result_rows = list(error_rows)

    for index, rule in enumerate(runnable_rules):
        if index >= len(pydeequ_rows):
            result_rows.append(
                build_error_result(
                    rule=rule,
                    message="PyDeequ did not return result for this rule.",
                    processing_date_hour=processing_date_hour,
                )
            )
            continue

        pydeequ_row = pydeequ_rows[index].asDict()

        constraint_status = map_constraint_status(
            pydeequ_row.get("constraint_status")
        )

        constraint_message = pydeequ_row.get("constraint_message")

        result_rows.append(
            build_result_row(
                rule=rule,
                constraint_status=constraint_status,
                constraint_message=constraint_message,
                checked_rows=None,
                processing_date_hour=processing_date_hour,
            )
        )

    return result_rows


# ============================================================
# 10. Main
# ============================================================

def main():
    args = parse_args()

    schema_name = validate_name(args.schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(
        args.processing_date_hour
    )

    pg_hook = PostgresHook(
        postgres_conn_id=args.datagate_db_conn_id
    )

    connection_config = get_connection_config(
        pg_hook=pg_hook,
        connection_name=args.connection_name,
    )

    catalog_name = connection_config["iceberg_catalog_name"]

    active_tables = get_active_tables(
        pg_hook=pg_hook,
        catalog_name=catalog_name,
        schema_name=schema_name,
    )

    if not active_tables:
        logger.warning(
            "No active tables found | connection=%s | catalog=%s | schema=%s",
            connection_config["connection_name"],
            catalog_name,
            schema_name,
        )
        return

    spark = create_spark_session(connection_config)

    try:
        total_rows = 0

        for table_info in active_tables:
            rules = get_active_rules(
                pg_hook=pg_hook,
                table_id=table_info["table_id"],
            )

            if not rules:
                logger.info(
                    "Skip table because no active rules | table=%s",
                    table_info["full_table_name"],
                )
                continue

            result_rows = verify_rules_for_table(
                spark=spark,
                table_info=table_info,
                rules=rules,
                processing_date_hour=processing_date_hour,
            )

            save_rule_verification_results(
                pg_hook=pg_hook,
                rows=result_rows,
            )

            total_rows += len(result_rows)

            logger.info(
                "Saved rule verification results | table=%s | rows=%s",
                table_info["full_table_name"],
                len(result_rows),
            )

        logger.info(
            "Rule verification completed | total_result_rows=%s",
            total_rows,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()