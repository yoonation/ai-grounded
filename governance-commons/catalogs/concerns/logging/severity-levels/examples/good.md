<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.severity-levels severity levels (good patterns)

## Pattern A: Severity-named methods (Python)

```python
log.debug("cache lookup", key=key, hit=hit)
log.info("user_login", user_id=user.id)
log.warning("retry_attempt", attempt=n, max_attempts=3)
log.error("payment_failed", reason_code=code)
log.critical("circuit_breaker_open", service="payments")
```

Why this satisfies logging.severity-levels: each call uses a severity-
named method from the standard logging vocabulary. The
serialized output includes the severity field with a value
from the documented RFC 5424 / OpenTelemetry-aligned set.

## Pattern B: Severity-named methods (Node.js pino)

```javascript
log.debug({ key, hit }, 'cache lookup');
log.info({ user_id }, 'user login');
log.warn({ attempt, max_attempts }, 'retry attempt');
log.error({ reason_code }, 'payment failed');
log.fatal({ service }, 'circuit breaker open');
```

Why this satisfies logging.severity-levels: pino's severity methods map to
its built-in vocabulary (trace, debug, info, warn, error,
fatal); each emitted record carries a "level" field.

## Pattern C: Severity-named methods (Go zerolog)

```go
log.Debug().Str("key", key).Bool("hit", hit).Msg("cache lookup")
log.Info().Str("user_id", userID).Msg("user login")
log.Warn().Int("attempt", n).Msg("retry attempt")
log.Error().Str("reason_code", code).Msg("payment failed")
log.Fatal().Str("service", "payments").Msg("circuit breaker open")
```

Why this satisfies logging.severity-levels: zerolog's level methods emit
records with the standard severity field. The fluent API does
not allow a level-less call.

## Pattern D: Logger configuration that includes severity field

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
```

Why this satisfies logging.severity-levels: the add_log_level processor
ensures every record carries the level field even when
upstream call sites use generic logger interfaces. The
processor is configured at the logger setup, not per call
site.

## Pattern E: Java slf4j severity mapping

```java
private static final Logger log = LoggerFactory.getLogger(MyService.class);

log.trace("cache lookup key={} hit={}", key, hit);
log.debug("fetched user user_id={}", userId);
log.info("user_login user_id={}", userId);
log.warn("retry_attempt attempt={} max={}", n, maxN);
log.error("payment_failed reason_code={}", code);
```

Why this satisfies logging.severity-levels: slf4j's severity methods map
to the standard vocabulary; the underlying appender records
the severity field in the structured output.

## Pattern F: Startup-time validation of severity in output

```python
import json
from io import StringIO
import logging

def validate_logger_emits_severity():
    """Run at app startup; fail-fast if severity is absent."""
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    handler.setFormatter(JsonFormatter())
    test_logger = logging.getLogger("startup-check")
    test_logger.addHandler(handler)
    test_logger.info("startup_check_sentinel")
    record = json.loads(buf.getvalue())
    if "level" not in record and "levelname" not in record:
        raise RuntimeError("logger does not emit severity field")
```

Why this satisfies logging.severity-levels: the startup-time check
captures a sample log record, parses it, and confirms the
severity field is present. Configuration drift that removes
the severity is caught before the application accepts
traffic.

## Cross-reference

- Anti-patterns: examples/logging/severity-levels-anti-pattern.md
- Substrate rule: logging.severity-levels
