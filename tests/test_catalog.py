"""Tests for scenarios.catalog."""
import io
import unittest
from contextlib import redirect_stdout

from scenarios.catalog import CATALOG, format_catalog, list_scenarios, main


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
            main()
        output = buffer.getvalue()
        self.assertIn("timeout", output)
        self.assertIn("circuit-breaker", output)


if __name__ == "__main__":
    unittest.main()
