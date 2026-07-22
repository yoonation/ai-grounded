<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.function-length function length (good pattern)

Substrate-original illustration. A long procedure is decomposed into
named steps, each short enough to read at a glance, so the top-level
function reads as a summary of what happens and each helper holds one
step. The threshold (substrate default 50 logical lines) is met not by
compressing code onto fewer lines but by extracting cohesive steps.

## Python: a long handler decomposed into named steps

```python
def settle_order(order, gateway, ledger, notifier):
    _validate_settleable(order)
    charge = _capture_payment(order, gateway)
    _record_settlement(order, charge, ledger)
    _notify_parties(order, charge, notifier)
    return charge


def _validate_settleable(order):
    if order.status != "confirmed":
        raise InvalidState(f"order {order.id} is {order.status}")
    if order.total <= 0:
        raise InvalidState(f"order {order.id} has non-positive total")


def _capture_payment(order, gateway):
    return gateway.capture(order.payment_intent, amount=order.total)


def _record_settlement(order, charge, ledger):
    ledger.post(account=order.account, amount=charge.amount, ref=charge.id)
    order.mark_settled(charge.id)


def _notify_parties(order, charge, notifier):
    notifier.customer(order.customer_email, charge)
    notifier.fulfillment(order.id)
```

Why this passes: the entry function is five lines and names the sequence;
each helper is a handful of lines with one responsibility. Length stays
under the threshold per function because each function does one thing,
not because logic was crammed. This composes with code-organization.module-boundary-cohesion
(cohesion): each extracted helper has a clear single responsibility.
