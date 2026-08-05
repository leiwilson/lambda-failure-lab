"""Deterministic clock for tests and simulations."""
from __future__ import annotations


class FakeClock:
    """Monotonic clock whose sleep advances time without blocking."""

    def __init__(self, start: float = 0.0):
        self._now = float(start)

    def monotonic(self) -> float:
        """Return the current fake monotonic time."""
        return self._now

    def sleep(self, seconds: float) -> None:
        """Advance fake time by seconds without sleeping."""
        if seconds < 0:
            raise ValueError("sleep length must be non-negative")
        self._now += float(seconds)
