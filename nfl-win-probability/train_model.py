"""
Train NFL win probability model and evaluate with Brier score, log loss, calibration.
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.calibration import calibration_curve
from sklearn.model_selection import GroupKFold
import xgboost as xgb

# Try importing load_and_prepare, fallback to loading CSV
DATA_DIR = Path(__file__).parent / "data"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

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


def load_or_prepare_data():
    """Load prepared features CSV or run load_and_prepare."""
    csv_path = DATA_DIR / "win_prob_features.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    print("Prepared data not found. Running load_and_prepare...")
    from load_and_prepare import main
    main()
    return pd.read_csv(csv_path)


def train_and_evaluate():
    """Train XGBoost model with game-level cross-validation, evaluate metrics."""
    df = load_or_prepare_data()
    df = df.dropna(subset=FEATURE_COLS + ["label"])

    X = df[FEATURE_COLS]
    y = df["label"].values
    groups = df["game_id"].values

    # GroupKFold: keep all plays from same game in same fold (no leakage)
    gkf = GroupKFold(n_splits=5)
    brier_scores = []
    log_losses = []
    models = []

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(X_train, y_train)

        proba = model.predict_proba(X_val)[:, 1]
        brier_scores.append(brier_score_loss(y_val, proba))
        log_losses.append(log_loss(y_val, proba))
        models.append(model)

    # Final model on all data
    final_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    final_model.fit(X, y)

    # Cross-validation metrics
    print("\n=== Cross-Validation Results ===")
    print(f"Brier score (mean): {np.mean(brier_scores):.4f} (+/- {np.std(brier_scores):.4f})")
    print(f"Log loss (mean):   {np.mean(log_losses):.4f} (+/- {np.std(log_losses):.4f})")

    # Calibration on holdout (use last fold)
    _, val_idx = list(gkf.split(X, y, groups))[-1]
    proba_val = final_model.predict_proba(X.iloc[val_idx])[:, 1]
    y_val = y[val_idx]
    fraction_of_positives, mean_predicted_value = calibration_curve(y_val, proba_val, n_bins=10)
    cal_df = pd.DataFrame({
        "mean_predicted_value": mean_predicted_value,
        "fraction_of_positives": fraction_of_positives,
    })
    cal_path = MODEL_DIR / "calibration.csv"
    cal_df.to_csv(cal_path, index=False)
    print(f"\nCalibration curve saved to {cal_path}")

    # Save model
    model_path = MODEL_DIR / "win_prob_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": final_model, "features": FEATURE_COLS}, f)
    print(f"Model saved to {model_path}")

    return final_model, np.mean(brier_scores), np.mean(log_losses)


if __name__ == "__main__":
    train_and_evaluate()
