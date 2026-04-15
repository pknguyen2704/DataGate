import argparse
from datetime import datetime
import json
import logging

import numpy as np
import pandas as pd
from pyspark.errors import AnalysisException
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import requests
import shap
import xgboost as xgb


SENSITIVITY_CONFIG = {
    "high": {"min_impacted_ratio": 0.01, "base_threshold": 0.10, "row_alert_score": 0.60},
    "medium": {"min_impacted_ratio": 0.02, "base_threshold": 0.14, "row_alert_score": 0.67},
    "low": {"min_impacted_ratio": 0.03, "base_threshold": 0.19, "row_alert_score": 0.74},
}

LOGGER = logging.getLogger(__name__)
SHAP_BACKGROUND_SIZE = 128
SHAP_EXPLAIN_SIZE = 256
TOP_ROW_EXPLANATIONS = 12


def get_sample(df, target_size):
    sampled = df.orderBy(F.rand(seed=42)).limit(target_size)
    return sampled.toPandas()


def _normalize_json_like(value):
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except (TypeError, ValueError):
                return None
    return None


def _looks_like_datetime(series):
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if not pd.api.types.is_object_dtype(series) and not pd.api.types.is_string_dtype(series):
        return False

    sample = series.dropna().astype(str).head(50)
    if sample.empty:
        return False

    parsed = pd.to_datetime(sample, errors="coerce")
    return parsed.notna().mean() >= 0.8


def _encode_json_column(encoded, feature_to_column, column_name, parsed_series):
    normalized = parsed_series.map(
        lambda value: value if isinstance(value, (dict, list)) else {}
    )
    serialized = normalized.map(lambda value: json.dumps(value, sort_keys=True) if value else "")

    encoded[f"{column_name}_json_size"] = serialized.str.len().fillna(0)
    feature_to_column[f"{column_name}_json_size"] = column_name

    encoded[f"{column_name}_json_keys"] = normalized.map(
        lambda value: len(value.keys()) if isinstance(value, dict) else len(value) if isinstance(value, list) else 0
    )
    feature_to_column[f"{column_name}_json_keys"] = column_name

    encoded[f"{column_name}_json_depth"] = normalized.map(
        lambda value: 1 + max(((1 if isinstance(child, (dict, list)) else 0) for child in value.values()), default=0)
        if isinstance(value, dict)
        else 1 if isinstance(value, list) and value else 0
    )
    feature_to_column[f"{column_name}_json_depth"] = column_name

    freq = serialized.value_counts(normalize=True).to_dict()
    encoded[f"{column_name}_json_freq"] = serialized.map(freq).fillna(0)
    feature_to_column[f"{column_name}_json_freq"] = column_name


def encode_features(raw_df):
    encoded = pd.DataFrame()
    feature_to_column = {}
    excluded_time_columns = []
    feature_summary = {}

    for column in raw_df.columns:
        column_series = raw_df[column]
        null_ratio = column_series.isnull().mean()
        if null_ratio > 0.99:
            continue

        null_feature = f"{column}_is_null"
        encoded[null_feature] = column_series.isnull().astype(int)
        feature_to_column[null_feature] = column
        feature_summary.setdefault(column, []).append(null_feature)

        parsed_json = column_series.map(_normalize_json_like)
        if parsed_json.notna().mean() >= 0.7:
            _encode_json_column(encoded, feature_to_column, column, parsed_json)
            feature_summary[column].extend(
                [
                    f"{column}_json_size",
                    f"{column}_json_keys",
                    f"{column}_json_depth",
                    f"{column}_json_freq",
                ]
            )
            continue

        if pd.api.types.is_bool_dtype(column_series):
            encoded[column] = column_series.fillna(False).astype(int)
            feature_to_column[column] = column
            feature_summary[column].append(column)
        elif pd.api.types.is_numeric_dtype(column_series):
            encoded[column] = column_series.fillna(column_series.median())
            feature_to_column[column] = column
            encoded[f"{column}_zscore"] = (
                (encoded[column] - encoded[column].mean()) / (encoded[column].std() or 1.0)
            ).fillna(0)
            feature_to_column[f"{column}_zscore"] = column
            feature_summary[column].extend([column, f"{column}_zscore"])
        elif _looks_like_datetime(column_series):
            excluded_time_columns.append(column)
        else:
            text_series = column_series.astype(str)
            freq = text_series.value_counts(normalize=True).to_dict()
            encoded[f"{column}_freq"] = text_series.map(freq).fillna(0)
            feature_to_column[f"{column}_freq"] = column
            encoded[f"{column}_len"] = text_series.str.len().fillna(0)
            feature_to_column[f"{column}_len"] = column
            encoded[f"{column}_digit_ratio"] = text_series.map(
                lambda value: sum(char.isdigit() for char in value) / max(len(value), 1)
            )
            feature_to_column[f"{column}_digit_ratio"] = column
            feature_summary[column].extend(
                [f"{column}_freq", f"{column}_len", f"{column}_digit_ratio"]
            )

    encoded = encoded.replace([np.inf, -np.inf], 0).fillna(0)
    return encoded, feature_to_column, excluded_time_columns, feature_summary


