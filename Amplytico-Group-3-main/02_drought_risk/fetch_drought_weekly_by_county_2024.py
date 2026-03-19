#!/usr/bin/env python3
"""
fetch_drought_weekly_by_county_2024.py

Wrangle weekly average drought statistics (drought level) for each county in the
continental U.S., using the U.S. Drought Monitor Comprehensive Statistics REST API.
Supports a single year (e.g. 2024) or the last 10 years (~3,100 counties × ~52 weeks × 10 years).

  API docs: https://droughtmonitor.unl.edu/DmData/DataDownload/WebServiceInfo.aspx
  API limit: max 1 year per request, so 10 years = 10 requests per state.

Output CSV columns:
  county_fips, week_end_date, year, week_number,
  pct_none, pct_d0, pct_d1, pct_d2, pct_d3, pct_d4, drought_level_avg

  drought_level_avg = weighted average 0–5 (0=None, 1=D0, …, 5=D4) from % area.

Continental US = exclude AK, HI, PR, VI, GU, AS, MP. DC included.

Usage:
  python fetch_drought_weekly_by_county_2024.py --output drought_weekly_by_county_2024.csv
  python fetch_drought_weekly_by_county_2024.py --years 10 --output drought_weekly_by_county_10yr.csv
  python fetch_drought_weekly_by_county_2024.py --start-year 2015 --end-year 2024 -o drought_10yr.csv
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Continental US state abbreviations (exclude AK, HI, territories)
CONTINENTAL_STATES = [
    "AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE",
    "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

BASE_URL = "https://usdmdataservices.unl.edu/api/CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent"


def fetch_state_county_drought(state_abbr: str, start_date: str, end_date: str, fmt: str = "json") -> str:
    """Fetch county drought % area for one state. Returns response body as string."""
    import urllib.request
    import urllib.error

    params = f"aoi={state_abbr}&startdate={start_date}&enddate={end_date}&statisticsType=1"
    url = f"{BASE_URL}?{params}"
    req = urllib.request.Request(url)
    if fmt == "json":
        req.add_header("Accept", "application/json")
    else:
        req.add_header("Accept", "text/csv")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def parse_csv_response(text: str) -> list[dict]:
    """Parse USDM CSV into list of dicts. Handle varying column names (MapDate, FIPS, D0, D1, ...)."""
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def parse_json_response(text: str) -> list[dict]:
    """Parse USDM JSON into list of dicts (flat rows)."""
    data = json.loads(text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "Table" in data:
        return data["Table"]
    if isinstance(data, dict):
        return [data]
    return []


def normalize_row(row: dict) -> dict | None:
    """
    Normalize a raw API row to standard keys: county_fips, week_end_date, pct_none, pct_d0, ..., pct_d4.
    Return None if row doesn't have required fields.
    """
    # Common API column name variants (case-insensitive)
    key_map = {}
    for k in row.keys():
        k_lower = k.lower()
        if "fips" in k_lower or k_lower == "fips":
            key_map[k] = "county_fips"
        elif "mapdate" in k_lower or "date" in k_lower and "week" in k_lower:
            key_map[k] = "week_end_date"
        elif k_lower in ("none", "d0", "d1", "d2", "d3", "d4"):
            key_map[k] = f"pct_{k_lower}"
        elif k_lower.startswith("d0") or "abnormally dry" in k_lower:
            key_map[k] = "pct_d0"
        elif k_lower.startswith("d1"):
            key_map[k] = "pct_d1"
        elif k_lower.startswith("d2"):
            key_map[k] = "pct_d2"
        elif k_lower.startswith("d3"):
            key_map[k] = "pct_d3"
        elif k_lower.startswith("d4"):
            key_map[k] = "pct_d4"

    out = {}
    for orig, new in key_map.items():
        val = row.get(orig)
        if val is not None and val != "":
            try:
                out[new] = float(val)
            except (TypeError, ValueError):
                out[new] = val

    # Require at least FIPS and a date
    if "county_fips" not in out:
        # Try to find FIPS in raw keys
        for k, v in row.items():
            if "fips" in k.lower() and v is not None:
                out["county_fips"] = str(v).strip().zfill(5) if str(v).isdigit() else str(v)
                break
    if "week_end_date" not in out:
        for k, v in row.items():
            if "date" in k.lower() and v:
                out["week_end_date"] = str(v).split("T")[0] if "T" in str(v) else str(v)
                break

    if "county_fips" not in out or "week_end_date" not in out:
        return None

    # Ensure 5-digit FIPS (API sometimes returns 9011 instead of 09011)
    fips = str(out["county_fips"]).strip()
    if "." in fips:
        fips = fips.split(".")[0]
    if fips.isdigit():
        out["county_fips"] = fips.zfill(5)

    # Normalize week_end_date to YYYY-MM-DD
    we = out.get("week_end_date")
    if we and "T" in str(we):
        out["week_end_date"] = str(we).split("T")[0]

    # Percent columns (may be named D0, D1, ... or pct_*)
    for i in range(5):
        dkey = f"pct_d{i}"
        if dkey not in out and f"D{i}" in row:
            try:
                out[dkey] = float(row[f"D{i}"])
            except (TypeError, ValueError):
                out[dkey] = 0.0
    if "pct_none" not in out and "None" in row:
        try:
            out["pct_none"] = float(row["None"])
        except (TypeError, ValueError):
            out["pct_none"] = 0.0

    return out


def compute_drought_level_avg(row: dict) -> float:
    """Weighted average drought level 0–5 from percent area in None, D0–D4."""
    pct_none = float(row.get("pct_none", 0) or 0)
    pct_d0 = float(row.get("pct_d0", 0) or 0)
    pct_d1 = float(row.get("pct_d1", 0) or 0)
    pct_d2 = float(row.get("pct_d2", 0) or 0)
    pct_d3 = float(row.get("pct_d3", 0) or 0)
    pct_d4 = float(row.get("pct_d4", 0) or 0)
    total = pct_none + pct_d0 + pct_d1 + pct_d2 + pct_d3 + pct_d4
    if total <= 0:
        return float("nan")
    # 0=None, 1=D0, 2=D1, 3=D2, 4=D3, 5=D4
    level = (0 * pct_none + 1 * pct_d0 + 2 * pct_d1 + 3 * pct_d2 + 4 * pct_d3 + 5 * pct_d4) / total
    return round(level, 4)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch weekly county drought statistics (continental US, 1 or 10 years)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output CSV path (default: drought_weekly_by_county_2024.csv or _10yr.csv if --years 10)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Request format from API (default: json)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=1,
        help="Number of years to fetch (default: 1). E.g. 10 for last 10 years. Uses --end-year as last year.",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=None,
        help="First year (overrides --years). E.g. 2015",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2024,
        help="Last year (default: 2024)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds between API calls (default: 0.5)",
    )
    parser.add_argument(
        "--states",
        default=None,
        help="Comma-separated state abbreviations to limit (default: all continental)",
    )
    parser.add_argument(
        "--normalize-week53",
        action="store_true",
        help="Map week 53 to week 52 so every year has 1–52 only (avoids weird aggs; only some years have ISO week 53).",
    )
    args = parser.parse_args()

    end_year = args.end_year
    if args.start_year is not None:
        start_year = args.start_year
    else:
        start_year = end_year - args.years + 1
    start_year = max(2015, start_year)  # API history limit
    years = list(range(start_year, end_year + 1))

    if args.output is not None:
        out_path = args.output.resolve()
    else:
        base = Path(__file__).resolve().parent.parent
        out_path = (base / f"drought_weekly_by_county_{start_year}_{end_year}.csv").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    states = [s.strip().upper() for s in args.states.split(",")] if args.states else CONTINENTAL_STATES
    out_columns = [
        "county_fips", "week_end_date", "year", "week_number",
        "pct_none", "pct_d0", "pct_d1", "pct_d2", "pct_d3", "pct_d4",
        "drought_level_avg",
    ]
    all_rows: list[dict] = []

    total_calls = len(states) * len(years)
    call_num = 0
    for year in years:
        start_date = f"1/1/{year}"
        end_date = f"12/31/{year}"
        for i, state in enumerate(states):
            call_num += 1
            print(f"[{call_num}/{total_calls}] {state} {year}...", flush=True)
            try:
                body = fetch_state_county_drought(state, start_date, end_date, args.format)
            except Exception as e:
                print(f"  ERROR {state} {year}: {e}", file=sys.stderr)
                continue

            if args.format == "json":
                raw = parse_json_response(body)
            else:
                raw = parse_csv_response(body)

            for r in raw:
                norm = normalize_row(r)
                if norm is None:
                    continue
                norm["drought_level_avg"] = compute_drought_level_avg(norm)
                for c in ["pct_none", "pct_d0", "pct_d1", "pct_d2", "pct_d3", "pct_d4"]:
                    norm.setdefault(c, 0.0)
                # Add year and week number for easier joining
                we = norm.get("week_end_date", "")
                norm["year"] = year
                if we:
                    try:
                        dt = datetime.strptime(we[:10], "%Y-%m-%d")
                        norm["week_number"] = dt.isocalendar()[1]
                    except Exception:
                        norm["week_number"] = ""
                else:
                    norm["week_number"] = ""
                if args.normalize_week53 and norm.get("week_number") == 53:
                    norm["week_number"] = 52
                all_rows.append({k: norm.get(k) for k in out_columns})

            time.sleep(args.delay)

    # Dedupe by (county_fips, week_end_date, year); keep last
    seen = set()
    unique = []
    for r in reversed(all_rows):
        key = (r.get("county_fips"), r.get("week_end_date"), r.get("year"))
        if key not in seen:
            seen.add(key)
            unique.append(r)
    all_rows = list(reversed(unique))

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {out_path}")
    if all_rows:
        counties = len({r["county_fips"] for r in all_rows})
        weeks = len({(r["week_end_date"], r.get("year")) for r in all_rows})
        print(f"  Counties: {counties}, distinct (week_end_date, year): {weeks}")


if __name__ == "__main__":
    main()
