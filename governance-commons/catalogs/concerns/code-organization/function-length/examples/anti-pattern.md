<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.function-length function length (anti-pattern)

Substrate-original illustration. One function carries the entire
settlement procedure inline: validation, capture, ledger posting, and
notification are all interleaved in a single body that runs well past the
threshold. The reader must hold the whole thing at once to follow it.

## Python: everything inline in one over-long function

```python
def settle_order(order, gateway, ledger, notifier):
    # validation
    if order.status != "confirmed":
        raise InvalidState(f"order {order.id} is {order.status}")
    if order.total <= 0:
        raise InvalidState(f"order {order.id} has non-positive total")
    # capture
    charge = gateway.capture(order.payment_intent, amount=order.total)
    if charge.status == "failed":
        order.mark_failed(charge.failure_code)
        notifier.customer(order.customer_email, charge)
        raise PaymentFailed(charge.failure_code)
    # ledger
    ledger.post(account=order.account, amount=charge.amount, ref=charge.id)
    order.mark_settled(charge.id)
    # notification
    notifier.customer(order.customer_email, charge)
    notifier.fulfillment(order.id)
    # ... and many more interleaved lines for refunds, tax, audit ...
    return charge
```

Why this is a finding: the function mixes four responsibilities in one
body and grows without bound as each gains edge cases. The remediation is
the good-pattern decomposition: extract each commented section into a
named helper. Note that the comments (# validation, # capture) are the
seams; their presence is a signal the function wants to be several
functions.
