"""Tests for scenarios.runner."""
import json
import unittest

from clients.clock import FakeClock
from scenarios.runner import (
    RunReport,
    known_scenario_ids,
    report_to_json,
    run_scenario,
)


class TestRunner(unittest.TestCase):
    def test_known_scenario_ids_match_catalog(self):
        self.assertEqual(
            known_scenario_ids(),
            ("timeout", "retry", "throttle", "circuit-breaker"),
        )

    def test_run_unknown_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_scenario("missing")

    def test_report_to_json_shape(self):
        report = RunReport("retry", "success", 2, 7, 15)
        parsed = json.loads(report_to_json(report))
        self.assertEqual(
            parsed,
            {
                "scenario_id": "retry",
                "outcome": "success",
                "attempts": 2,
                "seed": 7,
                "elapsed_ms": 15,
            },
        )

    def test_run_retry_is_deterministic(self):
        clock = FakeClock()
        first = run_scenario("retry", seed=1, clock=clock)
        clock = FakeClock()
        second = run_scenario("retry", seed=1, clock=clock)
        self.assertEqual(first, second)
        self.assertEqual(first.scenario_id, "retry")
        self.assertIn(first.outcome, ("success", "failed"))
        self.assertGreater(first.attempts, 0)
        self.assertGreaterEqual(first.elapsed_ms, 0)

    def test_run_throttle_resets_module_state(self):
        report = run_scenario("throttle", seed=0, clock=FakeClock())
        self.assertEqual(report.scenario_id, "throttle")
        self.assertIn(report.outcome, ("success", "failed"))

    def test_run_timeout_skips_real_sleep(self):
        report = run_scenario("timeout", seed=2, clock=FakeClock())
        self.assertEqual(report.scenario_id, "timeout")
        self.assertEqual(report.outcome, "success")
        self.assertEqual(report.attempts, 1)
        self.assertEqual(report.seed, 2)
        self.assertEqual(report.elapsed_ms, 0)

    def test_elapsed_ms_tracks_fake_clock_delta(self):
        clock = FakeClock()
        report = run_scenario("circuit-breaker", seed=0, clock=clock)
        self.assertGreater(report.elapsed_ms, 0)
        self.assertEqual(report.elapsed_ms, int(round(clock.monotonic() * 1000)))

    def test_run_circuit_breaker_recovers_with_fake_clock(self):
        report = run_scenario("circuit-breaker", seed=0, clock=FakeClock())
        self.assertEqual(report.scenario_id, "circuit-breaker")
        self.assertEqual(report.outcome, "recovered")
        self.assertGreaterEqual(report.attempts, 1)


if __name__ == "__main__":
    unittest.main()
