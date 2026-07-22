---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: data-classification.model-classification-label
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Confirming that every persisted data model carries a classification label is a coverage property, and identifying which models are persisted depends on framework knowledge, so it is review-decidable.
review-triggers:
  - A persisted data model or entity is added or changed
---

# Review checklist: persisted models carry a classification label

## Review questions

- Does every persisted data model or entity carry a class-level classification label from the scheme vocabulary?
- Is the label's value appropriate to the actual sensitivity of the data the model holds?
- Are transient or non-persisted structures correctly excluded from the requirement?
