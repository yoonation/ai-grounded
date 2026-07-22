<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.no-sensitive-data-in-logs no sensitive data in logs (good patterns)

Substrate-original good-pattern examples for logging.no-sensitive-data-in-logs.

## Pattern A: Type-level redaction wrapper

```python
from typing import NewType
import structlog

class SensitiveString:
    def __init__(self, value: str):
        self._value = value

    def __repr__(self) -> str:
        return "[REDACTED]"

    def __str__(self) -> str:
        return "[REDACTED]"

    def reveal(self) -> str:
        return self._value


def authenticate(user_id: str, password: SensitiveString):
    log = structlog.get_logger()
    log.info("auth_attempt", user_id=user_id, password=password)
    user = users.find(user_id)
    if user and user.verify(password.reveal()):
        return user
    return None
```

Why this satisfies logging.no-sensitive-data-in-logs: the SensitiveString wrapper's
__repr__ and __str__ return the redaction marker. The
structured logger serializes the wrapper via its repr; the
raw password value never reaches the log record.

## Pattern B: Explicit field selection avoiding whole-object logging

```python
from structlog import get_logger

log = get_logger()

def log_user_action(user, action):
    log.info("user_action",
        user_id=user.id,
        action=action,
        role=user.role,
    )
```

Why this satisfies logging.no-sensitive-data-in-logs: explicit field selection
includes only fields the consumer has confirmed are safe to
log. The whole user object (which might include password
hashes, session tokens, PII) is never serialized.

## Pattern C: Salted-hash for correlation without disclosure

```python
import hashlib
import os

# Salt is logging-pipeline-scoped, not application-scoped.
LOGGING_HASH_SALT = os.environ["LOGGING_HASH_SALT"]

def hash_for_logging(value: str) -> str:
    return hashlib.sha256(
        (LOGGING_HASH_SALT + value).encode()
    ).hexdigest()[:16]

log.info("payment_attempt",
    user_id=user.id,
    card_token_hash=hash_for_logging(card_token))
```

Why this satisfies logging.no-sensitive-data-in-logs: the card token never appears
in logs. The salted hash is stable within the pipeline for
join correlation but does not enable re-identification
outside the pipeline (the salt prevents rainbow-table attack).

## Pattern D: Express middleware that strips request body before logging

```javascript
const pinoHttp = require('pino-http')({
    serializers: {
        req: (req) => ({
            method: req.method,
            url: req.url,
            id: req.id,
        }),
        res: (res) => ({
            statusCode: res.statusCode,
        }),
    },
});

app.use(pinoHttp);
```

Why this satisfies logging.no-sensitive-data-in-logs: the serializers stanza
explicitly enumerates request fields safe to log. The
request body, headers, and query parameters are excluded by
default.

## Pattern E: Java MDC with sensitive value strip

```java
public class SensitiveDataFilter implements LoggingEventFilter {
    private static final List<String> SENSITIVE_KEYS = List.of(
        "password", "token", "ssn", "credit_card", "api_key"
    );

    @Override
    public LoggingEvent transform(LoggingEvent event) {
        Map<String, String> mdc = new HashMap<>(event.getMDCPropertyMap());
        for (String key : SENSITIVE_KEYS) {
            if (mdc.containsKey(key)) {
                mdc.put(key, "[REDACTED]");
            }
        }
        return event.withMDCPropertyMap(mdc);
    }
}
```

Why this satisfies logging.no-sensitive-data-in-logs: a defense-in-depth filter
strips sensitive keys from the MDC (slf4j's structured
context) before the record is serialized. Even if a call site
forgets discipline, the filter catches the substrate-
recognized vocabulary.

## Pattern F: Exception logging with sanitized summary

```python
try:
    user = authenticate(credentials)
except AuthenticationError as e:
    log.warning("authentication_failed",
        exception_type=type(e).__name__,
        reason_code=e.code,
        user_id=credentials.user_id)
```

Why this satisfies logging.no-sensitive-data-in-logs: exception logging captures the
type and a structured reason code, not str(e) which could
contain the rejected credentials, request body content, or
PII. The user_id is logged explicitly because the consumer
has confirmed user_id (an opaque identifier) is safe.

## Cross-reference

- Anti-patterns: examples/logging/no-sensitive-data-in-logs-anti-pattern.md
- Substrate rule: logging.no-sensitive-data-in-logs
- Related: secrets-management secrets-management.no-secrets-in-logs
