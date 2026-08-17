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

    def elapsed(self) -> float:
        """Return seconds since start; uncapped, may exceed timeout."""
        return self._clock.monotonic() - self._started_at

    def fraction_used(self) -> float:
        """Return elapsed/timeout clamped to [0, 1]; timeout==0 yields 1.0."""
        if self._timeout == 0:
            return 1.0
        ratio = self.elapsed() / self._timeout
        if ratio < 0:
            return 0.0
        if ratio > 1:
            return 1.0
        return ratio

    def remaining_fraction(self) -> float:
        """Return 1.0 - fraction_used(); timeout==0 yields 0.0."""
        return 1.0 - self.fraction_used()

    def remaining(self) -> float:
        """Return seconds left before the deadline (never negative)."""
        elapsed = self._clock.monotonic() - self._started_at
        left = self._timeout - elapsed
        return left if left > 0 else 0.0

    def remaining_ms(self) -> float:
        """Return milliseconds left before the deadline (never negative)."""
        return self.remaining() * 1000

    def expired(self) -> bool:
        """Return True when no time remains."""
        return self.remaining() <= 0

    def check(self) -> None:
        """Raise DeadlineExceeded when the deadline has expired."""
        if self.expired():
            raise DeadlineExceeded("deadline exceeded")
