import sys
import argparse
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import requests
import json
from datetime import datetime

def run_ml_anomaly(catalog, schema, table_name, backend_url, api_token):
    spark = SparkSession.builder \
        .appName(f"MLAnomalyDetection-{table_name}") \
        .getOrCreate()

    full_table = f"{catalog}.{schema}.{table_name}"
    print(f"🚀 Starting ML Anomaly Detection for {full_table}")

    # 1. Get Snapshots history to identify "Today" vs "Prior"
    snapshots_df = spark.read.table(f"{catalog}.{schema}.`{table_name}$snapshots`")
    latest_snapshot = snapshots_df.orderBy(F.desc("committed_at")).limit(1).collect()[0]
    latest_id = latest_snapshot.snapshot_id
    
    # Prior snapshots (excluding latest)
    prior_snapshots = snapshots_df.filter(F.col("snapshot_id") != latest_id) \
        .orderBy(F.desc("committed_at")).limit(3).collect()
    prior_ids = [s.snapshot_id for s in prior_snapshots]

    if not prior_ids:
        print("❌ Not enough historical snapshots for ML comparison.")
        return

    # 2. Sample Data
    # In Iceberg, we can query specific snapshots
    def get_sample(sid, size=10000):
        # Using Spark SQL to read specific snapshot
        return spark.read.option("snapshot-id", sid).table(full_table).sample(False, 0.1).limit(size)

    today_sample = get_sample(latest_id)
    today_pd = today_sample.toPandas()
    today_pd['target'] = 1

    prior_pd_list = []
    for sid in prior_ids:
        p_pd = get_sample(sid, size=4000).toPandas()
        p_pd['target'] = 0
        prior_pd_list.append(p_pd)
    
    prior_pd = pd.concat(prior_pd_list)
    df = pd.concat([today_pd, prior_pd]).reset_index(drop=True)

    # 3. Feature Engineering
    y = df['target']
    X_raw = df.drop(columns=['target'])
    
    X_encoded = pd.DataFrame()
    feature_to_col = {} # Maps encoded feature index back to original column name

    for col in X_raw.columns:
        # Skip if too many nulls or constant
        if X_raw[col].isnull().mean() > 0.99: continue
        
        # Is Null feature
        null_feat = f"{col}_is_null"
        X_encoded[null_feat] = X_raw[col].isnull().astype(int)
        feature_to_col[null_feat] = col

        if X_raw[col].dtype in [np.float64, np.int64]:
            X_encoded[col] = X_raw[col].fillna(X_raw[col].median())
            feature_to_col[col] = col
        else:
            # Categorical: Frequency Encoding
            freq = X_raw[col].value_counts(normalize=True).to_dict()
            X_encoded[f"{col}_freq"] = X_raw[col].map(freq).fillna(0)
            feature_to_col[f"{col}_freq"] = col

    # 4. Train XGBoost
    dtrain = xgb.DMatrix(X_encoded, label=y)
    params = {
        'max_depth': 4,
        'eta': 0.1,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss'
    }
    
    model = xgb.train(params, dtrain, num_boost_round=50)

    # 5. Explainability (SHAP)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_encoded)
    
    # Aggregate Shapley absolute values by original column
    col_scores = {}
    for i, feature_name in enumerate(X_encoded.columns):
        orig_col = feature_to_col[feature_name]
        importance = np.abs(shap_values[:, i]).mean()
        col_scores[orig_col] = col_scores.get(orig_col, 0) + importance

    # 6. Interpret Results
    # If the model gain is high, it means 'today' is significantly different
    # We use the mean absolute SHAP sum as a proxy for anomaly score
    total_anomaly_score = sum(col_scores.values())
    print(f"📊 Total Anomaly Score: {total_anomaly_score}")

    # Identify top anomalous columns
    top_cols = sorted(col_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    if total_anomaly_score > 0.5: # Threshold from book-ish logic
        severity = "high" if total_anomaly_score > 1.5 else "medium"
        msg = f"ML Anomaly detected! Significant distribution shift in columns: {', '.join([c[0] for c in top_cols])}. Total Score: {total_anomaly_score:.2f}"
        
        # Post Incident
        incident_data = {
            "table_name": f"{catalog}.{schema}.{table_name}",
            "incident_type": "ml_anomaly",
            "severity": severity,
            "message": msg,
            "status": "open"
        }
        
        try:
            r = requests.post(f"{backend_url}/api/v1/observability/incidents/internal", 
                          json=incident_data, 
                          headers={"Authorization": f"Bearer {api_token}"})
            print(f"✅ Incident posted: {r.status_code}")
        except Exception as e:
            print(f"❌ Failed to post incident: {e}")

    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--backend_url", default="http://backend:8000")
    parser.add_argument("--token", default="internal_ops_token")
    args = parser.parse_args()

    run_ml_anomaly(args.catalog, args.schema, args.table, args.backend_url, args.token)
