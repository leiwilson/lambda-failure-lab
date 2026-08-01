# lambda-failure-lab

Lab scenarios for Lambda-style failure modes: timeouts, transient retries, and throttling.

## Scenarios

- `scenarios/timeout` — handler that can sleep past a configured timeout
- `scenarios/retry` — handler that raises a transient error
- `scenarios/throttle` — handler that simulates 429 / rate-limit responses

## Tests

```bash
python -m unittest tests/test_handlers.py
```
