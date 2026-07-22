<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.retention-limitation retention period per category, deletion at expiry (good pattern)

Substrate-original illustration.

```python
# Each category has a retention period and a job that enforces expiry.
RETENTION = {"support_ticket": days(365), "marketing_event": days(180)}

def enforce_retention(now) -> None:
    for category, period in RETENTION.items():
        for record in store.older_than(category, now - period):
            store.delete(record)        # or irreversible anonymization
```

## Why this satisfies the rule

Each personal-data category has a defined retention period tied to its purpose,
and an actual job deletes the data once the period elapses rather than leaving the
policy on paper. The expiry action is irreversible. Logging-sink retention is
coordinated with logging.retention-policy rather than redefined here.
