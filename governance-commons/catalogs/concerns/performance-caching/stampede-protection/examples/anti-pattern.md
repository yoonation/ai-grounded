<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.stampede-protection stampede protection (anti-pattern)

Substrate-original illustration.

```python
# An unprotected hot key: every concurrent miss recomputes independently.
def get_dashboard(cache, key, recompute):
    value = cache.get(key)
    if value is not None:
        return deserialize(value)
    fresh = recompute()                  # every missing request runs this
    cache.set(key, serialize(fresh), ex=120)
    return fresh
```

## Why this violates the rule

When this hot key expires, every concurrent request misses and independently
calls `recompute()`, so a thousand simultaneous requests run a thousand
expensive recomputations and a thousand identical loads against the source of
record at the same instant. The cache, which exists to protect the source,
becomes a load amplifier at every expiry boundary. A per-key single-flight
lock (or request coalescing, or stale-while-revalidate) collapses the herd
to one recomputation.
