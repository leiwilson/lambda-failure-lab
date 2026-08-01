"""Throttle / rate-limit failure scenario handler."""
from __future__ import annotations


class ThrottleError(Exception):
    """Simulated 429 Too Many Requests."""

    def __init__(self, message="simulated rate limit", retry_after=1):
        super().__init__(message)
        self.retry_after = retry_after
        self.status_code = 429


_CALLS = 0


def reset():
    global _CALLS
    _CALLS = 0


def handler(event, context=None, fail_after=1):
    """Succeed until fail_after invocations, then raise ThrottleError."""
    global _CALLS
    _CALLS += 1
    if _CALLS > fail_after:
        raise ThrottleError(retry_after=int(event.get("retry_after", 1)) if isinstance(event, dict) else 1)
    return {"ok": True, "calls": _CALLS}
