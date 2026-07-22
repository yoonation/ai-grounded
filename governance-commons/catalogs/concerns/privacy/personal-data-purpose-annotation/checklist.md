---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: privacy.personal-data-purpose-annotation
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Identifying which persisted fields hold personal data and confirming each carries a processing-purpose and lawful-basis annotation is a judgment a static tool cannot fully resolve; it is review-decidable.
review-triggers:
  - A persisted field or model that may hold personal data is added or changed
---

# Review checklist: personal-data fields declare purpose and lawful basis

## Review questions

- Does every persisted field or model holding personal data carry a processing-purpose annotation naming the declared purpose?
- Does it carry a lawful-basis annotation naming the basis on which the processing relies?
- Are the declared purpose and basis consistent with how the data is actually used?
