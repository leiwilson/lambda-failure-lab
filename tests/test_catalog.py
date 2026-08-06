"""Tests for scenarios.catalog."""
import io
import json
import unittest
from contextlib import redirect_stdout

from scenarios.catalog import (
    CATALOG,
    catalog_entries_json,
    format_catalog,
    format_catalog_json,
    list_scenarios,
    main,
)


class TestCatalog(unittest.TestCase):
    def test_lists_all_scenarios(self):
        ids = [entry.scenario_id for entry in list_scenarios()]
        self.assertEqual(ids, ["timeout", "retry", "throttle", "circuit-breaker"])

    def test_catalog_has_descriptions(self):
        for entry in CATALOG:
            self.assertTrue(entry.description)
            self.assertTrue(entry.location)

    def test_format_catalog_includes_entries(self):
        text = format_catalog()
        for entry in CATALOG:
            self.assertIn(entry.scenario_id, text)
            self.assertIn(entry.description, text)

    def test_main_prints_catalog(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            main([])
        output = buffer.getvalue()
        self.assertIn("timeout", output)
        self.assertIn("circuit-breaker", output)

    def test_catalog_entries_json_shape(self):
        entries = catalog_entries_json()
        self.assertEqual(len(entries), len(CATALOG))
        for entry in entries:
            self.assertIn("scenario_id", entry)
            self.assertIn("description", entry)
            self.assertEqual(set(entry.keys()), {"scenario_id", "description"})

    def test_format_catalog_json_is_stable(self):
        parsed = json.loads(format_catalog_json())
        self.assertEqual(
            [entry["scenario_id"] for entry in parsed],
            ["timeout", "retry", "throttle", "circuit-breaker"],
        )

    def test_main_json_format(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            main(["--format", "json"])
        parsed = json.loads(buffer.getvalue())
        self.assertEqual(len(parsed), 4)
        self.assertEqual(parsed[0]["scenario_id"], "timeout")


if __name__ == "__main__":
    unittest.main()
