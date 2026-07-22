<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.ttl-on-write TTL on write (good pattern)

Substrate-original illustration.

```python
# Every cache write sets an explicit, bounded time-to-live derived from the
# value's recorded staleness budget (performance-caching.staleness-tolerance).
PROFILE_TTL = 300  # seconds; "tolerates-minutes" staleness budget

def cache_user_profile(cache, user_id, profile):
    key = f"user-profile:v2:{user_id}"
    cache.set(key, serialize(profile), ex=PROFILE_TTL)
```

## Why this satisfies the rule

The write passes an explicit expiry (`ex=PROFILE_TTL`), so the entry cannot
serve unbounded staleness and cannot occupy memory indefinitely. The
duration traces to a recorded staleness budget rather than a copied default.
Even if a later write fails to invalidate this key, the time-to-live bounds
the worst-case staleness to five minutes.
