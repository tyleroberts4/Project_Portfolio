"""
Load NFL schedule and lines data for CLV analysis.

Uses nflverse schedule (includes spread_line, total_line - typically closing).
For open lines, provide a CSV with columns: game_id, spread_open, total_open.
"""

from pathlib import Path

import pandas as pd


def load_schedule_lines(seasons: list[int]) -> pd.DataFrame:
    """Load schedule with Vegas lines from nflverse."""
    try:
        import nfl_data_py as nfl
    except ImportError:
        raise ImportError("nfl_data_py required: pip install nfl_data_py")

    if isinstance(seasons, int):
        seasons = [seasons]

    sched = nfl.import_schedules(seasons)
    if hasattr(sched, "to_pandas"):
        sched = sched.to_pandas()

    df = sched[sched["game_type"] == "REG"].copy()
    df = df.dropna(subset=["home_score", "away_score", "spread_line", "total_line"])
    df["margin"] = df["home_score"] - df["away_score"]
    df["total"] = df["home_score"] + df["away_score"]
    return df


def main():
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    df = load_schedule_lines([2022, 2023])
    df.to_csv(data_dir / "schedule_lines.csv", index=False)
    print(f"Saved {len(df)} games to {data_dir / 'schedule_lines.csv'}")


if __name__ == "__main__":
    main()
