# NFL Line Movement and Closing Line Value (CLV) Analysis

Analysis of open vs. closing line movement and Closing Line Value (CLV)—how often your bet price was better than the closing line. CLV is an industry proxy for bet quality.

## Overview

Demonstrates understanding of **trading concepts** beyond raw prediction accuracy. Sharp bettors and books evaluate performance partly by CLV: did you get a better price than the market at close?

## Requirements

- **Open and closing lines** – nflverse schedule data includes `spread_line` and `total_line` (often closing). For open lines, use a dataset with both (e.g. [Kaggle NFL scores and betting data](https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data)).

## Project Structure

| File | Description |
|------|-------------|
| `load_data.py` | Load schedule/lines data |
| `clv_analysis.py` | Compute CLV by bet type, line movement stats |
| `report.md` | Summary of market efficiency and CLV findings |

## Usage

```bash
pip install -r requirements.txt
python load_data.py
python clv_analysis.py
```

## Outputs

- Line movement (open → close) by game
- CLV rate: % of hypothetical bets that beat the closing line
- Short report on market efficiency
