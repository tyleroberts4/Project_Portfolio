"""
Train XGBoost models for spread and total prediction.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

DATA_DIR = Path(__file__).parent / "data"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

FEATURE_COLS = ["home_off_ppg", "home_def_ppg", "away_off_ppg", "away_def_ppg", "rest_diff", "off_diff", "def_diff"]


def main():
    feats_path = DATA_DIR / "game_features.csv"
    if not feats_path.exists():
        from build_team_features import main as build_main
        build_main()

    df = pd.read_csv(feats_path).dropna(subset=FEATURE_COLS + ["margin", "total"])
    X = df[FEATURE_COLS]
    y_spread = df["margin"].values
    y_total = df["total"].values

    # Train spread model (regression)
    spread_model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    spread_model.fit(X, y_spread)
    df["pred_margin"] = spread_model.predict(X)
    df["pred_spread"] = -df["pred_margin"]

    # Train total model
    total_model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    total_model.fit(X, y_total)
    df["pred_total"] = total_model.predict(X)

    # Metrics
    spread_mae = np.abs(df["margin"] - df["pred_margin"]).mean()
    total_mae = np.abs(df["total"] - df["pred_total"]).mean()
    spread_hit = (np.sign(df["margin"] + df["pred_spread"]) == np.sign(df["pred_spread"])).mean()
    print(f"Spread MAE: {spread_mae:.2f}")
    print(f"Total MAE:  {total_mae:.2f}")
    print(f"Spread hit rate (covered): {spread_hit:.1%}")

    import pickle
    with open(MODEL_DIR / "spread_model.pkl", "wb") as f:
        pickle.dump({"model": spread_model, "features": FEATURE_COLS}, f)
    with open(MODEL_DIR / "total_model.pkl", "wb") as f:
        pickle.dump({"model": total_model, "features": FEATURE_COLS}, f)
    df.to_csv(DATA_DIR / "predictions.csv", index=False)
    print(f"Models and predictions saved to {MODEL_DIR}")


if __name__ == "__main__":
    main()
