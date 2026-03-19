#!/usr/bin/env python3
"""
build_drought_summary_by_county.py

Creates a compact county-level drought summary from the (large) weekly US Drought Monitor
county dataset used in the project.

This is intended for GitHub submissions where the full weekly CSV may be too large.
The summary contains exactly the drought statistics used downstream in the report:
  - mean_drought (0-5) over the period
  - max_drought  (0-5) over the period
  - pct_weeks_d1_plus (% weeks with drought_level_avg >= 1, 0-100)
  - pct_weeks_d2_plus (% weeks with drought_level_avg >= 2, severe drought, 0-100)

Usage:
  # Recommended for this submission repo (weekly file included compressed):
  python scripts/build_drought_summary_by_county.py

  # Or point at your own weekly drought file:
  python scripts/build_drought_summary_by_county.py \
    --input "/path/to/drought_weekly_by_county_2015_2024_week52only_fixed_2.0.csv.gz"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _norm_fips(s: pd.Series) -> pd.Series:
    # API sometimes yields floats or strings with ".0"
    return (
        s.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(5)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build drought summary by county (D1+ and D2+).")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=False,
        default=None,
        help="Weekly drought CSV (e.g. drought_weekly_by_county_2015_2024_week52only_fixed_2.0.csv.gz). "
             "If omitted, the script uses the week52only file included in this submission.",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=Path,
        default=None,
        help="Output path (default: 04_analysis_data/drought_summary_by_county.csv)",
    )
    parser.add_argument(
        "--counties",
        type=Path,
        default=None,
        help="Optional county lookup CSV for county_name/state_abbr (default: 04_analysis_data/counties.csv if present).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    default_out = repo_root / "04_analysis_data" / "drought_summary_by_county.csv"
    out_path = args.out if args.out is not None else default_out

    counties_path = (
        args.counties
        if args.counties is not None
        else (repo_root / "04_analysis_data" / "counties.csv")
    )

    # If the compact output already exists (typical for this submission),
    # allow the builder to run without the weekly CSV.
    if out_path.is_file() and args.input is None:
        print(f"Output already exists: {out_path}. Skipping regeneration.")
        return

    if args.input is None:
        args.input = (
            repo_root
            / "02_drought_risk"
            / "drought_weekly_by_county_2015_2024_week52only_fixed_2.0.csv.gz"
        )

    if not args.input.is_file():
        raise FileNotFoundError(f"Input drought CSV not found: {args.input}")

    df = pd.read_csv(args.input, low_memory=False)
    if "county_fips" not in df.columns or "drought_level_avg" not in df.columns:
        raise ValueError(
            "Input drought CSV must contain 'county_fips' and 'drought_level_avg' columns."
        )

    df["county_fips"] = _norm_fips(df["county_fips"])

    summary = df.groupby("county_fips", as_index=False).agg(
        mean_drought=("drought_level_avg", "mean"),
        max_drought=("drought_level_avg", "max"),
        pct_weeks_d1_plus=("drought_level_avg", lambda s: (s >= 1).mean() * 100),
        pct_weeks_d2_plus=("drought_level_avg", lambda s: (s >= 2).mean() * 100),  # severe (D2-D4)
    ).round(4)

    if counties_path.is_file():
        counties = pd.read_csv(counties_path)
        if "county_fips" in counties.columns:
            counties["county_fips"] = _norm_fips(counties["county_fips"])
        join_cols = [c for c in ["county_name", "state_abbr"] if c in counties.columns]
        if join_cols:
            summary = summary.merge(counties[["county_fips", *join_cols]].drop_duplicates("county_fips"), on="county_fips", how="left")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_path, index=False)
    print(f"Wrote drought summary: {out_path} ({len(summary)} counties)")

    # Manifest: helps reviewers confirm which drought file/version was used.
    try:
        import datetime as _dt
        import json as _json

        import datetime as _dt

        manifest = {
            "source_weekly_drought_file": str(args.input),
            "generated_at_utc": _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "rows_in_summary": int(len(summary)),
        }
        out_path.with_suffix(".manifest.json").write_text(
            _json.dumps(manifest, indent=2), encoding="utf-8"
        )
    except Exception:
        # Best-effort only.
        pass


if __name__ == "__main__":
    main()

