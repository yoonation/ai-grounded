---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: responsible-ai.model-documentation-artifact
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether every deployed model carries a documentation artifact is a release-coverage property; the artifact's schema validity is a mechanical assist but presence on every deployed model is review-decidable.
review-triggers:
  - A model or AI system is deployed or updated
---

# Review checklist: deployed models carry documentation

## Review questions

- Does every deployed model or AI system carry a model card, system card, or structured metadata record?
- Does it record intended use, known limitations, and an evaluation summary?
- Is the artifact kept current with the deployed version rather than stale?
