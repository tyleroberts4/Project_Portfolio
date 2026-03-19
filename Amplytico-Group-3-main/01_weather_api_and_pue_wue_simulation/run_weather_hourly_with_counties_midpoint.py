#!/usr/bin/env python3
"""
run_weather_hourly_with_counties_midpoint.py

Take pre-joined hourly weather + county data and compute midpoint PUE/WUE
for both AE and WEC systems, one row per hour.

Input:  weather_hourly_with_counties.csv
        (from DuckDB export via export_weather_with_counties.py)
Expected columns (at minimum):
    county_fips, county_name, state_abbr, state_full,
    year, timestamp, temp_c, rh_pct, pressure_hpa

Output: same columns plus:
    AE_PUE, AE_WUE, WEC_PUE, WEC_WUE

You can optionally:
  - limit to a maximum number of rows (for a quick test),
  - filter to a single county_fips.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

# Import simulator helpers from county_pipeline (same directory)
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SCRIPT_DIR))

from county_pipeline import get_sim, build_w_ae, build_w_wec  # type: ignore


def compute_pue_wue_for_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Given a DataFrame with temp_c, rh_pct, pressure_hpa, add AE/WEC PUE/WUE columns."""
    required = {"temp_c", "rh_pct", "pressure_hpa"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {sorted(missing)}")

    sim = get_sim()

    ae_pue: list[float] = []
    ae_wue: list[float] = []
    wec_pue: list[float] = []
    wec_wue: list[float] = []

    n = len(df)
    has_county = "county_fips" in df.columns
    seen_counties: set[str] = set()

    for idx, row in df.iterrows():
        T_oa = float(row["temp_c"])
        RH_oa = float(row["rh_pct"])
        # Convert hPa to Pa for simulator
        P_oa = float(row["pressure_hpa"]) * 100.0

        # AE
        try:
            w_ae = build_w_ae(T_oa, RH_oa, P_oa)
            pue_ae, wue_ae = sim.PUE_WUE_AE_Chiller(w_ae)
            if np.isfinite(pue_ae) and np.isfinite(wue_ae):
                ae_pue.append(float(pue_ae))
                ae_wue.append(float(wue_ae))
            else:
                ae_pue.append(np.nan)
                ae_wue.append(np.nan)
        except Exception:
            ae_pue.append(np.nan)
            ae_wue.append(np.nan)

        # WEC
        try:
            w_wec = build_w_wec(T_oa, RH_oa, P_oa)
            pue_wec, wue_wec = sim.PUE_WUE_Chiller_Watereconomier(w_wec)
            if np.isfinite(pue_wec) and np.isfinite(wue_wec):
                wec_pue.append(float(pue_wec))
                wec_wue.append(float(wue_wec))
            else:
                wec_pue.append(np.nan)
                wec_wue.append(np.nan)
        except Exception:
            wec_pue.append(np.nan)
            wec_wue.append(np.nan)

        # Progress logging for long runs
        if has_county:
            c = str(row["county_fips"])
            if c not in seen_counties:
                seen_counties.add(c)
                logging.info(
                    "Now processing county %s (%d unique counties seen, %d / %d rows)",
                    c,
                    len(seen_counties),
                    idx + 1,
                    n,
                )
        if (idx + 1) % 10000 == 0:
            logging.info("Processed %d / %d rows total", idx + 1, n)

    df = df.copy()
    df["AE_PUE"] = ae_pue
    df["AE_WUE"] = ae_wue
    df["WEC_PUE"] = wec_pue
    df["WEC_WUE"] = wec_wue
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute midpoint AE/WEC PUE/WUE for each row in "
            "weather_hourly_with_counties.csv"
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=(SCRIPT_DIR / "weather_hourly_with_counties_sample.csv"),
        help="Input CSV with hourly weather + counties (default: sample file included in submission).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(SCRIPT_DIR / "weather_hourly_with_counties_with_pue_wue.csv"),
        help="Output CSV with added AE/WEC PUE/WUE columns",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="If set, only process the first N rows (useful for a fast practice run)",
    )
    parser.add_argument(
        "--county-fips",
        type=str,
        default=None,
        help="If set, only process rows for this county_fips",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger()

    in_path = args.input if args.input.is_absolute() else (SCRIPT_DIR.parent / args.input).resolve()
    out_path = args.output if args.output.is_absolute() else (SCRIPT_DIR / args.output).resolve()

    if not in_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_path}")

    log.info("Reading input CSV: %s", in_path)
    df = pd.read_csv(in_path)

    if args.county_fips is not None:
        target = str(args.county_fips)
        before = len(df)
        df = df[df["county_fips"].astype(str) == target].copy()
        log.info(
            "Filtered to county_fips=%s: %d -> %d rows",
            target,
            before,
            len(df),
        )

    if args.max_rows is not None:
        before = len(df)
        df = df.head(args.max_rows).copy()
        log.info(
            "Limiting to first %d rows: %d -> %d rows",
            args.max_rows,
            before,
            len(df),
        )

    log.info("Computing AE and WEC PUE/WUE for %d rows...", len(df))
    df_out = compute_pue_wue_for_dataframe(df)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, index=False)
    log.info("Done. Wrote %d rows to %s", len(df_out), out_path)


if __name__ == "__main__":
    main()

