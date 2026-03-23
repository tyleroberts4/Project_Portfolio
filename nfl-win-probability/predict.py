"""
Generate win probabilities for NFL plays using the trained model.
"""

import argparse
import pickle
from pathlib import Path

import pandas as pd

from load_and_prepare import load_pbp_data, get_game_outcomes, prepare_features

MODEL_DIR = Path(__file__).parent / "models"
FEATURE_COLS = [
    "score_diff",
    "game_seconds_remaining",
    "half_seconds_remaining",
    "yardline_100",
    "down",
    "ydstogo",
    "goal_to_go",
    "timeout_diff",
    "is_home",
]


def load_model():
    """Load trained model from disk."""
    model_path = MODEL_DIR / "win_prob_model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run train_model.py first."
        )
    with open(model_path, "rb") as f:
        obj = pickle.load(f)
    return obj["model"], obj["features"]


def predict_season(season: int) -> pd.DataFrame:
    """Load season data, prepare features, return predictions."""
    pbp = load_pbp_data(season)
    outcomes = get_game_outcomes(pbp)
    df = prepare_features(pbp, outcomes)

    model, features = load_model()
    X = df[features]
    df["win_probability"] = model.predict_proba(X)[:, 1]

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate NFL win probabilities")
    parser.add_argument("--season", type=int, default=2024, help="Season year")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    df = predict_season(args.season)
    out_path = args.output or Path(__file__).parent / "data" / f"predictions_{args.season}.csv"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df):,} predictions to {out_path}")


if __name__ == "__main__":
    main()
