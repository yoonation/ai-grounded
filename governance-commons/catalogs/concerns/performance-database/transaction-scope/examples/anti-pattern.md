<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.transaction-scope transaction scope (anti-pattern)

Substrate-original illustration. An HTTP call to a payment provider is made
while the transaction holds a row lock.

```python
def place_order(cart):
    with db.begin():
        order = db.insert_order(cart)
        db.decrement_inventory(cart.items)
        # External call INSIDE the transaction: the row locks are held for
        # as long as the payment provider takes to respond (seconds, on a
        # slow path), and a provider timeout can deadlock under load.
        charge_payment(cart.total)
    return order
```

Why this violates the rule: the database's lock duration is now coupled to a
remote system's latency and failure. Under contention this serializes other
orders and risks deadlock and pool exhaustion. The fix is to move the charge
outside the transaction.
