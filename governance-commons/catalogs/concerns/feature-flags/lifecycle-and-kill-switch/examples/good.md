<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.lifecycle-and-kill-switch lifecycle and kill switch (good patterns)

Substrate-original good-pattern example for feature-flags.lifecycle-and-kill-switch. Every flag carries an
owner, a type, and an expiry; kill switches are reachable without a deploy and
are exercised on a cadence.

## Flag inventory: owner, type, expiry per flag

```yaml
flags:
  - key: checkout.new-pricing-engine
    type: release        # short-lived; remove after full rollout
    owner: checkout-team
    expiry: 2026-09-01
  - key: ops.payments-circuit-breaker
    type: kill-switch    # long-lived operational control
    owner: payments-oncall
    expiry: review-annually
```

## Kill switch exercised without a deploy

```python
# toggled at the provider during an incident; no redeploy, no restart
if flags.get_boolean("ops.payments-circuit-breaker", default=True):
    return queue_for_retry(payment)   # safe path when tripped
return process_payment(payment)
```

Each flag has an accountable owner and a retirement date; the kill switch
defaults to the safe path, is owned by on-call, and is tested in game-days.
