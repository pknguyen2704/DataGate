import os
import sys
import gc
from contextlib import suppress
import argparse
import logging
import uuid
import threading
from datetime import datetime, timedelta

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import Json, execute_values

from pyspark import StorageLevel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.functions import vector_to_array
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
    DateType,
    TimestampType,
)
from pyspark.sql.window import Window
from synapse.ml.lightgbm import LightGBMClassifier


# Log
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "batch_anomaly_detection"

DEFAULT_EXCLUDE_COLS = {
    "label",
}

NUMERIC_TYPES = (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
)


def parse_bool(value):
    value = str(value).strip().lower()
    if value in {"1", "true", "yes", "y"}:
        return True
    if value in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datagate_db_conn_id", default="datagate_db_default")
    parser.add_argument("--connection_name", required=True)
    parser.add_argument("--schema_name", required=True)
    parser.add_argument("--processing_date_hour", required=True)
    parser.add_argument("--lgbm-use-barrier-execution-mode", type=parse_bool)
    parser.add_argument("--lgbm-num-tasks", type=int)
    parser.add_argument("--lgbm-num-threads", type=int)
    parser.add_argument("--lgbm-timeout", type=int)
    parser.add_argument("--lgbm-use-single-dataset-mode", type=parse_bool)
    parser.add_argument("--lgbm-data-transfer-mode", default="streaming")
    parser.add_argument("--lgbm-verbosity", type=int)
    parser.add_argument("--spark-cleanup-timeout-seconds", type=int)
    parser.add_argument("--py4j-cleanup-timeout-seconds", type=int)
    return parser.parse_args()


def build_runtime_config(args):
    return {
        "use_barrier_execution_mode": args.lgbm_use_barrier_execution_mode,
        "num_tasks": args.lgbm_num_tasks,
        "num_threads": args.lgbm_num_threads,
        "max_streaming_omp_threads": args.lgbm_num_threads,
        "timeout": args.lgbm_timeout,
        "use_single_dataset_mode": args.lgbm_use_single_dataset_mode,
        "data_transfer_mode": args.lgbm_data_transfer_mode,
        "verbosity": args.lgbm_verbosity,
        "spark_cleanup_timeout_seconds": args.spark_cleanup_timeout_seconds,
        "py4j_cleanup_timeout_seconds": args.py4j_cleanup_timeout_seconds,
    }


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



def to_dt(value):
    return datetime.fromisoformat(str(value).replace("T", " "))

def to_ts(value):
    return value.strftime("%Y-%m-%d %H:%M:%S")

def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return list(value)

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


