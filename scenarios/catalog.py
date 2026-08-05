"""Catalog of failure-lab scenarios and client patterns."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioEntry:
    """One catalog entry with id, location and summary."""

    scenario_id: str
    location: str
    description: str


CATALOG: tuple[ScenarioEntry, ...] = (
    ScenarioEntry(
        "timeout",
        "scenarios/timeout",
        "Sleep past a configured timeout to simulate Lambda time limits.",
    ),
    ScenarioEntry(
        "retry",
        "scenarios/retry",
        "Raise transient errors so callers can exercise retry logic.",
    ),
    ScenarioEntry(
        "throttle",
        "scenarios/throttle",
        "Simulate 429 rate-limit responses with optional Retry-After.",
    ),
    ScenarioEntry(
        "circuit-breaker",
        "clients/circuit_breaker.py",
        "Open the circuit after repeated failures and recover after a cooldown.",
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


def main() -> None:
    """Print the scenario catalog."""
    print(format_catalog())


if __name__ == "__main__":
    main()
