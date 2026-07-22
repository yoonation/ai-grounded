<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.graceful-degradation graceful degradation (good pattern)

Substrate-original illustration. A degradable dependency (a product-
recommendation service) has a defined fallback that triggers on both
failure and slowness, and the degraded state is recorded.

```python
async def render_product_page(product_id: str) -> Page:
    base = await load_product(product_id)        # critical
    recs = await _recommendations_or_fallback(product_id)
    return Page(product=base, recommendations=recs)

async def _recommendations_or_fallback(product_id: str) -> list[Rec]:
    try:
        # Short timeout: a slow recs service must not slow the page.
        async with asyncio.timeout(0.15):
            return await recs_client.get(product_id)
    except (RecsError, asyncio.TimeoutError):
        metrics.increment("recs.degraded")       # observable
        return _popular_fallback(product_id)      # defined fallback
```

Why this satisfies the rule: the recommendation dependency is classified
degradable, its loss yields a documented fallback (popular items) rather
than a failed page, the fallback triggers on slow as well as failed, and
the degradation is counted so operators can see it. The critical
dependency (the product itself) is not degraded.
