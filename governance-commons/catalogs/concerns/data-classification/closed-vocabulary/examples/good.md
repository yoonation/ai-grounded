<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.closed-vocabulary closed vocabulary (good pattern)

Substrate-original illustration.

```python
# Labels are drawn from the closed scheme vocabulary via an enum, the same
# four values the infrastructure data-sensitivity tags use.
class DataClass(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class HealthRecord(models.Model):
    data_classification = DataClass.RESTRICTED   # in-vocabulary, via enum
```

## Why this satisfies the rule

The label value is a member of the closed four-class vocabulary, expressed
through a scheme enum so the type system enforces it too. Because it is the
same vocabulary the infrastructure data-sensitivity tags use (infrastructure-misconfiguration.governance-tagging),
the datum's class in code and the tag on the store that holds it agree.
