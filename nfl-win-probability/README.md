# NFL Win Probability Model

An in-game win probability model built from play-by-play data. Uses play-level features (score differential, time remaining, field position, down/distance) to predict the probability the team with possession wins the game.

## Overview

This project demonstrates probabilistic sports forecasting for odds origination. Win probability is core to pricing spreads, totals, and live markets. The model evaluates using Brier score, log loss, and calibration—the same metrics used in professional sports analytics.

## Tech Stack

- **Data:** nflverse/nflfastR via nfl_data_py (play-by-play 1999–present)
- **Model:** XGBoost Classifier (probabilistic output)
- **Metrics:** Brier score, log loss, calibration curves

## Project Structure

| File | Description |
|------|-------------|
| `load_and_prepare.py` | Loads play-by-play data, engineers features, creates win/loss labels |
| `train_model.py` | Trains XGBoost model, evaluates with Brier/log loss/calibration |
| `predict.py` | Generates win probabilities for historical games |
| `notebooks/win_probability_model.ipynb` | End-to-end notebook with visualizations |

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Train the model (uses 2022–2023 seasons by default)

```bash
python train_model.py
```

### Generate predictions for a season

```bash
python predict.py --season 2024
```

### Run the full pipeline in Jupyter

Open `notebooks/win_probability_model.ipynb` and run all cells.

## Key Features Engineered

- **Score differential** – current point margin (possession team perspective)
- **Time remaining** – game_seconds_remaining, half_seconds_remaining
- **Field position** – yardline_100 (yards from opponent goal line)
- **Down and distance** – down, ydstogo, goal_to_go
- **Timeout leverage** – posteam_timeouts_remaining vs defteam_timeouts_remaining
- **Possession/context** – home_team, posteam, receive_2h_ko (2nd half kickoff receiver)

## Evaluation Metrics

- **Brier score** – probabilistic forecast accuracy (lower is better)
- **Log loss** – standard for probability models
- **Calibration** – reliability diagram (predicted vs actual win rates by probability bin)

## License

Portfolio project for educational use.
