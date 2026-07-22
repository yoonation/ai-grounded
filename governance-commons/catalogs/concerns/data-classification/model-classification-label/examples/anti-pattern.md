<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.model-classification-label model classification label (anti-pattern)

Substrate-original illustration.

```python
# A persisted model with no classification label.
class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    ssn = models.CharField(max_length=11)   # clearly sensitive, unclassified
```

## Why this violates the rule

The persisted model carries no classification label, so nobody decided how
sensitive it is, even though it holds a government identifier and contact
data that are plainly restricted and confidential. The per-class handling
rules have no class to key off, so the data inherits whatever protection its
storage happens to provide. A class-level label drawn from the scheme
vocabulary is the fix.
