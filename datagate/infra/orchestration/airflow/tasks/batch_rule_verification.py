import argparse
import gc
import logging
import os
import sys
import uuid
from contextlib import suppress
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.checks import Check, CheckLevel, ConstrainableDataTypes
from pydeequ.verification import VerificationSuite, VerificationResult
from pyspark.sql import SparkSession


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "batch_rule_verification"

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--datagate_db_conn_id", default="datagate_db_default")
    p.add_argument("--connection_name", required=True)
    p.add_argument("--schema_name", required=True)
    p.add_argument("--processing_date_hour", required=True)
    return p.parse_args()


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


def get_connection_config(pg_hook, connection_name):
    if connection_name is None or str(connection_name).strip() == "":
        raise ValueError("connection_name must not be None or empty.")

    row = pg_hook.get_first(
        """
        SELECT
            id,
            connection_name,
            rest_url,
            catalog_warehouse,
            catalog_name,
            storage_endpoint_url,
            storage_access_key,
            storage_secret_key
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,)
    )

    if row is None:
        raise ValueError(f"No active connection found with name={connection_name}")

    return {
        "connection_id": str(row[0]),
        "connection_name": row[1],
        "rest_url": row[2],
        "catalog_warehouse": row[3],
        "catalog_name": validate_name(row[4], "catalog_name"),
        "storage_endpoint_url": row[5],
        "storage_access_key": row[6],
        "storage_secret_key": row[7]
    }

def get_active_tables(pg_hook, connection_id, catalog_name, schema_name):
    schema_name = validate_name(schema_name, "schema_name")

    rows = pg_hook.get_records(
        """
        SELECT id, table_name
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(connection_id, catalog_name, schema_name)
    )

    return [
        {
            "table_id": str(row[0]),
            "table_name": validate_name(row[1], "table_name"),
            "full_table_name": f"{catalog_name}.{schema_name}.{row[1]}"
        }
        for row in rows
    ]


def get_active_rules(pg_hook, table_id):
    rows = pg_hook.get_records(
        """
        SELECT id, column_name, constraint_name, code_for_constraint, severity_level
        FROM rules
        WHERE table_id = %s
          AND is_active = TRUE
        ORDER BY column_name, code_for_constraint
        """,
        parameters=(table_id,)
    )

    return [
        {
            "rule_id": str(row[0]),
            "table_id": table_id,
            "column_name": row[1],
            "constraint": row[2] or row[3],
            "code_for_constraint": row[3],
            "severity_level": row[4]
        }
        for row in rows
    ]


