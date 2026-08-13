"""Tests for scenarios.cli."""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from scenarios.cli import main
from scenarios.runner import RunReport, known_scenario_ids


class TestCli(unittest.TestCase):
    def test_list_text_includes_scenarios(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["list"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("timeout", output)
        self.assertIn("circuit-breaker", output)

    def test_list_json_format(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["list", "--format", "json"])
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertEqual(len(parsed), 4)
        self.assertEqual(parsed[0]["scenario_id"], "timeout")

    def test_run_text_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run", "retry", "--seed", "1"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("scenario_id=retry", output)
        self.assertIn("seed=1", output)

    def test_run_json_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run", "timeout", "--format", "json"])
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertEqual(parsed["scenario_id"], "timeout")
        self.assertEqual(set(parsed.keys()), {"scenario_id", "outcome", "attempts", "seed", "elapsed_ms"})

    def test_run_unknown_scenario_returns_error(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run", "missing"])
        self.assertEqual(code, 1)

    def test_run_all_text_one_line_per_scenario(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run-all", "--seed", "0"])
        self.assertEqual(code, 0)
        lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
        ids = known_scenario_ids()
        self.assertEqual(len(lines), len(ids))
        for line, scenario_id in zip(lines, ids):
            self.assertIn(f"scenario_id={scenario_id}", line)
            self.assertIn("seed=0", line)

    def test_run_all_json_list(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run-all", "--format", "json", "--seed", "2"])
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), len(known_scenario_ids()))
        self.assertEqual(
            [item["scenario_id"] for item in parsed],
            list(known_scenario_ids()),
        )
        for item in parsed:
            self.assertEqual(set(item.keys()), {"scenario_id", "outcome", "attempts", "seed", "elapsed_ms"})
            self.assertEqual(item["seed"], 2)

    def test_run_all_exit_nonzero_on_failed_or_open(self):
        ids = list(known_scenario_ids())
        fake_reports = [
            RunReport(ids[0], "success", 1, 0, 0),
            RunReport(ids[1], "failed", 3, 0, 0),
            RunReport(ids[2], "success", 1, 0, 0),
            RunReport(ids[3], "recovered", 2, 0, 0),
        ]

        def fake_run(scenario_id, seed=0, clock=None):
            del seed, clock
            return next(r for r in fake_reports if r.scenario_id == scenario_id)

        buffer = io.StringIO()
        with patch("scenarios.cli.run_scenario", side_effect=fake_run):
            with redirect_stdout(buffer):
                code = main(["run-all", "--seed", "0"])
        self.assertEqual(code, 1)

    def test_run_all_treats_recovered_as_success(self):
        ids = list(known_scenario_ids())
        fake_reports = [
            RunReport(scenario_id, "recovered" if scenario_id == "circuit-breaker" else "success", 1, 0, 0)
            for scenario_id in ids
        ]

        def fake_run(scenario_id, seed=0, clock=None):
            del seed, clock
            return next(r for r in fake_reports if r.scenario_id == scenario_id)

        buffer = io.StringIO()
        with patch("scenarios.cli.run_scenario", side_effect=fake_run):
            with redirect_stdout(buffer):
                code = main(["run-all", "--seed", "0"])
        self.assertEqual(code, 0)

    def test_run_all_exit_nonzero_on_open(self):
        ids = list(known_scenario_ids())
        fake_reports = [
            RunReport(scenario_id, "open" if scenario_id == "circuit-breaker" else "success", 1, 0, 0)
            for scenario_id in ids
        ]

        def fake_run(scenario_id, seed=0, clock=None):
            del seed, clock
            return next(r for r in fake_reports if r.scenario_id == scenario_id)

        buffer = io.StringIO()
        with patch("scenarios.cli.run_scenario", side_effect=fake_run):
            with redirect_stdout(buffer):
                code = main(["run-all"])
        self.assertEqual(code, 1)


    def test_run_all_text_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run-all", "--seed", "0"])
        self.assertEqual(code, 0)
        lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 4)
        self.assertTrue(any("scenario_id=timeout" in line for line in lines))
        self.assertTrue(any("scenario_id=circuit-breaker" in line for line in lines))

    def test_run_all_json_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run-all", "--seed", "0", "--format", "json"])
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 4)
        self.assertEqual(
            set(parsed[0].keys()), {"scenario_id", "outcome", "attempts", "seed", "elapsed_ms"}
        )
        outcomes = {item["scenario_id"]: item["outcome"] for item in parsed}
        self.assertNotIn(outcomes.get("circuit-breaker"), {"failed", "open"})

    def test_show_text_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["show", "retry"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("retry", output)
        self.assertIn("scenarios/retry", output)

    def test_show_json_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["show", "retry", "--format", "json"])
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertEqual(parsed["scenario_id"], "retry")
        self.assertEqual(parsed["location"], "scenarios/retry")
        self.assertIn("description", parsed)

    def test_show_unknown_scenario_returns_error(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["show", "missing"])
        self.assertEqual(code, 1)


    def test_version_prints_package_version(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["version"])
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), "0.1.0")

    def test_ids_prints_one_id_per_line(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["ids"])
        self.assertEqual(code, 0)
        lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
        self.assertEqual(lines, list(known_scenario_ids()))

    def test_count_prints_known_scenario_count(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["count"])
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), str(len(known_scenario_ids())))


if __name__ == "__main__":
    unittest.main()
