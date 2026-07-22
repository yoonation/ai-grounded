---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authentication.account-lockout-lockout-policy"
title: "authentication.account-lockout test template: bounded recoverable lockout"
substrate-rule: "authentication.account-lockout"
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

# authentication.account-lockout test template: bounded recoverable lockout

## Scenario 1: Lockout triggers at threshold

**Preconditions**
- Rate-limit state cleared
- Test user account exists

**Action**
- Submit failed login attempts targeting one account until the
  per-account threshold is reached

**Expected**
- Account is in lockout state after threshold
- Subsequent attempts (correct or incorrect credentials) return
  the generic auth-failure response

## Scenario 2: Lockout self-clears after duration

**Preconditions**
- Account is in lockout state
- Substrate-recommended duration: 15-30 minutes

**Action**
- Wait for the configured lockout duration plus a small buffer
- Submit a login attempt with correct credentials

**Expected**
- The lockout has cleared
- The login attempt succeeds normally
- Total elapsed time is consistent with the configured duration

Note: this scenario is long-running. Use a shortened duration
(60 seconds) in test environments if production uses 15-30
minutes.

## Scenario 3: Lockout window does not extend on additional attempts

**Preconditions**
- Account is in lockout state with T minutes remaining

**Action**
- Submit several failed login attempts during the lockout window
- Wait for the original lockout duration to elapse
- Submit a login attempt with correct credentials

**Expected**
- The lockout clears at the original expiration time, not at
  T + additional-attempt-times
- Login succeeds after original duration regardless of activity

## Scenario 4: Self-service recovery via password reset

**Preconditions**
- Account is in lockout state

**Action**
- Submit a password-reset request (subject to authentication.rate-limiting rate
  limiting on the reset endpoint)
- Complete the password reset with a new password
- Attempt to log in with the new password

**Expected**
- Password reset flow proceeds normally (not blocked by lockout)
- Lockout state is cleared after successful password reset
- Login with new password succeeds immediately

## Scenario 5: Lockout response is uniform with auth failure

**Preconditions**
- Account is in lockout state

**Action**
- Submit a login attempt with CORRECT password to the locked
  account
- Capture the response

**Expected**
- Response is byte-identical to a standard wrong-password response
- Response time is within the timing-equivalence band
- Client cannot distinguish "locked, would-have-authenticated"
  from "incorrect credentials"

## Scenario 6: Failure counter uses time-windowed reset

**Preconditions**
- Account has accumulated some failed attempts but is below
  threshold

**Action**
- Wait for the configured counter window to elapse
- Submit failed login attempts

**Expected**
- The pre-window failures do not count toward the current
  threshold; the window has reset
- Lockout triggers at threshold within the new window only

## Scenario 7: Lockout audit logging

**Preconditions**
- Audit log accessible via test infrastructure

**Action**
- Trigger lockout by exceeding threshold

**Expected**
- Audit log contains a lockout event with: target account,
  triggering source identifier, lockout expiration timestamp,
  threshold value

## Cross-reference

- Substrate rule: authentication.account-lockout in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Good examples: examples/authentication/lockout-policy-good.md
- Anti-patterns: examples/authentication/lockout-policy-anti-pattern.md
