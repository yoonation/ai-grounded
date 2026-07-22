<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.replica-routing replica routing (good pattern)

Substrate-original illustration. A read-your-writes path reads the primary;
a lag-tolerant analytics read uses a replica.

```python
def order_confirmation(order_id):
    # User just placed this order: must see their own write. Read primary.
    return db.primary.get_order(order_id)

def sales_dashboard():
    # Aggregate analytics tolerate seconds of staleness. Use a replica.
    return db.replica.aggregate_daily_sales()
```

Why this satisfies the rule: each read path is routed by its declared lag
tolerance. The confirmation reads the primary so the user sees their own
write, while the dashboard gains read-scaling from a replica because it
tolerates lag. Routing is explicit at the call site, not incidental.
