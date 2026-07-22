---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: responsible-ai.ai-disclosure-marker
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether every user-facing path returning model-generated content attaches an AI-generated disclosure is a UI-coverage property a static tool cannot fully resolve; it is review-decidable.
review-triggers:
  - New or changed user-facing path that returns model-generated content
---

# Review checklist: AI-generated output is disclosed

## Review questions

- Does every user-facing output path that returns model-generated content attach a disclosure that the content is AI-generated?
- Is the disclosure visible to the person, whether as a response flag, a labeled UI element, or a content provenance marker?
- Is the disclosure applied consistently across all such surfaces, not only the primary one?
