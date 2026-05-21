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
from pydeequ.suggestions import ConstraintSuggestionRunner, DEFAULT
from pyspark.sql import SparkSession, functions as F

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "batch_rule_suggestion"

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--datagate_db_conn_id", default="datagate_db_default")
    p.add_argument("--connection_name", required=True)
    p.add_argument("--schema_names", nargs="+", required=True)
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

# Normalize schema names
def normalize_schema_names(schema_names):
    result = []
    for item in schema_names:
        for part in str(item).split(","):
            name = part.strip()
            if name and name not in result:
                result.append(validate_name(name, "schema_name"))
    if not result:
        raise ValueError("schema_names must not be empty.")
    return result

def get_connection_config(pg_hook, connection_name):
    row = pg_hook.get_first(
        """
        SELECT id, connection_name, rest_url, catalog_warehouse, catalog_name,
               storage_endpoint_url, storage_access_key, storage_secret_key
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,)
    )
    if row is None:
        raise ValueError(f"No active connection found: {connection_name}")
    return {
        "connection_id": str(row[0]),
        "connection_name": row[1],
        "rest_url": row[2],
        "catalog_warehouse": row[3],
        "catalog_name": validate_name(row[4], "catalog_name"),
        "storage_endpoint_url": row[5],
        "storage_access_key": row[6],
        "storage_secret_key": row[7],
    }


def get_active_tables(pg_hook, connection_id, catalog_name, schema_names):
    placeholders = ", ".join(["%s"] * len(schema_names))
    rows = pg_hook.get_records(
        f"""
        SELECT id, schema_name, table_name
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND schema_name IN ({placeholders})
          AND is_active = TRUE
        ORDER BY schema_name, table_name
        """,
        parameters=tuple([connection_id, catalog_name] + schema_names),
    )
    return [
        {
            "table_id": str(r[0]),
            "schema_name": validate_name(r[1], "schema_name"),
            "table_name": validate_name(r[2], "table_name"),
            "full_table_name": f"{catalog_name}.{r[1]}.{r[2]}",
        }
        for r in rows
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
        logger.warning("Skip table without processing_date_hour | table=%s", table_name)
        return None
    return spark.sql(f"""
        SELECT *
        FROM {table_name}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
    """)


def prepare_suggestion_df(df):
    cols = [c for c in df.columns]
    if not cols:
        return df.select()
    df = df.select(cols)
    if not df.take(1):
        return df.select()
    counts = df.agg(*[F.count(F.col(c)).alias(c) for c in cols]).first().asDict()
    cols = [c for c in cols if (counts.get(c) or 0) > 0]
    return df.select(cols) if cols else df.select()


def run_suggestion(spark, df):
    return (
        ConstraintSuggestionRunner(spark).onData(df).addConstraintRule(DEFAULT()).run()
    )


def build_rule_rows(table_info, result):
    rows = []
    for item in result.get("constraint_suggestions", []):
        column_name = item.get("column_name")
        code = item.get("code_for_constraint")
        if not column_name or not code:
            continue
        rows.append(
            {
                "table_id": table_info["table_id"],
                "column_name": validate_name(column_name, "column_name"),
                "constraint_name": item.get("constraint_name"),
                "description": item.get("description"),
                "current_value": item.get("current_value"),
                "suggesting_rule": item.get("suggesting_rule"),
                "code_for_constraint": code,
            }
        )
    return rows


def save_rules(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO rules (
            id,
            table_id,
            source,
            is_active,
            severity_level,
            column_name,
            constraint_name,
            description,
            current_value,
            suggesting_rule,
            code_for_constraint,
            frequency,
            created_by,
            last_modified_by,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (table_id, source, column_name, code_for_constraint)
        DO UPDATE SET
            frequency = rules.frequency + 1,
            constraint_name = EXCLUDED.constraint_name,
            description = EXCLUDED.description,
            current_value = EXCLUDED.current_value,
            suggesting_rule = EXCLUDED.suggesting_rule,
            updated_at = NOW()
    """

    values = [
        (
            str(uuid.uuid4()),
            r["table_id"],
            "system",
            False,
            "warning",
            r["column_name"],
            r["constraint_name"],
            r["description"],
            r["current_value"],
            r["suggesting_rule"],
            r["code_for_constraint"],
            1,
            None,
            None,
        )
        for r in rows
    ]

    conn = pg_hook.get_conn()

    with conn.cursor() as cur:
        execute_values(
            cur,
            sql,
            values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
        )

    conn.commit()


def suggest_rules_for_table(spark, pg_hook, table_info, processing_date_hour):
    df = read_batch_table(spark, table_info["full_table_name"], processing_date_hour)
    if df is None:
        return 0
    df = prepare_suggestion_df(df)
    if not df.columns:
        return 0
    result = run_suggestion(spark, df)
    rows = build_rule_rows(table_info, result)
    save_rules(pg_hook, rows)
    logger.info(
        "Suggested rules saved | schema=%s | table=%s | rows=%s",
        table_info["schema_name"],
        table_info["table_name"],
        len(rows),
    )
    return len(rows)


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
    schema_names = normalize_schema_names(args.schema_names)
    connection_name = validate_name(args.connection_name, "connection_name")
    processing_date_hour = normalize_processing_date_hour(args.processing_date_hour)

    pg_hook = None
    spark = None

    try:
        pg_hook = PostgresHook(postgres_conn_id=args.datagate_db_conn_id)
        connection_config = get_connection_config(pg_hook, connection_name)
        catalog_name = connection_config["catalog_name"]
        active_tables = get_active_tables(pg_hook,connection_config["connection_id"],catalog_name,schema_names)

        if not active_tables:
            logger.info("No active tables found | schemas=%s", schema_names)
            return 0

        spark = create_spark_session(connection_config)
        total = sum(
            suggest_rules_for_table(spark, pg_hook, table, processing_date_hour)
            for table in active_tables
        )
        logger.info(
            "Rule suggestion completed | schemas=%s | tables=%s | total_rules=%s",
            schema_names,
            len(active_tables),
            total
        )
        return 0

    except Exception:
        logger.exception(
            "Rule suggestion failed | connection=%s | schemas=%s | hour=%s",
            connection_name,
            schema_names,
            processing_date_hour
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
