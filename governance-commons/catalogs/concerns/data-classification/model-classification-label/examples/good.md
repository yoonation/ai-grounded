<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.model-classification-label model classification label (good pattern)

Substrate-original illustration.

```python
# Every persisted model carries a class-level classification label drawn
# from the scheme vocabulary.
from enum import Enum

class DataClass(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class Customer(models.Model):
    data_classification = DataClass.CONFIDENTIAL   # class-level label
    name = models.CharField(max_length=200)
    email = models.EmailField()
```

## Why this satisfies the rule

The persisted model carries a class-level `data_classification` label, so its
sensitivity was decided rather than assumed and the per-class handling rules
(encryption, access, retention) have a class to key off. The label is
expressed through the scheme enum, which also satisfies the closed-vocabulary
rule.
