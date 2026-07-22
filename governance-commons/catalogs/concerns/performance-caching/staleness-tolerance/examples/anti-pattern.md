<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.staleness-tolerance staleness tolerance (anti-pattern)

Substrate-original illustration.

```python
# One default time-to-live copied across items with very different needs.
DEFAULT_TTL = 300  # "we just use five minutes everywhere"

def cache_value(cache, key, value):
    cache.set(key, serialize(value), ex=DEFAULT_TTL)

cache_value(cache, "marketing-banner:v1:home", banner)      # could be hours
cache_value(cache, "account-balance:v1:42", balance)        # must be fresh
```

## Why this violates the rule

A single default time-to-live is applied to every item regardless of how
stale each may acceptably be. The marketing banner, which could be cached for
hours, expires every five minutes and wastes the hit rate; the account
balance, which must be fresh, is served up to five minutes stale, which is a
correctness risk. The freshness decision was made by whoever copied the
default, not by the data. Each item needs a recorded staleness budget that
sets its time-to-live.
