"""
Kelly Criterion calculator for sports betting.

Computes optimal bet size given edge (implied probability vs true probability)
and odds. Supports full, half, and fractional Kelly for risk adjustment.
"""


def implied_probability(odds: float, odds_format: str = "decimal") -> float:
    """
    Convert odds to implied probability.

    Args:
        odds: Odds value (e.g. 2.0 for even money, -110 for American)
        odds_format: "decimal" (european), "american", or "fractional" (e.g. "2/1")

    Returns:
        Implied probability in [0, 1]
    """
    if odds_format == "decimal":
        return 1.0 / odds
    if odds_format == "american":
        if odds > 0:
            return 100.0 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)
    if odds_format == "fractional":
        num, denom = odds if isinstance(odds, tuple) else (odds, 1)
        return denom / (num + denom)
    raise ValueError("odds_format must be decimal, american, or fractional")


def kelly_fraction(
    edge: float,
    odds: float,
    fraction: float = 1.0,
    odds_format: str = "decimal",
) -> float:
    """
    Kelly Criterion: optimal fraction of bankroll to bet.

    Kelly formula: f* = (b*p - q) / b
    where b = odds - 1 (decimal), p = win prob, q = 1 - p

    Args:
        edge: True win probability minus implied probability (e.g. 0.05 for 5% edge)
        odds: Decimal odds (payout per unit stake, e.g. 2.0 = even money)
        fraction: Kelly fraction (1.0 = full Kelly, 0.5 = half Kelly)
        odds_format: "decimal", "american", or "fractional"

    Returns:
        Optimal fraction of bankroll to bet, clipped to [0, 1]
    """
    imp = implied_probability(odds, odds_format)
    p = imp + edge  # true win probability
    q = 1 - p
    b = odds - 1  # decimal: profit per unit
    kelly = (b * p - q) / b
    kelly = max(0.0, min(1.0, kelly))
    return kelly * fraction


def optimal_bet(
    edge: float,
    odds: float,
    bankroll: float,
    fraction: float = 0.5,
    odds_format: str = "decimal",
) -> float:
    """
    Dollar amount to bet using Kelly Criterion.

    Args:
        edge: True edge (e.g. 0.05)
        odds: Decimal odds
        bankroll: Current bankroll
        fraction: Kelly fraction (0.5 = half Kelly recommended)
        odds_format: Odds format

    Returns:
        Recommended bet size in dollars
    """
    frac = kelly_fraction(edge, odds, fraction, odds_format)
    return bankroll * frac


def edge_from_odds(
    win_prob: float,
    odds: float,
    odds_format: str = "decimal",
) -> float:
    """
    Compute edge given model's win probability and market odds.

    Args:
        win_prob: Model's estimated win probability
        odds: Market odds
        odds_format: Odds format

    Returns:
        Edge (win_prob - implied_prob)
    """
    imp = implied_probability(odds, odds_format)
    return win_prob - imp
