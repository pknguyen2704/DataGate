import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
import pyarrow.parquet as pq
from tabulate import tabulate


DEFAULT_SAMPLE_ROWS = 50_000
DEFAULT_TOP_K = 10


@dataclass
class ProfileResult:
    file_path: Path
    num_rows: int
    num_columns: int
    num_row_groups: int
    file_size_mb: float
    sample_rows: int
    markdown: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a quick data overview for parquet files."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--file", help="Single parquet file path")
    source_group.add_argument("--data-dir", help="Directory containing parquet files")
    parser.add_argument("--pattern", default="*.parquet", help="Glob pattern for --data-dir")
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=DEFAULT_SAMPLE_ROWS,
        help="Maximum number of rows to load for column profiling",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help="Top values to show for categorical columns",
    )
    parser.add_argument(
        "--output",
        help="Write the generated markdown report to a file",
    )
    return parser.parse_args()


def collect_files(args: argparse.Namespace) -> List[Path]:
    if args.file:
        file_path = Path(args.file).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return [file_path]

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    files = sorted(data_dir.glob(args.pattern))
    if not files:
        raise FileNotFoundError(f"No parquet files found in {data_dir} with pattern {args.pattern}")
    return files


def load_sample_dataframe(file_path: Path, sample_rows: int) -> pd.DataFrame:
    parquet_file = pq.ParquetFile(file_path)
    batches = []
    loaded_rows = 0

    for batch in parquet_file.iter_batches(batch_size=min(sample_rows, 10_000)):
        remaining = sample_rows - loaded_rows
        if remaining <= 0:
            break

        df_batch = batch.to_pandas()
        if len(df_batch) > remaining:
            df_batch = df_batch.head(remaining)

        batches.append(df_batch)
        loaded_rows += len(df_batch)

        if loaded_rows >= sample_rows:
            break

    if not batches:
        return pd.DataFrame()

    return pd.concat(batches, ignore_index=True)


def format_table(rows: List[List[object]], headers: List[str]) -> str:
    if not rows:
        return "_No data available._"
    return tabulate(rows, headers=headers, tablefmt="github", floatfmt=".4f")


def profile_columns(sample_df: pd.DataFrame) -> str:
    rows = []
    for column in sample_df.columns:
        series = sample_df[column]
        null_pct = (series.isna().mean() * 100) if len(series) else 0.0
        nunique = series.nunique(dropna=True)
        rows.append(
            [
                column,
                str(series.dtype),
                int(series.notna().sum()),
                int(series.isna().sum()),
                null_pct,
                int(nunique),
            ]
        )

    return format_table(
        rows,
        ["column", "dtype", "non_null", "null", "null_%", "unique_in_sample"],
    )


def profile_numeric(sample_df: pd.DataFrame) -> str:
    numeric_columns = sample_df.select_dtypes(include=["number"]).columns
    rows = []
    for column in numeric_columns:
        series = sample_df[column].dropna()
        if series.empty:
            continue
        rows.append(
            [
                column,
                series.min(),
                series.quantile(0.25),
                series.median(),
                series.mean(),
                series.quantile(0.75),
                series.max(),
                series.std(),
            ]
        )

    return format_table(
        rows,
        ["column", "min", "p25", "median", "mean", "p75", "max", "std"],
    )


def profile_datetime(sample_df: pd.DataFrame) -> str:
    rows = []
    for column in sample_df.columns:
        series = sample_df[column]
        if pd.api.types.is_datetime64_any_dtype(series):
            cleaned = series.dropna()
        elif is_datetime_candidate(column, series):
            converted = pd.to_datetime(series, errors="coerce")
            cleaned = converted.dropna()
            if len(cleaned) < max(3, int(len(series.dropna()) * 0.8)):
                continue
        else:
            continue

        if cleaned.empty:
            continue

        rows.append(
            [
                column,
                cleaned.min(),
                cleaned.max(),
                (cleaned.max() - cleaned.min()),
            ]
        )

    return format_table(rows, ["column", "min_ts", "max_ts", "span"])


def is_datetime_candidate(column: str, series: pd.Series) -> bool:
    if not (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
    ):
        return False

    lowered = column.lower()
    keywords = ("date", "time", "timestamp", "_at")
    return any(keyword in lowered for keyword in keywords)


def profile_categorical(sample_df: pd.DataFrame, top_k: int) -> str:
    rows = []
    candidate_columns = [
        column
        for column in sample_df.columns
        if (
            pd.api.types.is_object_dtype(sample_df[column])
            or pd.api.types.is_string_dtype(sample_df[column])
            or pd.api.types.is_bool_dtype(sample_df[column])
            or sample_df[column].nunique(dropna=True) <= top_k * 3
        )
    ]

    for column in candidate_columns:
        counts = sample_df[column].fillna("<NULL>").value_counts(dropna=False).head(top_k)
        formatted = ", ".join(f"{value}: {count}" for value, count in counts.items())
        rows.append([column, formatted])

    return format_table(rows, ["column", f"top_{top_k}_values_in_sample"])


