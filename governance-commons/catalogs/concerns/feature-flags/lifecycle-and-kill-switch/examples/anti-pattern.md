<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.lifecycle-and-kill-switch lifecycle and kill switch (anti-patterns)

Substrate-original anti-pattern examples for feature-flags.lifecycle-and-kill-switch. Flags have no owner,
type, or expiry; stale flags accumulate; and the only way to disable a feature
is to ship a code change, so there is no real kill switch.

## Stale flag with no owner or expiry, long past full rollout

```python
# enabled for everyone 14 months ago; never retired, both branches still ship
if flags.get_boolean("search.semantic-ranking", default=False):
    results = semantic_rank(query)
else:
    results = lexical_rank(query)   # unreachable, untested, still maintained
```

## Disabling a feature requires a deploy (no kill switch)

```python
# the only off-switch is editing this constant and redeploying under pressure
PAYMENTS_ENABLED = True
if PAYMENTS_ENABLED:
    return process_payment(payment)
```

Why this is flagged: the first flag is unowned, undated, and long stale, so the
dead branch rots and the inventory cannot be reconciled; the second has no
provider-backed off-switch, so an incident response needs a build and deploy.
The remediation is to assign owner, type, and expiry to every flag, retire
stale flags, and back operational kills with a provider toggle that works
without a deploy.
