# NFL Spread and Total Prediction Model

Pre-game prediction of point spreads and totals, with comparison to Vegas opening and closing lines. Identifies potential value where the model disagrees with the market.

## Overview

Demonstrates **odds origination**—producing your own numbers rather than consuming them. Uses team-level features (offensive/defensive efficiency, rest, situational factors) to predict game margins and totals.

## Data Sources

- **nflverse/nfl_data_py** – Schedules, scores, game outcomes
- **Lines** – Provide a CSV with columns: `game_id`, `season`, `week`, `home_team`, `away_team`, `spread_line`, `total_line`, `home_score`, `away_score` (or use the Kaggle dataset [NFL scores and betting data](https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data))

## Project Structure

| File | Description |
|------|-------------|
| `load_schedules.py` | Load NFL schedules and results from nflverse |
| `build_team_features.py` | Compute rolling off/def efficiency, rest days |
| `train_spread_total.py` | Train XGBoost models for spread and total |
| `compare_to_vegas.py` | MAE, hit rate, value identification vs Vegas |
| `data/sample_lines.csv` | Sample lines format (add your data) |

## Setup

```bash
pip install -r requirements.txt
```

## Usage

1. **Download lines data** (e.g. from Kaggle) and place in `data/lines.csv` with the expected schema.

2. **Build features and train:**
   ```bash
   python build_team_features.py
   python train_spread_total.py
   ```

3. **Compare to Vegas:**
   ```bash
   python compare_to_vegas.py
   ```

## Outputs

- Spread MAE and hit rate vs Vegas
- Total MAE and over/under hit rate
- "Value" games where model disagrees with market by a threshold
