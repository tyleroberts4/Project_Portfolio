# scripts

These Python scripts build compact derived tables used in the report.

## Files
- `build_weather_hourly_with_counties_sample.py`  
  Fetches a tiny Open-Meteo weather sample and writes `01_weather_api_and_pue_wue_simulation/weather_hourly_with_counties_sample.csv` so the midpoint scripts can run without the full multi-GB pre-joined weather file.
- `build_drought_summary_by_county.py`  
  Converts the large weekly USDM drought CSV into:
  `04_analysis_data/drought_summary_by_county.csv`

- `build_water_stress_and_effective_costs.py`  
  Combines:
  `county_week_rollup.csv` + `counties_wue_water.csv` + `drought_summary_by_county.csv`
  into:
  - `water_stress_by_county_system.csv`
  - `effective_utility_cost_by_county_system.csv`

