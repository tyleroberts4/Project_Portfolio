# Sports Betting Risk Management Toolkit

Kelly Criterion bet sizing, bankroll simulation, and exposure tracking for sports betting. Implements the core math used in risk management and trading.

## Overview

Demonstrates understanding of **risk management** and **trading** concepts—key to Swish Analytics' product suite. Includes full, half, and fractional Kelly; Monte Carlo bankroll simulation; and a simple exposure tracker.

## Components

| Module | Description |
|--------|-------------|
| `kelly.py` | Kelly Criterion calculator (edge + odds → optimal bet size) |
| `simulation.py` | Monte Carlo bankroll growth simulation |
| `exposure.py` | Simple exposure tracker by game/line |
| `USAGE.md` | Practical usage guide |

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from kelly import kelly_fraction, optimal_bet
from simulation import simulate_bankroll

# Kelly: edge=5%, decimal odds=2.0, fraction=0.5 (half Kelly)
frac = kelly_fraction(edge=0.05, odds=2.0, fraction=0.5)
bet_pct = optimal_bet(edge=0.05, odds=2.0, bankroll=1000, fraction=0.5)
# bet_pct = fraction of bankroll to bet

# Monte Carlo: 1000 bets, 5% edge, 2.0 odds, half Kelly
trajectory = simulate_bankroll(n_bets=1000, edge=0.05, odds=2.0, kelly_frac=0.5)
```

## API Summary

### Kelly Criterion

- `kelly_fraction(edge, odds, fraction=1.0)` – Optimal fraction of bankroll (0 to 1)
- `optimal_bet(edge, odds, bankroll, fraction=0.5)` – Dollar amount to bet

### Simulation

- `simulate_bankroll(n_bets, edge, odds, kelly_frac=0.5, initial=1000)` – Returns array of bankroll after each bet

### Exposure

- `ExposureTracker` – Add positions, query by game/line, total exposure
