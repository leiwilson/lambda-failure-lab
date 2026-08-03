"""Tests for clients.backoff retry helper."""
import unittest

from clients.backoff import retry_with_backoff
from scenarios.retry.handler import TransientError
from scenarios.throttle.handler import ThrottleError, reset as throttle_reset


class TestBackoff(unittest.TestCase):
    def test_retries_transient_then_succeeds(self):
        state = {"n": 0}

        def flaky():
            state["n"] += 1
            if state["n"] < 3:
                raise TransientError("boom")
            return {"ok": True, "n": state["n"]}

        result = retry_with_backoff(
            flaky,
            retries=3,
            base_delay=0.001,
            max_delay=0.002,
            retry_on=(TransientError,),
            jitter=False,
        )
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["n"], 3)

    def test_exhausts_retries(self):
        def always_fail():
            raise TransientError("nope")

        with self.assertRaises(TransientError):
            retry_with_backoff(
                always_fail,
                retries=2,
                base_delay=0.001,
                max_delay=0.002,
                retry_on=(TransientError,),
                jitter=False,
            )

    def test_retries_throttle(self):
        throttle_reset()
        calls = {"n": 0}

        def call():
            calls["n"] += 1
            # fail_after=1 means first call ok, later calls raise
            from scenarios.throttle.handler import handler
            return handler({}, fail_after=1)

        # First direct success path already consumed; reset and use fail_after=0 style via raise first
        throttle_reset()

        def always_throttle():
            raise ThrottleError(retry_after=1)

        with self.assertRaises(ThrottleError):
            retry_with_backoff(
                always_throttle,
                retries=1,
                base_delay=0.001,
                max_delay=0.002,
                retry_on=(ThrottleError,),
                jitter=False,
            )


if __name__ == "__main__":
    unittest.main()
