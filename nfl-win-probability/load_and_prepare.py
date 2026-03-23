"""
Load NFL play-by-play data and prepare features for win probability modeling.

Uses nflverse/nflfastR data via nfl_data_py. Engineers play-level features
(score differential, time, field position, down/distance) and creates
binary labels: did the team with possession win the game?
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_pbp_data(seasons: list[int] | int) -> pd.DataFrame:
    """Load play-by-play data from nflverse."""
    try:
        import nfl_data_py as nfl
    except ImportError:
        raise ImportError(
            "nfl_data_py is required. Install with: pip install nfl_data_py"
        )

    if isinstance(seasons, int):
        seasons = [seasons]

    print(f"Loading play-by-play data for seasons {seasons}...")
    df = nfl.import_pbp_data(seasons, downcast=True, cache=True)
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()

    return df


def get_game_outcomes(pbp: pd.DataFrame) -> pd.DataFrame:
    """Get final score and winner for each game."""
    last_plays = pbp.sort_values(["game_id", "play_id"]).groupby("game_id").last().reset_index()

    outcomes = last_plays[["game_id", "home_team", "away_team"]].copy()

    home_score_col = "total_home_score" if "total_home_score" in last_plays.columns else "home_score"
    away_score_col = "total_away_score" if "total_away_score" in last_plays.columns else "away_score"

    if home_score_col in last_plays.columns and away_score_col in last_plays.columns:
        outcomes["home_final"] = last_plays[home_score_col].values
        outcomes["away_final"] = last_plays[away_score_col].values
    else:
        outcomes["home_final"] = np.nan
        outcomes["away_final"] = np.nan
        for _, row in last_plays.iterrows():
            gid = row["game_id"]
            posteam = row["posteam"]
            home = row["home_team"]
            post = row.get("posteam_score", np.nan)
            defe = row.get("defteam_score", np.nan)
            if posteam == home:
                outcomes.loc[outcomes.game_id == gid, "home_final"] = post
                outcomes.loc[outcomes.game_id == gid, "away_final"] = defe
            else:
                outcomes.loc[outcomes.game_id == gid, "home_final"] = defe
                outcomes.loc[outcomes.game_id == gid, "away_final"] = post

    outcomes["home_won"] = (outcomes["home_final"] > outcomes["away_final"]).astype(int)

    return outcomes


def prepare_features(pbp: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    """Engineer features and merge game outcomes."""
    df = pbp.copy()

    # Only use plays with valid possession
    df = df.dropna(subset=["posteam"])
    df = df[df["posteam"].notna() & (df["posteam"] != "")]

    # Merge outcomes (use home_team, away_team from pbp; add outcome cols from outcomes)
    outcome_cols = outcomes[["game_id", "home_final", "away_final", "home_won"]]
    df = df.merge(outcome_cols, on="game_id", how="inner")

    # Label: did posteam win?
    df["posteam_won"] = np.where(
        df["posteam"] == df["home_team"],
        df["home_won"],
        1 - df["home_won"],
    )

    # Score differential from possession team's perspective
    if "score_differential" in df.columns:
        df["score_diff"] = df["score_differential"]
    elif "posteam_score" in df.columns and "defteam_score" in df.columns:
        df["score_diff"] = df["posteam_score"] - df["defteam_score"]
    else:
        df["score_diff"] = 0

    # Fill missing score_diff (e.g. before first score)
    df["score_diff"] = df["score_diff"].fillna(0)

    # Time features
    df["game_seconds_remaining"] = pd.to_numeric(df.get("game_seconds_remaining", 0), errors="coerce").fillna(0)
    df["half_seconds_remaining"] = pd.to_numeric(df.get("half_seconds_remaining", 0), errors="coerce").fillna(0)

    # Field position
    df["yardline_100"] = pd.to_numeric(df.get("yardline_100", 50), errors="coerce").fillna(50)

    # Down and distance
    df["down"] = pd.to_numeric(df.get("down", 1), errors="coerce").fillna(1).astype(int)
    df["ydstogo"] = pd.to_numeric(df.get("ydstogo", 10), errors="coerce").fillna(10)
    df["goal_to_go"] = df.get("goal_to_go", 0).fillna(0).astype(int)

    # Timeouts
    df["posteam_timeouts"] = pd.to_numeric(df.get("posteam_timeouts_remaining", 3), errors="coerce").fillna(3)
    df["defteam_timeouts"] = pd.to_numeric(df.get("defteam_timeouts_remaining", 3), errors="coerce").fillna(3)
    df["timeout_diff"] = df["posteam_timeouts"] - df["defteam_timeouts"]

    # 2nd half kickoff receiver (affects pre-game expectation)
    df["receive_2h_ko"] = df.get("receive_2h_ko", df["posteam"]).fillna("")
    df["is_home"] = (df["posteam"] == df["home_team"]).astype(int)

    # Build feature matrix
    feature_cols = [
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

    for c in feature_cols:
        if c not in df.columns:
            raise ValueError(f"Missing feature column: {c}")

    X = df[feature_cols].copy()
    X["down"] = X["down"].clip(1, 4)
    y = df["posteam_won"].values

    out = df[["game_id", "play_id", "season", "posteam", "home_team", "away_team"]].copy()
    out["label"] = y
    for c in feature_cols:
        out[c] = X[c].values

    return out


def main():
    """Load data, prepare features, save to CSV."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    pbp = load_pbp_data([2022, 2023])
    outcomes = get_game_outcomes(pbp)
    df = prepare_features(pbp, outcomes)

    out_path = data_dir / "win_prob_features.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df):,} rows to {out_path}")

    return df


if __name__ == "__main__":
    main()