def build_column_shap_matrix(shap_values, encoded_columns, feature_to_column):
    frame = pd.DataFrame(shap_values, columns=encoded_columns)
    aggregated = {}
    for feature_name in encoded_columns:
        original_column = feature_to_column[feature_name]
        aggregated.setdefault(original_column, 0)
        aggregated[original_column] = aggregated[original_column] + np.abs(frame[feature_name])

    return pd.DataFrame(aggregated)


def compute_shap_values(model, encoded_df):
    background_size = min(SHAP_BACKGROUND_SIZE, len(encoded_df))
    explain_size = min(SHAP_EXPLAIN_SIZE, len(encoded_df))

    if background_size == 0 or explain_size == 0:
        raise ValueError("No encoded samples available for SHAP explanation.")

    background = encoded_df.sample(n=background_size, random_state=42)
    explain_frame = encoded_df.sample(n=explain_size, random_state=7)

    def predict_fn(data):
        matrix = xgb.DMatrix(pd.DataFrame(data, columns=encoded_df.columns))
        return model.predict(matrix)

    explainer = shap.KernelExplainer(predict_fn, background)
    shap_values = explainer.shap_values(explain_frame, nsamples=min(200, explain_size))

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    return np.asarray(shap_values), explain_frame


def build_dynamic_threshold(reference_probs, current_probs, sensitivity):
    config = SENSITIVITY_CONFIG.get((sensitivity or "medium").lower(), SENSITIVITY_CONFIG["medium"])
    reference_center = float(np.mean(reference_probs))
    reference_noise = float(np.std(reference_probs))
    current_center = float(np.mean(current_probs))
    drift_gap = max(0.0, current_center - reference_center)
    dynamic_threshold = min(0.95, config["base_threshold"] + reference_noise * 1.5)
    return {
        "min_impacted_ratio": config["min_impacted_ratio"],
        "row_alert_score": config["row_alert_score"],
        "base_threshold": config["base_threshold"],
        "reference_center": reference_center,
        "reference_noise": reference_noise,
        "current_center": current_center,
        "drift_gap": drift_gap,
        "dynamic_threshold": dynamic_threshold,
    }


def build_row_explanations(explained_raw_df, shap_values, explained_columns, feature_to_column, row_scores):
    rows = []

    for row_position in np.argsort(-row_scores)[:TOP_ROW_EXPLANATIONS]:
        per_column_scores = {}
        per_column_cells = {}
        for feature_index, feature_name in enumerate(explained_columns):
            origin = feature_to_column[feature_name]
            contribution = float(abs(shap_values[row_position, feature_index]))
            per_column_scores[origin] = per_column_scores.get(origin, 0.0) + contribution

            if origin not in per_column_cells or contribution > per_column_cells[origin]["contribution"]:
                raw_value = explained_raw_df.iloc[row_position][origin] if origin in explained_raw_df.columns else None
                if isinstance(raw_value, (dict, list)):
                    raw_value = json.dumps(raw_value)[:160]
                per_column_cells[origin] = {
                    "feature_name": feature_name,
                    "contribution": contribution,
                    "value": None if pd.isna(raw_value) else str(raw_value)[:160],
                }

        top_columns = sorted(per_column_scores.items(), key=lambda item: item[1], reverse=True)[:3]
        rows.append(
            {
                "row_rank": int(len(rows) + 1),
                "row_score": float(row_scores[row_position]),
                "top_columns": [
                    {
                        "column_name": column_name,
                        "importance_score": float(score),
                        "top_feature": per_column_cells[column_name]["feature_name"],
                        "cell_value": per_column_cells[column_name]["value"],
                    }
                    for column_name, score in top_columns
                ],
            }
        )

    return rows


