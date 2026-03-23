"""
Compare model predictions to Vegas lines: MAE, hit rate, value identification.
"""

from pathlib import Path

import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).parent / "data"


def main():
    pred_path = DATA_DIR / "predictions.csv"
    if not pred_path.exists():
        from train_spread_total import main as train_main
        train_main()

    df = pd.read_csv(pred_path)

    has_vegas = "vegas_spread" in df.columns and "vegas_total" in df.columns
    if not has_vegas:
        print("Vegas lines (vegas_spread, vegas_total) not found in data.")
        print("nflverse schedule data includes these for recent seasons.")
        print("Model metrics (without Vegas comparison):")
        print(f"  Spread MAE: {np.abs(df['margin'] - df['pred_margin']).mean():.2f}")
        print(f"  Total MAE:  {np.abs(df['total'] - df['pred_total']).mean():.2f}")
        return

    df = df.dropna(subset=["vegas_spread", "vegas_total"])

    # Spread: Vegas uses negative for home favored, our pred_spread = -pred_margin
    spread_mae_model = np.abs(df["margin"] - df["pred_margin"]).mean()
    spread_mae_vegas = np.abs(df["margin"] - (-df["vegas_spread"])).mean()
    spread_hit_model = (np.sign(df["margin"] + df["pred_spread"]) == np.sign(df["pred_spread"])).mean()
    spread_hit_vegas = (np.sign(df["margin"] + df["vegas_spread"]) == np.sign(df["vegas_spread"])).mean()

    # Total
    total_mae_model = np.abs(df["total"] - df["pred_total"]).mean()
    total_mae_vegas = np.abs(df["total"] - df["vegas_total"]).mean()

    print("=== Spread Comparison ===")
    print(f"Model MAE:  {spread_mae_model:.2f}  Hit rate: {spread_hit_model:.1%}")
    print(f"Vegas MAE:  {spread_mae_vegas:.2f}  Hit rate: {spread_hit_vegas:.1%}")
    print()
    print("=== Total Comparison ===")
    print(f"Model MAE:  {total_mae_model:.2f}")
    print(f"Vegas MAE:  {total_mae_vegas:.2f}")

    # Value: model disagrees with Vegas by >= 3 points
    df["spread_diff"] = df["pred_spread"] - df["vegas_spread"]
    df["total_diff"] = df["pred_total"] - df["vegas_total"]
    value_spread = df[np.abs(df["spread_diff"]) >= 3]
    value_total = df[np.abs(df["total_diff"]) >= 3]
    print()
    print("=== Value Games (model disagrees with Vegas by 3+ points) ===")
    print(f"Spread: {len(value_spread)} games")
    print(f"Total:  {len(value_total)} games")
    if len(value_spread) > 0:
        value_spread.to_csv(DATA_DIR / "value_spread.csv", index=False)
        print(f"Saved value spread games to {DATA_DIR / 'value_spread.csv'}")


if __name__ == "__main__":
    main()
