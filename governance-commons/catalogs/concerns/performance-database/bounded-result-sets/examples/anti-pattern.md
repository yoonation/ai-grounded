<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.bounded-result-sets bounded result sets (anti-pattern)

Substrate-original illustration. The endpoint fetches and serializes every
matching row with no bound, so its cost is the size of the data.

```python
def list_orders():
    # No LIMIT, no pagination. Returns 12 rows in dev, 12 million in prod.
    rows = Order.objects.all()
    return [serialize(o) for o in rows]
```

Why this violates the rule: the unbounded query scans and returns the whole
table, paid for in database scan time, network transfer, and the
application memory to hold and serialize it. It is the data-tier form of the
unbounded buffer reliability.bounded-buffers prohibits. The fix is a LIMIT and a pagination
contract.