def cluster_impacted_columns(column_impact_df, top_columns):
    if column_impact_df.empty or len(top_columns) <= 1:
        return [[column] for column in top_columns]

    selected = [column for column in top_columns if column in column_impact_df.columns]
    if len(selected) <= 1:
        return [[column] for column in selected]

    correlation = column_impact_df[selected].corr().fillna(0)
    visited = set()
    groups = []

    for column in selected:
      if column in visited:
        continue

      stack = [column]
      cluster = []
      while stack:
        current = stack.pop()
        if current in visited:
          continue
        visited.add(current)
        cluster.append(current)
        neighbours = [candidate for candidate in selected if abs(correlation.loc[current, candidate]) >= 0.55 and candidate not in visited]
        stack.extend(neighbours)

      groups.append(sorted(cluster))

    return groups


def save_results(backend_url, payload):
    requests.post(f"{backend_url}/api/v1/ml/runs/internal", json=payload, timeout=20)


def post_incident(backend_url, payload):
    requests.post(f"{backend_url}/api/v1/observability/incidents/internal", json=payload, timeout=20)


def load_target_table(spark, full_table):
    try:
        return spark.read.table(full_table)
    except AnalysisException as exc:
        raise ValueError(
            f"Table '{full_table}' was not found in the Spark catalog."
        ) from exc


