<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.bounded-eviction bounded eviction (good pattern)

Substrate-original illustration.

```ini
# Distributed cache backend: a configured maximum memory and an LRU
# eviction policy, so the cache degrades predictably when full.
maxmemory 2gb
maxmemory-policy allkeys-lru
```

```python
# In-process cache: a bounded-capacity LRU, not an unbounded dictionary.
from functools import lru_cache

@lru_cache(maxsize=1024)   # bounded; evicts least-recently-used at capacity
def render_template_fragment(fragment_id, locale):
    return expensive_render(fragment_id, locale)
```

## Why this satisfies the rule

The distributed backend declares both a maximum memory and an eviction
policy appropriate to a cache, so it sheds the least-recently-used entries
instead of exhausting the host. The in-process cache uses a bounded LRU with
an explicit `maxsize`, so it cannot grow without limit (which would
otherwise be a reliability.bounded-buffers unbounded-collection finding).
