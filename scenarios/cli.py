"""Command-line interface for lambda-failure-lab."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from scenarios.catalog import catalog_entries_json, format_catalog
from scenarios.runner import known_scenario_ids, report_to_json, run_scenario

_FAILURE_OUTCOMES = frozenset({"failed", "open"})


def build_parser() -> argparse.ArgumentParser:
    """Build the failure-lab CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python -m scenarios.cli",
        description="List and run lambda-failure-lab scenarios",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List catalog scenarios")
    list_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )

    run_parser = subparsers.add_parser("run", help="Run one catalog scenario")
    run_parser.add_argument("scenario_id", help="Scenario id from the catalog")
    run_parser.add_argument("--seed", type=int, default=0, help="Deterministic seed")
    run_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )

    run_all_parser = subparsers.add_parser(
        "run-all", help="Run every catalog scenario"
    )
    run_all_parser.add_argument("--seed", type=int, default=0, help="Deterministic seed")
    run_all_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    return parser


def format_run_text(report) -> str:
    """Render a run report as plain text."""
    return (
        f"scenario_id={report.scenario_id} "
        f"outcome={report.outcome} "
        f"attempts={report.attempts} "
        f"seed={report.seed}"
    )


def main(argv: list[str] | None = None) -> int:
    """Run the failure-lab CLI."""
    args = build_parser().parse_args(argv)

    if args.command == "list":
        if args.format == "json":
            print(json.dumps(catalog_entries_json(), indent=2))
        else:
            print(format_catalog())
        return 0

    if args.command == "run":
        try:
            report = run_scenario(args.scenario_id, seed=args.seed)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if args.format == "json":
            print(report_to_json(report))
        else:
            print(format_run_text(report))
        return 0

    if args.command == "run-all":
        reports = [
            run_scenario(scenario_id, seed=args.seed)
            for scenario_id in known_scenario_ids()
        ]
        if args.format == "json":
            print(json.dumps([asdict(report) for report in reports], indent=2))
        else:
            for report in reports:
                print(format_run_text(report))
        if any(report.outcome in _FAILURE_OUTCOMES for report in reports):
            return 1
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
