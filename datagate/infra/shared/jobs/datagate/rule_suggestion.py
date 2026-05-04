import argparse
import json
import logging
import os
import uuid
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

os.environ.setdefault("SPARK_VERSION", "3.5")

from py4j.protocol import Py4JJavaError
from pydeequ.suggestions import ConstraintSuggestionRunner, DEFAULT
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SPARK_APP_NAME = "batch_rule_suggestion"

EXCLUDED_COLUMNS = {
    "date_hour",
    "processing_date_hour",
}


# ============================================================
# 1. Input arguments
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate PyDeequ rule suggestions for active tables in a connection"
    )

    parser.add_argument(
        "--datagate_db_conn_id",
        default="datagate_db_default",
        help="Airflow Postgres connection id for DataGate DB",
    )

    parser.add_argument(
        "--connection_name",
        required=True,
        help="Connection name in DataGate connections table",
    )

    return parser.parse_args()


# ============================================================
# 2. Validation helpers
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


def truncate(value, max_length):
    if value is None:
        return None

    text = str(value)

    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


# ============================================================
# 3. Read connection and active tables
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


def get_active_tables(pg_hook, connection_id, catalog_name):
    """
    Lấy tất cả bảng active thuộc connection.

    Không cần input schema_name nữa.
    Job sẽ chạy cho mọi schema/table active trong connection đó.
    """

    rows = pg_hook.get_records(
        """
        SELECT
            id,
            catalog_name,
            schema_name,
            table_name
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND is_active = TRUE
        ORDER BY schema_name, table_name
        """,
        parameters=(connection_id, catalog_name),
    )

    tables = []

    for row in rows:
        table_id = str(row[0])
        table_catalog = validate_name(row[1], "catalog_name")
        schema_name = validate_name(row[2], "schema_name")
        table_name = validate_name(row[3], "table_name")

        tables.append(
            {
                "table_id": table_id,
                "catalog_name": table_catalog,
                "schema_name": schema_name,
                "table_name": table_name,
                "full_table_name": f"{table_catalog}.{schema_name}.{table_name}",
            }
        )

    return tables


# ============================================================
# 4. Save rules
# ============================================================

