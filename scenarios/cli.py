"""Command-line interface for lambda-failure-lab."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from scenarios.catalog import CATALOG, catalog_entries_json, format_catalog
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

    show_parser = subparsers.add_parser("show", help="Show one catalog scenario")
    show_parser.add_argument("scenario_id", help="Scenario id from the catalog")
    show_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )

    subparsers.add_parser("version", help="Print package version")

    ids_parser = subparsers.add_parser("ids", help="Print known scenario ids")
    ids_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )

    subparsers.add_parser("count", help="Print number of known scenarios")

    has_parser = subparsers.add_parser(
        "has", help="Check whether a scenario id is known"
    )
    has_parser.add_argument("scenario_id", help="Scenario id from the catalog")

    location_parser = subparsers.add_parser(
        "location", help="Print catalog location for a scenario id"
    )
    location_parser.add_argument("scenario_id", help="Scenario id from the catalog")

    find_parser = subparsers.add_parser(
        "find", help="Find scenarios by id or description substring"
    )
    find_parser.add_argument("query", help="Case-insensitive match on id or description")
    return parser


def format_run_text(report) -> str:
    """Render a run report as plain text."""
    return (
        f"scenario_id={report.scenario_id} "
        f"outcome={report.outcome} "
        f"attempts={report.attempts} "
        f"seed={report.seed} "
        f"elapsed_ms={report.elapsed_ms}"
    )


def format_show_text(entry) -> str:
    """Render one catalog entry as plain text."""
    return (
        f"{entry.scenario_id} ({entry.location})\n"
        f"  {entry.description}"
    )


def lookup_scenario(scenario_id: str):
    """Return a catalog entry or None when unknown."""
    for entry in CATALOG:
        if entry.scenario_id == scenario_id:
            return entry
    return None


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

    if args.command == "show":
        entry = lookup_scenario(args.scenario_id)
        if entry is None:
            print(f"unknown scenario: {args.scenario_id}", file=sys.stderr)
            return 1
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "scenario_id": entry.scenario_id,
                        "location": entry.location,
                        "description": entry.description,
                    },
                    indent=2,
                )
            )
        else:
            print(format_show_text(entry))
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

    if args.command == "version":
        print("0.1.0")
        return 0

    if args.command == "ids":
        ids = list(known_scenario_ids())
        if args.format == "json":
            print(json.dumps(ids, indent=2))
        else:
            for scenario_id in ids:
                print(scenario_id)
        return 0

    if args.command == "count":
        print(len(known_scenario_ids()))
        return 0

    if args.command == "has":
        if args.scenario_id in known_scenario_ids():
            return 0
        print(f"unknown scenario: {args.scenario_id}", file=sys.stderr)
        return 1

    if args.command == "location":
        entry = lookup_scenario(args.scenario_id)
        if entry is None:
            print(f"unknown scenario: {args.scenario_id}", file=sys.stderr)
            return 1
        print(entry.location)
        return 0

    if args.command == "find":
        query = args.query.casefold()
        matches = [
            entry.scenario_id
            for entry in CATALOG
            if query in entry.scenario_id.casefold()
            or query in entry.description.casefold()
        ]
        if not matches:
            return 1
        for scenario_id in matches:
            print(scenario_id)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
