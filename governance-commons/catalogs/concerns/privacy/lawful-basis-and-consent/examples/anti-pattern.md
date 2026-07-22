<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.lawful-basis-and-consent lawful basis recorded, consent checked and withdrawable (anti-pattern)

Substrate-original illustration.

```python
# A single blanket "I agree" gates everything, and processing never re-checks it.
def on_signup(user):
    user.agreed_to_terms = True   # one bundled flag for all processing

def send_marketing(subject_id: str) -> None:
    mailer.send(subject_id)       # never checks a purpose-specific consent
```

## Why this violates the rule

A single bundled agreement is treated as consent for every purpose, so the
consent is neither specific nor freely given, and the marketing path never checks
a purpose-specific consent or honors a withdrawal. The consent is not valid by
construction. Requesting consent per purpose, checking it before processing, and
honoring withdrawal is the fix.
