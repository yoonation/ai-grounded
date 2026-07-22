---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authentication.mfa-enrollment-mfa-enrollment"
title: "authentication.mfa-enrollment test template: MFA enrollment hardening"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authentication.mfa-enrollment test template: MFA enrollment hardening

## Scenario 1: MFA enrollment without fresh auth is rejected

**Preconditions**
- Test user authenticated via standard login (no recent MFA
  challenge or fresh re-auth)

**Action**
- Attempt to enroll a new MFA factor

**Expected**
- Request rejected with MFA-required indication (per authentication.mfa-on-privileged-operations)
- No factor is enrolled

## Scenario 2: MFA enrollment with fresh auth succeeds

**Preconditions**
- Test user re-authenticated within the fresh-auth window

**Action**
- Submit MFA factor enrollment request (e.g., TOTP)

**Expected**
- Enrollment succeeds
- Factor stored server-side
- Backup codes generated and returned in the response

## Scenario 3: Backup codes are single-use

**Preconditions**
- Test user has enrolled MFA with backup codes
- One backup code captured (call it BC1)

**Action**
- Use BC1 to satisfy an MFA challenge; capture result
- Attempt to use BC1 again to satisfy a subsequent MFA challenge

**Expected**
- First use succeeds
- Second use is rejected (code invalidated after first use)

## Scenario 4: Backup codes are stored hashed

**Preconditions**
- Direct database access to the test environment

**Action**
- Inspect the backup codes table for the test user

**Expected**
- Stored values are hashes (Argon2id, bcrypt, or equivalent
  password-grade hash); not plaintext codes
- Hashes are not retrievable as plaintext via any UI

## Scenario 5: Backup codes are not retrievable after initial display

**Preconditions**
- Test user has enrolled MFA and seen backup codes at enrollment

**Action**
- Authenticate, navigate to account settings or MFA management
  page
- Look for "view backup codes" or equivalent affordance

**Expected**
- The previously-shown codes are NOT retrievable
- The user may have an affordance to "regenerate backup codes"
  (which invalidates the prior set and produces new codes shown
  once)

## Scenario 6: Recovery requires identity proof outside session

**Preconditions**
- Test user has lost access to their MFA factor
- Test user is otherwise authenticated to the application

**Action**
- Initiate the MFA recovery flow with the user's session

**Expected**
- Recovery requires at least one of: support-channel verification,
  pre-registered recovery method (separate from primary contact),
  alternate enrolled factor
- Recovery does NOT proceed solely based on session authenticity
  plus an email confirmation to the primary contact

## Scenario 7: Recovery initiation triggers notifications

**Preconditions**
- Test user has registered email and (if applicable) phone

**Action**
- Initiate MFA recovery

**Expected**
- Notifications sent to all registered contact channels
  immediately
- Notifications clearly state "MFA recovery initiated; if this
  was not you, click here to cancel"
- Cancellation link works during the delay window

## Scenario 8: Recovery has delay window before completion

**Preconditions**
- MFA recovery initiated

**Action**
- Attempt to complete recovery before the substrate-recommended
  delay window (24-48 hours)
- After the delay window elapses, complete recovery

**Expected**
- Pre-delay completion is rejected
- Post-delay completion succeeds
- Cancellation during the delay window aborts recovery

Note: this scenario is long-running. Use a shortened delay (5-10
minutes) in test environments if production uses 24-48 hours.

## Scenario 9: Recovery actions are audit-logged

**Preconditions**
- Audit log accessible

**Action**
- Initiate recovery, perform identity proof, complete recovery

**Expected**
- Every step (initiation, identity proof submission, completion,
  any cancellation) appears in the audit log with timestamps,
  user identifier, source IP, and result

## Cross-reference

- Substrate rule: authentication.mfa-enrollment in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Good examples: examples/authentication/mfa-enrollment-good.md
- Anti-patterns: examples/authentication/mfa-enrollment-anti-pattern.md
