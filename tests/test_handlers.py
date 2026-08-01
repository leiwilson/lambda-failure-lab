"""Minimal tests for failure-lab handlers."""
import unittest

from scenarios.retry.handler import TransientError, handler as retry_handler
from scenarios.timeout import handler as timeout_mod
from scenarios.throttle import handler as throttle_mod


class TestHandlers(unittest.TestCase):
    def test_timeout_handler_exists(self):
        self.assertTrue(callable(timeout_mod.handler))

    def test_retry_handler_raises_transient(self):
        with self.assertRaises(TransientError):
            retry_handler({})

    def test_throttle_raises_after_limit(self):
        throttle_mod.reset()
        self.assertEqual(throttle_mod.handler({}, fail_after=1)["ok"], True)
        with self.assertRaises(throttle_mod.ThrottleError) as ctx:
            throttle_mod.handler({}, fail_after=1)
        self.assertEqual(ctx.exception.status_code, 429)


if __name__ == "__main__":
    unittest.main()