def build_reference_and_current_samples(table_df, sample_size):
    reference_df, current_df = table_df.randomSplit([0.7, 0.3], seed=42)

    reference_pd = get_sample(reference_df, max(1000, sample_size))
    current_pd = get_sample(current_df, sample_size)

    if current_pd.empty or reference_pd.empty:
        fallback_pd = get_sample(table_df, max(sample_size * 2, 2000))
        if fallback_pd.empty:
            raise ValueError("The selected table does not contain enough rows for ML sampling.")

        midpoint = max(1, len(fallback_pd) // 2)
        reference_pd = fallback_pd.iloc[:midpoint].copy()
        current_pd = fallback_pd.iloc[midpoint:].copy()

    return reference_pd, current_pd


def run_ml_anomaly(catalog, schema, table_name, backend_url, effective_date, sample_size, sensitivity):
    spark = SparkSession.builder.appName(f"MLAnomalyDetection-{table_name}").getOrCreate()
    full_table = f"{catalog}.{schema}.{table_name}"
    asset_table_name = f"{schema}.{table_name}"
    print(f"Starting ML Anomaly Detection for {full_table}")

    table_df = load_target_table(spark, full_table)
    reference_pd, current_pd = build_reference_and_current_samples(table_df, sample_size)
    reference_pd["target"] = 0
    current_pd["target"] = 1

    model_df = pd.concat([current_pd, reference_pd]).reset_index(drop=True)
    labels = model_df["target"]
    features_raw = model_df.drop(columns=["target"])

    encoded_df, feature_to_column, excluded_time_columns, feature_summary = encode_features(features_raw)
    training_matrix = xgb.DMatrix(encoded_df, label=labels)
    params = {
        "max_depth": 4,
        "eta": 0.1,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "base_score": 0.5,
        "seed": 42,
    }
    model = xgb.train(params, training_matrix, num_boost_round=50)
    predicted_probabilities = model.predict(training_matrix)
    current_mask = labels.to_numpy() == 1
    reference_mask = labels.to_numpy() == 0
    current_probabilities = predicted_probabilities[current_mask]
    reference_probabilities = predicted_probabilities[reference_mask]
    threshold_state = build_dynamic_threshold(reference_probabilities, current_probabilities, sensitivity)

    shap_values, explained_df = compute_shap_values(model, encoded_df)
    explained_indices = explained_df.index
    explained_labels = labels.iloc[explained_indices].to_numpy()
    explained_raw_df = features_raw.iloc[explained_indices].reset_index(drop=True)
    explained_probabilities = model.predict(xgb.DMatrix(explained_df))
    row_scores = np.abs(explained_probabilities - 0.5) * 2.0
    explained_current_mask = explained_labels == 1

    column_scores = {}
    for index, feature_name in enumerate(explained_df.columns):
        origin = feature_to_column[feature_name]
        importance = float(np.abs(shap_values[:, index]).mean())
        column_scores[origin] = column_scores.get(origin, 0) + importance

    current_row_scores = row_scores[explained_current_mask]
    impacted_ratio = float(
        np.mean(current_row_scores >= threshold_state["row_alert_score"])
    ) if len(current_row_scores) else 0.0
    total_score = float(threshold_state["drift_gap"] + impacted_ratio)
    status = (
        "ALERT"
        if impacted_ratio >= threshold_state["min_impacted_ratio"]
        and threshold_state["drift_gap"] >= threshold_state["dynamic_threshold"]
        else "PASS"
    )
    top_columns = sorted(column_scores.items(), key=lambda item: item[1], reverse=True)[:8]
    shap_by_column = build_column_shap_matrix(shap_values, list(explained_df.columns), feature_to_column)
    cluster_groups = cluster_impacted_columns(shap_by_column, [column for column, _ in top_columns])
    row_explanations = build_row_explanations(explained_raw_df, shap_values, list(explained_df.columns), feature_to_column, row_scores)
    severity = "high" if impacted_ratio >= max(0.05, threshold_state["min_impacted_ratio"] * 2) else "medium"

    result_payload = {
        "table_name": asset_table_name,
        "batch_time": datetime.utcnow().isoformat(),
        "partition_key": effective_date or datetime.utcnow().date().isoformat(),
        "anomaly_score": total_score,
        "status": status,
        "raw_json": {
            "effective_date": effective_date or datetime.utcnow().date().isoformat(),
            "sample_size": sample_size,
            "sensitivity": sensitivity,
            "seasonality_mode": "adaptive_threshold_with_time_feature_exclusion",
            "cluster_groups": cluster_groups,
            "excluded_time_columns": excluded_time_columns,
            "feature_summary": feature_summary,
            "specificity": {
                "reference_center": threshold_state["reference_center"],
                "reference_noise": threshold_state["reference_noise"],
                "dynamic_threshold": threshold_state["dynamic_threshold"],
            },
            "drift_metrics": {
                "current_center": threshold_state["current_center"],
                "drift_gap": threshold_state["drift_gap"],
                "impacted_ratio": impacted_ratio,
                "min_impacted_ratio": threshold_state["min_impacted_ratio"],
                "row_alert_score": threshold_state["row_alert_score"],
            },
            "row_explanations": row_explanations,
            "sampled_rows": {
                "reference": int(len(reference_pd)),
                "current": int(len(current_pd)),
                "explained": int(len(explained_df)),
            },
        },
        "features": [
            {
                "column_name": column_name,
                "importance_score": score,
            }
            for column_name, score in top_columns
        ],
    }
    save_results(backend_url, result_payload)

    if status == "ALERT":
        post_incident(
            backend_url,
            {
                "table_name": asset_table_name,
                "incident_type": "ml_anomaly",
                "severity": severity,
                "message": (
                    f"ML anomaly detected for {asset_table_name}. Sensitive columns: "
                    f"{', '.join(column for column, _ in top_columns[:3])}. "
                    f"Column groups: {' | '.join(', '.join(group) for group in cluster_groups[:3])}. "
                    f"Impacted ratio={impacted_ratio:.3%}, drift gap={threshold_state['drift_gap']:.3f}"
                ),
                "status": "open",
            },
        )

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--effective_date", default="")
    parser.add_argument("--sample_size", type=int, default=10000)
    parser.add_argument("--sensitivity", default="medium")
    parser.add_argument("--backend_url", default="http://host.docker.internal:8000")
    parser.add_argument("--token", default="internal_ops_token")
    args = parser.parse_args()

    run_ml_anomaly(
        args.catalog,
        args.schema,
        args.table,
        args.backend_url,
        args.effective_date,
        args.sample_size,
        args.sensitivity,
    )
