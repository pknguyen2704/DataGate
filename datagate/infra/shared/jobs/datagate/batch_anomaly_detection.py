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
from psycopg2.extras import execute_values, Json

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


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "batch_anomaly_detection"

SPARK_DRIVER_CORES = "2"
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_INSTANCES = "2"
SPARK_EXECUTOR_CORES = "6"
SPARK_EXECUTOR_MEMORY = "10g"
SPARK_SQL_SHUFFLE_PARTITIONS = "24"
SPARK_DEFAULT_PARALLELISM = "24"
SPARK_TIMEZONE = "Asia/Ho_Chi_Minh"

USE_BARRIER_EXECUTION_MODE = True
LGBM_NUM_TASKS = 4
LGBM_NUM_THREADS = 3
LGBM_TIMEOUT = 1200
LGBM_USE_SINGLE_DATASET_MODE = True
LGBM_DATA_TRANSFER_MODE = "streaming"
LGBM_VERBOSITY = -1
SPARK_CLEANUP_TIMEOUT_SECONDS = 30
DB_CLEANUP_TIMEOUT_SECONDS = 10

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datagate_db_conn_id", default="datagate_db_default")
    parser.add_argument("--connection_name", required=True)
    parser.add_argument("--schema_name", required=True)
    parser.add_argument("--processing_date_hour", required=True)
    return parser.parse_args()


def validate_name(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value


def validate_identifier(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for char in value:
        if not (char.isalnum() or char == "_"):
            raise ValueError(f"Invalid SQL identifier {field_name}: {value}.")
    return value


def normalize_hour(value):
    value = str(value or "").strip().replace("T", " ")
    if not value:
        raise ValueError("processing_date_hour must not be empty.")
    return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")


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
        "catalog_name": validate_identifier(row[3], "iceberg_catalog_name"),
        "minio_endpoint_url": row[4],
        "minio_access_key": row[5],
        "minio_secret_key": row[6],
    }


def get_active_tables(pg_hook, catalog_name, schema_name):
    catalog_name = validate_identifier(catalog_name, "catalog_name")
    schema_name = validate_identifier(schema_name, "schema_name")

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
            "table_name": validate_identifier(row[1], "table_name"),
            "full_table_name": f"{catalog_name}.{schema_name}.{validate_identifier(row[1], 'table_name')}",
        }
        for row in rows
    ]


def get_anomaly_config(pg_hook, table_id):
    row = pg_hook.get_first(
        """
        SELECT
            batch_time_col,
            required_history_days,
            previous_batch_hours,
            history_days,
            target_sample_per_group,
            test_size,
            random_state,
            p_value_alpha,
            min_history_auc_points,
            exclude_cols,
            categorical_cols,
            numeric_cols
        FROM lightgbm_anomaly_configs
        WHERE table_id = %s
        LIMIT 1
        """,
        parameters=(table_id,),
    )

    if row is None:
        return None

    cfg = {
        "batch_time_col": validate_identifier(row[0], "batch_time_col"),
        "required_history_days": int(row[1]),
        "previous_batch_hours": int(row[2]),
        "history_days": [int(x) for x in as_list(row[3])],
        "target_sample_per_group": int(row[4]),
        "test_size": float(row[5]),
        "random_state": int(row[6]),
        "p_value_alpha": float(row[7]),
        "min_history_auc_points": int(row[8]),
        "exclude_cols": [
            validate_identifier(col, "exclude_col")
            for col in as_list(row[9])
        ],
        "categorical_cols": [
            validate_identifier(col, "categorical_col")
            for col in as_list(row[10])
        ],
        "numeric_cols": [
            validate_identifier(col, "numeric_col")
            for col in as_list(row[11])
        ],
    }

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

    if cfg["p_value_alpha"] <= 0 or cfg["p_value_alpha"] >= 1:
        raise ValueError("p_value_alpha must be between 0 and 1.")

    if cfg["min_history_auc_points"] <= 0:
        raise ValueError("min_history_auc_points must be greater than 0.")

    return cfg


