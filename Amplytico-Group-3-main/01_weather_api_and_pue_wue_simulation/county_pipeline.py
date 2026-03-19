"""
county_pipeline.py

Reusable county → weather → PUE/WUE pipeline. Returns a DataFrame (no file I/O).
Used by run_county_hourly_midpoint.py (CLI) and the Streamlit dashboard.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Paths (relative to this file)
# -----------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_BASE_DIR = _SCRIPT_DIR.parent
PUE_WUE_SIM = _BASE_DIR.parent / "PUE_WUE_SIM"
if not PUE_WUE_SIM.exists():
    PUE_WUE_SIM = _BASE_DIR / "PUE_WUE_SIM"

OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"


def load_county_centroids(csv_path: Path | str) -> pd.DataFrame:
    """Load county centroids CSV; ensure numeric lat/lon and county_fips_str."""
    df = pd.read_csv(csv_path)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    if "county_fips" in df.columns:
        df["county_fips_str"] = df["county_fips"].astype(str).str.zfill(5)
    return df


def resolve_county(
    centroids: pd.DataFrame,
    county_fips: str | None = None,
    county_name: str | None = None,
    state_fips: str | int | None = None,
) -> tuple[str, str, float, float]:
    """Resolve to (county_fips, county_name, latitude, longitude). Raises ValueError if not found."""
    if county_fips is not None:
        fips_str = str(county_fips).zfill(5)
        row = centroids[centroids["county_fips_str"] == fips_str]
        if len(row) == 0:
            raise ValueError(f"County FIPS not found: {county_fips}")
        r = row.iloc[0]
        return (str(r["county_fips"]), str(r["county_name"]), float(r["latitude"]), float(r["longitude"]))
    if county_name is not None and state_fips is not None:
        sf = str(state_fips).zfill(2)
        name_upper = county_name.strip().upper()
        row = centroids[
            (centroids["county_name"].str.upper() == name_upper)
            & (centroids["state_fips"].astype(str).str.zfill(2) == sf)
        ]
        if len(row) == 0:
            raise ValueError(f"County not found: {county_name}, state_fips={state_fips}")
        if len(row) > 1:
            raise ValueError(f"Multiple counties match: {county_name}, state_fips={state_fips}")
        r = row.iloc[0]
        return (str(r["county_fips"]), str(r["county_name"]), float(r["latitude"]), float(r["longitude"]))
    raise ValueError("Specify either county_fips or (county_name and state_fips)")


def fetch_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Fetch hourly historical weather from Open-Meteo. Columns: time, T_oa_C, RH_pct, P_atm_Pa."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure",
    }
    url = OPEN_METEO_ARCHIVE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "PUE-WUE-Simulator/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.load(resp)
    h = data.get("hourly", {})
    if not h or "time" not in h:
        raise RuntimeError("Weather API returned no hourly data")
    df = pd.DataFrame({
        "time": pd.to_datetime(h["time"]),
        "T_oa_C": h["temperature_2m"],
        "RH_pct": h["relative_humidity_2m"],
        "surface_pressure_hPa": h["surface_pressure"],
    })
    df["P_atm_Pa"] = df["surface_pressure_hPa"] * 100.0
    df = df.drop(columns=["surface_pressure_hPa"])
    return df


def _load_simulator():
    if str(PUE_WUE_SIM) not in sys.path:
        sys.path.insert(0, str(PUE_WUE_SIM))
    orig_cwd = os.getcwd()
    os.chdir(PUE_WUE_SIM)
    import simulation_funs_DC as sim
    os.chdir(orig_cwd)
    return sim


_sim = None


def get_sim():
    global _sim
    if _sim is None:
        _sim = _load_simulator()
    return _sim


# AE 32-param midpoints
_AE_BOUNDS = [
    [-10, 40], [0, 100], [101325 * 0.9, 101325 * 1.1],
    [0.90, 0.99], [0.00, 0.02], [0.00, 0.002],
    [25 * 5 / 9, 35 * 5 / 9], [300, 700], [0.65, 0.90],
    [7_000_000 * 0.9, 7_000_000 * 1.1], [0.6, 0.8],
    [2.8, 6.7], [0.2, 0.8], [5, 10],
    [143_658 * 0.8, 143_658 * 1.2], [0.6, 0.8],
    [4, 6], [208_660 * 0.8, 208_660 * 1.2], [0.6, 0.8],
    [0.005 / 100, 0.5 / 100], [3.0, 15.0],
    [100, 400], [0.65, 0.90], [0.95, 0.99], [0.2, 4],
    [27, 35], [10, 18], [15, 27], [-12, -9], [0.60, 0.90], [0.08, 0.20],
    [-0.11, 0.11],
]
_AE_MIDPOINTS = np.array([(b[0] + b[1]) / 2 for b in _AE_BOUNDS])


def build_w_ae(T_oa: float, RH_oa: float, P_oa: float) -> np.ndarray:
    w = _AE_MIDPOINTS.copy().astype(float)
    w[0], w[1], w[2] = T_oa, RH_oa, P_oa
    return w


# WEC 36-param midpoints
_WEC_BOUNDS = [
    [-10, 40], [0, 100], [101325 * 0.9, 101325 * 1.1],
    [0.90, 0.99], [0.00, 0.02], [0.00, 0.002], [0.95, 0.99], [25 * 5 / 9, 35 * 5 / 9],
    [300, 700], [0.65, 0.90],
    [7_000_000 * 0.9, 7_000_000 * 1.1], [0.6, 0.8],
    [0.7, 0.9], [5, 10], [2.8, 6.7], [1.7, 2.8],
    [114_900, 172_400], [0.6, 0.8],
    [143_658 * 0.8, 143_658 * 1.2], [0.6, 0.8],
    [0.2, 0.8], [4, 6], [208_660 * 0.8, 208_660 * 1.2], [0.6, 0.8],
    [0.005 / 100, 0.5 / 100], [3.0, 15.0], [0.2, 4],
    [100, 400], [0.65, 0.90],
    [27, 35], [10, 18], [15, 27], [-12, -9], [0.60, 0.90], [0.08, 0.20],
    [-0.11, 0.11],
]
_WEC_MIDPOINTS = np.array([(b[0] + b[1]) / 2 for b in _WEC_BOUNDS])


def build_w_wec(T_oa: float, RH_oa: float, P_oa: float) -> np.ndarray:
    w = _WEC_MIDPOINTS.copy().astype(float)
    w[0], w[1], w[2] = T_oa, RH_oa, P_oa
    return w


def run_county(
    county_fips: str,
    start_date: str,
    end_date: str,
    *,
    system: str = "both",
    centroids_df: pd.DataFrame | None = None,
    centroids_path: Path | str | None = None,
    max_hours: int | None = None,
) -> pd.DataFrame:
    """
    Run the full pipeline for one county and return a DataFrame with columns:
    county_fips, county_name, latitude, longitude, hour, time, T_oa, RH_oa, P_oa, system, PUE, WUE.

    system: "AE", "WEC", or "both".
    Provide either centroids_df (e.g. from dashboard) or centroids_path to resolve the county.
    """
    if centroids_df is None:
        if centroids_path is None:
            # In the original repo this default pointed at a local Downloads path; here we default
            # to the submission dataset (04_analysis_data/county_centroids.csv).
            _default = _SCRIPT_DIR.parent / "04_analysis_data" / "county_centroids.csv"
            for candidate in [
                _default,
                _SCRIPT_DIR / "us_county_centroids.csv",
                Path.home() / "us_county_centroids.csv",
            ]:
                if Path(candidate).exists():
                    centroids_path = candidate
                    break
            else:
                raise FileNotFoundError("No centroids file found; set centroids_path or centroids_df")
        centroids_df = load_county_centroids(centroids_path)

    county_fips, county_name, lat, lon = resolve_county(centroids_df, county_fips=county_fips)
    weather_df = fetch_historical_weather(lat, lon, start_date, end_date)
    n_hours = min(len(weather_df), max_hours) if max_hours else len(weather_df)
    if n_hours == 0:
        return pd.DataFrame()

    sim = get_sim()
    run_ae = system in ("AE", "both")
    run_wec = system in ("WEC", "both")
    base_cols = ["county_fips", "county_name", "latitude", "longitude", "hour", "time", "T_oa", "RH_oa", "P_oa"]
    rows = []

    if run_ae:
        for h in range(n_hours):
            row = weather_df.iloc[h]
            T_oa, RH_oa, P_oa = float(row["T_oa_C"]), float(row["RH_pct"]), float(row["P_atm_Pa"])
            w = build_w_ae(T_oa, RH_oa, P_oa)
            try:
                pue, wue = sim.PUE_WUE_AE_Chiller(w)
                if np.isfinite(pue) and np.isfinite(wue):
                    rows.append({
                        **dict(zip(base_cols, [county_fips, county_name, lat, lon, h, row["time"], T_oa, RH_oa, P_oa])),
                        "system": "AE", "PUE": float(pue), "WUE": float(wue),
                    })
            except Exception:
                pass

    if run_wec:
        for h in range(n_hours):
            row = weather_df.iloc[h]
            T_oa, RH_oa, P_oa = float(row["T_oa_C"]), float(row["RH_pct"]), float(row["P_atm_Pa"])
            w = build_w_wec(T_oa, RH_oa, P_oa)
            try:
                pue, wue = sim.PUE_WUE_Chiller_Watereconomier(w)
                if np.isfinite(pue) and np.isfinite(wue):
                    rows.append({
                        **dict(zip(base_cols, [county_fips, county_name, lat, lon, h, row["time"], T_oa, RH_oa, P_oa])),
                        "system": "WEC", "PUE": float(pue), "WUE": float(wue),
                    })
            except Exception:
                pass

    return pd.DataFrame(rows)
