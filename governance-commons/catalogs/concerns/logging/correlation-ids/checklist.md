---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: logging.correlation-ids
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Deciding that every request, job, and transaction-scoped log carries a
  correlation identifier requires judgment about which code paths are in scope
  and whether the identifier propagates correctly across boundaries, which a
  static tool cannot fully resolve.
review-triggers:
  - New request-handling, job-execution, or transaction-scoped code path
  - Changes to logging setup, middleware, or context propagation
  - A new entry point or service boundary is added
---

# Review checklist: logs carry a correlation identifier

## Review questions

- Do log records emitted from request, job, and transaction-scoped paths include
  a correlation identifier as a structured field?
- Is the identifier propagated from inbound context where one exists, and
  generated at the boundary where one does not?
- Does the identifier flow to downstream calls so a single unit of work can be
  traced end to end?
- Is the field name consistent with the project's logging convention?

## Mechanical assist

The lint gate can confirm a structured logger is in use; it cannot confirm the
correlation field is present on every in-scope path. Review confirms scope.
