<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.no-import-cycles no import cycles (good pattern)

Substrate-original illustration. Two modules that both need a shared
concept depend on a third module that owns it, rather than importing each
other. The dependency graph is a tree, not a cycle.

## Python: shared abstraction extracted into a third module

```python
# money.py  (owns the shared concept; depends on neither caller)
class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency


# orders.py
from money import Money

def order_total(lines):
    return Money(sum(l.amount for l in lines), "USD")


# billing.py
from money import Money

def invoice_amount(order_total: Money, tax: Money) -> Money:
    return Money(order_total.amount + tax.amount, order_total.currency)
```

Dependency direction: orders -> money, billing -> money. No back-edge,
no cycle. Either module can be tested in isolation with only money
present. This is the dependency-inversion remediation: the thing both
needed was extracted to a module both depend on. An import-linter
independence contract between orders and billing keeps it that way.
