---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: error-handling.error-status-code
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  A static tool can flag an error path that returns a success status, but it
  cannot decide whether the specific code chosen (for example 404 versus 400
  versus 409) correctly represents the outcome. That mapping is review-decidable.
review-triggers:
  - New or changed error-handling or response-construction code
  - A new error condition or failure mode is introduced on a network surface
  - API contract or documented error-response changes
---

# Review checklist: error responses use the correct status code

## Review questions

- Do error outcomes return a 4xx or 5xx status rather than a success code?
- Is the specific code correct for the outcome (client input fault in the 4xx
  range, server or dependency fault in the 5xx range), per RFC 9110?
- Does the chosen code match the documented API contract for that condition?
- Are dependency failures surfaced with a code that reflects the application's
  responsibility (for example 502 or 503), not a misleading 500 or 200?

## Mechanical assist

The lint and sast gates can flag obvious mismatches (success status on a known
error path). Treat a clean run as necessary, not sufficient.
