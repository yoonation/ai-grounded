<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.ttl-on-write TTL on write (anti-pattern)

Substrate-original illustration.

```python
# A cache write with no expiry: the entry is eternal.
def cache_user_profile(cache, user_id, profile):
    key = f"user-profile:{user_id}"
    cache.set(key, serialize(profile))   # no ex= : never expires
```

## Why this violates the rule

The write sets no time-to-live, so the entry is unbounded in two ways. Its
staleness is unbounded: if a later write fails to invalidate this key, the
old profile is served forever. Its lifetime is unbounded: the entry is freed
only by explicit deletion or by eviction under memory pressure, so a cache
of eternal entries grows until it hits its ceiling and evicts entries that
are still wanted. The fix is a single explicit `ex=` sized to a staleness
budget.
