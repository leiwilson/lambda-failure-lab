"""Simple retry helper for transient and throttle failures."""
from __future__ import annotations

import random
import time
from typing import Callable, Iterable, Protocol, Type


class SleepClock(Protocol):
    """Clock that can advance time during backoff delays."""

    def sleep(self, seconds: float) -> None:
        """Pause or simulate a delay of seconds."""


def retry_with_backoff(
    fn: Callable[[], object],
    *,
    retries: int = 3,
    base_delay: float = 0.01,
    max_delay: float = 0.2,
    retry_on: Iterable[Type[BaseException]] = (),
    jitter: bool = True,
    clock: SleepClock | None = None,
):
    """Call fn, retrying on selected exceptions with exponential backoff."""
    sleep = clock.sleep if clock is not None else time.sleep
    errors = tuple(retry_on) or (Exception,)
    attempt = 0
    while True:
        try:
            return fn()
        except errors as exc:
            if attempt >= retries:
                raise
            delay = min(max_delay, base_delay * (2 ** attempt))
            if jitter:
                delay = delay * (0.5 + random.random())
            # Prefer Retry-After when present (ThrottleError).
            retry_after = getattr(exc, "retry_after", None)
            if retry_after is not None:
                delay = max(delay, float(retry_after) * 0.01)
            sleep(delay)
            attempt += 1
