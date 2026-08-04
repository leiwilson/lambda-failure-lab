"""Tiny circuit breaker for repeated transient failures."""
from __future__ import annotations

import time
from typing import Callable, Iterable, Type


class CircuitOpenError(Exception):
    """Raised when the circuit is open and calls are short-circuited."""


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout: float = 0.05,
        watch: Iterable[Type[BaseException]] = (),
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.watch = tuple(watch) or (Exception,)
        self.failures = 0
        self.opened_at = None

    @property
    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if (time.monotonic() - self.opened_at) >= self.recovery_timeout:
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
                self.opened_at = time.monotonic()
            raise
        self.failures = 0
        self.opened_at = None
        return result
