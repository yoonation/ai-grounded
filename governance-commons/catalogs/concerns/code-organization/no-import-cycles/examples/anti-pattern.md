<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.no-import-cycles no import cycles (anti-pattern)

Substrate-original illustration. An orders module and a billing module
import each other, forming a two-node cycle. Neither can be loaded,
tested, or reused without the other.

## Python: a direct two-module cycle

```python
# orders.py
from billing import invoice_amount   # <-- imports billing

def order_total(lines):
    total = sum(l.amount for l in lines)
    return invoice_amount(total, tax=compute_tax(total))


# billing.py
from orders import order_total        # <-- imports orders back

def invoice_amount(subtotal, tax):
    return subtotal + tax

def reconcile(order):
    return order_total(order.lines)    # reaches back into orders
```

Why this is a finding: orders -> billing -> orders is a strongly
connected component of size two. Import-time, this risks a partially-
initialized module; structurally, the two modules are one unit wrongly
split. Detected by import-linter (independence contract), eslint-plugin-
import no-cycle, or Pylint R0401. Remediation: extract the shared concept
(here, the Money type and the tax rule) into a third module both depend
on, as in the good-pattern example, removing the back-edge.
