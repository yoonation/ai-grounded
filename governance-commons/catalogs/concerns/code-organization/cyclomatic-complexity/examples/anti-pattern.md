<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.cyclomatic-complexity complexity (anti-pattern)

Substrate-original illustration. The same shipping calculation is written
as a deeply nested set of conditionals. Cognitive complexity is high
because each condition is nested inside the last, so the reader tracks a
growing stack of context.

## Python: nested conditionals

```python
def shipping_cost(order):
    if not order.is_free_shipping:
        if order.region in SUPPORTED_REGIONS:
            if order.method == "standard":
                base = 5.00
                if order.weight_kg > HEAVY_THRESHOLD:
                    base += HEAVY_SURCHARGE
                return base
            elif order.method == "express":
                base = 12.00
                if order.weight_kg > HEAVY_THRESHOLD:
                    base += HEAVY_SURCHARGE
                return base
            elif order.method == "overnight":
                base = 25.00
                if order.weight_kg > HEAVY_THRESHOLD:
                    base += HEAVY_SURCHARGE
                return base
            else:
                raise UnknownMethod(order.method)
        else:
            raise UnsupportedRegion(order.region)
    else:
        return 0.0
```

Why this is a finding: four levels of nesting and a duplicated
weight-surcharge block inside each branch drive cognitive complexity past
the threshold, and the duplication also trips code-organization.duplication-and-abstraction. The
remediation is the good pattern: invert the conditions into guard clauses
and replace the method chain with a table lookup.
