<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.graceful-degradation graceful degradation (anti-pattern)

Substrate-original illustration. A non-critical dependency is on the
critical path with no fallback and no timeout, so its failure or slowness
takes down the whole page.

```python
async def render_product_page(product_id: str) -> Page:
    base = await load_product(product_id)
    # Recommendations are non-critical, but here a failure propagates
    # and a hang blocks the page indefinitely. No fallback, no timeout.
    recs = await recs_client.get(product_id)
    return Page(product=base, recommendations=recs)
```

Why this fails the rule: a dependency whose loss should be invisible
(missing recommendations) instead fails the entire request, because there
is no fallback and the exception propagates. Worse, with no timeout a
hung recommendation service hangs every product page. The fix is to
classify the dependency degradable and give it a bounded, observable
fallback as in the good example.
