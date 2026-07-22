<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.closed-vocabulary closed vocabulary (anti-pattern)

Substrate-original illustration.

```python
# An ad-hoc, free-text classification label outside the scheme.
class HealthRecord(models.Model):
    data_classification = "super-secret"   # not a scheme value
```

## Why this violates the rule

The label value `super-secret` is not a member of the closed four-class
vocabulary, so it joins to none of the per-class handling rules, access
policies, or infrastructure tags that key off the scheme. The data is
effectively unclassified while appearing classified: every rule that looks
for `restricted` passes it by. A scheme value (here, `restricted`), ideally
via the scheme enum, is the fix.
