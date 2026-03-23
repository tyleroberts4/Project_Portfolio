"""
Monte Carlo simulation of bankroll growth under Kelly betting.
"""

import numpy as np


def simulate_bankroll(
    n_bets: int = 1000,
    edge: float = 0.05,
    odds: float = 2.0,
    kelly_frac: float = 0.5,
    initial: float = 1000.0,
    seed: int | None = None,
) -> np.ndarray:
    """
    Simulate bankroll trajectory using Kelly-sized bets.

    Args:
        n_bets: Number of bets to simulate
        edge: True win probability minus implied probability
        odds: Decimal odds
        kelly_frac: Kelly fraction (0.5 = half Kelly)
        initial: Starting bankroll
        seed: Random seed for reproducibility

    Returns:
        Array of bankroll values [initial, after bet 1, ..., after bet n_bets]
    """
    if seed is not None:
        np.random.seed(seed)

    imp = 1.0 / odds
    win_prob = imp + edge
    b = odds - 1

    kelly = (b * win_prob - (1 - win_prob)) / b
    kelly = max(0, min(1, kelly)) * kelly_frac

    bankroll = np.zeros(n_bets + 1)
    bankroll[0] = initial

    for i in range(n_bets):
        br = bankroll[i]
        bet = br * kelly
        won = np.random.random() < win_prob
        if won:
            bankroll[i + 1] = br + bet * b
        else:
            bankroll[i + 1] = br - bet

    return bankroll


def simulate_many(
    n_sims: int = 500,
    n_bets: int = 1000,
    edge: float = 0.05,
    odds: float = 2.0,
    kelly_frac: float = 0.5,
    initial: float = 1000.0,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run many Monte Carlo simulations and return percentiles.

    Args:
        n_sims: Number of simulation runs
        n_bets: Bets per run
        edge, odds, kelly_frac, initial: Same as simulate_bankroll
        seed: Random seed

    Returns:
        (final_bankrolls, percentile_trajectory)
        final_bankrolls: array of end bankrolls
        percentile_trajectory: (n_bets+1, 3) array with [median, p25, p75] per step
    """
    if seed is not None:
        np.random.seed(seed)

    trajectories = np.zeros((n_sims, n_bets + 1))
    for i in range(n_sims):
        trajectories[i] = simulate_bankroll(n_bets, edge, odds, kelly_frac, initial, seed=None)

    final = trajectories[:, -1]
    pct_traj = np.column_stack([
        np.median(trajectories, axis=0),
        np.percentile(trajectories, 25, axis=0),
        np.percentile(trajectories, 75, axis=0),
    ])
    return final, pct_traj
