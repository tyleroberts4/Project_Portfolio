# 01 Weather API + PUE/WUE Simulation

This folder contains the **Open-Meteo weather integration** and the scripts that run the **AE (airside economizer)** and **WEC (waterside economizer)** PUE/WUE simulator.

## Files
- `county_pipeline.py`  
  Core reusable pipeline:
  - fetches hourly historical weather from Open-Meteo (`archive-api.open-meteo.com`)
  - maps weather inputs into AE/WEC midpoint parameter vectors
  - runs `simulation_funs_DC.py` to compute PUE/WUE per hour
  - defaults to centroids from `../04_analysis_data/county_centroids.csv` (use `--centroids` / `centroids_path` to override)

- `run_county_hourly_midpoint.py`  
  CLI wrapper around `county_pipeline.run_county()` for a single county + date range.

- `run_weather_hourly_with_counties_midpoint.py`  
  Computes AE/WEC PUE/WUE for a **pre-joined** hourly dataset `weather_hourly_with_counties.csv` (one row per county-hour).
  The submission repo includes a tiny `weather_hourly_with_counties_sample.csv` so the script can run without downloading the full dataset.

- `run_weather_parallel_by_county.py`  
  Parallelizes `run_weather_hourly_with_counties_midpoint.py` by `county_fips` (writes one CSV per county).

## Simulator core (required by `county_pipeline.py`)
- `PUE_WUE_SIM/` (repo root)  
  Contains:
  - `simulation_funs_DC.py`
  - `COP_2.pkl`, `COP_DX.pkl`, `COP_AC.pkl` model pickles

