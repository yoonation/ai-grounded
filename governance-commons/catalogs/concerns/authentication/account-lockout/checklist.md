---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.account-lockout-lockout-policy"
title: "authentication.account-lockout review checklist: bounded recoverable lockout"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes to account lockout logic"
  - "Code changes to authentication failure handling"
  - "Code changes to account recovery flows"
---

# authentication.account-lockout review checklist: bounded recoverable lockout

## Review questions

### 1. Lockout duration bounded

Is the lockout duration time-bounded (substrate-recommended:
15-30 minutes for standard accounts)?

What good looks like: lockout duration is a configuration value
in the substrate-recommended range; lockout self-clears after
duration elapses.

What needs follow-up: lockout duration is "indefinite" or
"forever" requiring manual admin unlock for standard accounts;
duration is hours-long without documented rationale.

### 2. Window does not reset on activity

Does the lockout window expire on the timer rather than resetting
on each failed attempt?

What good looks like: lockout starts when the threshold is reached
and ends after the configured duration regardless of further
attempts.

What needs follow-up: each failed attempt extends the lockout
window indefinitely; an attacker can keep the account locked by
making one failed attempt per window.

### 3. Self-service recovery available

Can the user recover from lockout via password reset (subject to
authentication.rate-limiting rate limiting on the reset endpoint)?

What good looks like: successful password reset clears the
lockout state; the user is operational immediately after reset.

What needs follow-up: lockout state persists through password
reset; user must wait for lockout window to expire regardless
of reset.

### 4. Lockout state not signaled in response

Is the lockout state concealed in the authentication response
(preserving authentication.generic-failure-responses enumeration protection)?

What good looks like: locked accounts produce the same response
as invalid-credentials; the response time is also equalized.

What needs follow-up: locked accounts receive a distinct
"account locked, try again in N minutes" response.

### 5. Failure counter window

Does the failure counter reset after a window of activity rather
than persisting indefinitely?

What good looks like: the per-account failure counter uses a
sliding or fixed time window (matching the lockout duration or
similar); failures from weeks ago do not contribute to current
lockout decisions.

What needs follow-up: lifetime failure count accumulates without
reset; user accumulates lockout triggers from years of typos.

### 6. Audit logging present

Are lockout events logged for security monitoring?

What good looks like: each lockout event records target account,
triggering source pattern, and lockout expiration; security
monitoring alerts on lockout spikes.

What needs follow-up: lockout events not logged or only logged
at DEBUG level.

### 7. High-value account differentiation

For high-value or administrative accounts (if applicable), is
lockout policy differentiated appropriately?

What good looks like: admin accounts have longer lockout (1-2
hours) or stricter recovery (support-channel identity proof);
documented per substrate guidance.

What needs follow-up: admin accounts have the same policy as
standard accounts and are equally vulnerable to DoS-via-lockout.

## Reviewer attestation

```
authentication.account-lockout review checklist: complete
- Lockout duration bounded: PASS / FOLLOW-UP / EXEMPT
- Window does not reset on activity: PASS / FOLLOW-UP / EXEMPT
- Self-service recovery available: PASS / FOLLOW-UP / EXEMPT
- Lockout state not signaled: PASS / FOLLOW-UP / EXEMPT
- Failure counter window: PASS / FOLLOW-UP / EXEMPT
- Audit logging: PASS / FOLLOW-UP / EXEMPT
- High-value account differentiation: PASS / FOLLOW-UP / EXEMPT
```

## Cross-reference

- Substrate rule: authentication.account-lockout in catalogs/concerns/authentication.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/authentication/lockout-policy-good.md
- Anti-patterns: examples/authentication/lockout-policy-anti-pattern.md
