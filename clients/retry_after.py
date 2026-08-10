"""Retry-After aware sleep helper for throttle-style errors."""
from __future__ import annotations

import time
from typing import Protocol


class SleepClock(Protocol):
    """Clock that can advance time during Retry-After delays."""

    def sleep(self, seconds: float) -> None:
        """Pause or simulate a delay of seconds."""


def sleep_for_retry_after(error: BaseException, clock: SleepClock | None = None) -> float:
    """Sleep according to error.retry_after when present.

    Returns the number of seconds slept (0 when Retry-After is absent or invalid).
    Uses clock.sleep when a clock is injected; otherwise time.sleep.
    """
    retry_after = getattr(error, "retry_after", None)
    if retry_after is None:
        return 0.0
    try:
        seconds = float(retry_after)
    except (TypeError, ValueError):
        return 0.0
    if seconds < 0:
        return 0.0
    sleep = clock.sleep if clock is not None else time.sleep
    sleep(seconds)
    return seconds
