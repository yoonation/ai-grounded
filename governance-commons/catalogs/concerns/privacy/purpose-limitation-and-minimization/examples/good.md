<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.purpose-limitation-and-minimization collection limited to declared purpose, secondary use gated (good pattern)

Substrate-original illustration.

```python
# Only fields a declared purpose needs are collected; reuse is gated on a basis.
def collect_signup(form: SignupForm) -> Customer:
    # shipping needs a coarse region, not a precise location
    return Customer(email=form.email, region=form.region)

def use_for_analytics(customer: Customer) -> None:
    if not basis.compatible(customer, purpose="analytics"):
        raise PurposeError("analytics needs its own compatible basis")
    analytics.record(customer)
```

## Why this satisfies the rule

Collection is limited to the fields a declared purpose needs (a coarse region
rather than a precise location), and reusing the data for analytics is gated on a
recorded compatible basis rather than happening silently. Whether a field is
truly necessary is a review judgment; this shows the enforced shape.
