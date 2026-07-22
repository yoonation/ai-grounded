<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.no-cache-call-in-loop no cache call in loop (anti-pattern)

Substrate-original illustration.

```python
# One cache round trip per item: the cache N+1.
def load_profiles(cache, user_ids):
    result = {}
    for uid in user_ids:                       # N iterations
        raw = cache.get(f"user-profile:v2:{uid}")  # one round trip each
        if raw is not None:
            result[uid] = deserialize(raw)
    return result
```

## Why this violates the rule

A single-key `get` is issued once per user inside the loop, so a request for
500 users makes 500 sequential round trips to the cache. The fixed cost of
each round trip is multiplied by the collection size, and the collection
size grows with load. The cache was added to reduce latency, and this
pattern reintroduces it. A single `mget` over the collected keys replaces
the loop with one round trip.
