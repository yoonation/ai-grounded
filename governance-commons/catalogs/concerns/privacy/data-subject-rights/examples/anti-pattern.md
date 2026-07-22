<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.data-subject-rights rights reach every store (anti-pattern)

Substrate-original illustration.

```python
# Erasure touches only the primary database; copies live on elsewhere.
def erase_subject(subject_id: str) -> None:
    primary_db.erase(subject_id)   # cache, search index, warehouse still hold it
```

## Why this violates the rule

The erasure removes the subject from the primary database only, leaving copies in
the cache, the search index, and the warehouse, so the right to erasure is partial
in a way the subject cannot see. A right that does not reach every store is not
operable. Fanning out to every store in the inventory, with backups governed by
expiry, is the fix.
