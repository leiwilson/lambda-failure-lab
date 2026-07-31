"""Timeout failure scenario handler."""
from __future__ import annotations

import os
import time


def handler(event, context=None):
    """Sleep longer than TIMEOUT_SECONDS to simulate a timeout."""
    timeout = float(os.environ.get("TIMEOUT_SECONDS", "1"))
    sleep_for = float(event.get("sleep_seconds", timeout + 5))
    time.sleep(sleep_for)
    return {"status": "ok", "slept": sleep_for}
