# 06 Climate Zone Analysis

This folder contains the **climate zone-level** datasets, scripts, and Tableau workbooks used for report sections:
- **Section 5:** Climate zone analysis (15 IECC zones; zone weather patterns + zone PUE simulation)
- **Section 6:** Sensitivity analysis (Sobol-style sensitivity results for key drivers)

## Contents

### `data/` (zone-level datasets)
- `zone_pue_summary.csv`  
  Annual average PUE by cooling system (`AE`/`WEC`) and IECC zone.
- `WEC_midpoint_percentile_by_zone.csv`  
  WEC midpoint percentile distribution by zone (plus P05/P50/P95).
- `iecc_zone_centroids.csv`, `iecc_zone_5points.csv`  
  Zone representative points used for weather queries and zone-level simulations.
- `iecc_zones.geojson`  
  Geometry for mapping the IECC climate zones.
- `ClimateZones_County_ Final.csv`  
  County-to-climate-zone mapping used for linking the zone layer to county views.
- `Zone*_2025_with_PUE.csv`  
  Hourly PUE time series by zone for each IECC zone (`Zone1A_2025_with_PUE.csv`, ...).

### `scripts/` (how the inputs/outputs were generated)
- `ClimateZoningPythonScripts/API_weather_pull.py`  
  Open-Meteo weather pull logic used to populate zone/weather series.
- `ClimateZoningPythonScripts/climate_zones_gis.py`  
  GIS logic for mapping/generating zone geometry/assignments.
- `PUE Electricity Analysis/pue_avg_by_zone.py`  
  Computes zone-level average PUE from hourly zone series.
- `PUE Electricity Analysis/era5_lat_long_grid.py.py`  
  Helpers for lat/long grid selection for climate zone sampling.

### `tableau/` (report workbooks)
- `CountyClimateData.twb`  
  Zone/county climate zone visuals.
- `CLIMATE ZONE COMPARISONS.twb`  
  Cross-zone comparisons used in the report figures.
- `Temperature Data.twb`  
  Climate/temperature distributions used to explain weather impacts.
- `AllZonesSensitivityAnalysis_AE_CLean.twb`, `AllZonesSensitivityAnalysis_WEC_Clean.twb`  
  Sobol sensitivity visualizations for AE and WEC.

### `sensitivity/` (Sobol numeric summaries + figures)
- Copies of `sobol_WUE_AE_full/*` and `sobol_WUE_WEC_full/*` (CSV + PNGs) used for WUE sensitivity results.

