---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.mfa-on-privileged-operations-mfa-on-privileged-ops"
title: "authentication.mfa-on-privileged-operations review checklist: MFA on privileged operations"
substrate-rule: "authentication.mfa-on-privileged-operations"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.1.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-18"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove privileged operation endpoints"
  - "Code changes to MFA challenge middleware or freshness tracking"
  - "Design of new admin endpoints or sensitive user-facing flows"
---

# authentication.mfa-on-privileged-operations review checklist: MFA on privileged operations

## Review questions

### 1. Privileged operations identified

Has the change author identified which operations in the codebase
are privileged? Common categories: credential changes, payment
method management, role/permission changes, API key issuance,
account deletion, sensitive data export, MFA factor management.

What good looks like: the change author lists the privileged
operations the PR touches; existing endpoints in the same area
are reviewed for consistency.

What needs follow-up: the change adds a new endpoint that handles
account state but is not gated by fresh MFA.

### 2. Freshness check before execution

Does each privileged operation handler check the MFA freshness
timestamp before executing the operation?

What good looks like: a decorator, middleware, or first-line check
in the handler verifies the timestamp; the operation is atomic
with the check.

What needs follow-up: partial operation runs before the check
(database mutations before the freshness verification); the check
is conditionally skipped for certain users or admin roles.

### 3. Freshness window appropriate

Is the freshness window appropriate for the operation's
sensitivity? Substrate-recommended starting points: 5 minutes for
account deletion or PII export; 10 minutes for payment method
changes; 15 minutes for password changes.

What good looks like: the window is short (within substrate
ranges) and is configurable per operation type or per
sensitivity level.

What needs follow-up: the window is hours or days long; the
window is the same as session lifetime (effectively disabling the
freshness check).

### 4. Challenge response is clear

When the freshness check fails, does the response clearly signal
MFA-required (rather than appearing to be a general auth failure)?

What good looks like: structured response with a code field
indicating MFA is required; the client can render an MFA challenge
UI based on the response.

What needs follow-up: the response is a generic 401 indistinguishable
from session expiry; the client cannot tell whether to re-login or
re-challenge.

### 5. Partial operation safety

If the freshness check fails after some state mutation has
occurred (rare with good code structure but possible with complex
operations), is the partial state safely handled?

What good looks like: privileged operations are designed atomically;
the freshness check is the first action.

What needs follow-up: partial state is left in place when the
freshness check fails mid-operation.

### 6. Audit logging present

Are privileged operation attempts (passed, stale, failed) logged
for security monitoring?

What good looks like: every attempt is logged with the requesting
user, the operation type, the MFA freshness result, and a
timestamp; logs flow to the security aggregator.

What needs follow-up: only successful operations are logged;
freshness failures are silent; logs are at DEBUG level and lost
in production.

### 7. Recovery flow handling

For users who lost their MFA factor, does the recovery flow
require identity proof outside the session (per authentication.mfa-enrollment)?

What good looks like: recovery requires support-channel
verification, pre-registered recovery method, or alternate
enrolled factor; recovery does not silently grant access based
on session.

What needs follow-up: recovery flow accepts any authenticated
session and a single email confirmation.

## Reviewer attestation

```
authentication.mfa-on-privileged-operations review checklist: complete
- Privileged ops identified: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Freshness check before execution: PASS / FOLLOW-UP / EXEMPT
- Freshness window appropriate: PASS / FOLLOW-UP / EXEMPT
- Challenge response is clear: PASS / FOLLOW-UP / EXEMPT
- Partial operation safety: PASS / FOLLOW-UP / EXEMPT
- Audit logging present: PASS / FOLLOW-UP / EXEMPT
- Recovery flow handling: PASS / FOLLOW-UP / EXEMPT
```

## Cross-reference

- Substrate rule: authentication.mfa-on-privileged-operations in catalogs/concerns/authentication.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/authentication/mfa-on-privileged-ops-good.md
- Anti-patterns: examples/authentication/mfa-on-privileged-ops-anti-pattern.md