def save_suggested_rules(pg_hook, rows):
    """
    Ghi suggested rules vào bảng rules.

    Nếu rule đã tồn tại theo:
    - table_id
    - source
    - column_name
    - code_for_constraint

    thì:
    - frequency = frequency + 1
    - cập nhật thông tin gợi ý mới nhất
    - giữ nguyên status hiện tại, không override active/inactive/pending
    """

    if not rows:
        return

    sql = """
        INSERT INTO rules (
            id,
            table_id,
            source,
            status,
            importance_level,
            column_name,
            description,
            constraint_name,
            frequency,
            current_value,
            suggesting_rule,
            code_for_constraint,
            rule_description,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (
            table_id,
            source,
            column_name,
            code_for_constraint
        )
        WHERE code_for_constraint IS NOT NULL
        DO UPDATE SET
            frequency = rules.frequency + 1,
            importance_level = EXCLUDED.importance_level,
            description = EXCLUDED.description,
            constraint_name = EXCLUDED.constraint_name,
            current_value = EXCLUDED.current_value,
            suggesting_rule = EXCLUDED.suggesting_rule,
            rule_description = EXCLUDED.rule_description,
            updated_at = EXCLUDED.updated_at,

            -- Giữ nguyên trạng thái do user quyết định trên UI.
            status = rules.status
    """

    now = datetime.utcnow()
    values = []

    for row in rows:
        values.append(
            (
                str(uuid.uuid4()),
                row["table_id"],
                "system",
                "pending",
                row["importance_level"],
                row["column_name"],
                row["description"],
                row["constraint_name"],
                1,
                row["current_value"],
                row["suggesting_rule"],
                row["code_for_constraint"],
                row["rule_description"],
                now,
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
# 6. Read latest batch and prepare data
# ============================================================

def get_batch_column(table_df):
    if "processing_date_hour" in table_df.columns:
        return "processing_date_hour"

    if "date_hour" in table_df.columns:
        return "date_hour"

    return None


def get_latest_batch_hour(spark, full_table_name, batch_column):
    row = spark.sql(
        f"""
        SELECT MAX({batch_column}) AS latest_batch_hour
        FROM {full_table_name}
        """
    ).first()

    if row is None:
        return None

    return row["latest_batch_hour"]


def read_latest_batch(spark, full_table_name):
    """
    Đọc batch mới nhất của table.

    Vì job chỉ nhận connection_name, không nhận processing_date_hour,
    nên mỗi table sẽ tự lấy MAX(processing_date_hour) hoặc MAX(date_hour).
    """

    table_df = spark.table(full_table_name)
    batch_column = get_batch_column(table_df)

    if batch_column is None:
        raise ValueError(
            f"Table {full_table_name} does not contain processing_date_hour or date_hour."
        )

    latest_batch_hour = get_latest_batch_hour(
        spark=spark,
        full_table_name=full_table_name,
        batch_column=batch_column,
    )

    if latest_batch_hour is None:
        return None, batch_column, None

    batch_df = spark.sql(
        f"""
        SELECT *
        FROM {full_table_name}
        WHERE {batch_column} = TIMESTAMP '{latest_batch_hour}'
        """
    )

    return batch_df, batch_column, latest_batch_hour


def sanitize_dataframe_for_suggestion(df):
    """
    Bỏ các cột kỹ thuật và các cột all-null trước khi chạy suggestion.
    """

    candidate_columns = [
        column_name
        for column_name in df.columns
        if column_name not in EXCLUDED_COLUMNS
    ]

    if not candidate_columns:
        return df.select()

    sample = df.take(1)

    if not sample:
        return df.select(*candidate_columns)

    non_null_counts = (
        df
        .agg(
            *[
                F.count(F.col(column_name)).alias(column_name)
                for column_name in candidate_columns
            ]
        )
        .first()
        .asDict()
    )

    retained_columns = [
        column_name
        for column_name in candidate_columns
        if (non_null_counts.get(column_name) or 0) > 0
    ]

    if not retained_columns:
        return df.select()

    return df.select(*retained_columns)


# ============================================================
# 7. Rule suggestion
# ============================================================

def run_rule_suggestion(spark, df):
    return (
        ConstraintSuggestionRunner(spark)
        .onData(df)
        .addConstraintRule(DEFAULT())
        .run()
    )


def normalize_constraint_name(column_name, code_for_constraint):
    if not column_name:
        return None

    code = str(code_for_constraint or "")

    if ".isComplete(" in code:
        suffix = "not_null"
    elif ".isNonNegative(" in code:
        suffix = "non_negative"
    elif ".isUnique(" in code:
        suffix = "unique"
    elif ".isContainedIn(" in code:
        suffix = "allowed_values"
    elif ".hasCompleteness(" in code:
        suffix = "completeness"
    elif ".hasMin(" in code:
        suffix = "min"
    elif ".hasMax(" in code:
        suffix = "max"
    else:
        suffix = "rule"

    return f"{column_name}_{suffix}"


def infer_importance_level(code_for_constraint):
    """
    Default đơn giản:
    - not_null, non_negative, unique: high
    - allowed values/completeness/min/max: medium
    - còn lại: low
    """

    code = str(code_for_constraint or "")

    if (
        ".isComplete(" in code
        or ".isNonNegative(" in code
        or ".isUnique(" in code
    ):
        return "high"

    if (
        ".isContainedIn(" in code
        or ".hasCompleteness(" in code
        or ".hasMin(" in code
        or ".hasMax(" in code
    ):
        return "medium"

    return "low"


def normalize_suggestions(table_info, suggestion_result):
    suggestions = suggestion_result.get("constraint_suggestions", [])
    rows = []

    for suggestion in suggestions:
        column_name = suggestion.get("column_name")
        code_for_constraint = suggestion.get("code_for_constraint")

        if not column_name or not code_for_constraint:
            continue

        column_name = validate_name(column_name, "column_name")
        code_for_constraint = truncate(code_for_constraint, 512)

        rows.append(
            {
                "table_id": table_info["table_id"],
                "column_name": column_name,
                "description": suggestion.get("description")
                or suggestion.get("rule_description"),
                "constraint_name": truncate(
                    normalize_constraint_name(
                        column_name=column_name,
                        code_for_constraint=code_for_constraint,
                    ),
                    512,
                ),
                "current_value": truncate(
                    suggestion.get("current_value"),
                    255,
                ),
                "suggesting_rule": truncate(
                    suggestion.get("suggesting_rule"),
                    255,
                ),
                "code_for_constraint": code_for_constraint,
                "rule_description": suggestion.get("rule_description"),
                "importance_level": infer_importance_level(code_for_constraint),
            }
        )

    return rows


def suggest_rules_for_table(spark, pg_hook, table_info):
    full_table_name = table_info["full_table_name"]

    logger.info("Suggesting rules | table=%s", full_table_name)

    try:
        batch_df, batch_column, latest_batch_hour = read_latest_batch(
            spark=spark,
            full_table_name=full_table_name,
        )
    except Exception as exc:
        logger.warning(
            "Skip table because latest batch cannot be read | table=%s | error=%s",
            full_table_name,
            str(exc),
        )
        return 0

    if batch_df is None:
        logger.info(
            "Skip table because no latest batch found | table=%s",
            full_table_name,
        )
        return 0

    sanitized_df = sanitize_dataframe_for_suggestion(batch_df)

    if not sanitized_df.columns:
        logger.info(
            "Skip table because no analyzable columns | table=%s",
            full_table_name,
        )
        return 0

    try:
        suggestion_result = run_rule_suggestion(
            spark=spark,
            df=sanitized_df,
        )
    except Py4JJavaError as exc:
        if "EmptyStateException" in str(exc):
            logger.warning(
                "Skip table because PyDeequ returned EmptyStateException | table=%s",
                full_table_name,
            )
            return 0

        raise

    rows = normalize_suggestions(
        table_info=table_info,
        suggestion_result=suggestion_result,
    )

    save_suggested_rules(
        pg_hook=pg_hook,
        rows=rows,
    )

    logger.info(
        "Saved suggested rules | table=%s | batch_column=%s | latest_batch=%s | rows=%s",
        full_table_name,
        batch_column,
        latest_batch_hour,
        len(rows),
    )

    return len(rows)


# ============================================================
# 8. Main
# ============================================================

def main():
    args = parse_args()

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
        connection_id=connection_config["connection_id"],
        catalog_name=catalog_name,
    )

    if not active_tables:
        logger.warning(
            "No active tables found for connection=%s",
            connection_config["connection_name"],
        )
        return

    spark = create_spark_session(connection_config)

    try:
        total_written = 0

        for table_info in active_tables:
            total_written += suggest_rules_for_table(
                spark=spark,
                pg_hook=pg_hook,
                table_info=table_info,
            )

        logger.info(
            "Rule suggestion completed | connection=%s | total_written=%s",
            connection_config["connection_name"],
            total_written,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()