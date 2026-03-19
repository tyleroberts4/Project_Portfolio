#!/usr/bin/env python3
"""
run_county_hourly_midpoint.py

County → Weather API → PUE/WUE pipeline (CLI).

1. Resolve selected county to (latitude, longitude) via us_county_centroids.csv.
2. Fetch historical hourly weather (T_oa, RH_oa, P_oa) from Open-Meteo Historical API.
3. Build w with weather from API and midpoints for all other parameters.
4. Run PUE_WUE simulator (AE and/or WEC) per hour and write CSV.

Uses county_pipeline for the actual run; this script handles argparse and file output.

Usage:
  python run_county_hourly_midpoint.py --county-fips 6037 --start 2024-01-01 --end 2024-12-31 --system AE --out county_AE.csv
  python run_county_hourly_midpoint.py --county-fips 6079 --start 2025-01-01 --end 2025-12-31 --system both
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Import from same directory
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from county_pipeline import load_county_centroids, resolve_county, run_county


def main():
    parser = argparse.ArgumentParser(
        description="County → Weather API → hourly PUE/WUE (midpoint params)"
    )
    parser.add_argument("--centroids", type=Path, default=None, help="Path to us_county_centroids.csv")
    parser.add_argument("--county-fips", type=str, default=None, help="County FIPS (e.g. 6037 or 06037)")
    parser.add_argument("--county", type=str, default=None, help="County name (use with --state-fips)")
    parser.add_argument("--state-fips", type=str, default=None, help="State FIPS 2-digit (e.g. 06 for CA)")
    parser.add_argument("--start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--system", type=str, choices=["AE", "WEC", "both"], default="AE", help="AE, WEC, or both")
    parser.add_argument("--out", type=Path, default=None, help="Output CSV path")
    parser.add_argument("--max-hours", type=int, default=None, help="Cap hours for testing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger()

    # Resolve centroids path.
    # In the original repo this default pointed at a local Downloads path; here we default to
    # the submission dataset (4_analysis_data/county_centroids.csv).
    DEFAULT_CENTROIDS = SCRIPT_DIR.parent / "04_analysis_data" / "county_centroids.csv"
    if args.centroids is not None:
        centroids_path = args.centroids if args.centroids.is_absolute() else (SCRIPT_DIR / args.centroids).resolve()
    else:
        for candidate in [DEFAULT_CENTROIDS, SCRIPT_DIR / "us_county_centroids.csv", Path.home() / "us_county_centroids.csv", SCRIPT_DIR / "us_county_centroids_sample.csv"]:
            if candidate.exists():
                centroids_path = candidate
                break
        else:
            centroids_path = DEFAULT_CENTROIDS

    if not centroids_path.exists():
        log.error("Centroids CSV not found: %s", centroids_path)
        sys.exit(1)

    centroids = load_county_centroids(centroids_path)
    try:
        county_fips, county_name, lat, lon = resolve_county(
            centroids,
            county_fips=args.county_fips,
            county_name=args.county,
            state_fips=args.state_fips,
        )
    except ValueError as e:
        log.error("%s", e)
        sys.exit(1)

    log.info("County: %s (%s) at (%.4f, %.4f)", county_name, county_fips, lat, lon)

    try:
        df = run_county(
            county_fips,
            args.start,
            args.end,
            system=args.system,
            centroids_df=centroids,
            max_hours=args.max_hours,
        )
    except Exception as e:
        log.error("Pipeline failed: %s", e)
        sys.exit(1)

    if df.empty:
        log.error("No results")
        sys.exit(1)

    out_path = args.out
    if out_path is None:
        out_path = SCRIPT_DIR / f"county_{county_fips}_{args.system}_midpoint.csv"
    out_path = out_path if out_path.is_absolute() else (SCRIPT_DIR / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    log.info("Saved %d rows to %s", len(df), out_path)


if __name__ == "__main__":
    main()
