<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.propagation-inheritance propagation inheritance (anti-pattern)

Substrate-original illustration.

```python
# A confidential value cached in a shared tier that cannot meet its class.
def get_profile(shared_cache, db, user_id):
    cached = shared_cache.get(f"profile:{user_id}")
    if cached:
        return cached
    profile = db.load_profile(user_id)   # confidential
    shared_cache.set(f"profile:{user_id}", profile)  # class dropped on the way in
    return profile
```

## Why this violates the rule

The confidential profile is written into a shared cache tier without carrying
its class, so the cached copy is effectively unclassified: it sits in a tier
that may not meet the confidential class's encryption and access requirements
and is readable by every consumer of the shared cache. The classification
stopped at the system of record instead of traveling with the data. Refusing
to cache the value in a tier its class forbids, or routing it to a tier that
can protect it, is the fix; this is a data-classification.propagation-inheritance finding even though the
caching mechanics are otherwise fine.
