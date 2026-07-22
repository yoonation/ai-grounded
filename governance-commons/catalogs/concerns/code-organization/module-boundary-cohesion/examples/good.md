<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.module-boundary-cohesion module-boundary cohesion (good pattern)

Substrate-original illustration. A feature is organized into a module
whose contents all change for the same business reason, and the module
can be described in one responsibility-statement without "and".

## Package layout: organized by domain capability

```
pricing/
    __init__.py        # public surface: price_quote, PriceBreakdown
    quote.py           # builds a price quote from a cart
    discounts.py       # discount rules
    taxes.py           # tax computation
    _rounding.py       # internal rounding helpers (not exported)
```

Responsibility statement: "the pricing module is responsible for turning
a cart into a final price." Every file inside changes when pricing rules
change, and for no other reason. Tax, discount, and rounding logic live
together because they are all part of computing a price, not because they
are all "calculations." Fan-in is moderate: callers depend on the package
surface (price_quote), not on its internals.

Why this passes: the boundary tracks a cohesive responsibility (review
question 1), there is no grab-bag (question 2), and a newcomer asked
where a new discount rule goes would correctly predict discounts.py
(question 5).
