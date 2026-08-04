"""Tests for clients.circuit_breaker."""
import time
import unittest

from clients.circuit_breaker import CircuitBreaker, CircuitOpenError
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
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01, watch=(TransientError,))
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
        time.sleep(0.02)
        self.assertEqual(breaker.call(sometimes)["ok"], True)


if __name__ == "__main__":
    unittest.main()
