---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.mfa-enrollment-mfa-enrollment"
title: "authentication.mfa-enrollment review checklist: MFA enrollment hardening"
substrate-rule: "authentication.mfa-enrollment"
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
  - "Code changes to MFA enrollment, modification, or removal flows"
  - "Code changes to MFA recovery flows"
  - "Code changes to backup code generation, storage, or verification"
  - "Design of new MFA factor types"
---

# authentication.mfa-enrollment review checklist: MFA enrollment hardening

## Review questions

### 1. Fresh authentication required for enrollment

Does MFA enrollment, modification, or removal require fresh
authentication per authentication.mfa-on-privileged-operations?

What good looks like: enrollment endpoints carry the fresh-MFA
freshness check; user re-authenticates before adding/removing
factors.

What needs follow-up: enrollment accepts any authenticated
session; session compromise alone allows attacker to enroll
their own factor.

### 2. Backup codes generated securely

Are backup codes generated using a cryptographically secure
random source with adequate entropy (10 codes, 8-10 characters
each, generated via secrets module or equivalent)?

What good looks like: codes generated via secrets.token_urlsafe
(Python), crypto.randomBytes (Node), SecureRandom (Java) or
equivalent; entropy is at least 40 bits per code.

What needs follow-up: codes generated via math.random or
predictable PRNG; codes are sequential or pattern-based.

### 3. Backup codes shown once

Are backup codes displayed to the user once at enrollment with
clear "save these now" messaging?

What good looks like: codes displayed once with download or copy
affordance; user prompted to confirm they have stored them
before continuing; codes are not retrievable from the UI later.

What needs follow-up: codes are persistently visible in account
settings; codes can be retrieved with only session credentials
later.

### 4. Backup codes hashed server-side

Are backup codes stored hashed (not plaintext) server-side?

What good looks like: codes stored using the same Argon2id or
bcrypt as passwords; lookup is timing-safe.

What needs follow-up: codes stored plaintext; codes hashed with
fast hash (SHA-256) rather than password-grade hash.

### 5. Single-use enforcement

Are backup codes single-use? Once a code is presented and
verified, is it invalidated?

What good looks like: on code verification, the matching stored
hash is removed atomically; replay of the same code subsequently
fails.

What needs follow-up: codes reusable; codes only invalidated on
explicit user action.

### 6. Recovery requires identity proof outside session

For MFA loss recovery, does the flow require identity proof
outside the session (support-channel verification, pre-registered
recovery method, or alternate enrolled factor)?

What good looks like: recovery requires at least one of:
support-channel identity verification; pre-registered recovery
email or phone separate from primary account contact; previously-
enrolled secondary factor.

What needs follow-up: recovery proceeds based on session
authenticity and a single email confirmation; recovery is
silent (no audit log entry); recovery completes immediately
without delay window.

### 7. Recovery audit logging

Are recovery actions audit-logged with detail and triggering
security alerts?

What good looks like: every recovery initiation, intermediate
step, and completion is logged with timestamps; security
monitoring alerts on unusual recovery patterns (geographic
anomaly, recovery shortly after compromised-credentials event).

What needs follow-up: recovery is silent; recovery logs are at
DEBUG level; no alerting tied to recovery events.

### 8. Delay window before recovery completes

For irreversible recovery actions, is there a delay window
between initiation and completion that allows the legitimate
user to receive notifications and cancel unauthorized recovery?

What good looks like: 24-48 hour delay between recovery initiation
and MFA bypass; notifications sent to all registered contact
channels during the delay; legitimate user can cancel.

What needs follow-up: recovery completes immediately; legitimate
user has no opportunity to detect or cancel unauthorized recovery.

## Reviewer attestation

```
authentication.mfa-enrollment review checklist: complete
- Fresh authentication for enrollment: PASS / FOLLOW-UP / EXEMPT
- Backup codes generated securely: PASS / FOLLOW-UP / EXEMPT
- Backup codes shown once: PASS / FOLLOW-UP / EXEMPT
- Backup codes hashed server-side: PASS / FOLLOW-UP / EXEMPT
- Single-use enforcement: PASS / FOLLOW-UP / EXEMPT
- Recovery requires identity proof outside session: PASS / FOLLOW-UP / EXEMPT
- Recovery audit logging: PASS / FOLLOW-UP / EXEMPT
- Delay window before completion: PASS / FOLLOW-UP / EXEMPT
```

## Cross-reference

- Substrate rule: authentication.mfa-enrollment in catalogs/concerns/authentication.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/authentication/mfa-enrollment-good.md
- Anti-patterns: examples/authentication/mfa-enrollment-anti-pattern.md
