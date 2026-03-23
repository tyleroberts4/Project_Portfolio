"""
Simple exposure tracker: positions by game, line, bet type.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    """Single bet position."""
    game_id: str
    bet_type: str  # "spread", "total", "moneyline"
    line: Optional[float]  # spread value, total, or None for ML
    side: str  # "home", "away", "over", "under"
    risk: float
    to_win: float


class ExposureTracker:
    """
    Track betting exposure by game and line.

    Usage:
        tracker = ExposureTracker()
        tracker.add("2024_01_KC_BUF", "spread", -3.5, "home", risk=100, to_win=91)
        tracker.add("2024_01_KC_BUF", "total", 47.5, "over", risk=50, to_win=45)
        tracker.by_game("2024_01_KC_BUF")
        tracker.total_exposure()
    """

    def __init__(self) -> None:
        self._positions: list[Position] = []

    def add(
        self,
        game_id: str,
        bet_type: str,
        line: Optional[float],
        side: str,
        risk: float,
        to_win: float,
    ) -> None:
        """Add a position."""
        self._positions.append(
            Position(game_id=game_id, bet_type=bet_type, line=line, side=side, risk=risk, to_win=to_win)
        )

    def by_game(self, game_id: str) -> list[Position]:
        """Return all positions for a game."""
        return [p for p in self._positions if p.game_id == game_id]

    def by_bet_type(self, bet_type: str) -> list[Position]:
        """Return all positions of a given type."""
        return [p for p in self._positions if p.bet_type == bet_type]

    def total_risk(self) -> float:
        """Total risk across all positions."""
        return sum(p.risk for p in self._positions)

    def total_to_win(self) -> float:
        """Total potential win across all positions."""
        return sum(p.to_win for p in self._positions)

    def exposure_by_game(self) -> dict[str, float]:
        """Risk exposure per game."""
        out: dict[str, float] = defaultdict(float)
        for p in self._positions:
            out[p.game_id] += p.risk
        return dict(out)
