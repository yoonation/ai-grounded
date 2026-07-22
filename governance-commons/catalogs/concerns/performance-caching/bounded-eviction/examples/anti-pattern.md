<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.bounded-eviction bounded eviction (anti-pattern)

Substrate-original illustration.

```ini
# Distributed cache backend with no bound and no eviction policy.
# (no maxmemory set)
# (no maxmemory-policy set; defaults to noeviction)
```

```python
# In-process cache as an unbounded dictionary fed by a high-cardinality key.
_render_cache = {}   # never bounded, never evicted

def render_fragment(fragment_id, locale, user_id):
    key = (fragment_id, locale, user_id)        # per-user: high cardinality
    if key not in _render_cache:
        _render_cache[key] = expensive_render(fragment_id, locale, user_id)
    return _render_cache[key]
```

## Why this violates the rule

The distributed backend sets no maximum memory and no eviction policy, so it
grows until it exhausts the host and then, under the default no-eviction
policy, begins refusing writes. The in-process dictionary is unbounded and
keyed per user, so a high-cardinality key space grows it without limit (a
reliability.bounded-buffers unbounded-collection finding). Both need a configured bound: a
maxmemory plus an LRU policy on the backend, and a bounded LRU structure in
process.
