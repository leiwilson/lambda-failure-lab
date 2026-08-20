"""Tiny circuit breaker for repeated transient failures."""
from __future__ import annotations

import time
from typing import Callable, Iterable, Protocol, Type


class CircuitOpenError(Exception):
    """Raised when the circuit is open and calls are short-circuited."""


class MonotonicClock(Protocol):
    """Clock that exposes monotonic time for recovery windows."""

    def monotonic(self) -> float:
        """Return monotonic seconds."""


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout: float = 0.05,
        watch: Iterable[Type[BaseException]] = (),
        clock: MonotonicClock | None = None,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.watch = tuple(watch) or (Exception,)
        self._monotonic = clock.monotonic if clock is not None else time.monotonic
        self.failures = 0
        self.opened_at = None

    @property
    def state(self) -> str:
        """Return read-only breaker state: closed, open, or half_open."""
        if self.opened_at is None:
            return "closed"
        if (self._monotonic() - self.opened_at) >= self.recovery_timeout:
            return "half_open"
        return "open"

    def seconds_until_half_open(self) -> float:
        """Return seconds until half-open; 0.0 when closed or half-open."""
        if self.opened_at is None:
            return 0.0
        elapsed = self._monotonic() - self.opened_at
        remaining = self.recovery_timeout - elapsed
        return remaining if remaining > 0 else 0.0

    def reset(self) -> None:
        """Clear failure count and close the circuit."""
        self.failures = 0
        self.opened_at = None

    @property
    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if (self._monotonic() - self.opened_at) >= self.recovery_timeout:
            # half-open: allow one trial
            return False
        return True

    def call(self, fn: Callable[[], object]):
        if self.is_open:
            raise CircuitOpenError("circuit open")
        try:
            result = fn()
        except self.watch:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.opened_at = self._monotonic()
            raise
        self.failures = 0
        self.opened_at = None
        return result
