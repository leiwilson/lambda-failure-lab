"""Retry / transient failure scenario handler."""
from __future__ import annotations


class TransientError(Exception):
    """Error that callers should retry."""


def handler(event, context=None):
    """Always raise a transient error so retries can be exercised."""
    raise TransientError("simulated transient failure")
