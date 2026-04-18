import argparse
import os
from datetime import datetime

os.environ.setdefault("SPARK_VERSION", "3.5")

import requests
from pydeequ.suggestions import ConstraintSuggestionRunner, DEFAULT
from pyspark.errors import AnalysisException
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PRIORITY_RANK = {
    "completeness": "high",
    "uniqueness": "high",
    "compliance": "medium",
    "range": "medium",
    "distribution": "low",
    "validity": "medium",
}


def load_target_table(spark, full_table):
    try:
        return spark.read.table(full_table)
    except AnalysisException as exc:
        raise ValueError(f"Table '{full_table}' was not found in the Spark catalog.") from exc


def sample_for_suggestions(df, sample_size):
    return df.orderBy(F.rand(seed=42)).limit(sample_size)


def categorize_rule(description: str, code: str) -> tuple[str, str]:
    text = f"{description} {code}".lower()
    if "completeness" in text or "not null" in text or "iscomplete" in text:
        return "completeness", "high"
    if "unique" in text or "uniqueness" in text:
        return "uniqueness", "high"
    if "contained" in text or "compliance" in text or "pattern" in text:
        return "compliance", "medium"
    if "min" in text or "max" in text or "negative" in text:
        return "range", "medium"
    if "mean" in text or "std" in text or "distribution" in text:
        return "distribution", "low"
    return "validity", "medium"


def build_suggestions_payload(table_name, suggestion_result):
    suggestions = []
    for column_name, column_suggestions in suggestion_result.constraintSuggestions.items():
        for suggestion in column_suggestions:
            category, priority = categorize_rule(
                getattr(suggestion, "description", "") or "",
                suggestion.codeForConstraint,
            )
            suggestions.append(
                {
                    "table_name": table_name,
                    "column_name": column_name,
                    "rule_type": category,
                    "rule_expression": suggestion.codeForConstraint,
                    "category": category,
                    "priority": priority,
                    "source": "pydeequ",
                    "description": getattr(suggestion, "description", None),
                    "confidence_score": 0.95 if priority == "high" else 0.85 if priority == "medium" else 0.75,
                }
            )
    return {"table_name": table_name, "suggestions": suggestions}


def post_suggestions(backend_url, payload):
    response = requests.post(f"{backend_url}/api/v1/rules/suggestions/internal", json=payload, timeout=30)
    response.raise_for_status()


def run_rule_suggestion(catalog, schema, table_name, backend_url, sample_size):
    spark = SparkSession.builder.appName(f"RuleSuggestion-{table_name}").getOrCreate()
    full_table = f"{catalog}.{schema}.{table_name}"
    asset_table_name = f"{schema}.{table_name}"

    try:
        df = load_target_table(spark, full_table)
        sampled_df = sample_for_suggestions(df, sample_size)
        if sampled_df.count() == 0:
            raise ValueError(f"No sampled rows available for {asset_table_name}")

        suggestion_result = (
            ConstraintSuggestionRunner(spark)
            .onData(sampled_df)
            .addConstraintRule(DEFAULT())
            .run()
        )

        payload = build_suggestions_payload(asset_table_name, suggestion_result)
        post_suggestions(backend_url, payload)
        print(
            f"Generated {len(payload['suggestions'])} suggested rules for {asset_table_name} at {datetime.utcnow().isoformat()}"
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--sample_size", type=int, default=10000)
    parser.add_argument("--backend_url", default="http://host.docker.internal:8000")
    args = parser.parse_args()

    run_rule_suggestion(
        args.catalog,
        args.schema,
        args.table,
        args.backend_url,
        args.sample_size,
    )
