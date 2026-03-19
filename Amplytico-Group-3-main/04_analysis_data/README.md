# 04 Analysis Data (Compact, Report-Relevant CSVs)

These CSV files are the **report inputs** and **derived outputs** used to compute:
- drought exposure (summary)
- water stress metric
- effective electric/water costs and effective utility cost rankings

## Included raw/rollup datasets
- `county_week_rollup.csv`  
  County x ISO week (2024) weekly means for:
  - `AE_PUE`, `AE_WUE`, `WEC_PUE`, `WEC_WUE`

- `county_month_rollup.csv`  
  County x month (2024) means for the same PUE/WUE columns.

- `counties_wue_water.csv`  
  County-level averages and effective water cost components:
  - `AE_WUE_avg (L/kWh)`, `WEC_WUE_avg (L/kWh)`
  - `water_dollars_per_kgal ($/kgal)`
  - `effective_water_AE (¢/kWh IT)`, `effective_water_WEC (¢/kWh IT)`

- Lookup tables used for joins/labels:
  - `counties.csv` (county_name + state_abbr)
  - `county_centroids.csv` (latitude/longitude for Open-Meteo)
  - `county_fips_name_state_zone.csv` (zone mapping + identifiers)

## Derived outputs included (small)
- `drought_summary_by_county.csv`  
  County-level drought exposure over the 10-year window:
  - `mean_drought`
  - `pct_weeks_d1_plus`
  - `pct_weeks_d2_plus` (severe drought)

- `water_stress_by_county_system.csv`  
  Water stress per county and system:
  - `water_stress = WUE × (1 + pct_weeks_d2_plus/100)`

- `effective_utility_cost_by_county_system.csv`  
  Effective utility cost per county and system:
  - `effective_total_cost = effective_electric + effective_water` (both in ¢/kWh IT)

