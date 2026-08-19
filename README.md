# lambda-failure-lab

Lab scenarios for Lambda-style failure modes: timeouts, transient retries, and throttling.
Includes a small client-side exponential backoff helper for exercising those failures.

## Scenarios

- `scenarios/timeout` — handler that can sleep past a configured timeout
- `scenarios/retry` — handler that raises a transient error
- `scenarios/throttle` — handler that simulates 429 / rate-limit responses

The JSON catalog output (`python -m scenarios.catalog --format json`) now includes
`scenario_id`, `description`, and `tags` for each entry so downstream tooling can
filter by capability without parsing free-form text.

## Client helpers

- `clients/backoff.py` — exponential backoff retries
- `clients/circuit_breaker.py` — open the circuit after repeated failures

## Client helper

```python
from clients.backoff import retry_with_backoff
from scenarios.retry.handler import TransientError, handler

result = retry_with_backoff(
    lambda: handler({}),
    retries=3,
    retry_on=(TransientError,),
)
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## CI

GitHub Actions runs the unit tests on every push and pull request.
