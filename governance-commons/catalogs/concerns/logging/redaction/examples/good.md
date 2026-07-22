<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.redaction redaction strategy (good patterns)

## Pattern A: Documented per-field redaction policy

```yaml
# /docs/security/redaction-policy.yaml
version: 1.2
last-reviewed: 2026-04-15

fields:
  user_id:
    handling: allow-list
    rationale: "Opaque identifier, no disclosure risk"

  email:
    handling: hash-for-join
    rationale: "Join key for correlation; raw value is PII"

  password:
    handling: exclude
    rationale: "Authentication credential; substrate vocabulary"

  ssn:
    handling: exclude
    rationale: "PII; substrate vocabulary"

  negotiated_rate:
    handling: redact-on-emission
    rationale: "B2B contract term; application-specific sensitive"

  diagnosis_code:
    handling: exclude
    rationale: "PHI; HIPAA-protected"

  internal_score:
    handling: hash-for-join
    rationale: "Risk score; correlatable but not raw-loggable"
```

Why this satisfies logging.redaction: each sensitive field has an
explicit handling, a documented rationale, and the policy is
dated.

## Pattern B: Allow-list logger plugin

```python
import structlog

ALLOW_LISTED_FIELDS = {
    "user_id", "request_id", "trace_id", "service", "endpoint",
    "status_code", "latency_ms", "error_code", "event",
}

def allow_list_filter(_, __, event_dict):
    """Drop or redact fields not on the allow list."""
    safe = {}
    for k, v in event_dict.items():
        if k in ALLOW_LISTED_FIELDS:
            safe[k] = v
        elif k.startswith('_'):
            safe[k] = v  # internal substrate fields preserved
        else:
            safe[k] = "[UNCLASSIFIED-FIELD]"
    return safe

structlog.configure(
    processors=[
        allow_list_filter,
        structlog.processors.JSONRenderer(),
    ]
)
```

Why this satisfies logging.redaction: the allow-list framing
ensures new fields default to redaction. Adding a new field
to log requires explicit classification.

## Pattern C: Salted-hash for join-correlatable PII

```python
import hashlib
import os

LOGGING_HASH_SALT = os.environ['LOGGING_HASH_SALT']

def hash_for_logging(value: str) -> str:
    if value is None:
        return None
    return hashlib.sha256(
        (LOGGING_HASH_SALT + str(value)).encode()
    ).hexdigest()[:16]

def log_user_event(user, event):
    log.info("user_event",
        user_id=user.id,
        email_hash=hash_for_logging(user.email),
        event=event)
```

Why this satisfies logging.redaction: email is hashed with a
pipeline-scoped salt. Join correlation across records is
preserved (same email produces same hash); disclosure is
prevented (raw email never reaches logs); rainbow-table
re-identification by an external attacker is prevented (the
salt is not exposed outside the pipeline).

## Pattern D: Pipeline-side scrubbing as defense in depth

```yaml
# Datadog log scrubbing rules
processors:
  - type: pii-scanner
    name: credit-card
    pattern: '\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}'
    replacement: '[REDACTED-CC]'
  - type: pii-scanner
    name: pem-private-key
    pattern: '-----BEGIN [A-Z ]+PRIVATE KEY-----'
    replacement: '[REDACTED-KEY]'
  - type: pii-scanner
    name: jwt-token
    pattern: 'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
    replacement: '[REDACTED-JWT]'
```

Why this satisfies logging.redaction: the aggregator scrubs known
patterns even when the call site has not redacted them. The
finding triggers a security review of how the pattern
reached the aggregator.

## Pattern E: Debug logging that respects redaction

```python
def debug_user_state(user):
    if not log.isEnabledFor(logging.DEBUG):
        return
    # Even debug path applies redaction
    log.debug("user_state",
        user_id=user.id,
        email_hash=hash_for_logging(user.email),
        # Note: full user object is NOT logged
        role=user.role,
        last_login=user.last_login)
```

Why this satisfies logging.redaction: the debug path does not
bypass redaction. A developer running with DEBUG enabled
sees the same redacted output as production logs. Un-
redacted access for debugging requires an out-of-band,
approval-gated procedure.

## Pattern F: Application-specific field with explicit redaction

```python
from dataclasses import dataclass

@dataclass
class NegotiatedRate:
    """B2B contract negotiated price; sensitive per logging.redaction."""
    value: float
    currency: str

    def __repr__(self):
        return f"NegotiatedRate(value=[REDACTED], currency={self.currency!r})"

    def __str__(self):
        return self.__repr__()


# In the application:
rate = NegotiatedRate(value=1500.00, currency="USD")
log.info("contract_negotiated",
    customer_id=customer.id,
    rate=rate)  # ← serializes via __repr__
```

Why this satisfies logging.redaction: an application-specific
sensitive type carries its own redaction. The type-system
enforcement is consistent across every call site that
serializes the value.

## Cross-reference

- Anti-patterns: examples/logging/redaction-anti-pattern.md
- Substrate rule: logging.redaction
- Review checklist: checklist.md
