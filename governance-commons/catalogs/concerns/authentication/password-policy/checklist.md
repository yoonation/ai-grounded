---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.password-policy-password-policy"
title: "authentication.password-policy review checklist: password policy strength"
substrate-rule: "authentication.password-policy"
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
  - "Code changes to password validation logic"
  - "Code changes to signup or password-change flows"
  - "Code changes to password policy configuration"
---

# authentication.password-policy review checklist: password policy strength

## Review questions

### 1. Minimum length adequate

Is the minimum-length requirement at least 8 characters
(substrate floor) with 12 characters recommended?

What good looks like: minimum length 12+; minimum is documented;
enforcement is on the server (client-side check is supplementary).

What needs follow-up: minimum length below 8; no minimum at all;
client-side check only without server enforcement.

### 2. Maximum length permits passphrases

Is the maximum length at least 64 characters (substrate floor)?

What good looks like: maximum length 64+ (up to bcrypt's 72-byte
limit or Argon2id's effective limit); long passphrases accepted.

What needs follow-up: maximum length below 64; truncation
silently applied to long passwords; rejection of long passwords
without clear messaging.

### 3. No composition rules

Are composition rules absent (no mandatory uppercase, lowercase,
number, symbol)?

What good looks like: passwords accepted regardless of character
class composition; long memorable passphrases accepted.

What needs follow-up: composition rules enforced (mandatory
uppercase, mandatory number, etc.); rules produce predictable
substitution patterns attackers handle.

### 4. Breach corpus screening present

Is the application screening passwords against a breach corpus
(HaveIBeenPwned Pwned Passwords or equivalent)?

What good looks like: signup and password-change flows query the
breach corpus using k-anonymity (5-character SHA-1 prefix); the
password or its full hash is never sent to a third party; breached
passwords rejected with clear messaging.

What needs follow-up: no breach screening; screening implementation
sends full password or full hash to a third party.

### 5. No mandatory periodic expiration

Is mandatory periodic password expiration absent (no "change
every 90 days" requirement)?

What good looks like: passwords do not expire on a calendar;
expiration is triggered only on credible compromise signal.

What needs follow-up: mandatory periodic expiration in place;
users adopt minimal-change patterns that weaken passwords.

### 6. Signup and change flows both validate

Are BOTH the signup flow and the password-change flow applying
the policy (including breach screening)?

What good looks like: shared validation function called from both
flows; same rules in both contexts.

What needs follow-up: signup checks policy but password-change
skips it (or vice versa); rules drift between the two flows.

### 7. Rejection message clear

When a password is rejected, does the error message explain why
without being so specific that it helps password-guessing
attackers?

What good looks like: "Password too short" or "This password
appears in a known breach corpus" with link to guidance; clear
to legitimate users.

What needs follow-up: generic "invalid password" without
specifics that confuses users; or overly specific message that
reveals the exact policy rule and helps attackers craft bypasses.

## Reviewer attestation

```
authentication.password-policy review checklist: complete
- Minimum length adequate: PASS / FOLLOW-UP / EXEMPT
- Maximum length permits passphrases: PASS / FOLLOW-UP / EXEMPT
- No composition rules: PASS / FOLLOW-UP / EXEMPT
- Breach corpus screening: PASS / FOLLOW-UP / EXEMPT
- No mandatory periodic expiration: PASS / FOLLOW-UP / EXEMPT
- Signup and change flows both validate: PASS / FOLLOW-UP / EXEMPT
- Rejection message clear: PASS / FOLLOW-UP / EXEMPT
```

## Cross-reference

- Substrate rule: authentication.password-policy in catalogs/concerns/authentication.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/authentication/password-policy-good.md
- Anti-patterns: examples/authentication/password-policy-anti-pattern.md
