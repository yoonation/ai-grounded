<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.bounded-buffers bounded buffers (anti-pattern)

Substrate-original illustration. The queue and cache are unbounded, so a
burst or a slow consumer accumulates in memory until the process is
OOM-killed. The static binding flags the unbounded constructors.

```python
import asyncio

# Unbounded: no maxsize. A fast producer with a slow consumer grows
# this without limit until the event-loop process is killed.
work_queue: asyncio.Queue = asyncio.Queue()

async def produce(job):
    work_queue.put_nowait(job)  # never blocks, never sheds

# Module-level dict used as a cache, keyed on a per-request value,
# with no eviction. Grows for the life of the process.
_rate_cache = {}

def resolve(symbol):
    if symbol not in _rate_cache:
        _rate_cache[symbol] = _expensive_lookup(symbol)
    return _rate_cache[symbol]
```

Why this fails the rule: neither structure has an upper bound. The queue
is unbounded by construction (reliability.bounded-buffers static finding), and the cache
grows once per distinct key with no eviction. The failure mode is a slow
memory climb that ends in a crash, often far from the code that caused
it. The fix is an explicit maxsize on the queue and a capacity-bounded
cache with eviction.
