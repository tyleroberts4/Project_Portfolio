#!/usr/bin/env python3
"""
build_weather_hourly_with_counties_sample.py

Creates a tiny `weather_hourly_with_counties_sample.csv` inside:
  `01_weather_api_and_pue_wue_simulation/`

This is included so the submission's weather+PUE/WUE scripts can be executed
without downloading the full multi-GB pre-joined dataset.

It fetches hourly historical weather from Open-Meteo for a small number of
county centroids (default: first 2 counties) and writes the minimal columns
needed by:
  - `01_weather_api_and_pue_wue_simulation/run_weather_hourly_with_counties_midpoint.py`
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a small weather_hourly_with_counties sample CSV.")
    parser.add_argument("--counties", type=int, default=2, help="Number of counties to sample.")
    parser.add_argument("--start", type=str, default="2024-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, default="2024-01-03", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output CSV path (default: 01_weather_api_and_pue_wue_simulation/weather_hourly_with_counties_sample.csv).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    weather_dir = repo_root / "01_weather_api_and_pue_wue_simulation"
    centroids_path = repo_root / "04_analysis_data" / "county_centroids.csv"
    out_path = args.out if args.out is not None else weather_dir / "weather_hourly_with_counties_sample.csv"

    if not centroids_path.is_file():
        raise FileNotFoundError(f"Centroids not found: {centroids_path}")

    # Import the shared Open-Meteo weather function.
    import sys

    sys.path.insert(0, str(weather_dir))
    from county_pipeline import fetch_historical_weather  # type: ignore

    centroids = pd.read_csv(centroids_path, low_memory=False)
    if "county_fips" not in centroids.columns or "latitude" not in centroids.columns or "longitude" not in centroids.columns:
        raise ValueError("county_centroids.csv must contain county_fips, latitude, longitude")

    centroids["county_fips"] = centroids["county_fips"].astype(str).str.replace(r"\\.0$", "", regex=True).str.zfill(5)
    centroids = centroids.sort_values("county_fips").head(args.counties)

    frames: list[pd.DataFrame] = []
    for _, r in centroids.iterrows():
        county_fips = str(r["county_fips"])
        lat = float(r["latitude"])
        lon = float(r["longitude"])
        hourly = fetch_historical_weather(lat, lon, args.start, args.end)
        hourly = hourly.copy()
        hourly["county_fips"] = county_fips
        hourly["year"] = hourly["time"].dt.year
        hourly["timestamp"] = hourly["time"].astype("string")
        # Map names to what the midpoint script expects.
        hourly = hourly.rename(columns={"T_oa_C": "temp_c", "RH_pct": "rh_pct"})
        hourly["pressure_hpa"] = hourly["P_atm_Pa"] / 100.0
        keep = ["county_fips", "year", "timestamp", "temp_c", "rh_pct", "pressure_hpa"]
        frames.append(hourly[keep])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.concat(frames, ignore_index=True)
    out_df.to_csv(out_path, index=False)
    print(f"Wrote sample weather file: {out_path} ({len(out_df)} rows)")


if __name__ == "__main__":
    main()

