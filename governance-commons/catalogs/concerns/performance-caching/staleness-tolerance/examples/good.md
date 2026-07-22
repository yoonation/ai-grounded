<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.staleness-tolerance staleness tolerance (good pattern)

Substrate-original illustration.

```python
# Time-to-live is derived from a recorded staleness budget per data class,
# not a single copied default.
STALENESS_BUDGET = {
    "marketing-banner": 3600,   # tolerates-hours
    "product-summary":   300,   # tolerates-minutes
    "account-balance":   None,  # must-be-fresh: not cached, read-through only
}

def cache_value(cache, data_class, key, value):
    ttl = STALENESS_BUDGET[data_class]
    if ttl is None:
        return  # must-be-fresh class is never cached
    cache.set(key, serialize(value), ex=ttl)
```

## Why this satisfies the rule

Each data class has an explicit, recorded staleness budget, and the
time-to-live follows from it: a banner that may be an hour old is cached for
an hour, a product summary for minutes, and an account balance (must be
fresh) is not cached at all. The freshness decision is deliberate rather
than inherited from a copied default.
