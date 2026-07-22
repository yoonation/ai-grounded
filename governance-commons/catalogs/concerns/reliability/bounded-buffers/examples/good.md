<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.bounded-buffers bounded buffers (good pattern)

Substrate-original illustration. The in-memory work queue is constructed
with an explicit bound, so a producer that outruns the consumer applies
backpressure (or sheds) rather than growing the queue until the process
is killed.

```python
import asyncio

# Bounded: maxsize caps in-flight work. put() awaits when full,
# which propagates backpressure to the producer.
work_queue: asyncio.Queue[Job] = asyncio.Queue(maxsize=1000)

async def produce(job: Job) -> None:
    # If the consumer has fallen behind, this awaits rather than
    # letting the queue grow without limit.
    await work_queue.put(job)

# An in-process cache with a capacity and eviction, not an unbounded dict.
from functools import lru_cache

@lru_cache(maxsize=10_000)
def resolve(symbol: str) -> Rate:
    return _expensive_lookup(symbol)
```

Why this satisfies the rule: the queue and the cache both have a declared
upper bound. Under sustained overload the service fails fast and
predictably (backpressure or eviction) instead of dying slowly from
memory exhaustion. The chosen bound values are justified against the
instance memory budget in the reliability.failure-isolation sizing review.
