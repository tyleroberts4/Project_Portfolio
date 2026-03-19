
"""
Compute average PUE by climate zone (and system inferred from filename) and write a compact CSV.

Usage examples:
  python make_zone_pue_summary.py AE_hourly_midpoint.csv
  python make_zone_pue_summary.py AE_hourly_midpoint.csv WEC_hourly_midpoint.csv -o zone_pue_summary.csv

Output columns:
  system, zone, avg_pue, n_rows
"""

import argparse
import os
import re
from pathlib import Path

import pandas as pd


def infer_system_from_filename(path: str) -> str:
    name = Path(path).name.lower()
    # tweak these rules if your naming differs
    if "wec" in name:
        return "WEC"
    if "ae" in name:
        return "AE"
    return "UNKNOWN"


def normalize_zone(z) -> str:
    # Keep things like "4B" or "1A" consistent
    if pd.isna(z):
        return None
    s = str(z).strip().upper()
    # common cleanup: remove spaces like "4 B" -> "4B"
    s = re.sub(r"\s+", "", s)
    return s or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="One or more hourly PUE CSVs (AE/WEC).")
    ap.add_argument("-o", "--out", default="zone_pue_summary.csv", help="Output CSV path.")
    ap.add_argument("--zone-col", default="zone", help="Zone column name (default: zone).")
    ap.add_argument("--pue-col", default="PUE", help="PUE column name (default: PUE).")
    args = ap.parse_args()

    summaries = []

    for f in args.files:
        df = pd.read_csv(f)

        # Try to find zone/pue columns robustly (case-insensitive)
        cols_lower = {c.lower(): c for c in df.columns}
        zone_col = cols_lower.get(args.zone_col.lower(), None)
        pue_col = cols_lower.get(args.pue_col.lower(), None)

        if zone_col is None:
            raise ValueError(
                f"Could not find zone column '{args.zone_col}' in {f}. "
                f"Available columns: {list(df.columns)}"
            )
        if pue_col is None:
            raise ValueError(
                f"Could not find PUE column '{args.pue_col}' in {f}. "
                f"Available columns: {list(df.columns)}"
            )

        df = df[[zone_col, pue_col]].copy()
        df["zone"] = df[zone_col].map(normalize_zone)
        df["PUE"] = pd.to_numeric(df[pue_col], errors="coerce")
        df = df.dropna(subset=["zone", "PUE"])

        system = infer_system_from_filename(f)
        g = (
            df.groupby("zone", as_index=False)
            .agg(avg_pue=("PUE", "mean"), n_rows=("PUE", "size"))
        )
        g.insert(0, "system", system)
        summaries.append(g)

    out_df = pd.concat(summaries, ignore_index=True)

    # Sort nicely (system then zone)
    out_df = out_df.sort_values(["system", "zone"]).reset_index(drop=True)

    out_df.to_csv(args.out, index=False)
    print(f"Wrote {len(out_df)} rows to: {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
