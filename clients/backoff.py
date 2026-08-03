"""Simple retry helper for transient and throttle failures."""
from __future__ import annotations

import random
import time
from typing import Callable, Iterable, Type


def retry_with_backoff(
    fn: Callable[[], object],
    *,
    retries: int = 3,
    base_delay: float = 0.01,
    max_delay: float = 0.2,
    retry_on: Iterable[Type[BaseException]] = (),
    jitter: bool = True,
):
    """Call fn, retrying on selected exceptions with exponential backoff."""
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
            time.sleep(delay)
            attempt += 1
