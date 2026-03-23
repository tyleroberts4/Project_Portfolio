"""
Load NFL schedules and game results from nflverse.
"""

from pathlib import Path

import pandas as pd


def load_schedules(seasons: list[int] | int) -> pd.DataFrame:
    """Load schedule and results from nflverse."""
    try:
        import nfl_data_py as nfl
    except ImportError:
        raise ImportError("nfl_data_py required: pip install nfl_data_py")

    if isinstance(seasons, int):
        seasons = [seasons]

    print(f"Loading schedules for seasons {seasons}...")
    schedules = []
    for year in seasons:
        sched = nfl.import_schedules([year])
        if hasattr(sched, "to_pandas"):
            sched = sched.to_pandas()
        schedules.append(sched)
    df = pd.concat(schedules, ignore_index=True)
    return df


def get_game_results(schedules: pd.DataFrame) -> pd.DataFrame:
    """Extract game results (home/away teams, scores, margin, total) and Vegas lines if present."""
    df = schedules[schedules["game_type"] == "REG"].copy()
    df = df.dropna(subset=["home_score", "away_score"])

    df["margin"] = df["home_score"] - df["away_score"]
    df["total"] = df["home_score"] + df["away_score"]

    # Vegas lines (nflverse schedule includes spread_line, total_line)
    if "spread_line" in df.columns:
        df["vegas_spread"] = df["spread_line"]  # negative = home favored
    if "total_line" in df.columns:
        df["vegas_total"] = df["total_line"]

    return df


if __name__ == "__main__":
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    sched = load_schedules([2022, 2023])
    results = get_game_results(sched)
    results.to_csv(data_dir / "game_results.csv", index=False)
    print(f"Saved {len(results)} games to {data_dir / 'game_results.csv'}")
