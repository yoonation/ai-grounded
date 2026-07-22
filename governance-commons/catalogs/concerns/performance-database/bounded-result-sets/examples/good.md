<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.bounded-result-sets bounded result sets (good pattern)

Substrate-original illustration. The collection endpoint paginates with an
explicit page size and a stable, indexed order, so its cost is bounded
regardless of table size.

```python
PAGE_SIZE = 50

def list_orders(cursor: str | None):
    q = Order.objects.order_by("-created_at", "id")
    if cursor:
        q = q.filter(created_at__lt=decode(cursor))
    rows = list(q[:PAGE_SIZE])
    return rows, encode_cursor(rows)
```

Why this satisfies the rule: the slice bounds the rows the query returns to
the page size, and the deterministic order makes pages stable. The endpoint
costs the same whether the table holds a thousand orders or ten million.
