<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.retention-limitation retention period per category, deletion at expiry (anti-pattern)

Substrate-original illustration.

```python
# No retention period and no expiry mechanism: personal data accumulates forever.
def save_event(event) -> None:
    store.insert(event)   # kept indefinitely, no category period, no deletion job
```

## Why this violates the rule

Personal data is written and kept indefinitely with no defined retention period
per category and no mechanism that deletes or anonymizes at expiry, so the data
becomes risk with no offsetting purpose. Defining a period per category and a job
that deletes or irreversibly anonymizes at expiry is the fix.
