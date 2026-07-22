<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.redaction redaction strategy

## Anti-pattern A: Reliance on substrate vocabulary alone

```python
# Only L1-002 substrate-recognized vocabulary is filtered
# (password, token, ssn, credit_card). Application-specific
# sensitive fields are silently logged.

log.info("contract_negotiated",
    customer_id=customer.id,
    negotiated_rate=1500.00,  # ← B2B-sensitive, not in substrate vocab
    diagnosis_code="F32.0",   # ← PHI, not in substrate vocab
    internal_score=87.4)      # ← business-sensitive
```

Why this violates logging.redaction: the application-specific
sensitive fields are not classified. L1-002 covers generic
vocabulary; L2-003 covers the application-specific gap.
Without the classification, these reach logs.

## Anti-pattern B: Deny-list approach

```python
DENY_LIST = ['password', 'ssn', 'credit_card']

def redact_field(name, value):
    if name in DENY_LIST:
        return '[REDACTED]'
    return value
```

Why this violates logging.redaction: deny-list framing requires
remembering to add every new sensitive field. A new field
(diagnosis_code) added by a feature team silently logs unless
the list is updated. The substrate-recommended posture is
allow-list framing.

## Anti-pattern C: Whole-object serialization with to_dict

```python
def log_user_action(user, action):
    log.info("user_action",
        user=user.to_dict(),  # ← bypasses redaction wrapper
        action=action)
```

Why this violates logging.redaction: to_dict() returns the model's
default serialization, which typically includes hashed
password, session token, and any PII fields. The redaction
wrapper is bypassed.

## Anti-pattern D: Debug bypass

```python
DEBUG = os.environ.get('DEBUG') == 'true'

def authenticate(user, password):
    if DEBUG:
        log.debug("auth_attempt", user_id=user.id, password=password)
    # Production path correctly avoids password in log
    if not user.verify(password):
        log.warning("auth_failed", user_id=user.id)
```

Why this violates logging.redaction: the debug path logs the raw
password. If DEBUG is set in any environment (a misconfigured
staging, a forgotten dev flag), credentials reach logs.

## Anti-pattern E: Application-scoped salt for hashing

```python
# Salt is the same as the application's encryption salt
SALT = config['ENCRYPTION_SALT']

def hash_for_log(value):
    return hashlib.sha256(SALT + value.encode()).hexdigest()
```

Why this violates logging.redaction: an application-scoped salt is
exposed in more contexts than logging. An attacker with
encryption-salt access can produce the same hashes for
known inputs (rainbow-table attack against the log hashes).
The substrate-recommended scope is logging-pipeline-specific.

## Anti-pattern F: No pipeline-side defense

```yaml
# Aggregator has no scrubbing configured;
# relies entirely on call-site discipline.
aggregator:
  ingest_pipeline: []  # ← no scrubbing rules
```

Why this violates logging.redaction: the aggregator has no
defense-in-depth scrubbing. When a call site accidentally
emits sensitive data (e.g., during a new code path), the
disclosure reaches the aggregator unmitigated.

## Anti-pattern G: Exception logging via str(e)

```python
class PaymentError(Exception):
    def __init__(self, card_token, reason):
        self.card_token = card_token
        self.reason = reason
        super().__init__(f"Payment failed for {card_token}: {reason}")

try:
    process_payment(card_token)
except PaymentError as e:
    log.error(f"payment_error: {e}")  # ← includes card_token
```

Why this violates logging.redaction: the exception's __str__ method
returns the card_token in the message. log.error then logs
that. Sensitive data reaches the aggregator via the
exception channel.

## Cross-reference

- Good patterns: examples/logging/redaction-good.md
- Substrate rule: logging.redaction
