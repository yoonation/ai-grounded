<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.failure-isolation failure isolation (anti-pattern)

Substrate-original illustration. All downstream calls share one global
connection pool, so a single slow dependency consumes every connection
and starves unrelated, critical work.

```python
# One shared pool for everything. When "search" slows down, every
# in-flight search holds a connection until it times out, and
# "checkout" cannot get a connection at all.
shared_pool = ConnectionPool(max_connections=50)

async def call_search(q: Query) -> Results:
    async with shared_pool.acquire() as conn:
        return await conn.request(search_url, q)   # slow path

async def call_checkout(order: Order) -> Receipt:
    async with shared_pool.acquire() as conn:      # starves here
        return await conn.request(checkout_url, order)
```

Why this fails the rule: there is no bulkhead. A slowdown in the
non-critical search path drains the shared pool, and the critical
checkout path fails for lack of connections, even though checkout's own
dependency is perfectly healthy. This is the canonical cascading failure
the rule exists to prevent. The fix is per-dependency concurrency limits
as in the good example.
