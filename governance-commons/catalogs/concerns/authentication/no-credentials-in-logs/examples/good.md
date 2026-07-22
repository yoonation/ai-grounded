<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.no-credentials-in-logs credentials in logs (good patterns)

Substrate-original good-pattern examples for authentication.no-credentials-in-logs.

## Pattern A: Log user identifier, never credential (Python)

```python
import logging
logger = logging.getLogger(__name__)

# Log authentication events with user identifier only.
# The password is never named as a log argument.
def login(username, password):
    user = authenticate(username, password)
    if user:
        logger.info("Authentication success", extra={"user_id": user.id})
        return user
    else:
        # Failure path also logs user_id when available, or
        # the supplied username (which is not a credential).
        # Never logs the password.
        logger.info("Authentication failure", extra={"username": username})
        return None
```

Why this satisfies authentication.no-credentials-in-logs:
- Credential variable never appears as a log argument
- Log includes useful context (user_id, username) without secrets
- Failure path is symmetric with success path for log content

## Pattern B: Structured logging with redaction filter (Python / structlog)

```python
import structlog

# Configure structlog with a processor that redacts known
# credential field names from any log event.
def redact_credentials(logger, method_name, event_dict):
    sensitive_keys = {
        "password", "passwd", "pwd",
        "token", "access_token", "refresh_token",
        "secret", "api_key", "apikey",
        "authorization", "cookie", "session_id",
    }
    for key in list(event_dict.keys()):
        if key.lower() in sensitive_keys:
            event_dict[key] = "[REDACTED]"
    return event_dict

structlog.configure(
    processors=[
        redact_credentials,
        structlog.processors.JSONRenderer(),
    ],
)

# Even if a credential variable is accidentally passed to log
# context, the filter redacts it before serialization.
log = structlog.get_logger()
log.info("api_request", api_key=api_key)
# Output: {"event": "api_request", "api_key": "[REDACTED]"}
```

Why this satisfies authentication.no-credentials-in-logs:
- Structured logging with explicit redaction processor
- Defense in depth: even accidental inclusion is caught
- Configuration is centralized

## Pattern C: Token fingerprint instead of full token (Python)

```python
import hashlib
import logging
logger = logging.getLogger(__name__)

def token_fingerprint(token):
    # First 8 chars of SHA-256 hex digest. Useful for
    # correlation in logs without revealing the token.
    return hashlib.sha256(token.encode()).hexdigest()[:8]

def verify_token(token):
    user = lookup_user_by_token(token)
    if user:
        logger.info(
            "Token verified",
            extra={
                "user_id": user.id,
                "token_fp": token_fingerprint(token),
            },
        )
        return user
    else:
        logger.warning(
            "Token verification failed",
            extra={"token_fp": token_fingerprint(token)},
        )
        return None
```

Why this satisfies authentication.no-credentials-in-logs:
- Fingerprint allows correlation across log entries
- Full token never appears in logs
- Reversing fingerprint to recover token is computationally
  intractable

## Pattern D: Express middleware with redacted request body (Node.js)

```javascript
const pino = require("pino");

const logger = pino({
  // Pino built-in redaction. Configured field names are
  // replaced with [Redacted] in all log output.
  redact: {
    paths: [
      "req.headers.authorization",
      "req.headers.cookie",
      "req.body.password",
      "req.body.token",
      "req.body.api_key",
      "res.headers.authorization",
    ],
    censor: "[REDACTED]",
  },
});

app.use((req, res, next) => {
  logger.info({ req }, "request received");
  next();
});
```

Why this satisfies authentication.no-credentials-in-logs:
- Framework-level redaction for known credential field names
- Catches credentials at log-emission time, not at log call sites
- Works even when third-party middleware logs request data

## What good patterns have in common

- Log identifiers (user_id, request_id, correlation_id), never
  credentials
- When credential context is needed (debugging, correlation),
  use a fingerprint or masked form
- Centralize redaction in the logging framework configuration
- Symmetric logging for success and failure to avoid leaking
  cause via log presence

## Cross-reference

- Substrate rule: authentication.no-credentials-in-logs in catalogs/concerns/authentication.oscal.yaml
- Tool binding: checklist.md
- Anti-patterns: examples/authentication/credentials-in-logs-anti-pattern.md
