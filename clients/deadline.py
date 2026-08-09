"""Deadline helper for FakeClock-aware timeout budgets."""
from __future__ import annotations

from typing import Protocol


class DeadlineExceeded(Exception):
    """Raised when a deadline has no remaining time."""


class MonotonicClock(Protocol):
    """Clock that exposes monotonic time for deadline tracking."""

    def monotonic(self) -> float:
        """Return monotonic seconds."""


class Deadline:
    """Track remaining time against a clock-backed timeout budget."""

    def __init__(self, clock: MonotonicClock, timeout: float):
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        self._clock = clock
        self._timeout = float(timeout)
        self._started_at = clock.monotonic()

    def remaining(self) -> float:
        """Return seconds left before the deadline (never negative)."""
        elapsed = self._clock.monotonic() - self._started_at
        left = self._timeout - elapsed
        return left if left > 0 else 0.0

    def expired(self) -> bool:
        """Return True when no time remains."""
        return self.remaining() <= 0

    def check(self) -> None:
        """Raise DeadlineExceeded when the deadline has expired."""
        if self.expired():
            raise DeadlineExceeded("deadline exceeded")
