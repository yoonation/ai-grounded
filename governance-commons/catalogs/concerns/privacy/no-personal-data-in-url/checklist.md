---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: privacy.no-personal-data-in-url
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Unlike credentials, personal data has no reliable detectable signature, so identifying it in URL construction and route definitions is a judgment a static tool cannot fully resolve; it is review-decidable.
review-triggers:
  - New or changed route definition or outbound request construction
---

# Review checklist: personal data is not placed in URLs

## Review questions

- Are personal values kept out of URL path segments and query strings on requests the application constructs?
- Do server routes avoid defining personal-data identifiers as path parameters, carrying such values in the request body or headers instead?
- Where an identifier must appear in a path, is it an opaque non-personal surrogate rather than a personal value?
