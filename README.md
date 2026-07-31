# lambda-failure-lab

Lab scenarios for Lambda-style failure modes: timeouts and transient retries.

## Scenarios

- `scenarios/timeout` — handler that can sleep past a configured timeout
- `scenarios/retry` — handler that raises a transient error

## Tests

```bash
python -m unittest tests/test_handlers.py
```
