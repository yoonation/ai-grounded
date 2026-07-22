---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: performance-database.pooled-connections
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether request-path database connections come from a pool established once at
  startup, versus constructed per request, is an architectural property that
  depends on how the connection lifecycle is wired, which a static tool cannot
  fully resolve.
review-triggers:
  - New or changed database connection setup or lifecycle code
  - A new data store or driver is integrated
  - Changes to request-path data access
---

# Review checklist: request-path connections are pooled

## Review questions

- Are connections used on the request path drawn from a pool established once at
  process or worker startup, rather than constructed per request?
- Is each connection returned to the pool when the unit of work completes,
  including on error paths?
- Is the pool sized and bounded so it cannot exhaust the database under load?

## Mechanical assist

The sast gate can flag obvious per-request connection construction in some
frameworks; the lifecycle property is review-decidable.
