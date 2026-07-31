"""Minimal tests for failure-lab handlers."""
import unittest

from scenarios.retry.handler import TransientError, handler as retry_handler
from scenarios.timeout import handler as timeout_mod


class TestHandlers(unittest.TestCase):
    def test_timeout_handler_exists(self):
        self.assertTrue(callable(timeout_mod.handler))

    def test_retry_handler_raises_transient(self):
        with self.assertRaises(TransientError):
            retry_handler({})


if __name__ == "__main__":
    unittest.main()
