# 02 Drought Risk (USDM API Integration)

This folder contains the scripts used to pull **county-level weekly drought severity** from the U.S. Drought Monitor API and to clean common dataset issues (week 53 and FIPS formatting).

## Files
- `fetch_drought_weekly_by_county_2024.py`
  - Pulls weekly drought severity statistics by county from the USDM Comprehensive Statistics REST API
  - Outputs a weekly CSV suitable for computing:
    - mean/max drought level (0–5)
    - `% of weeks in D1+` and `% of weeks in D2+` (severe drought)

- `fix_drought_week53.py`
  - Normalizes ISO week 53 to week 52 so week-based aggregations stay consistent across years.

- `fix_drought_fips.py`
  - Fixes/normalizes county FIPS formatting so joins work reliably with other county datasets.

- `add_county_fill_to_drought_csv.py`
  - Adds a deterministic `county_fill_hex` column (mainly for consistent dashboard/table colors).

## Compact summary included in this repo
Because the full weekly drought CSV is large, the submission repo includes the compact output:
`04_analysis_data/drought_summary_by_county.csv`

You can regenerate it from the weekly file (if you have it) using:
`../scripts/build_drought_summary_by_county.py`

## Weekly drought file included
For reviewers who need to run the drought builders without downloading extra data, this submission includes:
`drought_weekly_by_county_2015_2024_week52only_fixed_2.0.csv.gz`

This is the newest week52only version (week 53 already normalized) and is used by default by the drought summary builder.

