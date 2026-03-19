#!/usr/bin/env python3
"""
run_weather_parallel_by_county.py

Parallel version of weather_hourly_with_counties_midpoint:
- Splits work by county_fips
- Runs multiple processes in parallel
- Each process computes AE/WEC PUE/WUE for its counties and writes a per-county CSV

It does NOT change the simulator; it just parallelizes the existing pipeline.

Recommended shell settings before running (to avoid nested threading):

  export OMP_NUM_THREADS=1
  export MKL_NUM_THREADS=1
  export OPENBLAS_NUM_THREADS=1
"""

from __future__ import annotations

import argparse
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from pathlib import Path
from typing import Iterable, List

import pandas as pd

# Import the existing single-process logic
from run_weather_hourly_with_counties_midpoint import (  # type: ignore
    compute_pue_wue_for_dataframe,
)


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent


def _process_one_county(county_fips: str, input_csv: str, out_dir: str) -> str:
    """
    Worker: read input CSV, filter to one county_fips, run simulator, write per-county CSV.
    Runs in a separate process.
    """
    log = logging.getLogger(f"worker-{county_fips}")

    df = pd.read_csv(input_csv)
    df = df[df["county_fips"].astype(str) == county_fips].copy()
    if df.empty:
        log.warning("No rows for county_fips=%s", county_fips)
        return ""

    log.info("Processing county_fips=%s with %d rows", county_fips, len(df))
    df_out = compute_pue_wue_for_dataframe(df)

    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    out_path = out_dir_path / f"weather_hourly_with_pue_wue_{county_fips}.csv"
    df_out.to_csv(out_path, index=False)
    log.info("Wrote %d rows for county_fips=%s to %s", len(df_out), county_fips, out_path)
    return str(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Parallel: compute AE/WEC PUE/WUE per county_fips using multiple processes. "
            "Each county is written to its own CSV."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=(SCRIPT_DIR / "weather_hourly_with_counties_sample.csv"),
        help="Input CSV with hourly weather + counties (same as single-process script)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=(SCRIPT_DIR / "weather_parallel_by_county"),
        help="Directory to write per-county CSVs",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Number of worker processes (default: min(cpu_count, number of counties))",
    )
    parser.add_argument(
        "--limit-counties",
        type=int,
        default=None,
        help="For testing: only process the first N counties",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger("parallel-main")

    input_csv = args.input if args.input.is_absolute() else (BASE_DIR / args.input).resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else (SCRIPT_DIR / args.out_dir).resolve()

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    log.info("Input CSV: %s", input_csv)
    log.info("Output directory: %s", out_dir)

    # Discover counties from a lightweight read
    df0 = pd.read_csv(input_csv, usecols=["county_fips"])
    counties = sorted(df0["county_fips"].astype(str).unique())
    if args.limit_counties is not None:
        counties = counties[: args.limit_counties]
    log.info("Total counties to process: %d", len(counties))

    if not counties:
        log.error("No counties found in input; nothing to do.")
        return

    cpu_available = cpu_count() or 1
    max_workers = args.max_workers or min(len(counties), cpu_available)
    log.info("Using %d worker processes (CPU available: %d)", max_workers, cpu_available)

    out_dir.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures: List = []
        for c in counties:
            futures.append(
                executor.submit(_process_one_county, c, str(input_csv), str(out_dir))
            )

        completed = 0
        for fut in as_completed(futures):
            completed += 1
            try:
                path = fut.result()
                if path:
                    log.info("Completed %d / %d counties (last: %s)", completed, len(counties), path)
                else:
                    log.info("Completed %d / %d counties (last had no data)", completed, len(counties))
            except Exception as e:
                log.error("Worker failed: %s", e)

    log.info("All counties submitted. Per-county CSVs are in: %s", out_dir)


if __name__ == "__main__":
    # Strongly recommended to set:
    #   export OMP_NUM_THREADS=1
    #   export MKL_NUM_THREADS=1
    #   export OPENBLAS_NUM_THREADS=1
    main()

