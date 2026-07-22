<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.lawful-basis-and-consent lawful basis recorded, consent checked and withdrawable (good pattern)

Substrate-original illustration.

```python
# Consent-based processing checks a valid consent first; withdrawal halts it.
def send_marketing(subject_id: str) -> None:
    if not consent.is_valid(subject_id, purpose="marketing"):
        return  # no valid consent: do not process
    mailer.send(subject_id)

def withdraw_marketing_consent(subject_id: str) -> None:
    consent.withdraw(subject_id, purpose="marketing")  # stops the processing above
```

## Why this satisfies the rule

The processing that relies on consent checks for a valid, purpose-specific
consent before it runs, and a withdrawal halts the dependent processing and is as
easy to exercise as the grant. The basis (consent) is recorded per purpose. Which
basis is correct for the purpose is informed by the privacy.lawful-basis-and-consent-policy policy.
