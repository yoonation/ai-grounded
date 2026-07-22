<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.retention-disposal retention disposal (anti-pattern)

Substrate-original illustration.

```python
# Classified records retained indefinitely with no disposal schedule.
def archive_order(store, order):
    store.put(order)   # written once, never expired

# there is no purge job; nothing ever deletes classified records
```

## Why this violates the rule

Classified records are written and never disposed of, so they accumulate
indefinitely. Every record kept past its purpose enlarges the blast radius of
any future breach, lengthens the window for misuse, and increases the burden
of any deletion obligation, all while providing no further value. A per-class
retention period with a scheduled purge that also reaches backups and derived
copies is the fix.
