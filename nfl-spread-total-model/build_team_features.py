"""
Build team-level features for spread/total prediction: rolling efficiency, rest days.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def rolling_efficiency(games: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Compute rolling points scored and allowed per game for each team."""
    teams = pd.concat([
        games.assign(team=games["home_team"], pts_for=games["home_score"], pts_against=games["away_score"]),
        games.assign(team=games["away_team"], pts_for=games["away_score"], pts_against=games["home_score"]),
    ]).sort_values(["team", "season", "week"])

    teams["off_ppg_roll"] = teams.groupby("team")["pts_for"].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    teams["def_ppg_roll"] = teams.groupby("team")["pts_against"].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    return teams


def build_game_features(games: pd.DataFrame) -> pd.DataFrame:
    """Merge home/away rolling stats and rest days into game-level features."""
    # Rolling efficiency per team per game
    team_stats = rolling_efficiency(games)

    home_stats = team_stats.merge(
        games[["game_id", "home_team"]],
        left_on=["game_id", "team"],
        right_on=["game_id", "home_team"],
    )[["game_id", "home_team", "off_ppg_roll", "def_ppg_roll"]].rename(
        columns={"off_ppg_roll": "home_off_ppg", "def_ppg_roll": "home_def_ppg"}
    )
    away_stats = team_stats.merge(
        games[["game_id", "away_team"]],
        left_on=["game_id", "team"],
        right_on=["game_id", "away_team"],
    )[["game_id", "away_team", "off_ppg_roll", "def_ppg_roll"]].rename(
        columns={"off_ppg_roll": "away_off_ppg", "def_ppg_roll": "away_def_ppg"}
    )

    merged = games.merge(home_stats, on=["game_id", "home_team"], how="left")
    merged = merged.merge(away_stats, on=["game_id", "away_team"], how="left")

    # Rest days (if available)
    if "home_rest" in merged.columns and "away_rest" in merged.columns:
        merged["rest_diff"] = merged["home_rest"] - merged["away_rest"]
    else:
        merged["rest_diff"] = 0

    merged["off_diff"] = merged["home_off_ppg"] - merged["away_def_ppg"]
    merged["def_diff"] = merged["away_off_ppg"] - merged["home_def_ppg"]
    merged["expected_total"] = merged["home_off_ppg"] + merged["away_off_ppg"]
    merged["expected_margin"] = merged["off_diff"]

    return merged


def main():
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    results_path = data_dir / "game_results.csv"
    if not results_path.exists():
        from load_schedules import load_schedules, get_game_results
        sched = load_schedules([2022, 2023])
        results = get_game_results(sched)
        results.to_csv(results_path, index=False)

    games = pd.read_csv(results_path)
    feats = build_game_features(games)
    feats.to_csv(data_dir / "game_features.csv", index=False)
    print(f"Saved features for {len(feats)} games to {data_dir / 'game_features.csv'}")


if __name__ == "__main__":
    main()
