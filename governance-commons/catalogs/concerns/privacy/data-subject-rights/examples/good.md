<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.data-subject-rights rights reach every store (good pattern)

Substrate-original illustration.

```python
# Erasure and access fan out to every store in the inventory, not just primary.
STORES = [primary_db, cache, search_index, warehouse]

def erase_subject(subject_id: str) -> None:
    for store in STORES:
        store.erase(subject_id)         # derived copies included
    backups.schedule_expiry(subject_id) # backups handled by expiry / crypto-shred

def export_subject(subject_id: str) -> dict:
    return merge(store.read(subject_id) for store in STORES)
```

## Why this satisfies the rule

Both erasure and access fan out to every store that holds the subject's personal
data, including derived copies, with backups handled by their own expiry. The
right is operable end to end rather than only in the primary database. How the
propagation is designed is the privacy.data-subject-rights-and-retention architecture decision.
