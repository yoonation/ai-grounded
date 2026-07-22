---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: authentication.generic-failure-responses
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether every authentication failure path returns an indistinguishable
  response, so that cause categories (account missing, wrong password, locked,
  disabled, not yet activated) cannot be inferred, is a property of the response
  flow across all failure branches that a static tool cannot decide. It is
  review-decidable.
review-triggers:
  - New or changed authentication endpoint or failure branch
  - New account-state condition (locked, disabled, pending) is introduced
  - Changes to auth error messages, status codes, or response timing
---

# Review checklist: authentication failures are indistinguishable by cause

## Review questions

- Do all authentication failure causes return the same response body, the same
  status code, and the same error identifier to the client?
- Is the distinction between "account does not exist" and "password incorrect"
  unobservable from the response?
- Are locked, disabled, and not-yet-activated states handled without revealing
  which state applies, routing the user to recovery generically?
- Is response timing across failure causes close enough that timing does not leak
  the cause (for example, a password hash is computed even when the account does
  not exist)?
