<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.staged-rollout-and-context staged rollout and context (anti-patterns)

Substrate-original anti-pattern examples for feature-flags.staged-rollout-and-context. Rollout is faked in
application code instead of provider targeting, bucketing is nondeterministic,
and the evaluation context leaks secrets and excess PII.

## Python: random bucketing and a secret in the context

```python
# nondeterministic: the same account flips between variants across calls
if random.random() < 0.10:
    enabled = True
else:
    enabled = flags.get_boolean("billing.new-invoicing", default=False, context={
        "targetingKey": account.email,     # PII used as the key
        "api_token": account.api_token,    # secret leaked into flag context
        "full_address": account.address,   # PII no rule consumes
    })
```

Why this is flagged: client-side random bucketing is not reproducible, so a
user can see the new path on one request and the old path on the next; the
context uses an email as the targeting key and carries a token and address that
no targeting rule needs. The remediation is to move staging into provider
targeting rules keyed on a stable opaque identifier, and to strip the context
down to non-secret attributes the rules actually consume.
