"""Execute catalog scenarios and emit stable run reports."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from clients.backoff import retry_with_backoff
from clients.circuit_breaker import CircuitBreaker, CircuitOpenError
from clients.clock import FakeClock
from scenarios.catalog import CATALOG
from scenarios.retry.handler import TransientError
from scenarios.throttle import handler as throttle_mod
from scenarios.timeout import handler as timeout_mod


@dataclass(frozen=True)
class RunReport:
    """Stable JSON report for one scenario execution."""

    scenario_id: str
    outcome: str
    attempts: int
    seed: int
    elapsed_ms: int


def known_scenario_ids() -> tuple[str, ...]:
    """Return catalog scenario ids in display order."""
    return tuple(entry.scenario_id for entry in CATALOG)


def run_scenario(
    scenario_id: str,
    *,
    seed: int = 0,
    clock: FakeClock | None = None,
) -> RunReport:
    """Run one catalog scenario and return a deterministic report."""
    clock = clock or FakeClock()
    runners = {
        "retry": _run_retry,
        "throttle": _run_throttle,
        "timeout": _run_timeout,
        "circuit-breaker": _run_circuit_breaker,
    }
    runner = runners.get(scenario_id)
    if runner is None:
        raise ValueError(f"unknown scenario: {scenario_id}")
    started = clock.monotonic()
    report = runner(seed=seed, clock=clock)
    elapsed_ms = int(round((clock.monotonic() - started) * 1000))
    return RunReport(
        report.scenario_id,
        report.outcome,
        report.attempts,
        report.seed,
        elapsed_ms,
    )


def report_to_json(report: RunReport) -> str:
    """Serialize a run report as stable JSON."""
    return json.dumps(asdict(report), indent=2)


def _run_retry(*, seed: int, clock: FakeClock) -> RunReport:
    max_failures = (seed % 3) + 1
    state = {"attempts": 0}

    def flaky():
        state["attempts"] += 1
        if state["attempts"] <= max_failures:
            raise TransientError("simulated transient failure")
        return {"ok": True}

    try:
        retry_with_backoff(
            flaky,
            retries=5,
            base_delay=0.01,
            max_delay=0.2,
            retry_on=(TransientError,),
            jitter=False,
            clock=clock,
        )
    except TransientError:
        return RunReport("retry", "failed", state["attempts"], seed, 0)
    return RunReport("retry", "success", state["attempts"], seed, 0)


def _run_throttle(*, seed: int, clock: FakeClock) -> RunReport:
    throttle_mod.reset()
    fail_after = (seed % 2) + 1
    state = {"attempts": 0}

    def call_throttle():
        state["attempts"] += 1
        return throttle_mod.handler({}, fail_after=fail_after)

    try:
        retry_with_backoff(
            call_throttle,
            retries=3,
            base_delay=0.01,
            max_delay=0.2,
            retry_on=(throttle_mod.ThrottleError,),
            jitter=False,
            clock=clock,
        )
    except throttle_mod.ThrottleError:
        return RunReport("throttle", "failed", state["attempts"], seed, 0)
    return RunReport("throttle", "success", state["attempts"], seed, 0)


def _run_timeout(*, seed: int, clock: FakeClock) -> RunReport:
    del clock
    timeout_mod.handler({"sleep_seconds": 0})
    return RunReport("timeout", "success", 1, seed, 0)


def _run_circuit_breaker(*, seed: int, clock: FakeClock) -> RunReport:
    threshold = (seed % 3) + 1
    breaker = CircuitBreaker(
        failure_threshold=threshold,
        recovery_timeout=0.05,
        watch=(TransientError,),
        clock=clock,
    )
    attempts = 0

    def boom():
        nonlocal attempts
        attempts += 1
        raise TransientError("simulated transient failure")

    for _ in range(threshold):
        try:
            breaker.call(boom)
        except TransientError:
            pass

    outcome = "open"
    try:
        breaker.call(boom)
    except CircuitOpenError:
        pass

    clock.sleep(breaker.recovery_timeout)
    try:
        breaker.call(lambda: {"ok": True})
        outcome = "recovered"
        attempts += 1
    except CircuitOpenError:
        pass

    return RunReport("circuit-breaker", outcome, attempts, seed, 0)
