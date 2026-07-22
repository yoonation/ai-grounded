<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.replica-routing replica routing (anti-pattern)

Substrate-original illustration. A read-your-writes confirmation page reads a
lagging replica and shows stale data.

```python
def order_confirmation(order_id):
    # Routed to a replica by a blanket "all reads go to replicas" rule.
    # If replication lag exceeds the gap between the write and this read,
    # the just-placed order is not found, and the user sees an error or an
    # empty page right after a successful purchase.
    return db.replica.get_order(order_id)
```

Why this violates the rule: a read that requires read-your-writes
consistency was routed to a replica with no per-path lag classification,
producing an intermittent staleness bug that appears only when lag is high.
The fix is to classify this path as freshness-requiring and route it to the
primary.
