import os
from typing import Any, Dict, List

# PyDeequ requires SPARK_VERSION before import.
os.environ.setdefault("SPARK_VERSION", "3.5")

from pydeequ.analyzers import (
    AnalysisRunner,
    AnalyzerContext,
    ApproxCountDistinct,
    Completeness,
    Distinctness,
    MaxLength,
    Maximum,
    Mean,
    MinLength,
    Minimum,
    StandardDeviation,
)
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    ByteType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    StringType,
)

PROFILE_METRICS = {
    "Completeness",
    "Mean",
    "StandardDeviation",
    "Minimum",
    "Maximum",
    "MinLength",
    "MaxLength",
    "Distinctness",
    "ApproxCountDistinct",
}
NUMERIC_TYPES = (ByteType, ShortType, IntegerType, LongType, FloatType, DoubleType, DecimalType)


def add_common_column_analyzers(analysis_runner, column_name: str):
    return (
        analysis_runner
        .addAnalyzer(Completeness(column_name))
        .addAnalyzer(ApproxCountDistinct(column_name))
        .addAnalyzer(Distinctness(column_name))
    )


def add_numeric_column_analyzers(analysis_runner, column_name: str):
    return (
        analysis_runner
        .addAnalyzer(Minimum(column_name))
        .addAnalyzer(Maximum(column_name))
        .addAnalyzer(Mean(column_name))
        .addAnalyzer(StandardDeviation(column_name))
    )


def add_string_column_analyzers(analysis_runner, column_name: str):
    return (
        analysis_runner
        .addAnalyzer(MinLength(column_name))
        .addAnalyzer(MaxLength(column_name))
    )


def build_analysis_runner(spark: SparkSession, df: DataFrame):
    analysis_runner = AnalysisRunner(spark).onData(df)

    for field in df.schema.fields:
        column_name = field.name
        analysis_runner = add_common_column_analyzers(analysis_runner, column_name)

        if isinstance(field.dataType, NUMERIC_TYPES):
            analysis_runner = add_numeric_column_analyzers(analysis_runner, column_name)

        if isinstance(field.dataType, StringType):
            analysis_runner = add_string_column_analyzers(analysis_runner, column_name)

    return analysis_runner


def run_analyzers(spark: SparkSession, df: DataFrame) -> DataFrame:
    analysis_result = build_analysis_runner(spark=spark, df=df).run()
    return AnalyzerContext.successMetricsAsDataFrame(spark, analysis_result)


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_profile_metrics(metric_rows: List[Dict[str, Any]]) -> Dict[tuple[str, str], float]:
    normalized: Dict[tuple[str, str], float] = {}
    for row in metric_rows:
        column_name = row.get("instance")
        metric_name = row.get("name")
        metric_value = safe_float(row.get("value"))

        if not column_name or metric_name not in PROFILE_METRICS or metric_value is None:
            continue

        normalized[(column_name, metric_name)] = metric_value

    return normalized
