import argparse
import logging
import os
import uuid
from datetime import datetime, timedelta

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

from pyspark import StorageLevel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.functions import vector_to_array
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
    StringType,
    DateType,
    TimestampType,
)

from synapse.ml.lightgbm import LightGBMClassifier


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SPARK_APP_NAME = "batch_lightgbm_auc_detection"


# ============================================================
# 1. Fixed job config
# ============================================================

TARGET_SAMPLE_PER_GROUP = int(os.getenv("TARGET_SAMPLE_PER_GROUP", "10000"))
MIN_ROWS_PER_GROUP = int(os.getenv("MIN_ROWS_PER_GROUP", "1000"))

TEST_SIZE = float(os.getenv("TEST_SIZE", "0.15"))
VALID_SIZE = float(os.getenv("VALID_SIZE", "0.15"))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))

# History comparison:
# - previous batch: target - 12h
# - historical same-hour style offsets: 1d, 7d, 14d
PREVIOUS_BATCH_HOURS = int(os.getenv("PREVIOUS_BATCH_HOURS", "12"))
HISTORY_DAYS = [
    int(x.strip())
    for x in os.getenv("HISTORY_DAYS", "1,7,14").split(",")
    if x.strip()
]

# SynapseML fixed params not stored in current table model.
LGBM_NUM_TASKS = int(os.getenv("LGBM_NUM_TASKS", "4"))
LGBM_NUM_THREADS = int(os.getenv("LGBM_NUM_THREADS", "3"))
LGBM_TIMEOUT = int(os.getenv("LGBM_TIMEOUT", "600"))

LGBM_USE_SINGLE_DATASET_MODE = os.getenv("LGBM_USE_SINGLE_DATASET_MODE", "true").lower() == "true"
LGBM_DATA_TRANSFER_MODE = os.getenv("LGBM_DATA_TRANSFER_MODE", "streaming")
LGBM_VERBOSITY = int(os.getenv("LGBM_VERBOSITY", "-1"))

MAX_CATEGORICAL_CARDINALITY = int(os.getenv("MAX_CATEGORICAL_CARDINALITY", "100"))