def generate_insights(sample_df: pd.DataFrame) -> str:
    insights: List[str] = []
    sample_size = len(sample_df)

    if sample_size == 0:
        return "- Sample is empty, cannot infer data quality signals."

    duplicate_rows = int(sample_df.duplicated().sum())
    insights.append(f"- Duplicate rows in sample: `{duplicate_rows}` / `{sample_size}`.")

    high_null = [
        column
        for column in sample_df.columns
        if sample_df[column].isna().mean() >= 0.5
    ]
    if high_null:
        insights.append(
            f"- Columns with >= 50% null in sample: {', '.join(f'`{column}`' for column in high_null)}."
        )

    constant_columns = [
        column
        for column in sample_df.columns
        if sample_df[column].nunique(dropna=True) <= 1
    ]
    if constant_columns:
        insights.append(
            f"- Near-constant columns in sample: {', '.join(f'`{column}`' for column in constant_columns)}."
        )

    id_like = []
    for column in sample_df.columns:
        ratio = sample_df[column].nunique(dropna=True) / sample_size
        if ratio >= 0.95:
            id_like.append(column)
    if id_like:
        insights.append(
            f"- High-cardinality / ID-like columns: {', '.join(f'`{column}`' for column in id_like[:8])}."
        )

    negative_numeric = []
    for column in sample_df.select_dtypes(include=["number"]).columns:
        if sample_df[column].dropna().lt(0).any():
            negative_numeric.append(column)
    if negative_numeric:
        insights.append(
            f"- Numeric columns containing negative values: {', '.join(f'`{column}`' for column in negative_numeric)}."
        )

    return "\n".join(insights) if insights else "- No obvious data quality issue found in the current sample."


def profile_file(file_path: Path, sample_rows: int, top_k: int) -> ProfileResult:
    parquet_file = pq.ParquetFile(file_path)
    schema = parquet_file.schema_arrow
    sample_df = load_sample_dataframe(file_path, sample_rows)
    file_size_mb = file_path.stat().st_size / (1024 * 1024)

    schema_rows = [[field.name, str(field.type), field.nullable] for field in schema]
    overview_rows = [
        ["file", str(file_path)],
        ["rows", parquet_file.metadata.num_rows],
        ["columns", len(schema)],
        ["row_groups", parquet_file.num_row_groups],
        ["file_size_mb", round(file_size_mb, 2)],
        ["sample_rows_loaded", len(sample_df)],
    ]

    markdown = "\n".join(
        [
            f"# Data Overview: {file_path.name}",
            "",
            "## Dataset Summary",
            "",
            format_table(overview_rows, ["metric", "value"]),
            "",
            "## Schema",
            "",
            format_table(schema_rows, ["column", "parquet_type", "nullable"]),
            "",
            "## Column Health (sample-based)",
            "",
            profile_columns(sample_df),
            "",
            "## Numeric Statistics (sample-based)",
            "",
            profile_numeric(sample_df),
            "",
            "## Datetime Coverage (sample-based)",
            "",
            profile_datetime(sample_df),
            "",
            f"## Top Values (sample-based, top {top_k})",
            "",
            profile_categorical(sample_df, top_k),
            "",
            "## Data Quality Signals",
            "",
            generate_insights(sample_df),
            "",
            "## Sample Preview",
            "",
            sample_df.head(10).to_markdown(index=False) if not sample_df.empty else "_No sample rows loaded._",
            "",
        ]
    )

    return ProfileResult(
        file_path=file_path,
        num_rows=parquet_file.metadata.num_rows,
        num_columns=len(schema),
        num_row_groups=parquet_file.num_row_groups,
        file_size_mb=file_size_mb,
        sample_rows=len(sample_df),
        markdown=markdown,
    )


def build_directory_summary(results: List[ProfileResult]) -> str:
    rows = [
        [
            result.file_path.name,
            result.num_rows,
            result.num_columns,
            result.num_row_groups,
            round(result.file_size_mb, 2),
            result.sample_rows,
        ]
        for result in results
    ]
    return "\n".join(
        [
            "# Directory Overview",
            "",
            format_table(
                rows,
                ["file", "rows", "columns", "row_groups", "file_size_mb", "sample_rows"],
            ),
            "",
        ]
    )


def write_output(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    files = collect_files(args)
    results = [profile_file(file_path, args.sample_rows, args.top_k) for file_path in files]

    sections: List[str] = []
    if len(results) > 1:
        sections.append(build_directory_summary(results))
    sections.extend(result.markdown for result in results)

    report = "\n\n".join(sections)
    print(report)

    if args.output:
        output_path = Path(args.output).resolve()
        write_output(output_path, report)
        print(f"\n[DATAGATE] Markdown report written to {output_path}")


if __name__ == "__main__":
    main()