def get_lgbm_config(pg_hook, table_id):
    row = pg_hook.get_first(
        """
        SELECT id, learning_rate, num_leaves, max_depth, min_data_in_leaf,
               bagging_fraction, bagging_freq, feature_fraction,
               lambda_l1, lambda_l2, min_gain_to_split, max_bin,
               num_iterations
        FROM lightgbm_parameters
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


def get_auc_threshold(pg_hook, parameter_id):
    row = pg_hook.get_first(
        """
        SELECT id, auc_threshold, severity_level
        FROM lightgbm_auc_manual_thresholds
        WHERE lightgbm_parameter_id = %s
          AND is_active = TRUE
        ORDER BY
            CASE severity_level
                WHEN 'critical' THEN 1
                WHEN 'warning' THEN 2
                ELSE 3
            END,
            updated_at DESC,
            created_at DESC
        LIMIT 1
        """,
        parameters=(parameter_id,),
    )

    if row is None:
        return None

    return {
        "manual_threshold_id": str(row[0]),
        "auc_threshold": float(row[1]),
        "severity_level": row[2],
    }


def get_historical_auc_scores(pg_hook, table_id, processing_hour):
    rows = pg_hook.get_records(
        """
        SELECT auc_score
        FROM lightgbm_auc
        WHERE table_id = %s
          AND processing_date_hour < %s
          AND auc_score IS NOT NULL
        ORDER BY processing_date_hour
        """,
        parameters=(table_id, processing_hour),
    )

    return [float(row[0]) for row in rows]


def empirical_p_value(history_scores, current_auc):
    return (sum(1 for score in history_scores if score >= current_auc) + 1) / (
        len(history_scores) + 1
    )


def create_spark_session(connection_config):
    catalog = connection_config["catalog_name"]

    return (
        SparkSession.builder.appName(JOB_NAME)
        .config("spark.driver.cores", SPARK_DRIVER_CORES)
        .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .config("spark.executor.instances", SPARK_EXECUTOR_INSTANCES)
        .config("spark.executor.cores", SPARK_EXECUTOR_CORES)
        .config("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        .config("spark.task.cpus", str(LGBM_NUM_THREADS))
        .config("spark.dynamicAllocation.enabled", "false")
        .config("spark.speculation", "false")
        .config("spark.scheduler.mode", "FIFO")
        .config("spark.executorEnv.OMP_NUM_THREADS", str(LGBM_NUM_THREADS))
        .config("spark.executorEnv.MKL_NUM_THREADS", "1")
        .config("spark.executorEnv.OPENBLAS_NUM_THREADS", "1")
        .config("spark.executorEnv.NUMEXPR_NUM_THREADS", "1")
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


def batch_exists(spark, table_name, batch_time_col, hour):
    batch_time_col = validate_identifier(batch_time_col, "batch_time_col")

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
    hours += [
        target_dt - timedelta(days=days)
        for days in anomaly_cfg["history_days"]
    ]

    return [to_ts(hour) for hour in sorted(set(hours))]


def build_work_df(spark, table_name, target_hour, anomaly_cfg):
    seed = anomaly_cfg["random_state"]

    pos = read_batch(
        spark=spark,
        table_name=table_name,
        hour=target_hour,
        label=1,
        seed=seed,
        anomaly_cfg=anomaly_cfg,
    )

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

        part = read_batch(
            spark=spark,
            table_name=table_name,
            hour=hour,
            label=0,
            seed=seed + index + 1,
            anomaly_cfg=anomaly_cfg,
        )

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

        self.cat_cols = [
            col
            for col in configured_cat_cols
            if col in cols
        ]

        if configured_num_cols:
            self.num_cols = [
                col
                for col in configured_num_cols
                if col in cols
            ]
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

        self.categorical_slots = [
            self.feature_cols.index(col)
            for col in self.idx_cols
        ]

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


def train_lgbm(train, test, cfg, cat_slots):
    lgbm_train = train.repartition(LGBM_NUM_TASKS).persist(StorageLevel.MEMORY_AND_DISK)

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
            "useBarrierExecutionMode": USE_BARRIER_EXECUTION_MODE,
            "numTasks": LGBM_NUM_TASKS,
            "numThreads": LGBM_NUM_THREADS,
            "maxStreamingOMPThreads": LGBM_NUM_THREADS,
            "timeout": LGBM_TIMEOUT,
            "useSingleDatasetMode": LGBM_USE_SINGLE_DATASET_MODE,
            "dataTransferMode": LGBM_DATA_TRANSFER_MODE,
            "verbosity": LGBM_VERBOSITY,
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


def build_parameter_snapshot(cfg, anomaly_cfg, feature_cols):
    return {
        "lightgbm": {
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
            "use_barrier_execution_mode": USE_BARRIER_EXECUTION_MODE,
            "num_tasks": LGBM_NUM_TASKS,
            "num_threads": LGBM_NUM_THREADS,
            "max_streaming_omp_threads": LGBM_NUM_THREADS,
            "timeout": LGBM_TIMEOUT,
            "use_single_dataset_mode": LGBM_USE_SINGLE_DATASET_MODE,
            "data_transfer_mode": LGBM_DATA_TRANSFER_MODE,
        },
        "anomaly_config": {
            "batch_time_col": anomaly_cfg["batch_time_col"],
            "required_history_days": anomaly_cfg["required_history_days"],
            "previous_batch_hours": anomaly_cfg["previous_batch_hours"],
            "history_days": anomaly_cfg["history_days"],
            "target_sample_per_group": anomaly_cfg["target_sample_per_group"],
            "test_size": anomaly_cfg["test_size"],
            "random_state": anomaly_cfg["random_state"],
            "p_value_alpha": anomaly_cfg["p_value_alpha"],
            "min_history_auc_points": anomaly_cfg["min_history_auc_points"],
            "exclude_cols": anomaly_cfg["exclude_cols"],
            "categorical_cols": anomaly_cfg["categorical_cols"],
            "numeric_cols": anomaly_cfg["numeric_cols"],
            "feature_cols": feature_cols,
        },
    }


def save_lgbm_result(
    pg_hook,
    table_id,
    cfg,
    anomaly_cfg,
    feature_cols,
    processing_hour,
    auc_score,
    p_value,
):
    sql = """
        INSERT INTO lightgbm_auc (
            id,
            table_id,
            lightgbm_parameter_id,
            processing_date_hour,
            auc_score,
            p_value,
            parameter_snapshot,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (table_id, processing_date_hour)
        DO UPDATE SET
            lightgbm_parameter_id = EXCLUDED.lightgbm_parameter_id,
            auc_score = EXCLUDED.auc_score,
            p_value = EXCLUDED.p_value,
            parameter_snapshot = EXCLUDED.parameter_snapshot,
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
                processing_hour,
                auc_score,
                p_value,
                Json(build_parameter_snapshot(cfg, anomaly_cfg, feature_cols)),
            ),
        )
        result_id = str(cur.fetchone()[0])

    conn.commit()

    logger.info(
        "Saved LightGBM AUC | result_id=%s | auc=%s | p_value=%s",
        result_id,
        auc_score,
        p_value,
    )

    return result_id


