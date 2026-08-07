"""Tests for clients.circuit_breaker."""
import unittest

from clients.circuit_breaker import CircuitBreaker, CircuitOpenError
from clients.clock import FakeClock
from scenarios.retry.handler import TransientError


class TestCircuitBreaker(unittest.TestCase):
    def test_opens_after_threshold(self):
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0, watch=(TransientError,))

        def boom():
            raise TransientError("x")

        with self.assertRaises(TransientError):
            breaker.call(boom)
        with self.assertRaises(TransientError):
            breaker.call(boom)
        with self.assertRaises(CircuitOpenError):
            breaker.call(boom)

    def test_recovers_after_timeout(self):
        clock = FakeClock()
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.01,
            watch=(TransientError,),
            clock=clock,
        )
        state = {"n": 0}

        def sometimes():
            state["n"] += 1
            if state["n"] == 1:
                raise TransientError("first")
            return {"ok": True}

        with self.assertRaises(TransientError):
            breaker.call(sometimes)
        with self.assertRaises(CircuitOpenError):
            breaker.call(sometimes)
        clock.sleep(0.02)
        self.assertEqual(breaker.call(sometimes)["ok"], True)

    def test_fake_clock_advances_recovery_without_sleep(self):
        clock = FakeClock()
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.5,
            watch=(TransientError,),
            clock=clock,
        )

        def boom():
            raise TransientError("x")

        with self.assertRaises(TransientError):
            breaker.call(boom)
        self.assertTrue(breaker.is_open)
        clock.sleep(0.5)
        self.assertFalse(breaker.is_open)

    def test_success_resets_failures(self):
        clock = FakeClock()
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1.0,
            watch=(TransientError,),
            clock=clock,
        )
        state = {"n": 0}

        def flaky():
            state["n"] += 1
            if state["n"] == 1:
                raise TransientError("once")
            return {"ok": True}

        with self.assertRaises(TransientError):
            breaker.call(flaky)
        self.assertEqual(breaker.failures, 1)
        self.assertEqual(breaker.call(flaky)["ok"], True)
        self.assertEqual(breaker.failures, 0)
        self.assertIsNone(breaker.opened_at)


if __name__ == "__main__":
    unittest.main()
