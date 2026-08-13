"""Tests for clients.deadline."""
import unittest

from clients.clock import FakeClock
from clients.deadline import Deadline, DeadlineExceeded


class TestDeadline(unittest.TestCase):
    def test_remaining_decreases_with_fake_clock(self):
        clock = FakeClock()
        deadline = Deadline(clock, timeout=1.0)
        self.assertAlmostEqual(deadline.remaining(), 1.0)
        clock.sleep(0.4)
        self.assertAlmostEqual(deadline.remaining(), 0.6)
        self.assertFalse(deadline.expired())

    def test_expired_when_budget_consumed(self):
        clock = FakeClock()
        deadline = Deadline(clock, timeout=0.5)
        clock.sleep(0.5)
        self.assertTrue(deadline.expired())
        self.assertEqual(deadline.remaining(), 0.0)

    def test_check_raises_when_expired(self):
        clock = FakeClock()
        deadline = Deadline(clock, timeout=0.1)
        deadline.check()
        clock.sleep(0.1)
        with self.assertRaises(DeadlineExceeded):
            deadline.check()

    def test_zero_timeout_is_already_expired(self):
        clock = FakeClock()
        deadline = Deadline(clock, timeout=0.0)
        self.assertTrue(deadline.expired())
        with self.assertRaises(DeadlineExceeded):
            deadline.check()

    def test_negative_timeout_rejected(self):
        clock = FakeClock()
        with self.assertRaises(ValueError):
            Deadline(clock, timeout=-1.0)

    def test_elapsed_tracks_fake_clock_uncapped(self):
        clock = FakeClock()
        deadline = Deadline(clock, timeout=0.5)
        self.assertAlmostEqual(deadline.elapsed(), 0.0)
        clock.sleep(0.4)
        self.assertAlmostEqual(deadline.elapsed(), 0.4)
        clock.sleep(0.4)
        self.assertAlmostEqual(deadline.elapsed(), 0.8)
        self.assertGreater(deadline.elapsed(), 0.5)


if __name__ == "__main__":
    unittest.main()
