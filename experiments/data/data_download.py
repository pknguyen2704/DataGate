import argparse
import os
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests

BASE = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DEFAULT_TIMEOUT = 30

@dataclass
class Target:
    dataset: str   # yellow/green/fhv/fhvhv
    year: int
    month: int

    @property
    def ym(self) -> str:
        return f"{self.year}-{self.month:02d}"

    @property
    def filename(self) -> str:
        return f"{self.dataset}_tripdata_{self.ym}.parquet"

    @property
    def url(self) -> str:
        return f"{BASE}/{self.filename}"

def parse_months(months_arg: Optional[str]) -> List[int]:
    """
    Accept:
      - None -> [1..12]
      - "2" -> [2]
      - "1,2,12" -> [1,2,12]
      - "1-6" -> [1..6]
      - "1-3,6,9-12" -> combined
    """
    if not months_arg:
        return list(range(1, 13))

    out = set()
    parts = [p.strip() for p in months_arg.split(",") if p.strip()]
    for p in parts:
        if "-" in p:
            a, b = p.split("-", 1)
            a, b = int(a), int(b)
            if a > b:
                a, b = b, a
            for m in range(a, b + 1):
                out.add(m)
        else:
            out.add(int(p))

    months = sorted(out)
    for m in months:
        if m < 1 or m > 12:
            raise ValueError(f"Invalid month: {m}. Month must be 1..12.")
    return months

def head_exists(url: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        # CloudFront thường trả 200 nếu có, 403/404 nếu không
        return r.status_code == 200
    except requests.RequestException:
        return False

def download_file(url: str, dest: str, timeout: int = DEFAULT_TIMEOUT, chunk_mb: int = 8) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    # Nếu đã tải rồi thì skip
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"[SKIP] {dest}")
        return

    tmp = dest + ".part"
    with requests.get(url, stream=True, allow_redirects=True, timeout=timeout) as r:
        r.raise_for_status()
        total = r.headers.get("Content-Length")
        total_str = f"{int(total)/1e9:.2f} GB" if total and total.isdigit() else "unknown"

        print(f"[GET ] {url}  (size: {total_str})")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_mb * 1024 * 1024):
                if chunk:
                    f.write(chunk)

    os.replace(tmp, dest)
    print(f"[OK  ] {dest}")

def build_targets(datasets: List[str], years: List[int], months: List[int]) -> List[Target]:
    targets: List[Target] = []
    for y in years:
        for m in months:
            for ds in datasets:
                targets.append(Target(ds, y, m))
    return targets

def main():
    ap = argparse.ArgumentParser(
        description="Download NYC TLC trip data (parquet) by year and optional months."
    )
    ap.add_argument(
        "--dataset",
        action="append",
        default=None,
        help="Dataset: yellow, green, fhv, fhvhv. You can pass multiple: --dataset yellow --dataset green",
    )

    ap.add_argument("--year", type=int, action="append", required=True,
                    help="Year to download. You can pass multiple: --year 2024 --year 2025")
    ap.add_argument("--months", default=None,
                    help="Months to download. Examples: '2' or '1,2,12' or '1-6' or '1-3,6,9-12'. "
                         "If omitted -> full year (1..12).")
    ap.add_argument("--out", default="./nyc_tlc_tripdata", help="Output directory")
    ap.add_argument("--dry-run", action="store_true", help="Only print URLs/files, do not download")
    ap.add_argument("--skip-missing-check", action="store_true",
                    help="Do not HEAD-check existence; try downloading directly (faster, but may error on missing months).")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout seconds")
    args = ap.parse_args()

    datasets = ["yellow"] if args.dataset is None else args.dataset
    datasets = [d.strip() for d in datasets if d and d.strip()]

    seen = set()
    datasets = [d for d in datasets if not (d in seen or seen.add(d))]

    years = args.year
    months = parse_months(args.months)

    targets = build_targets(datasets, years, months)

    if args.dry_run:
        for t in targets:
            print(t.url)
        print(f"\nTotal: {len(targets)} URLs (dry-run).")
        return

    ok = 0
    miss = 0
    err = 0

    for t in targets:
        dest = os.path.join(args.out, t.filename)

        if not args.skip_missing_check:
            if not head_exists(t.url, timeout=args.timeout):
                print(f"[MISS] {t.url}")
                miss += 1
                continue

        try:
            download_file(t.url, dest, timeout=args.timeout)
            ok += 1
        except requests.HTTPError as e:
            print(f"[ERR ] {t.url} -> HTTP error: {e}")
            err += 1
            # dọn file part nếu có
            try:
                if os.path.exists(dest + ".part"):
                    os.remove(dest + ".part")
            except OSError:
                pass
        except requests.RequestException as e:
            print(f"[ERR ] {t.url} -> Request error: {e}")
            err += 1
        except Exception as e:
            print(f"[ERR ] {t.url} -> {e}")
            err += 1

    print("\n===== Summary =====")
    print(f"Downloaded: {ok}")
    print(f"Missing   : {miss}")
    print(f"Errors    : {err}")
    print(f"Output dir: {os.path.abspath(args.out)}")

if __name__ == "__main__":
    # requests is required: pip install requests
    import time
    start_time = time.time()
    try:
        main()
    finally:
        print(f"Total execution time: {time.time() - start_time:.2f} seconds")
