# NFL Data Pipeline

SQL schema and ETL scripts for NFL play-by-play, schedules, and betting lines. Designed for analytics and trading workflows.

## Overview

Demonstrates **data engineering** for sports analytics. Uses nflverse/nflfastR as the source; loads into a normalized schema for fast analytical queries.

## Project Structure

| File | Description |
|------|-------------|
| `schema.sql` | MySQL schema: games, plays, teams, lines |
| `etl_load.py` | Python ETL: fetches nflverse data, loads into DB |
| `queries.sql` | Example analytical queries |
| `requirements.txt` | Python dependencies |

## Schema

- **games** – Season, week, home/away, scores, Vegas lines
- **plays** – Play-by-play (subset of key columns for analytics)
- **teams** – Team reference
- **lines** – Opening/closing lines by game

## Setup

```bash
pip install -r requirements.txt
```

For MySQL:
```bash
mysql -u user -p < schema.sql
python etl_load.py --seasons 2022 2023
```

For SQLite (no MySQL required):
```bash
python etl_load.py --seasons 2022 2023 --sqlite
```

## Usage

```bash
python etl_load.py --seasons 2022 2023 --sqlite
mysql -u user -p nfl_analytics < queries.sql
```
