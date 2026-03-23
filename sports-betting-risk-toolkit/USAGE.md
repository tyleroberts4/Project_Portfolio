# Sports Betting Risk Toolkit – Usage Guide

## Kelly Criterion

The Kelly Criterion gives the optimal bet size to maximize long-term growth. In practice, **half Kelly** or **quarter Kelly** is often used to reduce variance.

**When to use:** You have an edge (your model’s win probability differs from the market’s implied probability) and want to size bets accordingly.

```python
from kelly import kelly_fraction, optimal_bet

# 5% edge, 2.0 decimal odds (even money), half Kelly
frac = kelly_fraction(edge=0.05, odds=2.0, fraction=0.5)
# frac ≈ 0.05

# Bet size for $1000 bankroll
bet = optimal_bet(edge=0.05, odds=2.0, bankroll=1000, fraction=0.5)
# bet ≈ $50
```

**American odds:** Use `odds_format="american"` with values like -110 or +150.

## Monte Carlo Simulation

Simulate many betting sequences to see bankroll distribution and risk of ruin.

```python
from simulation import simulate_bankroll, simulate_many

# Single run: 1000 bets, 5% edge, half Kelly
traj = simulate_bankroll(n_bets=1000, edge=0.05, odds=2.0, kelly_frac=0.5, seed=42)

# Many runs: percentiles across 500 simulations
final_br, pct_traj = simulate_many(n_sims=500, n_bets=1000, edge=0.05, odds=2.0, kelly_frac=0.5)
# final_br: distribution of end bankrolls
# pct_traj: median, 25th, 75th percentile at each step
```

Use this to compare Kelly fractions (e.g., full vs half) or to estimate drawdown risk.

## Exposure Tracker

Track positions by game to monitor concentration and total risk.

```python
from exposure import ExposureTracker

tracker = ExposureTracker()
tracker.add("2024_01_KC_BUF", "spread", -3.5, "home", risk=100, to_win=91)
tracker.add("2024_01_KC_BUF", "total", 47.5, "over", risk=50, to_win=45)
tracker.add("2024_01_GB_CHI", "moneyline", None, "away", risk=200, to_win=180)

tracker.by_game("2024_01_KC_BUF")  # All positions on Chiefs-Bills
tracker.total_risk()               # 350
tracker.exposure_by_game()         # {"2024_01_KC_BUF": 150, "2024_01_GB_CHI": 200}
```

## Integration with Models

1. **Win probability model** → `edge = model_wp - implied_prob(odds)`
2. **Spread/total model** → Compare predicted margin/total to line; estimate edge from historical calibration
3. **Kelly** → Size bets from `optimal_bet(edge, odds, bankroll, fraction=0.5)`
4. **Exposure** → Log each bet in `ExposureTracker` to monitor risk