EXCLUDE_FEATURE_COLS = {
    "label",
    "date_hour",
    "processing_date_hour",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
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

INTEGER_TYPES = (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
)


# ============================================================
# 2. CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run SynapseML LightGBM AUC detection and save AUC + SHAP results"
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
# 3. Validation
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


def to_datetime(value):
    return datetime.fromisoformat(str(value).replace("T", " "))


def to_ts_string(value):
    return value.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 4. DataGate DB helpers
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


def get_latest_lightgbm_parameter(pg_hook, table_id):
    """
    Lấy parameter mới nhất của table.

    Nếu sau này bạn có cột is_best hoặc is_active trong lightgbm_parameters,
    có thể đổi ORDER BY updated_at DESC thành WHERE is_best = TRUE.
    """

    row = pg_hook.get_first(
        """
        SELECT
            id,
            "learningRate",
            "numLeaves",
            "maxDepth",
            "minDataInLeaf",
            "baggingFraction",
            "baggingFreq",
            "featureFraction",
            "lambdaL1",
            "lambdaL2",
            "minGainToSplit",
            "maxBin",
            "numIterations",
            "earlyStoppingRound",
            "useBarrierExecutionMode"
        FROM lightgbm_parameters
        WHERE table_id = %s
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        parameters=(table_id,),
    )

    if row is None:
        return None

    return {
        "id": str(row[0]),
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
        "numIterations": int(row[12] or 300),
        "earlyStoppingRound": int(row[13] or 30),
        "useBarrierExecutionMode": bool(row[14]) if row[14] is not None else True,
    }


def save_lightgbm_result(
    pg_hook,
    table_id,
    lightgbm_parameter_id,
    processing_date_hour,
    auc_score,
):
    sql = """
        INSERT INTO lightgbm_results (
            id,
            table_id,
            lightgbm_parameter_id,
            processing_date_hour,
            auc_score,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (table_id, lightgbm_parameter_id, processing_date_hour)
        DO UPDATE SET
            auc_score = EXCLUDED.auc_score,
            created_at = EXCLUDED.created_at
    """

    pg_hook.run(
        sql,
        parameters=(
            str(uuid.uuid4()),
            table_id,
            lightgbm_parameter_id,
            processing_date_hour,
            auc_score,
            datetime.utcnow(),
        ),
    )


def save_shap_results(
    pg_hook,
    table_id,
    lightgbm_parameter_id,
    processing_date_hour,
    shap_rows,
):
    if not shap_rows:
        return

    sql = """
        INSERT INTO shap_results (
            id,
            table_id,
            lightgbm_parameter_id,
            processing_date_hour,
            feature_name,
            shap_score,
            shap_rank,
            created_at
        )
        VALUES %s
        ON CONFLICT (
            table_id,
            lightgbm_parameter_id,
            processing_date_hour,
            feature_name
        )
        DO UPDATE SET
            shap_score = EXCLUDED.shap_score,
            shap_rank = EXCLUDED.shap_rank,
            created_at = EXCLUDED.created_at
    """

    now = datetime.utcnow()

    values = []

    for row in shap_rows:
        values.append(
            (
                str(uuid.uuid4()),
                table_id,
                lightgbm_parameter_id,
                processing_date_hour,
                row["feature_name"],
                float(row["shap_score"]),
                int(row["shap_rank"]),
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
# 6. Read target/history batches
# ============================================================

def read_batch_table(spark, full_table_name, processing_date_hour):
    table_df = spark.table(full_table_name)

    if "processing_date_hour" not in table_df.columns:
        raise ValueError(
            f"Table {full_table_name} does not have processing_date_hour column."
        )

    return spark.sql(
        f"""
        SELECT *
        FROM {full_table_name}
        WHERE processing_date_hour = TIMESTAMP '{processing_date_hour}'
        """
    )


def get_comparison_processing_hours(target_processing_date_hour):
    target_dt = to_datetime(target_processing_date_hour)

    comparison_hours = [
        target_dt - timedelta(hours=PREVIOUS_BATCH_HOURS)
    ]

    for days in HISTORY_DAYS:
        comparison_hours.append(target_dt - timedelta(days=days))

    unique_hours = sorted(set(comparison_hours))

    return [to_ts_string(x) for x in unique_hours]


def sample_batch(
    spark,
    full_table_name,
    processing_date_hour,
    label,
    max_rows,
    seed,
):
    batch_df = read_batch_table(
        spark=spark,
        full_table_name=full_table_name,
        processing_date_hour=processing_date_hour,
    )

    sampled_df = (
        batch_df
        .orderBy(F.rand(int(seed)))
        .limit(int(max_rows))
        .withColumn("label", F.lit(float(label)))
    )

    return sampled_df


def build_work_dataset(spark, table_info, target_processing_date_hour):
    full_table_name = table_info["full_table_name"]

    positive_df = sample_batch(
        spark=spark,
        full_table_name=full_table_name,
        processing_date_hour=target_processing_date_hour,
        label=1,
        max_rows=TARGET_SAMPLE_PER_GROUP,
        seed=RANDOM_STATE,
    )

    positive_count = positive_df.count()

    if positive_count < MIN_ROWS_PER_GROUP:
        raise ValueError(
            f"Target batch too small: rows={positive_count}, "
            f"min_rows={MIN_ROWS_PER_GROUP}"
        )

    negative_parts = []

    comparison_hours = get_comparison_processing_hours(
        target_processing_date_hour
    )

    for index, compare_hour in enumerate(comparison_hours):
        part = sample_batch(
            spark=spark,
            full_table_name=full_table_name,
            processing_date_hour=compare_hour,
            label=0,
            max_rows=TARGET_SAMPLE_PER_GROUP,
            seed=RANDOM_STATE + index + 1,
        )

        cnt = part.count()

        if cnt < MIN_ROWS_PER_GROUP:
            logger.warning(
                "Skip comparison batch | table=%s | processing_date_hour=%s | rows=%s",
                full_table_name,
                compare_hour,
                cnt,
            )
            continue

        negative_parts.append(part)

    if not negative_parts:
        raise ValueError(
            f"No valid historical batches found for table={full_table_name}"
        )

    negative_df = negative_parts[0]

    for part in negative_parts[1:]:
        negative_df = negative_df.unionByName(
            part,
            allowMissingColumns=True,
        )

    work_df = positive_df.unionByName(
        negative_df,
        allowMissingColumns=True,
    )

    work_df = work_df.persist(StorageLevel.MEMORY_AND_DISK)
    work_df.count()

    return work_df


# ============================================================
# 7. Split train/valid/test
# ============================================================

def split_train_valid_test(work_df):
    split_df = work_df.withColumn("_r", F.rand(RANDOM_STATE))

    test_df = split_df.filter(F.col("_r") < TEST_SIZE).drop("_r")
    valid_df = split_df.filter(
        (F.col("_r") >= TEST_SIZE)
        & (F.col("_r") < TEST_SIZE + VALID_SIZE)
    ).drop("_r")
    train_df = split_df.filter(F.col("_r") >= TEST_SIZE + VALID_SIZE).drop("_r")

    for name, df in [
        ("train", train_df),
        ("valid", valid_df),
        ("test", test_df),
    ]:
        label_count = df.groupBy("label").count().collect()

        if len(label_count) < 2:
            raise ValueError(
                f"{name} split does not contain both labels. "
                f"Please increase TARGET_SAMPLE_PER_GROUP or adjust split ratio."
            )

    return train_df, valid_df, test_df


# ============================================================
# 8. Feature pipeline
# ============================================================

class SimpleFeaturePipeline:
    def __init__(self):
        self.numeric_feature_cols_ = []
        self.categorical_numeric_cols_ = []
        self.categorical_string_cols_ = []
        self.string_indexer_models_ = []
        self.string_indexed_cols_ = []
        self.feature_cols_ = []
        self.categorical_slot_indexes_ = []
        self.assembler_ = None

    def fit(self, train_df):
        schema_map = {
            field.name: field.dataType
            for field in train_df.schema.fields
        }

        candidate_cols = []

        for field in train_df.schema.fields:
            col_name = field.name
            data_type = field.dataType

            if col_name in EXCLUDE_FEATURE_COLS:
                continue

            if isinstance(data_type, (DateType, TimestampType)):
                continue

            if isinstance(data_type, NUMERIC_TYPES) or isinstance(data_type, StringType):
                candidate_cols.append(col_name)

        numeric_cols = [
            c for c in candidate_cols
            if isinstance(schema_map[c], NUMERIC_TYPES)
        ]

        string_cols = [
            c for c in candidate_cols
            if isinstance(schema_map[c], StringType)
        ]

        categorical_numeric_cols = []

        for c in numeric_cols:
            if isinstance(schema_map[c], INTEGER_TYPES):
                approx_cardinality = (
                    train_df
                    .select(F.approx_count_distinct(F.col(c)).alias("n"))
                    .first()["n"]
                )

                if approx_cardinality is not None and int(approx_cardinality) <= MAX_CATEGORICAL_CARDINALITY:
                    categorical_numeric_cols.append(c)

        self.categorical_numeric_cols_ = categorical_numeric_cols

        self.numeric_feature_cols_ = [
            c for c in numeric_cols
            if c not in self.categorical_numeric_cols_
        ]

        self.categorical_string_cols_ = string_cols

        df = train_df

        self.string_indexer_models_ = []
        self.string_indexed_cols_ = []

        for c in self.categorical_string_cols_:
            idx_col = f"{c}__idx"

            indexer = StringIndexer(
                inputCol=c,
                outputCol=idx_col,
                handleInvalid="keep",
            )

            model = indexer.fit(df)

            self.string_indexer_models_.append(model)
            self.string_indexed_cols_.append(idx_col)

            df = model.transform(df)

        self.feature_cols_ = (
            self.numeric_feature_cols_
            + self.categorical_numeric_cols_
            + self.string_indexed_cols_
        )

        categorical_cols = (
            self.categorical_numeric_cols_
            + self.string_indexed_cols_
        )

        self.categorical_slot_indexes_ = [
            self.feature_cols_.index(c)
            for c in categorical_cols
        ]

        self.assembler_ = VectorAssembler(
            inputCols=self.feature_cols_,
            outputCol="features",
            handleInvalid="keep",
        )

        return self

    def transform(self, input_df):
        df = input_df

        for c in self.numeric_feature_cols_ + self.categorical_numeric_cols_:
            if c in df.columns:
                df = df.withColumn(c, F.col(c).cast("double"))

        for model in self.string_indexer_models_:
            df = model.transform(df)

        df = self.assembler_.transform(df)

        return df


def build_feature_datasets(train_raw_df, valid_raw_df, test_raw_df):
    feature_pipeline = SimpleFeaturePipeline()
    feature_pipeline.fit(train_raw_df)

    train_features_df = (
        feature_pipeline
        .transform(train_raw_df)
        .select("features", F.col("label").cast("double").alias("label"))
    )

    valid_features_df = (
        feature_pipeline
        .transform(valid_raw_df)
        .select("features", F.col("label").cast("double").alias("label"))
    )

    test_features_df = (
        feature_pipeline
        .transform(test_raw_df)
        .select("features", F.col("label").cast("double").alias("label"))
    )

    train_features_df = train_features_df.persist(StorageLevel.MEMORY_AND_DISK)
    valid_features_df = valid_features_df.persist(StorageLevel.MEMORY_AND_DISK)
    test_features_df = test_features_df.persist(StorageLevel.MEMORY_AND_DISK)

    train_features_df.count()
    valid_features_df.count()
    test_features_df.count()

    return feature_pipeline, train_features_df, valid_features_df, test_features_df


# ============================================================
# 9. LightGBM
# ============================================================

def build_lgbm_train_df(train_df, valid_df):
    train_part = (
        train_df
        .select("features", "label")
        .withColumn("is_validation", F.lit(False))
    )

    valid_part = (
        valid_df
        .select("features", "label")
        .withColumn("is_validation", F.lit(True))
    )

    out_df = train_part.unionByName(valid_part)
    out_df = out_df.persist(StorageLevel.MEMORY_AND_DISK)
    out_df.count()

    return out_df


def build_synapseml_params(parameter_row):
    return {
        "objective": "binary",
        "metric": "auc",
        "featuresCol": "features",
        "labelCol": "label",
        "validationIndicatorCol": "is_validation",

        "learningRate": float(parameter_row["learningRate"]),
        "numLeaves": int(parameter_row["numLeaves"]),
        "maxDepth": int(parameter_row["maxDepth"]),
        "minDataInLeaf": int(parameter_row["minDataInLeaf"]),

        "baggingFraction": float(parameter_row["baggingFraction"]),
        "baggingFreq": int(parameter_row["baggingFreq"]),
        "featureFraction": float(parameter_row["featureFraction"]),

        "lambdaL1": float(parameter_row["lambdaL1"]),
        "lambdaL2": float(parameter_row["lambdaL2"]),
        "minGainToSplit": float(parameter_row["minGainToSplit"]),
        "maxBin": int(parameter_row["maxBin"]),

        "numIterations": int(parameter_row["numIterations"]),
        "earlyStoppingRound": int(parameter_row["earlyStoppingRound"]),

        "numTasks": int(LGBM_NUM_TASKS),
        "numThreads": int(LGBM_NUM_THREADS),
        "maxStreamingOMPThreads": int(LGBM_NUM_THREADS),

        "timeout": int(LGBM_TIMEOUT),
        "useBarrierExecutionMode": bool(parameter_row["useBarrierExecutionMode"]),
        "useSingleDatasetMode": bool(LGBM_USE_SINGLE_DATASET_MODE),
        "dataTransferMode": LGBM_DATA_TRANSFER_MODE,
        "verbosity": int(LGBM_VERBOSITY),

        "featuresShapCol": "featuresShap",
    }


def train_and_predict(
    lgbm_train_df,
    test_features_df,
    parameter_row,
    categorical_slot_indexes,
):
    params = build_synapseml_params(parameter_row)

    if categorical_slot_indexes:
        params["categoricalSlotIndexes"] = [
            int(x) for x in categorical_slot_indexes
        ]

    estimator = LightGBMClassifier(**params)

    model = estimator.fit(lgbm_train_df)

    pred_df = model.transform(test_features_df)

    return model, pred_df


def evaluate_auc(pred_df):
    evaluator = BinaryClassificationEvaluator(
        labelCol="label",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC",
    )

    return float(evaluator.evaluate(pred_df))


# ============================================================
# 10. SHAP summary
# ============================================================

def build_shap_summary_rows(pred_df, feature_cols):
    if "featuresShap" not in pred_df.columns:
        return []

    target_pred_df = pred_df.filter(F.col("label") == F.lit(1.0))

    feature_map_items = []

    for index, feature_name in enumerate(feature_cols):
        feature_map_items.append(F.lit(int(index)))
        feature_map_items.append(F.lit(feature_name))

    feature_name_map = F.create_map(*feature_map_items)

    shap_long_df = (
        target_pred_df
        .select(
            F.posexplode(
                vector_to_array(F.col("featuresShap"))
            ).alias("feature_index", "shap_value")
        )
        .withColumn(
            "feature_name",
            feature_name_map[F.col("feature_index")]
        )
        .select(
            "feature_name",
            F.col("shap_value").cast("double").alias("shap_value"),
        )
    )

    shap_summary_df = (
        shap_long_df
        .groupBy("feature_name")
        .agg(
            F.avg(F.abs(F.col("shap_value"))).alias("shap_score")
        )
    )

    rank_window = Window.orderBy(F.col("shap_score").desc())

    shap_summary_df = (
        shap_summary_df
        .withColumn("shap_rank", F.row_number().over(rank_window))
        .orderBy("shap_rank")
    )

    rows = shap_summary_df.collect()

    return [
        {
            "feature_name": row["feature_name"],
            "shap_score": float(row["shap_score"]),
            "shap_rank": int(row["shap_rank"]),
        }
        for row in rows
    ]


# ============================================================
# 11. Run one table
# ============================================================

def run_lightgbm_for_table(
    spark,
    pg_hook,
    table_info,
    processing_date_hour,
):
    table_id = table_info["table_id"]
    full_table_name = table_info["full_table_name"]

    logger.info(
        "Run LightGBM AUC | table=%s | processing_date_hour=%s",
        full_table_name,
        processing_date_hour,
    )

    parameter_row = get_latest_lightgbm_parameter(
        pg_hook=pg_hook,
        table_id=table_id,
    )

    if parameter_row is None:
        logger.warning(
            "Skip table because no lightgbm_parameters found | table=%s",
            full_table_name,
        )
        return

    work_df = build_work_dataset(
        spark=spark,
        table_info=table_info,
        target_processing_date_hour=processing_date_hour,
    )

    train_raw_df, valid_raw_df, test_raw_df = split_train_valid_test(work_df)

    feature_pipeline, train_features_df, valid_features_df, test_features_df = build_feature_datasets(
        train_raw_df=train_raw_df,
        valid_raw_df=valid_raw_df,
        test_raw_df=test_raw_df,
    )

    lgbm_train_df = build_lgbm_train_df(
        train_df=train_features_df,
        valid_df=valid_features_df,
    )

    model, pred_df = train_and_predict(
        lgbm_train_df=lgbm_train_df,
        test_features_df=test_features_df,
        parameter_row=parameter_row,
        categorical_slot_indexes=feature_pipeline.categorical_slot_indexes_,
    )

    pred_df = pred_df.persist(StorageLevel.MEMORY_AND_DISK)
    pred_df.count()

    auc_score = evaluate_auc(pred_df)

    save_lightgbm_result(
        pg_hook=pg_hook,
        table_id=table_id,
        lightgbm_parameter_id=parameter_row["id"],
        processing_date_hour=processing_date_hour,
        auc_score=auc_score,
    )

    shap_rows = build_shap_summary_rows(
        pred_df=pred_df,
        feature_cols=feature_pipeline.feature_cols_,
    )

    save_shap_results(
        pg_hook=pg_hook,
        table_id=table_id,
        lightgbm_parameter_id=parameter_row["id"],
        processing_date_hour=processing_date_hour,
        shap_rows=shap_rows,
    )

    logger.info(
        "Saved LightGBM result | table=%s | auc=%s | shap_rows=%s",
        full_table_name,
        auc_score,
        len(shap_rows),
    )

    pred_df.unpersist()
    lgbm_train_df.unpersist()
    train_features_df.unpersist()
    valid_features_df.unpersist()
    test_features_df.unpersist()
    work_df.unpersist()


# ============================================================
# 12. Main
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
        for table_info in active_tables:
            try:
                run_lightgbm_for_table(
                    spark=spark,
                    pg_hook=pg_hook,
                    table_info=table_info,
                    processing_date_hour=processing_date_hour,
                )
            except Exception as exc:
                logger.exception(
                    "LightGBM job failed for table=%s | error=%s",
                    table_info["full_table_name"],
                    str(exc),
                )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()