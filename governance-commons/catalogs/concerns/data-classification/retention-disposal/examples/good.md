<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.retention-disposal retention disposal (good pattern)

Substrate-original illustration.

```python
# A per-class retention period with a scheduled purge that also covers
# backups and derived copies.
RETENTION_DAYS = {
    "internal": 365,
    "confidential": 730,
    "restricted": 1095,   # bounded by business purpose, not indefinite
}

def purge_expired(store, backups, exports, now):
    cutoff = {cls: now - days(d) for cls, d in RETENTION_DAYS.items()}
    for record in store.iter_classified():
        if record.created_at < cutoff[record.data_classification]:
            store.delete(record.id)
            backups.delete(record.id)     # disposal reaches backups
            exports.delete(record.id)     # and derived copies
```

## Why this satisfies the rule

Each class has a bounded retention period, and a scheduled purge deletes
records past their period from the primary store, the backups, and the
derived exports. Data does not accumulate indefinitely, and a disposed record
does not survive in a snapshot or an export.
