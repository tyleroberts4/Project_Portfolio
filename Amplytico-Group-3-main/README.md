# Amplytico Group 3 (Final Submission)

This repo contains the **analysis assets** for Team 3’s report:
**Climate-Aware Optimization of Hyperscale Data Center Cooling Systems**.

It’s intentionally “lean” for GitHub: it keeps the **latest report-relevant scripts + compact outputs**, without the multi-GB raw files used by the full application.

## Quick start (recommended)
Rebuild the compact county-level outputs used in the report:

```bash
python scripts/build_drought_summary_by_county.py
python scripts/build_water_stress_and_effective_costs.py
```

These generate:
- `04_analysis_data/drought_summary_by_county.csv`
- `04_analysis_data/water_stress_by_county_system.csv`
- `04_analysis_data/effective_utility_cost_by_county_system.csv`

## What’s included (by folder)
- `01_weather_api_and_pue_wue_simulation/`: Open-Meteo weather + AE/WEC midpoint simulation scripts + a small sample dataset
- `02_drought_risk/`: US Drought Monitor (USDM) integration + drought cleanup scripts (week 53 handling, FIPS formatting)
- `03_utility_pricing/`: `pricing_by_state.csv` (electric + water rates)
- `04_analysis_data/`: compact rollups + derived tables used directly in the report
- `05_tableau_visuals/`: Tableau workbooks + small supporting images
- `06_climate_zone_analysis/`: climate zone datasets + scripts + sensitivity assets
- `scripts/`: builder scripts (drought summary -> water stress -> effective utility cost)
- `docs/`: blueprints and pipeline documentation
- `PUE_WUE_SIM/` (repo root): simulator core (`simulation_funs_DC.py`) + COP model pickles

## Optional (weather sample)
If you want to regenerate the included weather sample:

```bash
python scripts/build_weather_hourly_with_counties_sample.py
```

## Tableau note
The `*.twb` workbooks may reference absolute paths/extracts from the original workspace. If Tableau asks to reconnect, point it to the compact CSVs in `04_analysis_data/`.

## Related app repo (full tool)
- [Hyperscale Data Center Optimization Tool](https://github.com/matthewkennedy22/Hyperscale-Data-Center-Optimization-Tool)

