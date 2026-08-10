"""Tests for clients.retry_after."""
import unittest
from unittest.mock import patch

from clients.clock import FakeClock
from clients.retry_after import sleep_for_retry_after


class _ErrorWithRetryAfter(Exception):
    def __init__(self, retry_after):
        super().__init__("retry")
        self.retry_after = retry_after


class TestRetryAfter(unittest.TestCase):
    def test_sleeps_using_fake_clock(self):
        clock = FakeClock()
        slept = sleep_for_retry_after(_ErrorWithRetryAfter(1.5), clock=clock)
        self.assertEqual(slept, 1.5)
        self.assertAlmostEqual(clock.monotonic(), 1.5)

    def test_missing_retry_after_is_noop(self):
        clock = FakeClock()
        slept = sleep_for_retry_after(Exception("plain"), clock=clock)
        self.assertEqual(slept, 0.0)
        self.assertEqual(clock.monotonic(), 0.0)

    def test_invalid_retry_after_is_noop(self):
        clock = FakeClock()
        slept = sleep_for_retry_after(_ErrorWithRetryAfter("later"), clock=clock)
        self.assertEqual(slept, 0.0)
        self.assertEqual(clock.monotonic(), 0.0)

    def test_negative_retry_after_is_noop(self):
        clock = FakeClock()
        slept = sleep_for_retry_after(_ErrorWithRetryAfter(-1), clock=clock)
        self.assertEqual(slept, 0.0)
        self.assertEqual(clock.monotonic(), 0.0)

    def test_real_sleep_when_no_clock(self):
        with patch("clients.retry_after.time.sleep") as mock_sleep:
            slept = sleep_for_retry_after(_ErrorWithRetryAfter(0.25))
        mock_sleep.assert_called_once_with(0.25)
        self.assertEqual(slept, 0.25)


if __name__ == "__main__":
    unittest.main()