def get_active_tables(pg_hook, connection_id, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT
            id,
            table_name
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(connection_id, catalog_name, schema_name),
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


def get_anomaly_config(pg_hook, table_id):
    row = pg_hook.get_first(
        """
        SELECT
            id,
            batch_time_col,
            required_history_days,
            previous_batch_hours,
            history_days,
            target_sample_per_group,
            test_size,
            random_state,
            exclude_cols,
            categorical_cols,
            numeric_cols
        FROM model_configs
        WHERE table_id = %s
        LIMIT 1
        """,
        parameters=(table_id,),
    )
    if row is None:
        return None
    cfg = {
        "model_config_id": str(row[0]),
        "batch_time_col": validate_name(row[1], "batch_time_col"),
    }
    cfg.update(
        {
            "required_history_days": int(row[2]),
            "previous_batch_hours": int(row[3]),
            "history_days": [int(x) for x in as_list(row[4])],
            "target_sample_per_group": int(row[5]),
            "test_size": float(row[6]),
            "random_state": int(row[7]),
            "exclude_cols": [
                validate_name(col, "exclude_col")
                for col in as_list(row[8])
            ],
            "categorical_cols": [
                validate_name(col, "categorical_col")
                for col in as_list(row[9])
            ],
            "numeric_cols": [
                validate_name(col, "numeric_col")
                for col in as_list(row[10])
            ],
        }
    )

    if cfg["required_history_days"] <= 0:
        raise ValueError("required_history_days must be greater than 0.")

    if cfg["previous_batch_hours"] <= 0:
        raise ValueError("previous_batch_hours must be greater than 0.")

    if not cfg["history_days"]:
        raise ValueError("history_days must not be empty.")

    if cfg["target_sample_per_group"] <= 0:
        raise ValueError("target_sample_per_group must be greater than 0.")

    if cfg["test_size"] <= 0 or cfg["test_size"] >= 1:
        raise ValueError("test_size must be between 0 and 1.")

    return cfg


def get_model_parameter(pg_hook, table_id):
    row = pg_hook.get_first(
        """
        SELECT
            id, learning_rate, num_leaves, max_depth, min_data_in_leaf,
            bagging_fraction, bagging_freq, feature_fraction, lambda_l1,
            lambda_l2, min_gain_to_split, max_bin, num_iterations
        FROM model_parameters
        WHERE table_id = %s
        LIMIT 1
        """,
        parameters=(table_id,),
    )

    if row is None:
        return None

    return {
        "parameter_id": str(row[0]),
        "learningRate": float(row[1]),
        "numLeaves": int(row[2]),
        "maxDepth": int(row[3]),
        "minDataInLeaf": int(row[4]),
        "baggingFraction": float(row[5]),
        "baggingFreq": int(row[6]),
        "featureFraction": float(row[7]),
        "lambdaL1": float(row[8]),
        "lambdaL2": float(row[9]),
        "minGainToSplit": float(row[10]),
        "maxBin": int(row[11]),
        "numIterations": int(row[12]),
    }


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

def batch_exists(spark, table_name, batch_time_col, hour):
    batch_time_col = validate_name(batch_time_col, "batch_time_col")
    row = spark.sql(
        f"""
        SELECT COUNT(*) AS n
        FROM {table_name}
        WHERE {batch_time_col} = TIMESTAMP '{hour}'
        """
    ).first()

    return int(row["n"] or 0) > 0

def has_enough_history(spark, table_name, target_hour, anomaly_cfg):
    batch_time_col = anomaly_cfg["batch_time_col"]
    required_history_days = anomaly_cfg["required_history_days"]
    required_hour = to_ts(to_dt(target_hour) - timedelta(days=required_history_days))

    if not batch_exists(spark, table_name, batch_time_col, target_hour):
        logger.info(
            "Skip anomaly detection: target batch not found | table=%s | hour=%s",
            table_name,
            target_hour,
        )
        return False

    if not batch_exists(spark, table_name, batch_time_col, required_hour):
        logger.info(
            "Skip anomaly detection: not enough exact history | table=%s | target=%s | required_history=%s",
            table_name,
            target_hour,
            required_hour,
        )
        return False

    logger.info(
        "History check passed | table=%s | target=%s | required_history=%s",
        table_name,
        target_hour,
        required_hour,
    )
    return True



def read_batch(spark, table_name, hour, label, seed, anomaly_cfg):
    batch_time_col = anomaly_cfg["batch_time_col"]
    sample_size = anomaly_cfg["target_sample_per_group"]

    return (
        spark.sql(
            f"""
            SELECT *
            FROM {table_name}
            WHERE {batch_time_col} = TIMESTAMP '{hour}'
            """
        )
        .orderBy(F.rand(seed))
        .limit(sample_size)
        .withColumn("label", F.lit(float(label)))
    )


def comparison_hours(target_hour, anomaly_cfg):
    target_dt = to_dt(target_hour)

    hours = [target_dt - timedelta(hours=anomaly_cfg["previous_batch_hours"])]
    hours += [target_dt - timedelta(days=days) for days in anomaly_cfg["history_days"]]

    return [to_ts(hour) for hour in sorted(set(hours))]


def build_work_df(spark, table_name, target_hour, anomaly_cfg):
    seed = anomaly_cfg["random_state"]

    pos = read_batch(spark,table_name, target_hour,1,seed,anomaly_cfg)

    pos_count = pos.count()

    if pos_count == 0:
        logger.info(
            "Skip anomaly detection: target batch is empty | table=%s | hour=%s",
            table_name,
            target_hour,
        )
        return None

    neg_parts = []

    for index, hour in enumerate(comparison_hours(target_hour, anomaly_cfg)):
        if not batch_exists(spark, table_name, anomaly_cfg["batch_time_col"], hour):
            logger.info(
                "Historical batch skipped: not found | table=%s | hour=%s",
                table_name,
                hour,
            )
            continue

        part = read_batch(spark,table_name,hour,0,seed + index + 1,anomaly_cfg)

        logger.info(
            "Historical batch loaded | table=%s | hour=%s | rows=%s",
            table_name,
            hour,
            part.count(),
        )

        neg_parts.append(part)

    if not neg_parts:
        logger.info(
            "Skip anomaly detection: no historical comparison batch | table=%s",
            table_name,
        )
        return None

    neg = neg_parts[0]

    for part in neg_parts[1:]:
        neg = neg.unionByName(part, allowMissingColumns=True)

    df = pos.unionByName(neg, allowMissingColumns=True).persist(
        StorageLevel.MEMORY_AND_DISK
    )

    logger.info("Training dataset built | table=%s | rows=%s", table_name, df.count())
    return df


def split_df(df, anomaly_cfg):
    random_state = anomaly_cfg["random_state"]
    test_size = anomaly_cfg["test_size"]

    df = df.withColumn("_r", F.rand(random_state))

    test = df.filter(F.col("_r") < test_size).drop("_r")
    train = df.filter(F.col("_r") >= test_size).drop("_r")

    for name, part in [("train", train), ("test", test)]:
        labels = part.select("label").distinct().count()
        rows = part.count()

        logger.info(
            "Split checked | name=%s | rows=%s | labels=%s",
            name,
            rows,
            labels,
        )

        if rows == 0:
            raise ValueError(f"{name} split is empty.")

        if labels < 2:
            raise ValueError(f"{name} split does not contain both labels.")

    return train, test


class FeaturePipeline:
    def __init__(self, anomaly_cfg):
        self.anomaly_cfg = anomaly_cfg
        self.num_cols = []
        self.cat_cols = []
        self.indexers = []
        self.idx_cols = []
        self.feature_cols = []
        self.output_feature_cols = []
        self.categorical_slots = []
        self.assembler = None

    def fit(self, df):
        schema = {field.name: field.dataType for field in df.schema.fields}

        exclude_cols = set(DEFAULT_EXCLUDE_COLS)
        exclude_cols.update(self.anomaly_cfg.get("exclude_cols", []))
        exclude_cols.add(self.anomaly_cfg["batch_time_col"])

        configured_cat_cols = set(self.anomaly_cfg.get("categorical_cols", []))
        configured_num_cols = set(self.anomaly_cfg.get("numeric_cols", []))

        cols = [
            field.name
            for field in df.schema.fields
            if field.name not in exclude_cols
            and not isinstance(field.dataType, (DateType, TimestampType))
        ]

        self.cat_cols = [col for col in configured_cat_cols if col in cols]

        if configured_num_cols:
            self.num_cols = [col for col in configured_num_cols if col in cols]
        else:
            self.num_cols = [
                col
                for col in cols
                if isinstance(schema[col], NUMERIC_TYPES)
                and col not in configured_cat_cols
            ]

        self.indexers = []
        self.idx_cols = []
        out = df

        for col in self.cat_cols:
            idx_col = f"{col}__idx"

            out = out.withColumn(col, F.col(col).cast("string"))

            model = StringIndexer(
                inputCol=col,
                outputCol=idx_col,
                handleInvalid="keep",
            ).fit(out)

            out = model.transform(out)
            self.indexers.append(model)
            self.idx_cols.append(idx_col)

        self.feature_cols = self.num_cols + self.idx_cols
        self.output_feature_cols = self.num_cols + self.cat_cols

        if not self.feature_cols:
            raise ValueError(
                "No usable feature columns found. "
                "Please check numeric_cols, categorical_cols, exclude_cols, and table schema."
            )

        self.categorical_slots = [self.feature_cols.index(col) for col in self.idx_cols]

        self.assembler = VectorAssembler(
            inputCols=self.feature_cols,
            outputCol="features",
            handleInvalid="keep",
        )

        logger.info(
            "Features prepared | numeric=%s | categorical=%s | total_features=%s | feature_cols=%s",
            len(self.num_cols),
            len(self.cat_cols),
            len(self.feature_cols),
            self.output_feature_cols,
        )

        return self

    def transform(self, df):
        for col in self.num_cols:
            df = df.withColumn(col, F.col(col).cast("double"))

        for col in self.cat_cols:
            df = df.withColumn(col, F.col(col).cast("string"))

        for model in self.indexers:
            df = model.transform(df)

        return self.assembler.transform(df).select(
            "features",
            F.col("label").cast("double").alias("label"),
        )


def build_features(train, test, anomaly_cfg):
    pipeline = FeaturePipeline(anomaly_cfg).fit(train)

    train_f = pipeline.transform(train).persist(StorageLevel.MEMORY_AND_DISK)
    test_f = pipeline.transform(test).persist(StorageLevel.MEMORY_AND_DISK)

    logger.info(
        "Feature data cached | train=%s | test=%s",
        train_f.count(),
        test_f.count(),
    )

    return pipeline, train_f, test_f


def train_lgbm(train, test, cfg, cat_slots, runtime_cfg):
    lgbm_train = train.repartition(runtime_cfg["num_tasks"]).persist(
        StorageLevel.MEMORY_AND_DISK
    )

    try:
        logger.info("Start LightGBM training | train_rows=%s", lgbm_train.count())

        params = {
            "objective": "binary",
            "metric": "auc",
            "featuresCol": "features",
            "labelCol": "label",
            "featuresShapCol": "featuresShap",
            "learningRate": cfg["learningRate"],
            "numLeaves": cfg["numLeaves"],
            "maxDepth": cfg["maxDepth"],
            "minDataInLeaf": cfg["minDataInLeaf"],
            "baggingFraction": cfg["baggingFraction"],
            "baggingFreq": cfg["baggingFreq"],
            "featureFraction": cfg["featureFraction"],
            "lambdaL1": cfg["lambdaL1"],
            "lambdaL2": cfg["lambdaL2"],
            "minGainToSplit": cfg["minGainToSplit"],
            "maxBin": cfg["maxBin"],
            "numIterations": cfg["numIterations"],
            "useBarrierExecutionMode": runtime_cfg["use_barrier_execution_mode"],
            "numTasks": runtime_cfg["num_tasks"],
            "numThreads": runtime_cfg["num_threads"],
            "maxStreamingOMPThreads": runtime_cfg["max_streaming_omp_threads"],
            "timeout": runtime_cfg["timeout"],
            "useSingleDatasetMode": runtime_cfg["use_single_dataset_mode"],
            "dataTransferMode": runtime_cfg["data_transfer_mode"],
            "verbosity": runtime_cfg["verbosity"],
        }

        if cat_slots:
            params["categoricalSlotIndexes"] = [int(slot) for slot in cat_slots]

        model = LightGBMClassifier(**params).fit(lgbm_train)
        pred = model.transform(test).persist(StorageLevel.MEMORY_AND_DISK)

        logger.info("LightGBM prediction completed | test_rows=%s", pred.count())
        return pred

    finally:
        with suppress(Exception):
            lgbm_train.unpersist(blocking=False)


def evaluate_auc(pred):
    return float(
        BinaryClassificationEvaluator(
            labelCol="label",
            rawPredictionCol="rawPrediction",
            metricName="areaUnderROC",
        ).evaluate(pred)
    )


def shap_summary(pred, feature_cols):
    if "featuresShap" not in pred.columns:
        logger.info("SHAP skipped: featuresShap column not found")
        return []

    pairs = []
    for index, name in enumerate(feature_cols):
        pairs += [F.lit(index), F.lit(name)]

    name_map = F.create_map(*pairs)

    df = (
        pred.filter(F.col("label") == 1.0)
        .select(F.posexplode(vector_to_array("featuresShap")).alias("i", "v"))
        .withColumn("feature_name", name_map[F.col("i")])
        .filter(F.col("feature_name").isNotNull())
        .groupBy("feature_name")
        .agg(F.avg(F.abs("v")).alias("shap_score"))
        .withColumn(
            "shap_rank",
            F.row_number().over(Window.orderBy(F.col("shap_score").desc())),
        )
        .orderBy("shap_rank")
    )

    return [
        {
            "feature_name": row["feature_name"],
            "shap_score": float(row["shap_score"]),
            "shap_rank": int(row["shap_rank"]),
        }
        for row in df.collect()
    ]


def build_parameter_snapshot(cfg, runtime_cfg):
    return {
        "model_parameter": {
            "learning_rate": cfg["learningRate"],
            "num_leaves": cfg["numLeaves"],
            "max_depth": cfg["maxDepth"],
            "min_data_in_leaf": cfg["minDataInLeaf"],
            "bagging_fraction": cfg["baggingFraction"],
            "bagging_freq": cfg["baggingFreq"],
            "feature_fraction": cfg["featureFraction"],
            "lambda_l1": cfg["lambdaL1"],
            "lambda_l2": cfg["lambdaL2"],
            "min_gain_to_split": cfg["minGainToSplit"],
            "max_bin": cfg["maxBin"],
            "num_iterations": cfg["numIterations"],
            "use_barrier_execution_mode": runtime_cfg["use_barrier_execution_mode"],
            "num_tasks": runtime_cfg["num_tasks"],
            "num_threads": runtime_cfg["num_threads"],
            "max_streaming_omp_threads": runtime_cfg["max_streaming_omp_threads"],
            "timeout": runtime_cfg["timeout"],
            "use_single_dataset_mode": runtime_cfg["use_single_dataset_mode"],
            "data_transfer_mode": runtime_cfg["data_transfer_mode"],
        },
    }


def build_config_snapshot(anomaly_cfg, feature_cols):
    return {
        "anomaly_config": {
            "batch_time_col": anomaly_cfg["batch_time_col"],
            "required_history_days": anomaly_cfg["required_history_days"],
            "previous_batch_hours": anomaly_cfg["previous_batch_hours"],
            "history_days": anomaly_cfg["history_days"],
            "target_sample_per_group": anomaly_cfg["target_sample_per_group"],
            "test_size": anomaly_cfg["test_size"],
            "random_state": anomaly_cfg["random_state"],
            "exclude_cols": anomaly_cfg["exclude_cols"],
            "categorical_cols": anomaly_cfg["categorical_cols"],
            "numeric_cols": anomaly_cfg["numeric_cols"],
            "feature_cols": feature_cols,
        },
    }


def save_auc_result(
    pg_hook,
    table_id,
    cfg,
    runtime_cfg,
    anomaly_cfg,
    feature_cols,
    processing_date_hour,
    auc_score,
):
    sql = """
        INSERT INTO anomaly_results (
            id,
            table_id,
            model_parameter_id,
            processing_date_hour,
            auc_score,
            parameter_snapshot,
            config_snapshot,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (table_id, processing_date_hour)
        DO UPDATE SET
            model_parameter_id = EXCLUDED.model_parameter_id,
            auc_score = EXCLUDED.auc_score,
            parameter_snapshot = EXCLUDED.parameter_snapshot,
            config_snapshot = EXCLUDED.config_snapshot,
            updated_at = NOW()
        RETURNING id
    """

    conn = pg_hook.get_conn()

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                str(uuid.uuid4()),
                table_id,
                cfg["parameter_id"],
                processing_date_hour,
                auc_score,
                Json(build_parameter_snapshot(cfg, runtime_cfg)),
                Json(build_config_snapshot(anomaly_cfg, feature_cols)),
            ),
        )
        result_id = str(cur.fetchone()[0])

    conn.commit()

    logger.info(
        "Saved AUC result | result_id=%s | auc=%s",
        result_id,
        auc_score,
    )

    return result_id


