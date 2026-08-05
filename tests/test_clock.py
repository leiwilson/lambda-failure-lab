"""Tests for clients.clock FakeClock."""
import unittest

from clients.clock import FakeClock


class TestFakeClock(unittest.TestCase):
    def test_monotonic_starts_at_zero(self):
        clock = FakeClock()
        self.assertEqual(clock.monotonic(), 0.0)

    def test_sleep_advances_monotonic_time(self):
        clock = FakeClock()
        clock.sleep(0.5)
        self.assertEqual(clock.monotonic(), 0.5)
        clock.sleep(1.25)
        self.assertAlmostEqual(clock.monotonic(), 1.75)

    def test_sleep_does_not_block(self):
        clock = FakeClock(start=10.0)
        clock.sleep(1000.0)
        self.assertEqual(clock.monotonic(), 1010.0)

    def test_negative_sleep_raises(self):
        clock = FakeClock()
        with self.assertRaises(ValueError):
            clock.sleep(-0.1)


if __name__ == "__main__":
    unittest.main()
