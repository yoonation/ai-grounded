---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: data-classification.no-classified-data-in-logs
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  This is the sensitive-data-in-logs class: deciding that data at or above the confidential tier never reaches logs or standard streams in plaintext requires contextual judgment a static tool cannot fully resolve; it is review-decidable.
review-triggers:
  - New or changed logging on a path that handles classified data
---

# Review checklist: classified data is not logged in plaintext

## Review questions

- Is data classified at or above the confidential tier kept out of logs and standard streams in plaintext?
- Where such data must be referenced, is a non-sensitive identifier or a masked form logged in its place?
- Is the discipline applied across all environments and severities?