def create_spark_session(connection_config):
    catalog_name = connection_config["catalog_name"]

    return (
        SparkSession.builder.appName(JOB_NAME)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(f"spark.sql.catalog.{catalog_name}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{catalog_name}.type", "rest")
        .config(
            f"spark.sql.catalog.{catalog_name}.uri", connection_config["rest_url"]
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.warehouse",
            connection_config["catalog_warehouse"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.io-impl", "org.apache.iceberg.aws.s3.S3FileIO"
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.endpoint",
            connection_config["storage_endpoint_url"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.access-key-id",
            connection_config["storage_access_key"],
        )
        .config(
            f"spark.sql.catalog.{catalog_name}.s3.secret-access-key",
            connection_config["storage_secret_key"],
        )
        .config(f"spark.sql.catalog.{catalog_name}.s3.path-style-access", "true")
        .config(f"spark.sql.catalog.{catalog_name}.s3.region", "us-east-1")
        .getOrCreate()
    )


def read_batch_table(spark, table_name, processing_date_hour):
    df = spark.table(table_name)

    if "processing_date_hour" not in df.columns:
        raise ValueError(
            f"Table {table_name} does not have processing_date_hour column."
        )

    return spark.sql(f"""
        SELECT *
        FROM {table_name}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)

# Read stored rule from database to code
def add_rule_to_check(check, rule):
    code = str(rule.get("code_for_constraint") or "").strip()

    if not code:
        raise ValueError("code_for_constraint must not be empty.")

    return eval(
        "check" + code,
        {"__builtins__": {}},
        {
            "check": check,
            "ConstrainableDataTypes": ConstrainableDataTypes,
        },
    )


def map_status(value):
    value = str(value or "").strip().lower()
    if value == "success":
        return "pass"
    if value == "failure":
        return "fail"
    return "error"


def save_results(pg_hook, rows, processing_date_hour):
    if not rows:
        return

    sql = """
        INSERT INTO quality_check_results (
            id, table_id, check_type, rule_id, column_name, metric_name,
            status, severity_level, message, is_resolved,
            processing_date_hour, created_at, updated_at
        )
        VALUES %s
        ON CONFLICT (table_id, check_type, rule_id, processing_date_hour) WHERE rule_id IS NOT NULL
        DO UPDATE SET
            column_name = EXCLUDED.column_name,
            metric_name = EXCLUDED.metric_name,
            status = EXCLUDED.status,
            severity_level = EXCLUDED.severity_level,
            message = EXCLUDED.message,
            is_resolved = FALSE,
            updated_at = NOW()
    """

    values = [
        (
            str(uuid.uuid4()),
            row["table_id"],
            "rule",
            row["rule_id"],
            row["column_name"],
            row["constraint"],
            row["constraint_status"],
            row["severity_level"],
            row["constraint_message"],
            processing_date_hour,
        )
        for row in rows
    ]

    conn = pg_hook.get_conn()

    with conn.cursor() as cur:
        execute_values(
            cur,
            sql,
            values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())",
        )

    conn.commit()


def verify_rules_for_table(spark, table_info, rules, processing_date_hour):
    if not rules:
        logger.info(
            "No active rules, skip table | table=%s", table_info["full_table_name"]
        )
        return []

    logger.info(
        "Start rule verification | table=%s | active_rules=%s",
        table_info["full_table_name"],
        len(rules),
    )

    try:
        df = read_batch_table(
            spark, table_info["full_table_name"], processing_date_hour
        )
    except Exception as exc:
        logger.warning(
            "Skip table because batch cannot be read | table=%s | error=%s",
            table_info["full_table_name"],
            str(exc),
        )
        return []

    check = Check(
        spark,
        CheckLevel.Warning,
        f"DataGate rules for {table_info['full_table_name']}",
    )

    runnable_rules = []

    for rule in rules:
        try:
            check = add_rule_to_check(check, rule)
            runnable_rules.append(rule)
        except Exception as exc:
            logger.warning(
                "Skip invalid rule | table=%s | rule_id=%s | column=%s | error=%s",
                table_info["full_table_name"],
                rule["rule_id"],
                rule["column_name"],
                str(exc),
            )

    if not runnable_rules:
        logger.info(
            "No runnable active rules, skip table | table=%s",
            table_info["full_table_name"],
        )
        return []

    try:
        result = VerificationSuite(spark).onData(df).addCheck(check).run()
        result_rows = VerificationResult.checkResultsAsDataFrame(
            spark, result
        ).collect()
    except Exception as exc:
        logger.warning(
            "Skip table because verification failed | table=%s | error=%s",
            table_info["full_table_name"],
            str(exc),
        )
        return []

    rows = []

    for index, rule in enumerate(runnable_rules):
        if index >= len(result_rows):
            continue

        item = result_rows[index].asDict()

        rows.append(
            {
                "rule_id": rule["rule_id"],
                "table_id": rule["table_id"],
                "column_name": rule["column_name"],
                "severity_level": rule["severity_level"],
                "constraint": rule["constraint"],
                "constraint_status": map_status(item.get("constraint_status")),
                "constraint_message": item.get("constraint_message"),
            }
        )

    logger.info(
        "Rule verification finished | table=%s | runnable_rules=%s | result_rows=%s",
        table_info["full_table_name"],
        len(runnable_rules),
        len(rows),
    )

    return rows


# Close hook connection
def close_hook_connection(hook):
    if hook is None:
        return
    for attr_name in ("conn", "_conn"):
        with suppress(Exception):
            conn = getattr(hook, attr_name, None)
            if conn is not None:
                conn.close()


def stop_spark_session(spark):
    if spark is None:
        return
    with suppress(Exception):
        spark.catalog.clearCache()
    with suppress(Exception):
        spark.sparkContext.cancelAllJobs()
    with suppress(Exception):
        spark.stop()


def main():
    args = parse_args()
    connection_name = validate_name(args.connection_name, "connection_name")
    schema_name = validate_name(args.schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(args.processing_date_hour)

    logger.info(
        "Rule verification job started | connection=%s | schema=%s | hour=%s",
        connection_name,
        schema_name,
        processing_date_hour,
    )

    pg_hook = None
    spark = None

    try:
        pg_hook = PostgresHook(postgres_conn_id=args.datagate_db_conn_id)
        connection_config = get_connection_config(pg_hook, connection_name)
        tables = get_active_tables(pg_hook, connection_config["connection_id"], connection_config["catalog_name"], schema_name)

        if not tables:
            logger.info("No active tables found | schema=%s", schema_name)
            return 0

        logger.info(
            "Found active tables | schema=%s | tables=%s", schema_name, len(tables)
        )

        spark = create_spark_session(connection_config)
        total = 0

        for table in tables:
            rules = get_active_rules(pg_hook, table["table_id"])

            logger.info(
                "Loaded rules | table=%s | active_rules=%s",
                table["full_table_name"],
                len(rules),
            )

            rows = verify_rules_for_table(spark, table, rules, processing_date_hour)

            save_results(pg_hook, rows, processing_date_hour)

            total += len(rows)

        logger.info(
            "Rule verification completed | schema=%s | tables=%s | saved_results=%s",
            schema_name,
            len(tables),
            total,
        )
        return 0

    except Exception:
        logger.exception(
            "Rule verification failed | connection=%s | schema=%s | hour=%s",
            connection_name,
            schema_name,
            processing_date_hour,
        )
        return 1

    finally:
        stop_spark_session(spark)
        close_hook_connection(pg_hook)
        gc.collect()


if __name__ == "__main__":
    exit_code = main()
    with suppress(Exception):
        sys.stdout.flush()
    with suppress(Exception):
        sys.stderr.flush()
    logging.shutdown()
    os._exit(exit_code)
