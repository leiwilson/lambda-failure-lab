"""Tests for scenarios.cli."""
import io
import json
import unittest
from contextlib import redirect_stdout

from scenarios.cli import main


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
        self.assertEqual(set(parsed.keys()), {"scenario_id", "outcome", "attempts", "seed"})

    def test_run_unknown_scenario_returns_error(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["run", "missing"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
