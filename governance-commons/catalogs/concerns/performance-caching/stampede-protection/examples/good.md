<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.stampede-protection stampede protection (good pattern)

Substrate-original illustration.

```python
# A per-key single-flight lock: only one request recomputes a hot key on a
# miss; concurrent callers wait briefly and read the freshly cached value.
def get_dashboard(cache, key, recompute):
    value = cache.get(key)
    if value is not None:
        return deserialize(value)
    lock = cache.lock(f"lock:{key}", timeout=10, blocking_timeout=5)
    if lock.acquire(blocking=True):
        try:
            value = cache.get(key)            # double-check after acquiring
            if value is not None:
                return deserialize(value)
            fresh = recompute()               # the single recomputation
            cache.set(key, serialize(fresh), ex=120)
            return fresh
        finally:
            lock.release()
    # could not acquire: fall back to a one-off recompute rather than block
    return recompute()
```

## Why this satisfies the rule

When a hot key expires and many requests miss at once, only the request that
wins the lock recomputes; the rest wait and read the value it caches. The
double-check after acquiring the lock prevents a second recomputation. The
source of record sees one recomputation, not one per concurrent request.
