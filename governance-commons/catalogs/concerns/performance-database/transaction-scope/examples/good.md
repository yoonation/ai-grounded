<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.transaction-scope transaction scope (good pattern)

Substrate-original illustration. The external call happens outside the
transaction; the transaction holds only the local writes that must be
atomic.

```python
def place_order(cart):
    # Local atomic writes only. Short, holds row locks briefly.
    with db.begin():
        order = db.insert_order(cart)
        db.decrement_inventory(cart.items)
    # External effect AFTER commit, via the outbox the commit enqueued.
    publish_order_placed(order.id)   # not holding any DB lock
    return order
```

Why this satisfies the rule: the transaction encloses only the database
work, so locks are held for microseconds rather than for the latency of the
payment or messaging system. Cross-system atomicity is achieved with a
post-commit dispatch rather than by holding the transaction open.
