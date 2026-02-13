#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from pandas.api.types import CategoricalDtype

import numpy as np
import pandas as pd


# -------------------------
# File loading
# -------------------------
def load_table(path: Path, max_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Load a dataset into a pandas DataFrame.
    For big files: you can set --max-rows to sample the first N rows (fast preview).
    """
    suffix = path.suffix.lower()

    if suffix == ".parquet":
        df = pd.read_parquet(path)  # requires pyarrow
        if max_rows is not None and len(df) > max_rows:
            df = df.head(max_rows)
        return df

    if suffix in [".csv", ".tsv"]:
        sep = "\t" if suffix == ".tsv" else ","
        df = pd.read_csv(path, sep=sep, nrows=max_rows)
        return df

    if suffix in [".json"]:
        # supports json lines too
        df = pd.read_json(path, lines=True)
        if max_rows is not None and len(df) > max_rows:
            df = df.head(max_rows)
        return df

    raise ValueError(f"Unsupported file type: {path}")


# -------------------------
# Profiling helpers
# -------------------------
def infer_datetime_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect datetime columns, including those already datetime dtype
    and string columns that look like datetime.
    """
    dt_cols = []

    # Already datetime dtype
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            dt_cols.append(c)

    # Try parse object columns with limited sampling
    obj_cols = [c for c in df.columns if df[c].dtype == "object"]
    for c in obj_cols:
        s = df[c].dropna()
        if s.empty:
            continue
        sample = s.sample(min(200, len(s)), random_state=42).astype(str)

        # quick heuristic: contains '-' or ':' often
        if not any(("-" in x or ":" in x) for x in sample.head(50)):
            continue

        parsed = pd.to_datetime(sample, errors="coerce", utc=False)
        ratio = parsed.notna().mean()
        if ratio >= 0.9:  # strong signal
            dt_cols.append(c)

    return sorted(set(dt_cols))


def outlier_rate_iqr(series: pd.Series) -> float:
    """
    Outlier rate using IQR rule. Returns a float in [0,1].
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 20:
        return np.nan
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    lo = q1 - 1.5 * iqr
    hi = q3 + 1.5 * iqr
    return float(((s < lo) | (s > hi)).mean())


def format_bytes(n: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.2f} {u}"
        x /= 1024
    return f"{x:.2f} TB"


def column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce a per-column summary table.
    """
    n = len(df)
    rows = []

    for c in df.columns:
        s = df[c]
        dtype = str(s.dtype)
        missing = int(s.isna().sum())
        missing_pct = (missing / n) if n else 0.0

        # cardinality (unique count) for all
        nunique = int(s.nunique(dropna=True))

        # top values for categorical-like
        top_values = ""

        is_cat = isinstance(s.dtype, CategoricalDtype)
        if s.dtype == "object" or is_cat:
            vc = s.astype("object").value_counts(dropna=True).head(5)
            top_values = "; ".join([f"{idx}({cnt})" for idx, cnt in vc.items()])

        # numeric stats
        num_stats = {}
        if pd.api.types.is_numeric_dtype(s):
            s_num = pd.to_numeric(s, errors="coerce")
            num_stats = {
                "min": float(np.nanmin(s_num)) if s_num.notna().any() else np.nan,
                "p25": float(np.nanpercentile(s_num.dropna(), 25)) if s_num.notna().any() else np.nan,
                "median": float(np.nanmedian(s_num)) if s_num.notna().any() else np.nan,
                "mean": float(np.nanmean(s_num)) if s_num.notna().any() else np.nan,
                "p75": float(np.nanpercentile(s_num.dropna(), 75)) if s_num.notna().any() else np.nan,
                "max": float(np.nanmax(s_num)) if s_num.notna().any() else np.nan,
                "std": float(np.nanstd(s_num)) if s_num.notna().any() else np.nan,
                "outlier_rate_iqr": outlier_rate_iqr(s_num),
            }

        rows.append(
            {
                "column": c,
                "dtype": dtype,
                "missing": missing,
                "missing_pct": missing_pct,
                "nunique": nunique,
                "top_values(5)": top_values,
                **num_stats,
            }
        )

    out = pd.DataFrame(rows)
    # order columns nicely
    base_cols = ["column", "dtype", "missing", "missing_pct", "nunique", "top_values(5)"]
    num_cols = [c for c in out.columns if c not in base_cols]
    return out[base_cols + num_cols]


def dataset_overview(df: pd.DataFrame) -> Dict[str, object]:
    """
    File-level overview stats.
    """
    nrows, ncols = df.shape
    mem = df.memory_usage(deep=True).sum()

    # duplicates (full-row)
    dup_rows = int(df.duplicated().sum()) if nrows else 0

    # datetime columns
    dt_cols = infer_datetime_columns(df)
    dt_ranges = {}
    for c in dt_cols:
        try:
            s = df[c]
            if s.dtype == "object":
                s = pd.to_datetime(s, errors="coerce")
            dt_ranges[c] = {
                "min": None if s.dropna().empty else str(s.min()),
                "max": None if s.dropna().empty else str(s.max()),
                "missing": int(s.isna().sum()),
            }
        except Exception:
            pass

    return {
        "rows": nrows,
        "cols": ncols,
        "memory_bytes": int(mem),
        "memory_human": format_bytes(mem),
        "duplicate_rows": dup_rows,
        "duplicate_pct": (dup_rows / nrows) if nrows else 0.0,
        "datetime_columns": dt_cols,
        "datetime_ranges": dt_ranges,
    }


def write_markdown_report(
    file_path: Path,
    df: pd.DataFrame,
    out_dir: Path,
    max_sample_rows: int = 20,
) -> Path:
    """
    Write a per-file Markdown report.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", file_path.name)
    report_path = out_dir / f"{safe_name}.md"

    overview = dataset_overview(df)
    colsum = column_summary(df)

    # sample
    sample = df.head(max_sample_rows)

    # markdown
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# Data Discovery Report — `{file_path.name}`\n\n")
        f.write("## Overview\n\n")
        f.write(f"- Path: `{file_path}`\n")
        f.write(f"- Shape: **{overview['rows']} rows × {overview['cols']} cols**\n")
        f.write(f"- Estimated memory (loaded): **{overview['memory_human']}**\n")
        f.write(f"- Duplicate rows: **{overview['duplicate_rows']}** ({overview['duplicate_pct']:.2%})\n\n")

        if overview["datetime_columns"]:
            f.write("## Datetime Columns\n\n")
            for c in overview["datetime_columns"]:
                r = overview["datetime_ranges"].get(c, {})
                f.write(f"- `{c}`: min={r.get('min')} | max={r.get('max')} | missing={r.get('missing')}\n")
            f.write("\n")

        f.write("## Column Summary\n\n")
        f.write(
            colsum.to_markdown(index=False, floatfmt=".4f")
            + "\n\n"
        )

        f.write("## Sample (first rows)\n\n")
        # Convert sample to markdown; limit wide columns
        f.write(sample.to_markdown(index=False) + "\n")

    return report_path


# -------------------------
# Folder runner
# -------------------------
def list_files(input_dir: Path, pattern: str) -> List[Path]:
    return sorted(input_dir.glob(pattern))


def main():
    ap = argparse.ArgumentParser(description="Professional data discovery for local datasets (Parquet/CSV/JSON).")
    ap.add_argument("--input", required=True, help="Input folder containing data files")
    ap.add_argument("--pattern", default="*.parquet", help="Glob pattern, e.g. '*.parquet' or 'yellow_tripdata_2025-*.parquet'")
    ap.add_argument("--out", default="./reports/data_discovery", help="Output folder for reports")
    ap.add_argument("--max-files", type=int, default=0, help="Limit number of files (0 = no limit)")
    ap.add_argument("--max-rows", type=int, default=0, help="Preview mode: only load first N rows per file (0 = load all)")
    args = ap.parse_args()

    input_dir = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()

    if not input_dir.exists():
        raise SystemExit(f"Input dir not found: {input_dir}")

    files = list_files(input_dir, args.pattern)
    if args.max_files and args.max_files > 0:
        files = files[: args.max_files]

    if not files:
        raise SystemExit(f"No files matched pattern '{args.pattern}' in {input_dir}")

    summary_rows = []

    print(f"Found {len(files)} files. Writing reports to: {out_dir}")
    for i, fp in enumerate(files, start=1):
        print(f"\n[{i}/{len(files)}] Profiling: {fp.name}")
        try:
            df = load_table(fp, max_rows=(args.max_rows if args.max_rows > 0 else None))
            report_path = write_markdown_report(fp, df, out_dir)

            ov = dataset_overview(df)
            summary_rows.append(
                {
                    "file": fp.name,
                    "rows": ov["rows"],
                    "cols": ov["cols"],
                    "memory_human": ov["memory_human"],
                    "duplicate_rows": ov["duplicate_rows"],
                    "duplicate_pct": ov["duplicate_pct"],
                    "datetime_columns": ",".join(ov["datetime_columns"]),
                    "report": str(report_path),
                }
            )
        except Exception as e:
            print(f"[ERR] {fp.name}: {e}")
            summary_rows.append({"file": fp.name, "error": str(e)})

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_df = pd.DataFrame(summary_rows)
    summary_csv = out_dir / "summary.csv"
    summary_df.to_csv(summary_csv, index=False)

    print("\nDone.")
    print(f"- Summary CSV: {summary_csv}")
    print(f"- Per-file reports: {out_dir}/*.md")


if __name__ == "__main__":
    import time
    start_time = time.time()
    try:
        main()
    finally:
        print(f"Total execution time: {time.time() - start_time:.2f} seconds")
