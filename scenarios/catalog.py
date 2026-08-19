"""Catalog of failure-lab scenarios and client patterns."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioEntry:
    """One catalog entry with id, location and summary."""

    scenario_id: str
    location: str
    description: str
    tags: tuple[str, ...]


CATALOG: tuple[ScenarioEntry, ...] = (
    ScenarioEntry(
        "timeout",
        "scenarios/timeout",
        "Sleep past a configured timeout to simulate Lambda time limits.",
        ("timeout", "latency", "failure-mode"),
    ),
    ScenarioEntry(
        "retry",
        "scenarios/retry",
        "Raise transient errors so callers can exercise retry logic.",
        ("retry", "transient", "backoff"),
    ),
    ScenarioEntry(
        "throttle",
        "scenarios/throttle",
        "Simulate 429 rate-limit responses with optional Retry-After.",
        ("throttle", "rate-limit", "retry-after"),
    ),
    ScenarioEntry(
        "circuit-breaker",
        "clients/circuit_breaker.py",
        "Open the circuit after repeated failures and recover after a cooldown.",
        ("circuit-breaker", "resilience", "recovery"),
    ),
)


def list_scenarios() -> list[ScenarioEntry]:
    """Return catalog entries in display order."""
    return list(CATALOG)


def format_catalog() -> str:
    """Render the catalog as plain text."""
    lines = ["lambda-failure-lab scenario catalog", ""]
    for entry in CATALOG:
        lines.append(f"- {entry.scenario_id} ({entry.location})")
        lines.append(f"  {entry.description}")
    return "\n".join(lines)


def catalog_entries_json() -> list[dict[str, object]]:
    """Return catalog entries as stable JSON-serializable dicts."""
    return [
        {
            "scenario_id": entry.scenario_id,
            "description": entry.description,
            "tags": list(entry.tags),
        }
        for entry in CATALOG
    ]


def format_catalog_json() -> str:
    """Render the catalog as a stable JSON list."""
    return json.dumps(catalog_entries_json(), indent=2)


def main(argv: list[str] | None = None) -> None:
    """Print the scenario catalog."""
    parser = argparse.ArgumentParser(description="List lambda-failure-lab scenarios")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args(argv)
    if args.format == "json":
        print(format_catalog_json())
    else:
        print(format_catalog())


if __name__ == "__main__":
    main()