def save_shap(pg_hook, result_id, processing_hour, rows):
    if not rows:
        return

    sql = """
        INSERT INTO shap_results (
            id,
            lightgbm_result_id,
            feature_name,
            shap_score,
            shap_rank,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (lightgbm_result_id, feature_name)
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
            processing_hour,
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

    conn.commit()

    logger.info("Saved SHAP rows | result_id=%s | rows=%s", result_id, len(rows))


def get_auc_p_value(threshold, history_scores, auc_score, anomaly_cfg):
    if threshold:
        return None

    min_history_auc_points = anomaly_cfg["min_history_auc_points"]

    if len(history_scores) < min_history_auc_points:
        logger.info(
            "Skip p-value: not enough historical AUC points | current=%s | required=%s",
            len(history_scores),
            min_history_auc_points,
        )
        return None

    return empirical_p_value(history_scores, auc_score)


def should_write_auc_verify(threshold, p_value):
    return bool(threshold) or p_value is not None


def save_auc_verify(pg_hook, result_id, threshold, auc_score, p_value, processing_hour, anomaly_cfg):
    if threshold:
        status = "fail" if auc_score >= threshold["auc_threshold"] else "pass"
        manual_threshold_id = threshold["manual_threshold_id"]
        auc_threshold = threshold["auc_threshold"]
        severity_level = threshold["severity_level"] if status == "fail" else None
    else:
        status = "fail" if p_value < anomaly_cfg["p_value_alpha"] else "pass"
        manual_threshold_id = None
        auc_threshold = None
        severity_level = "warning" if status == "fail" else None

    sql = """
        INSERT INTO lightgbm_auc_verify (
            id,
            lightgbm_result_id,
            manual_threshold_id,
            status,
            auc_score,
            auc_threshold,
            severity_level,
            is_resolved,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())
        ON CONFLICT (lightgbm_result_id)
        DO UPDATE SET
            manual_threshold_id = EXCLUDED.manual_threshold_id,
            status = EXCLUDED.status,
            auc_score = EXCLUDED.auc_score,
            auc_threshold = EXCLUDED.auc_threshold,
            severity_level = EXCLUDED.severity_level,
            processing_date_hour = EXCLUDED.processing_date_hour,
            updated_at = NOW()
        RETURNING id
    """

    conn = pg_hook.get_conn()

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                str(uuid.uuid4()),
                result_id,
                manual_threshold_id,
                status,
                auc_score,
                auc_threshold,
                severity_level,
                processing_hour,
            ),
        )
        verify_id = str(cur.fetchone()[0])

    conn.commit()

    logger.info(
        "Saved AUC verify | verify_id=%s | result_id=%s | status=%s | auc=%s | threshold=%s | p_value=%s",
        verify_id,
        result_id,
        status,
        auc_score,
        auc_threshold,
        p_value,
    )


def run_table(spark, pg_hook, table, processing_hour):
    logger.info(
        "Start anomaly detection | table=%s | hour=%s",
        table["full_table_name"],
        processing_hour,
    )

    anomaly_cfg = get_anomaly_config(pg_hook, table["table_id"])

    if anomaly_cfg is None:
        logger.info(
            "Skip anomaly detection: no anomaly config | table=%s",
            table["full_table_name"],
        )
        return

    cfg = get_lgbm_config(pg_hook, table["table_id"])

    if not cfg:
        logger.info(
            "Skip anomaly detection: no LightGBM parameter | table=%s",
            table["full_table_name"],
        )
        return

    if not has_enough_history(
        spark=spark,
        table_name=table["full_table_name"],
        target_hour=processing_hour,
        anomaly_cfg=anomaly_cfg,
    ):
        return

    work_df = None
    train_f = None
    test_f = None
    pred = None

    try:
        threshold = get_auc_threshold(pg_hook, cfg["parameter_id"])

        work_df = build_work_df(
            spark=spark,
            table_name=table["full_table_name"],
            target_hour=processing_hour,
            anomaly_cfg=anomaly_cfg,
        )

        if work_df is None:
            return

        train_df, test_df = split_df(work_df, anomaly_cfg)
        pipeline, train_f, test_f = build_features(train_df, test_df, anomaly_cfg)

        pred = train_lgbm(
            train=train_f,
            test=test_f,
            cfg=cfg,
            cat_slots=pipeline.categorical_slots,
        )

        auc_score = evaluate_auc(pred)

        history_scores = get_historical_auc_scores(
            pg_hook=pg_hook,
            table_id=table["table_id"],
            processing_hour=processing_hour,
        )

        p_value = get_auc_p_value(
            threshold=threshold,
            history_scores=history_scores,
            auc_score=auc_score,
            anomaly_cfg=anomaly_cfg,
        )

        result_id = save_lgbm_result(
            pg_hook=pg_hook,
            table_id=table["table_id"],
            cfg=cfg,
            anomaly_cfg=anomaly_cfg,
            feature_cols=pipeline.output_feature_cols,
            processing_hour=processing_hour,
            auc_score=auc_score,
            p_value=p_value,
        )

        save_shap(
            pg_hook=pg_hook,
            result_id=result_id,
            processing_hour=processing_hour,
            rows=shap_summary(pred, pipeline.output_feature_cols),
        )

        if should_write_auc_verify(threshold, p_value):
            save_auc_verify(
                pg_hook=pg_hook,
                result_id=result_id,
                threshold=threshold,
                auc_score=auc_score,
                p_value=p_value,
                processing_hour=processing_hour,
                anomaly_cfg=anomaly_cfg,
            )
        else:
            logger.info(
                "Skip AUC verify | result_id=%s | no_threshold=True | history_auc_points=%s | required=%s",
                result_id,
                len(history_scores),
                anomaly_cfg["min_history_auc_points"],
            )

        logger.info(
            "Completed anomaly detection | table=%s | auc=%s | p_value=%s | history_auc_points=%s | threshold_exists=%s",
            table["full_table_name"],
            auc_score,
            p_value,
            len(history_scores),
            bool(threshold),
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


def close_pg_hook(pg_hook):
    if pg_hook is None:
        return

    def close_conn():
        conn = getattr(pg_hook, "conn", None)
        if conn is not None and not conn.closed:
            conn.close()

    run_with_timeout("postgres-close", DB_CLEANUP_TIMEOUT_SECONDS, close_conn)


def stop_spark_session(spark):
    if spark is None:
        return

    def clear_cache():
        spark.catalog.clearCache()

    def cancel_jobs():
        spark.sparkContext.cancelAllJobs()

    def stop_spark():
        spark.stop()

    run_with_timeout("spark-clear-cache", SPARK_CLEANUP_TIMEOUT_SECONDS, clear_cache)
    run_with_timeout("spark-cancel-jobs", SPARK_CLEANUP_TIMEOUT_SECONDS, cancel_jobs)
    stopped = run_with_timeout("spark-stop", SPARK_CLEANUP_TIMEOUT_SECONDS, stop_spark)

    if not stopped:
        with suppress(Exception):
            spark.sparkContext._gateway.shutdown()


def main():
    args = parse_args()
    schema_name = validate_identifier(args.schema_name, "schema_name")
    processing_hour = normalize_hour(args.processing_date_hour)

    logger.info(
        "Job started | app=%s | connection=%s | schema=%s | hour=%s",
        JOB_NAME,
        args.connection_name,
        schema_name,
        processing_hour,
    )

    pg_hook = None
    spark = None

    try:
        pg_hook = PostgresHook(postgres_conn_id=args.datagate_db_conn_id)

        connection_config = get_connection_config(
            pg_hook=pg_hook,
            connection_name=args.connection_name,
        )

        tables = get_active_tables(
            pg_hook=pg_hook,
            catalog_name=connection_config["catalog_name"],
            schema_name=schema_name,
        )

        if not tables:
            logger.info("Job pass: no active tables found | schema=%s", schema_name)
            return 0

        spark = create_spark_session(connection_config)

        for table in tables:
            run_table(
                spark=spark,
                pg_hook=pg_hook,
                table=table,
                processing_hour=processing_hour,
            )

        logger.info(
            "Job completed successfully | schema=%s | hour=%s",
            schema_name,
            processing_hour,
        )

        return 0

    except Exception:
        logger.exception(
            "Job failed | schema=%s | hour=%s",
            schema_name,
            processing_hour,
        )
        return 1

    finally:
        stop_spark_session(spark)
        close_pg_hook(pg_hook)
        gc.collect()


if __name__ == "__main__":
    exit_code = main()

    with suppress(Exception):
        sys.stdout.flush()

    with suppress(Exception):
        sys.stderr.flush()

    logging.shutdown()
    os._exit(exit_code)
