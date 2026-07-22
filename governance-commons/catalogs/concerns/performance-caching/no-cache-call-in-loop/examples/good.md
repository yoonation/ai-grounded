<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.no-cache-call-in-loop no cache call in loop (good pattern)

Substrate-original illustration.

```python
# One batched round trip to the cache for all keys, not one per item.
def load_profiles(cache, user_ids):
    keys = [f"user-profile:v2:{uid}" for uid in user_ids]
    cached = cache.mget(keys)  # single MGET round trip
    result = {}
    misses = []
    for uid, raw in zip(user_ids, cached):
        if raw is not None:
            result[uid] = deserialize(raw)
        else:
            misses.append(uid)
    # one batched source read + one batched cache fill for the misses
    if misses:
        fetched = fetch_profiles_from_source(misses)
        pipe = cache.pipeline()
        for uid, profile in fetched.items():
            pipe.set(f"user-profile:v2:{uid}", serialize(profile), ex=300)
            result[uid] = profile
        pipe.execute()
    return result
```

## Why this satisfies the rule

The collection is read from the cache with a single `mget` and the misses
are filled with a single pipelined batch, so the number of cache round trips
is constant rather than proportional to the number of users. The cache
delivers the latency reduction it was added for.
