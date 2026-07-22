<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.purpose-limitation-and-minimization collection limited to declared purpose, secondary use gated (anti-pattern)

Substrate-original illustration.

```python
# Everything is collected just in case, and data is silently repurposed.
def collect_signup(form: SignupForm) -> Customer:
    return Customer(**form.all_fields())   # precise location, DOB, device id, all of it

def use_for_analytics(customer: Customer) -> None:
    analytics.record(customer)             # support data reused for analytics, no basis
```

## Why this violates the rule

The signup collects every available field on the chance it is useful later, with
no purpose that needs most of them, and data collected for support is silently
reused for analytics with no compatibility assessment. Both purpose limitation and
minimization are broken. Collecting only what a declared purpose needs, and gating
secondary use on a new compatible basis, is the fix.
