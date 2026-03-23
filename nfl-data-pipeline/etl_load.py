"""
ETL: Load NFL data from nflverse into MySQL or SQLite.
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def load_nfl_data(seasons: list[int]):
    """Load schedules and play-by-play from nflverse."""
    import nfl_data_py as nfl

    sched = nfl.import_schedules(seasons)
    if hasattr(sched, "to_pandas"):
        sched = sched.to_pandas()

    pbp = nfl.import_pbp_data(seasons, downcast=True, cache=True)
    if hasattr(pbp, "to_pandas"):
        pbp = pbp.to_pandas()

    return sched, pbp


def get_teams(sched: pd.DataFrame) -> pd.DataFrame:
    """Extract unique teams from schedule."""
    home = sched[["home_team"]].dropna().rename(columns={"home_team": "team_abbr"})
    away = sched[["away_team"]].dropna().rename(columns={"away_team": "team_abbr"})
    teams = pd.concat([home, away]).drop_duplicates()
    teams["team_name"] = teams["team_abbr"]
    return teams


def transform_games(sched: pd.DataFrame) -> pd.DataFrame:
    """Transform schedule to games table schema."""
    df = sched[sched["game_type"] == "REG"].copy()
    df = df.rename(columns={
        "home_score": "home_score",
        "away_score": "away_score",
    })
    df["total"] = df["home_score"] + df["away_score"]
    df["margin"] = df["home_score"] - df["away_score"]
    return df[["game_id", "season", "week", "game_type", "home_team", "away_team",
               "home_score", "away_score", "total", "margin", "spread_line", "total_line",
               "home_rest", "away_rest"]].dropna(subset=["home_team", "away_team"])


def transform_plays(pbp: pd.DataFrame, max_plays: int | None = None) -> pd.DataFrame:
    """Transform PBP to plays table schema (subset of columns)."""
    cols = ["play_id", "game_id", "season", "week", "posteam", "defteam", "down", "ydstogo",
            "yardline_100", "game_seconds_remaining", "score_differential", "posteam_score",
            "defteam_score", "yards_gained", "play_type"]
    avail = [c for c in cols if c in pbp.columns]
    df = pbp[avail].dropna(subset=["game_id", "play_id"])
    if max_plays:
        df = df.head(max_plays)
    return df


def load_sqlite(sched: pd.DataFrame, pbp: pd.DataFrame, db_path: Path) -> None:
    """Load data into SQLite."""
    conn = sqlite3.connect(db_path)

    teams = get_teams(sched)
    teams.to_sql("teams", conn, if_exists="replace", index=False)

    games = transform_games(sched)
    games.to_sql("games", conn, if_exists="replace", index=False)

    plays = transform_plays(pbp, max_plays=500_000)
    plays.to_sql("plays", conn, if_exists="replace", index=False)

    if "spread_line" in games.columns:
        lines = games[["game_id"]].copy()
        lines["line_type"] = "vegas"
        lines["spread"] = games["spread_line"]
        lines["total"] = games["total_line"]
        lines["source"] = "nflverse"
        lines.to_sql("lines", conn, if_exists="replace", index=False)

    conn.close()
    print(f"Loaded into SQLite: {db_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", nargs="+", type=int, default=[2022, 2023])
    parser.add_argument("--sqlite", action="store_true", help="Use SQLite instead of MySQL")
    parser.add_argument("--db-path", default="nfl_analytics.db")
    args = parser.parse_args()

    sched, pbp = load_nfl_data(args.seasons)
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / args.db_path if args.sqlite else Path(args.db_path)

    load_sqlite(sched, pbp, db_path)


if __name__ == "__main__":
    main()
