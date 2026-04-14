import sys
import json
import psycopg2
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline

def run_anomaly_ml():
    # Args
    REST_URI   = sys.argv[1]
    S3_ENDPOINT= sys.argv[2]
    ACCESS_KEY = sys.argv[3]
    SECRET_KEY = sys.argv[4]
    REGION     = sys.argv[5]
    TABLE      = sys.argv[6]
    LAST_BATCH = sys.argv[7]
    CUR_BATCH  = sys.argv[8]

    PG_URL  = sys.argv[9]
    PG_USER = sys.argv[10]
    PG_PASS = sys.argv[11]

    spark = SparkSession.builder \
        .appName(f"[DATAGATE] ML Anomaly Detection - {TABLE}") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.rest.RESTCatalog") \
        .config("spark.sql.catalog.iceberg.uri", REST_URI) \
        .config("spark.sql.catalog.iceberg.s3.endpoint", S3_ENDPOINT) \
        .config("spark.sql.catalog.iceberg.s3.access-key-id", ACCESS_KEY) \
        .config("spark.sql.catalog.iceberg.s3.secret-access-key", SECRET_KEY) \
        .config("spark.sql.catalog.iceberg.s3.path-style-access", "true") \
        .config("spark.sql.catalog.iceberg.s3.region", REGION) \
        .getOrCreate()

    try:
        full_table = f"iceberg.{TABLE}"
        partition_col = "date_hour"

        # 1. Load Today's Data (Label 1)
        df_today = spark.table(full_table) \
            .where((F.col(partition_col) > F.to_timestamp(F.lit(LAST_BATCH))) & \
                   (F.col(partition_col) <= F.to_timestamp(F.lit(CUR_BATCH)))) \
            .withColumn("label", F.lit(1.0))

        if df_today.count() == 0:
            print("⚠️ No data for today.")
            return

        # 2. Load History Data (Label 0) - Sampled
        df_history = spark.table(full_table) \
            .where(F.col(partition_col) <= F.to_timestamp(F.lit(LAST_BATCH))) \
            .orderBy(F.rand()) \
            .limit(df_today.count() * 2) \
            .withColumn("label", F.lit(0.0))

        if df_history.count() == 0:
            print("⚠️ No history data to compare.")
            return

        # Union
        df_total = df_today.unionByName(df_history)

        # 3. Feature Engineering (Baseline)
        # Identify numeric and categorical columns
        exclude_cols = ["label", partition_col, "id", "created_at"]
        cols = [c for c in df_total.columns if c not in exclude_cols]
        
        numeric_cols = [c for c, t in df_total.dtypes if t in ('int', 'double', 'float', 'long', 'bigint', 'decimal') and c in cols]
        categorical_cols = [c for c, t in df_total.dtypes if t == 'string' and c in cols]

        stages = []
        for col in categorical_cols:
            indexer = StringIndexer(inputCol=col, outputCol=f"{col}_idx", handleInvalid="keep")
            encoder = OneHotEncoder(inputCol=f"{col}_idx", outputCol=f"{col}_vec")
            stages += [indexer, encoder]

        assembler_inputs = numeric_cols + [f"{col}_vec" for col in categorical_cols]
        assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features", handleInvalid="skip")
        stages.append(assembler)

        # 4. Train Business
        rf = RandomForestClassifier(labelCol="label", featuresCol="features", numTrees=20)
        stages.append(rf)

        pipeline = Pipeline(stages=stages)
        model = pipeline.fit(df_total)

        # 5. Evaluate
        predictions = model.transform(df_total)
        evaluator = BinaryClassificationEvaluator(labelCol="label", metricName="areaUnderROC")
        auc = evaluator.evaluate(predictions)

        print(f"🎯 ML Anomaly Score (AUC): {auc}")

        # 6. Feature Important (SHAP placeholder - using RF importance)
        rf_model = model.stages[-1]
        importances = rf_model.featureImportances.toArray()
        
        # Mapping importance back to original columns (simplified)
        feat_imp = []
        for i, col in enumerate(assembler_inputs):
            feat_imp.append({"column": col.replace("_vec", ""), "score": float(importances[i])})
        
        feat_imp = sorted(feat_imp, key=lambda x: x['score'], reverse=True)[:5]

        # 7. Save to Postgres
        # Parse PG_URL (e.g., postgresql://user:pass@host:port/db)
        # For simplicity, we assume the format is correct or use psycopg2 directly
        try:
            conn_str = PG_URL.replace("postgresql://", "host=").replace("@", " ").replace(":", " port=").replace("/", " dbname=")
            # This is a bit hacky, better to parse properly
            import dj_database_url
            db_config = dj_database_url.parse(PG_URL)
            
            conn = psycopg2.connect(
                dbname=db_config['NAME'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                host=db_config['HOST'],
                port=db_config['PORT']
            )
            cur = conn.cursor()
            
            status = "ALERT" if auc > 0.8 else "PASS" # AUC > 0.8 means Today is very different from History
            
            cur.execute(
                "INSERT INTO ml_anomaly_runs (table_name, batch_time, partition_key, anomaly_score, status) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (TABLE, datetime.now(), CUR_BATCH, auc, status)
            )
            run_id = cur.fetchone()[0]
            
            for f in feat_imp:
                cur.execute(
                    "INSERT INTO ml_feature_importance (run_id, column_name, importance_score) VALUES (%s, %s, %s)",
                    (run_id, f['column'], f['score'])
                )
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Saved ML anomaly results. run_id={run_id}")
        except Exception as e:
            print(f"❌ DB Save Failed: {e}")

    finally:
        spark.stop()

if __name__ == "__main__":
    run_anomaly_ml()
