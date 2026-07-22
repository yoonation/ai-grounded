<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.failure-isolation failure isolation (good pattern)

Substrate-original illustration. Each downstream dependency has its own
bounded concurrency, so one slow dependency saturating its own limit
cannot consume the capacity the others need.

```python
# Separate bulkheads: a slow or failing "search" cannot exhaust the
# connections that "checkout" needs. Each pool is sized to its
# dependency, not shared globally.
search_sem = asyncio.Semaphore(20)
checkout_sem = asyncio.Semaphore(40)

async def call_search(q: Query) -> Results:
    async with search_sem:                    # bounded to search
        async with asyncio.timeout(0.5):
            return await search_client.query(q)

async def call_checkout(order: Order) -> Receipt:
    async with checkout_sem:                  # bounded to checkout
        async with asyncio.timeout(2.0):
            return await checkout_client.submit(order)
```

Why this satisfies the rule: search and checkout occupy distinct failure
domains with independent concurrency limits. When search slows and fills
its 20 permits, checkout still has its own 40. One dependency's trouble
stays contained to that dependency's traffic. The bulkhead sizes are
justified in the reliability.reliability-strategy isolation model.
