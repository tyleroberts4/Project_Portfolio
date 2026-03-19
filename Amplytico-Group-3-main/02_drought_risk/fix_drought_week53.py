#!/usr/bin/env python3
"""
fix_drought_week53.py

Fix week-53 in an existing drought weekly CSV so aggregations by (county, week_number)
are consistent. Only some years have ISO week 53 (e.g. 2015, 2016, 2020, 2021), so
averaging by week_number gives week 53 only 4 data points vs 10 for other weeks.

Options:
  --normalize-week53   Map week 53 -> 52 (keep rows; "last week of year" = 52).
  --drop-week53        Drop all week 53 rows (each county/year then has 52 weeks).

Usage:
  python fix_drought_week53.py --input drought_weekly_by_county_2015_2024.csv --output drought_weekly_by_county_2015_2024_fixed.csv --normalize-week53
  python fix_drought_week53.py -i drought_weekly_by_county_2015_2024.csv -o fixed.csv --drop-week53
"""

import argparse
import csv
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="Fix week 53 in drought weekly CSV")
    p.add_argument("--input", "-i", type=Path, required=True, help="Input drought CSV")
    p.add_argument("--output", "-o", type=Path, required=True, help="Output CSV (fixed)")
    p.add_argument("--normalize-week53", action="store_true", help="Set week_number 53 -> 52")
    p.add_argument("--drop-week53", action="store_true", help="Remove rows with week_number 53")
    args = p.parse_args()

    if not args.normalize_week53 and not args.drop_week53:
        p.error("Use --normalize-week53 or --drop-week53")

    inp = args.input.resolve()
    out = args.output.resolve()
    if not inp.is_file():
        raise FileNotFoundError(inp)

    with open(inp, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fieldnames = r.fieldnames

    if "week_number" not in fieldnames:
        print("No week_number column; copying file as-is.")
        out.write_bytes(inp.read_bytes())
        return

    week_col = "week_number"
    fixed = 0
    out_rows = []
    for row in rows:
        try:
            w = int(float(row[week_col]))
        except (TypeError, ValueError):
            out_rows.append(row)
            continue
        if w == 53:
            if args.drop_week53:
                continue
            if args.normalize_week53:
                row = dict(row)
                row[week_col] = 52
                fixed += 1
        out_rows.append(row)

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {out}")
    if args.normalize_week53:
        print(f"  Normalized {fixed} week-53 rows to week 52")
    if args.drop_week53:
        print(f"  Dropped week-53 rows (removed {len(rows) - len(out_rows)})")


if __name__ == "__main__":
    main()
