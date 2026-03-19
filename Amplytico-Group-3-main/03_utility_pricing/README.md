# 03 Utility Pricing Inputs

This folder contains the state-level electricity and water pricing inputs used throughout the project (as stored in the original DuckDB-derived exports).

## Files
- `pricing_by_state.csv`
  State-level averages:
  - `electric_cents_per_kwh`
  - `water_dollars_per_kgal`
  - `region` and state identifiers

- `surge_prices_by_state.csv`
  Severe-drought price increase parameter by state (used in the report’s drought-penalty discussion / pricing methodology).

- `export_pricing_by_state.py`
  Extracts `dim_state_prices` from the project DuckDB into `pricing_by_state.csv`.

