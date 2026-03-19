#!/usr/bin/env python3
"""
build_water_stress_and_effective_costs.py

Build compact analysis tables (small CSVs) that combine:
  - weather-derived PUE/WUE (county_week_rollup.csv + counties_wue_water.csv)
  - state-level pricing (pricing_by_state.csv via included counties_wue_water.csv)
  - 10-year drought exposure (drought_summary_by_county.csv)

Outputs:
  - water_stress_by_county_system.csv
      water_stress = WUE × (1 + pct_weeks_d2_plus/100)
  - effective_utility_cost_by_county_system.csv
      effective_total_cost = effective_electric + effective_water

All values are aligned with the project's units:
  - PUE is unitless
  - WUE is L/kWh (as in the WUE simulator and existing counties_wue_water.csv)
  - effective_* electric/water are in ¢/kWh IT
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _norm_fips(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build water stress and effective utility costs tables.")
    parser.add_argument("--rollup", type=Path, default=None, help="county_week_rollup.csv path.")
    parser.add_argument("--counties-wue-water", type=Path, default=None, help="counties_wue_water.csv path.")
    parser.add_argument("--pricing", type=Path, default=None, help="pricing_by_state.csv path (for electric rate join).")
    parser.add_argument("--drought-summary", type=Path, default=None, help="drought_summary_by_county.csv path.")
    parser.add_argument("--out-water-stress", type=Path, default=None, help="Output water stress CSV path.")
    parser.add_argument("--out-effective-cost", type=Path, default=None, help="Output effective cost CSV path.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    rollup_path = args.rollup if args.rollup is not None else repo_root / "04_analysis_data" / "county_week_rollup.csv"
    wue_water_path = (
        args.counties_wue_water
        if args.counties_wue_water is not None
        else repo_root / "04_analysis_data" / "counties_wue_water.csv"
    )
    pricing_path = args.pricing if args.pricing is not None else repo_root / "03_utility_pricing" / "pricing_by_state.csv"
    drought_summary_path = (
        args.drought_summary
        if args.drought_summary is not None
        else repo_root / "04_analysis_data" / "drought_summary_by_county.csv"
    )

    out_water = (
        args.out_water_stress
        if args.out_water_stress is not None
        else repo_root / "04_analysis_data" / "water_stress_by_county_system.csv"
    )
    out_cost = (
        args.out_effective_cost
        if args.out_effective_cost is not None
        else repo_root / "04_analysis_data" / "effective_utility_cost_by_county_system.csv"
    )

    for p in [rollup_path, wue_water_path, pricing_path, drought_summary_path]:
        if not p.is_file():
            raise FileNotFoundError(f"Required input file not found: {p}")

    rollup = pd.read_csv(rollup_path, low_memory=False)
    wue_water = pd.read_csv(wue_water_path, low_memory=False)
    pricing = pd.read_csv(pricing_path, low_memory=False)
    drought = pd.read_csv(drought_summary_path, low_memory=False)

    for df in [rollup, wue_water, drought]:
        if "county_fips" in df.columns:
            df["county_fips"] = _norm_fips(df["county_fips"])

    # ---- PUE means per county × system (from rollup) ----
    required_rollup_cols = {"county_fips", "county_name", "state_abbr", "AE_PUE", "WEC_PUE"}
    missing = required_rollup_cols - set(rollup.columns)
    if missing:
        raise ValueError(f"rollup CSV missing columns: {sorted(missing)}")

    pue_mean = rollup.groupby(["county_fips", "county_name", "state_abbr"], as_index=False).agg(
        AE_PUE=("AE_PUE", "mean"),
        WEC_PUE=("WEC_PUE", "mean"),
    )

    # ---- Join electric rate ----
    required_pricing_cols = {"state_abbr", "electric_cents_per_kwh"}
    missing = required_pricing_cols - set(pricing.columns)
    if missing:
        raise ValueError(f"pricing CSV missing columns: {sorted(missing)}")

    # Only pull electric rate here; water_dollars_per_kgal is taken from counties_wue_water.csv
    # to avoid column name conflicts during the merge.
    pricing_small = pricing[["state_abbr", "electric_cents_per_kwh"]].drop_duplicates("state_abbr")
    pue_mean = pue_mean.merge(pricing_small, on="state_abbr", how="left")

    # ---- Bring in WUE + effective water (already in ¢/kWh IT) ----
    required_wue_cols = {"county_fips", "county_name", "state_abbr", "AE_WUE_avg (L/kWh)", "WEC_WUE_avg (L/kWh)", "effective_water_AE (¢/kWh IT)", "effective_water_WEC (¢/kWh IT)", "water_dollars_per_kgal ($/kgal)"}
    # Some files may differ slightly in column naming depending on export. We'll map using suffix matching.

    # Robust column mapping for WUE/water columns
    col_map = {}
    for c in wue_water.columns:
        if c == "AE_WUE_avg (L/kWh)":
            col_map["AE_WUE_avg"] = c
        elif c == "WEC_WUE_avg (L/kWh)":
            col_map["WEC_WUE_avg"] = c
        elif c.startswith("effective_water_AE"):
            col_map["effective_water_AE"] = c
        elif c.startswith("effective_water_WEC"):
            col_map["effective_water_WEC"] = c
        elif c.startswith("water_dollars_per_kgal"):
            col_map["water_dollars_per_kgal"] = c

    needed = {"AE_WUE_avg", "WEC_WUE_avg", "effective_water_AE", "effective_water_WEC", "water_dollars_per_kgal"}
    missing = needed - set(col_map.keys())
    if missing:
        raise ValueError(f"counties_wue_water.csv missing expected columns: {sorted(missing)}")

    wue_small = wue_water[[
        "county_fips",
        "county_name",
        "state_abbr",
        col_map["AE_WUE_avg"],
        col_map["WEC_WUE_avg"],
        col_map["water_dollars_per_kgal"],
        col_map["effective_water_AE"],
        col_map["effective_water_WEC"],
    ]].copy()
    wue_small = wue_small.rename(columns={
        col_map["AE_WUE_avg"]: "AE_WUE_avg",
        col_map["WEC_WUE_avg"]: "WEC_WUE_avg",
        col_map["water_dollars_per_kgal"]: "water_dollars_per_kgal",
        col_map["effective_water_AE"]: "effective_water_AE",
        col_map["effective_water_WEC"]: "effective_water_WEC",
    })

    merged = pue_mean.merge(wue_small, on=["county_fips", "county_name", "state_abbr"], how="left")

    # ---- Join drought summary and compute water stress ----
    required_drought_cols = {"county_fips", "mean_drought", "pct_weeks_d2_plus"}
    missing = required_drought_cols - set(drought.columns)
    if missing:
        raise ValueError(f"drought summary CSV missing columns: {sorted(missing)}")

    drought_small = drought[["county_fips", "mean_drought", "pct_weeks_d2_plus"]].copy()
    merged = merged.merge(drought_small, on="county_fips", how="left")
    merged["mean_drought"] = merged["mean_drought"].fillna(0.0)
    merged["pct_weeks_d2_plus"] = merged["pct_weeks_d2_plus"].fillna(0.0)

    # water_stress = WUE × (1 + pct_weeks_d2_plus/100)
    merged["water_stress_AE"] = merged["AE_WUE_avg"] * (1 + merged["pct_weeks_d2_plus"] / 100.0)
    merged["water_stress_WEC"] = merged["WEC_WUE_avg"] * (1 + merged["pct_weeks_d2_plus"] / 100.0)

    # ---- Effective costs (¢/kWh IT) ----
    merged["effective_electric_AE"] = merged["AE_PUE"] * merged["electric_cents_per_kwh"]
    merged["effective_electric_WEC"] = merged["WEC_PUE"] * merged["electric_cents_per_kwh"]
    merged["effective_total_cost_AE"] = merged["effective_electric_AE"] + merged["effective_water_AE"]
    merged["effective_total_cost_WEC"] = merged["effective_electric_WEC"] + merged["effective_water_WEC"]

    # ---- Output long format: one row per county × system ----
    out_rows = []
    for _, r in merged.iterrows():
        for system in ["AE", "WEC"]:
            if system == "AE":
                out_rows.append({
                    "county_fips": r["county_fips"],
                    "county_name": r["county_name"],
                    "state_abbr": r["state_abbr"],
                    "system": "AE",
                    "PUE": r["AE_PUE"],
                    "WUE": r["AE_WUE_avg"],
                    "mean_drought": r["mean_drought"],
                    "pct_weeks_d2_plus": r["pct_weeks_d2_plus"],
                    "water_stress": r["water_stress_AE"],
                    "electric_cents_per_kwh": r["electric_cents_per_kwh"],
                    "water_dollars_per_kgal": r["water_dollars_per_kgal"],
                    "effective_electric": r["effective_electric_AE"],
                    "effective_water": r["effective_water_AE"],
                    "effective_total_cost": r["effective_total_cost_AE"],
                })
            else:
                out_rows.append({
                    "county_fips": r["county_fips"],
                    "county_name": r["county_name"],
                    "state_abbr": r["state_abbr"],
                    "system": "WEC",
                    "PUE": r["WEC_PUE"],
                    "WUE": r["WEC_WUE_avg"],
                    "mean_drought": r["mean_drought"],
                    "pct_weeks_d2_plus": r["pct_weeks_d2_plus"],
                    "water_stress": r["water_stress_WEC"],
                    "electric_cents_per_kwh": r["electric_cents_per_kwh"],
                    "water_dollars_per_kgal": r["water_dollars_per_kgal"],
                    "effective_electric": r["effective_electric_WEC"],
                    "effective_water": r["effective_water_WEC"],
                    "effective_total_cost": r["effective_total_cost_WEC"],
                })

    out_long = pd.DataFrame(out_rows)
    out_long.to_csv(out_cost, index=False)

    # Water-stress-only view (smaller & easier to inspect)
    out_water_df = out_long[[
        "county_fips",
        "county_name",
        "state_abbr",
        "system",
        "WUE",
        "mean_drought",
        "pct_weeks_d2_plus",
        "water_stress",
    ]].copy()
    out_water_df.to_csv(out_water, index=False)

    print(f"Wrote effective cost table: {out_cost} ({len(out_long)} rows)")
    print(f"Wrote water stress table: {out_water} ({len(out_water_df)} rows)")


if __name__ == "__main__":
    main()

