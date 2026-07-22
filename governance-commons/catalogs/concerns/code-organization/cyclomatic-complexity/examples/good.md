<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.cyclomatic-complexity complexity (good pattern)

Substrate-original illustration. Deeply nested conditional logic is
flattened with guard clauses and a lookup table, lowering both cyclomatic
and cognitive complexity. The branching that remains is flat and named.

## Python: guard clauses and a dispatch table

```python
SHIPPING_RATES = {
    "standard": 5.00,
    "express": 12.00,
    "overnight": 25.00,
}


def shipping_cost(order):
    if order.is_free_shipping:
        return 0.0
    if order.region not in SUPPORTED_REGIONS:
        raise UnsupportedRegion(order.region)

    base = SHIPPING_RATES[order.method]
    if order.weight_kg > HEAVY_THRESHOLD:
        base += HEAVY_SURCHARGE
    return base
```

Why this passes: early returns handle the special cases up front so the
main path is not nested inside them, and the per-method rate is a table
lookup rather than an if/elif chain. Cyclomatic complexity is low because
there are few independent paths; cognitive complexity is low because
nothing is nested deeply. A flat exhaustive table is preferable to nested
conditionals even when both have similar cyclomatic counts.
