---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: authentication.no-credentials-in-logs
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  This is the sensitive-data-in-logs class: deciding that no authentication
  credential reaches any log at any severity, including credentials embedded in
  request dumps or error context, requires contextual judgment a static tool
  cannot fully resolve. Static analysis flags a partial set; the property is
  review-decidable.
review-triggers:
  - New or changed authentication, session, or token-handling code
  - New or changed logging on an auth path
  - A log call begins carrying request or header content on an auth path
---

# Review checklist: authentication credentials do not reach logs

## Review questions

- Do log records on authentication paths exclude passwords, API keys, session and
  JWT tokens, OAuth tokens, and reset or verification tokens, at every severity?
- Where request, header, or body content is logged, are credential-bearing fields
  (Authorization headers, cookies, token parameters) redacted before logging?
- Are credentials kept out of exception messages and debug dumps that may be
  logged on auth error paths?

## Mechanical assist

The sast gate flags known credential-logging patterns. Treat findings as
violations pending review; a clean run is necessary but not sufficient.