def save_shap(pg_hook, result_id, processing_date_hour, rows):
    if not rows:
        return

    sql = """
        INSERT INTO shap_results (
            id, anomaly_result_id, feature_name, shap_score, shap_rank,
            processing_date_hour, created_at, updated_at
        )
        VALUES %s
        ON CONFLICT (anomaly_result_id, feature_name)
        DO UPDATE SET
            shap_score = EXCLUDED.shap_score,
            shap_rank = EXCLUDED.shap_rank,
            processing_date_hour = EXCLUDED.processing_date_hour,
            updated_at = NOW()
    """

    values = [
        (
            str(uuid.uuid4()),
            result_id,
            row["feature_name"],
            row["shap_score"],
            row["shap_rank"],
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
            template="(%s, %s, %s, %s, %s, %s, NOW(), NOW())",
        )
        cur.execute(
            """
            UPDATE anomaly_results
            SET shap_top_features = %s::jsonb,
                updated_at = NOW()
            WHERE id = %s
            """,
            (
                Json(
                    [
                        {
                            "feature_name": row["feature_name"],
                            "shap_score": row["shap_score"],
                            "shap_rank": row["shap_rank"],
                        }
                        for row in rows
                    ]
                ),
                result_id,
            ),
        )

    conn.commit()

    logger.info("Saved SHAP rows | result_id=%s | rows=%s", result_id, len(rows))

def run_anomaly_detection(spark, pg_hook, table, processing_date_hour, runtime_cfg):
    logger.info(
        "Start anomaly detection | table=%s | hour=%s",
        table["full_table_name"],
        processing_date_hour,
    )

    anomaly_cfg = get_anomaly_config(pg_hook, table["table_id"])
    if anomaly_cfg is None:
        logger.info(
            "Skip anomaly detection: missing model config | table=%s | table_id=%s | hour=%s",
            table["full_table_name"],
            table["table_id"],
            processing_date_hour,
        )
        return

    if not has_enough_history(
        spark,
        table["full_table_name"],
        processing_date_hour,
        anomaly_cfg=anomaly_cfg,
    ):
        return

    cfg = get_model_parameter(pg_hook, table["table_id"])

    if cfg is None:
        logger.info(
            "Skip anomaly detection: missing model parameter | table=%s | table_id=%s | hour=%s",
            table["full_table_name"],
            table["table_id"],
            processing_date_hour,
        )
        return

    work_df = None
    train_f = None
    test_f = None
    pred = None

    try:
        work_df = build_work_df(spark,table["full_table_name"],processing_date_hour,anomaly_cfg)

        if work_df is None:
            return

        train_df, test_df = split_df(work_df, anomaly_cfg)
        pipeline, train_f, test_f = build_features(train_df, test_df, anomaly_cfg)

        pred = train_lgbm(
            train=train_f,
            test=test_f,
            cfg=cfg,
            cat_slots=pipeline.categorical_slots,
            runtime_cfg=runtime_cfg,
        )

        auc_score = evaluate_auc(pred)

        result_id = save_auc_result(pg_hook,table["table_id"],cfg,runtime_cfg,anomaly_cfg,pipeline.output_feature_cols,processing_date_hour,auc_score=auc_score,)

        save_shap(pg_hook,result_id,processing_date_hour,rows=shap_summary(pred, pipeline.output_feature_cols))

        logger.info(
            "Completed anomaly detection result | table=%s | auc=%s",
            table["full_table_name"],
            auc_score,
        )

    finally:
        for df in [pred, train_f, test_f, work_df]:
            if df is not None:
                with suppress(Exception):
                    df.unpersist(blocking=False)


def run_with_timeout(name, timeout_seconds, fn):
    error = {}

    def target():
        try:
            fn()
        except Exception as exc:
            error["exception"] = exc

    thread = threading.Thread(target=target, name=name, daemon=True)
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        logger.warning(
            "Cleanup timed out and will be abandoned | step=%s | timeout_seconds=%s",
            name,
            timeout_seconds,
        )
        return False

    if "exception" in error:
        logger.warning(
            "Cleanup failed | step=%s | error=%s",
            name,
            error["exception"],
        )
        return False

    return True


def close_hook_connection(hook):
    if hook is None:
        return
    for attr_name in ("conn", "_conn"):
        with suppress(Exception):
            conn = getattr(hook, attr_name, None)
            if conn is not None:
                conn.close()


def stop_spark_session(spark, spark_timeout_seconds, py4j_timeout_seconds):
    if spark is None:
        return

    spark_context = getattr(spark, "sparkContext", None)
    gateway = getattr(spark_context, "_gateway", None)

    def clear_cache():
        spark.catalog.clearCache()

    def cancel_jobs():
        spark.sparkContext.cancelAllJobs()

    def stop_spark():
        spark.stop()

    def shutdown_gateway():
        if gateway is None:
            return

        callback_server = getattr(gateway, "_callback_server", None)
        gateway_client = getattr(gateway, "_gateway_client", None)

        for owner in (callback_server, gateway_client, gateway):
            if owner is None:
                continue
            for method_name in ("shutdown", "close"):
                method = getattr(owner, method_name, None)
                if callable(method):
                    with suppress(Exception):
                        method()

    run_with_timeout("spark-clear-cache", spark_timeout_seconds, clear_cache)
    run_with_timeout("spark-cancel-jobs", spark_timeout_seconds, cancel_jobs)
    stopped = run_with_timeout("spark-stop", spark_timeout_seconds, stop_spark)

    if not stopped:
        run_with_timeout(
            "spark-gateway-shutdown",
            py4j_timeout_seconds,
            shutdown_gateway,
        )


def main():
    args = parse_args()
    runtime_cfg = build_runtime_config(args)
    schema_name = validate_name(args.schema_name, "schema_name")
    connection_name = validate_name(args.connection_name, "connection_name")
    processing_date_hour = normalize_processing_date_hour(args.processing_date_hour)

    logger.info(
        "Job started | app=%s | connection=%s | schema=%s | hour=%s",
        JOB_NAME,
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
            logger.info("Job pass: no active tables found | schema=%s", schema_name)
            return 0

        spark = create_spark_session(connection_config)

        for table in tables:
            run_anomaly_detection(spark, pg_hook, table, processing_date_hour, runtime_cfg)

        logger.info(
            "Job completed successfully | schema=%s | hour=%s",
            schema_name,
            processing_date_hour,
        )

        return 0

    except Exception:
        logger.exception(
            "Job failed | schema=%s | hour=%s",
            schema_name,
            processing_date_hour,
        )
        return 1

    finally:
        stop_spark_session(
            spark,
            runtime_cfg["spark_cleanup_timeout_seconds"],
            runtime_cfg["py4j_cleanup_timeout_seconds"],
        )
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
