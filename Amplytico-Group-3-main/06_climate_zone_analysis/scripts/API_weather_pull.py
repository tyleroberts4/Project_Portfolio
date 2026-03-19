import time
import requests
import pandas as pd
from pathlib import Path

# Submission-friendly paths: use this submission's included zone points.
_SCRIPT_DIR = Path(__file__).resolve().parent
_DATA_DIR = _SCRIPT_DIR.parent / "data"

POINTS_CSV = _DATA_DIR / "iecc_zone_5points.csv"
OUT_XLSX = _DATA_DIR / "5Points2025ClimateZoneData_v2.xlsx"

YEAR = 2025
DEFAULT_START_DATE = f"{YEAR}-01-01"
DEFAULT_END_DATE = f"{YEAR}-12-31"

# Open-Meteo archive endpoint
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Variables we need
HOURLY_VARS = ["temperature_2m", "relative_humidity_2m", "surface_pressure"]

# Use UTC to avoid timezone/DST issues
TIMEZONE = "UTC"

# Polite retry + backoff
def fetch_open_meteo_hourly(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": TIMEZONE,
    }

    for attempt in range(5):
        r = requests.get(BASE_URL, params=params, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if "hourly" not in data or "time" not in data["hourly"]:
                raise RuntimeError(f"Unexpected response shape for lat={lat}, lon={lon}: {data.keys()}")
            hourly = data["hourly"]
            df = pd.DataFrame({
                "time": hourly["time"],
                "temperature_2m": hourly.get("temperature_2m"),
                "relative_humidity_2m": hourly.get("relative_humidity_2m"),
                "surface_pressure": hourly.get("surface_pressure"),
            })
            df["time"] = pd.to_datetime(df["time"])
            return df

        # backoff on non-200
        sleep_s = 2 ** attempt
        print(f"Request failed ({r.status_code}). Retrying in {sleep_s}s ...")
        time.sleep(sleep_s)

    raise RuntimeError(f"Failed to fetch Open-Meteo after retries for lat={lat}, lon={lon}")


def build_zone_hourly_average(
    zone_points: pd.DataFrame,
    *,
    start_date: str,
    end_date: str,
    delay_seconds: float,
) -> pd.DataFrame:
    """
    zone_points: rows for a single zone with columns zone, sample, lat, lon
    Returns: hourly averaged DF with required columns
    """
    per_point = []
    for _, row in zone_points.iterrows():
        lat, lon = float(row["lat"]), float(row["lon"])
        dfp = fetch_open_meteo_hourly(lat, lon, start_date, end_date)
        per_point.append(dfp.set_index("time"))

        # small delay to be polite to API
        time.sleep(delay_seconds)

    # Align on time and average across points
    stacked = pd.concat(per_point, axis=1, keys=range(len(per_point)))
    # stacked columns become MultiIndex: (point_id, variable)
    avg = stacked.groupby(level=1, axis=1).mean()  # mean across points for each variable

    avg = avg.reset_index()

    # Match your column names exactly
    avg = avg.rename(columns={
        "temperature_2m": "temperature_2m (°C)",
        "relative_humidity_2m": "relative_humidity_2m (%)",
        "surface_pressure": "surface_pressure (hPa)",
    })

    # Ensure column order
    avg = avg[["time", "temperature_2m (°C)", "relative_humidity_2m (%)", "surface_pressure (hPa)"]]

    # avg["time"] = avg["time"].dt.strftime("%Y-%m-%dT%H:%M")

    return avg


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Pull Open-Meteo hourly weather for each climate zone point (submission-friendly).")
    ap.add_argument("--year", type=int, default=YEAR)
    ap.add_argument("--start-date", type=str, default=None, help="YYYY-MM-DD (default: {year}-01-01)")
    ap.add_argument("--end-date", type=str, default=None, help="YYYY-MM-DD (default: {year}-12-31)")
    ap.add_argument("--points-csv", type=Path, default=POINTS_CSV)
    ap.add_argument("--out-xlsx", type=Path, default=OUT_XLSX)
    ap.add_argument("--delay-seconds", type=float, default=0.2)
    args = ap.parse_args()

    year = int(args.year)
    start_date = args.start_date if args.start_date is not None else f"{year}-01-01"
    end_date = args.end_date if args.end_date is not None else f"{year}-12-31"

    points = pd.read_csv(args.points_csv)
    # expected columns: zone, sample, lat, lon
    required_cols = {"zone", "sample", "lat", "lon"}
    missing = required_cols - set(points.columns)
    if missing:
        raise ValueError(f"Points CSV missing columns: {missing}")

    zones = sorted(points["zone"].unique())
    print("Zones found:", zones)

    args.out_xlsx.parent.mkdir(parents=True, exist_ok=True)

    # Write one sheet per zone
    with pd.ExcelWriter(args.out_xlsx, engine="openpyxl", mode="w") as writer:
        for z in zones:
            print(f"\n=== Zone {z} ===")
            zp = points[points["zone"] == z].copy()
            if len(zp) != 5:
                print(f"WARNING: Zone {z} has {len(zp)} points (expected 5). Proceeding anyway.")

            zone_avg = build_zone_hourly_average(
                zp, start_date=start_date, end_date=end_date, delay_seconds=args.delay_seconds
            )

            # Sheet name must be <= 31 chars; your zone names are fine ("1A", etc.)
            sheet_name = str(z)
            zone_avg.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Wrote sheet {sheet_name}: {len(zone_avg)} rows")

    print(f"\nDone. Excel written to: {args.out_xlsx.resolve()}")


if __name__ == "__main__":
    main()
