<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.staged-rollout-and-context staged rollout and context (good patterns)

Substrate-original good-pattern example for feature-flags.staged-rollout-and-context. Rollout is driven by
the provider's targeting rules with a stable targeting key, and the evaluation
context carries only the attributes targeting needs, with no secrets.

## Python: stable targeting key, minimal context, no secrets

```python
# stable key gives deterministic bucketing across instances and restarts
context = {
    "targetingKey": account.id,        # opaque, stable identifier
    "region": account.region,          # used by a geo-staged rule
    "plan": account.plan_tier,          # used by a plan-staged rule
}
# no email, no token, no PII beyond what a targeting rule consumes
enabled = flags.get_boolean("billing.new-invoicing", default=False, context=context)
```

```text
Provider rule: enable for region in {us-west} AND plan in {enterprise},
then ramp by 10/25/50/100 percent on targetingKey hash.
```

The same account always buckets the same way; the stage is moved at the
provider with no deploy; the context holds only targeting inputs.
