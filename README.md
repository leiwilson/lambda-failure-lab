# lambda-failure-lab

Lab scenarios for Lambda-style failure modes: timeouts, transient retries, and throttling.
Includes a small client-side exponential backoff helper for exercising those failures.

## Scenarios

- `scenarios/timeout` — handler that can sleep past a configured timeout
- `scenarios/retry` — handler that raises a transient error
- `scenarios/throttle` — handler that simulates 429 / rate-limit responses

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
