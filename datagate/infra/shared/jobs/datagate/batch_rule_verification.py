import argparse
import logging
import os
import uuid
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

SPARK_DRIVER_CORES = "2"
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_INSTANCES = "2"
SPARK_EXECUTOR_CORES = "6"
SPARK_EXECUTOR_MEMORY = "10g"
SPARK_SQL_SHUFFLE_PARTITIONS = "24"
SPARK_DEFAULT_PARALLELISM = "24"
SPARK_TIMEZONE = "Asia/Ho_Chi_Minh"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--datagate_db_conn_id", default="datagate_db_default")
    p.add_argument("--connection_name", required=True)
    p.add_argument("--schema_name", required=True)
    p.add_argument("--processing_date_hour", required=True)
    return p.parse_args()


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


def get_connection_config(pg_hook, connection_name):
    row = pg_hook.get_first(
        """
        SELECT connection_name, iceberg_rest_url, iceberg_warehouse, iceberg_catalog_name,
               minio_endpoint_url, minio_access_key, minio_secret_key
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(validate_name(connection_name, "connection_name"),),
    )

    if row is None:
        raise ValueError(f"No active connection found: {connection_name}")

    return {
        "connection_name": row[0],
        "iceberg_rest_url": row[1],
        "iceberg_warehouse": row[2],
        "catalog_name": validate_name(row[3], "iceberg_catalog_name"),
        "minio_endpoint_url": row[4],
        "minio_access_key": row[5],
        "minio_secret_key": row[6],
    }


def get_active_tables(pg_hook, catalog_name, schema_name):
    schema_name = validate_name(schema_name, "schema_name")

    rows = pg_hook.get_records(
        """
        SELECT id, table_name
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(catalog_name, schema_name),
    )

    return [
        {
            "table_id": str(row[0]),
            "table_name": validate_name(row[1], "table_name"),
            "full_table_name": f"{catalog_name}.{schema_name}.{row[1]}",
        }
        for row in rows
    ]


def get_active_rules(pg_hook, table_id):
    rows = pg_hook.get_records(
        """
        SELECT id, column_name, constraint_name, code_for_constraint, severity_level
        FROM rules
        WHERE table_id = %s
          AND status = 'active'
        ORDER BY column_name, code_for_constraint
        """,
        parameters=(table_id,),
    )

    return [
        {
            "rule_id": str(row[0]),
            "column_name": row[1],
            "constraint": row[2] or row[3],
            "code_for_constraint": row[3],
            "severity_level": row[4],
        }
        for row in rows
    ]


def create_spark_session(connection_config):
    catalog = connection_config["catalog_name"]

    return (
        SparkSession.builder.appName(JOB_NAME)
        .config("spark.driver.cores", SPARK_DRIVER_CORES)
        .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .config("spark.executor.instances", SPARK_EXECUTOR_INSTANCES)
        .config("spark.executor.cores", SPARK_EXECUTOR_CORES)
        .config("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        .config("spark.sql.session.timeZone", SPARK_TIMEZONE)
        .config("spark.sql.shuffle.partitions", SPARK_SQL_SHUFFLE_PARTITIONS)
        .config("spark.default.parallelism", SPARK_DEFAULT_PARALLELISM)
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config(f"spark.sql.catalog.{catalog}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{catalog}.type", "rest")
        .config(f"spark.sql.catalog.{catalog}.uri", connection_config["iceberg_rest_url"])
        .config(f"spark.sql.catalog.{catalog}.warehouse", connection_config["iceberg_warehouse"])
        .config(f"spark.sql.catalog.{catalog}.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .config(f"spark.sql.catalog.{catalog}.s3.endpoint", connection_config["minio_endpoint_url"])
        .config(f"spark.sql.catalog.{catalog}.s3.access-key-id", connection_config["minio_access_key"])
        .config(f"spark.sql.catalog.{catalog}.s3.secret-access-key", connection_config["minio_secret_key"])
        .config(f"spark.sql.catalog.{catalog}.s3.path-style-access", "true")
        .config(f"spark.sql.catalog.{catalog}.s3.region", "us-east-1")
        .getOrCreate()
    )


def read_batch_table(spark, table_name, processing_date_hour):
    df = spark.table(table_name)

    if "processing_date_hour" not in df.columns:
        raise ValueError(f"Table {table_name} does not have processing_date_hour column.")

    return spark.sql(f"""
        SELECT *
        FROM {table_name}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)


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
        return "success"

    if value == "failure":
        return "failed"

    return "error"

def save_results(pg_hook, rows, processing_date_hour):
    if not rows:
        return

    sql = """
        INSERT INTO rule_verify (
            id,
            rule_id,
            severity_level,
            "constraint",
            constraint_status,
            constraint_message,
            is_resolved,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (rule_id, processing_date_hour)
        DO UPDATE SET
            severity_level = EXCLUDED.severity_level,
            "constraint" = EXCLUDED."constraint",
            constraint_status = EXCLUDED.constraint_status,
            constraint_message = EXCLUDED.constraint_message,
            updated_at = NOW()
    """

    values = [
        (
            str(uuid.uuid4()),
            row["rule_id"],
            row["severity_level"],
            row["constraint"],
            row["constraint_status"],
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
            template="(%s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())",
        )

    conn.commit()

def verify_rules_for_table(spark, table_info, rules, processing_date_hour):
    if not rules:
        logger.info("No active rules, skip table | table=%s", table_info["full_table_name"])
        return []

    logger.info(
        "Start rule verification | table=%s | active_rules=%s",
        table_info["full_table_name"],
        len(rules),
    )

    try:
        df = read_batch_table(spark, table_info["full_table_name"], processing_date_hour)
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
        logger.info("No runnable active rules, skip table | table=%s", table_info["full_table_name"])
        return []

    try:
        result = VerificationSuite(spark).onData(df).addCheck(check).run()
        result_rows = VerificationResult.checkResultsAsDataFrame(spark, result).collect()
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


def main():
    args = parse_args()
    schema_name = validate_name(args.schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(args.processing_date_hour)

    logger.info(
        "Rule verification job started | connection=%s | schema=%s | hour=%s",
        args.connection_name,
        schema_name,
        processing_date_hour,
    )

    pg_hook = PostgresHook(postgres_conn_id=args.datagate_db_conn_id)
    connection_config = get_connection_config(pg_hook, args.connection_name)
    tables = get_active_tables(pg_hook, connection_config["catalog_name"], schema_name)

    if not tables:
        logger.info("No active tables found | schema=%s", schema_name)
        return

    logger.info("Found active tables | schema=%s | tables=%s", schema_name, len(tables))

    spark = create_spark_session(connection_config)

    try:
        total = 0

        for table in tables:
            rules = get_active_rules(pg_hook, table["table_id"])

            logger.info(
                "Loaded rules | table=%s | active_rules=%s",
                table["full_table_name"],
                len(rules),
            )

            rows = verify_rules_for_table(
                spark=spark,
                table_info=table,
                rules=rules,
                processing_date_hour=processing_date_hour,
            )

            save_results(
                pg_hook=pg_hook,
                rows=rows,
                processing_date_hour=processing_date_hour,
            )

            total += len(rows)

        logger.info(
            "Rule verification completed | schema=%s | tables=%s | saved_results=%s",
            schema_name,
            len(tables),
            total,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()