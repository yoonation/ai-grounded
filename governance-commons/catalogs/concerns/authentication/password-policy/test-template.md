---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authentication.password-policy-password-policy"
title: "authentication.password-policy test template: password policy strength"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authentication.password-policy test template: password policy strength

## Scenario 1: Signup rejects too-short password

**Preconditions**
- Application configured with minimum length (substrate-recommended
  12; absolute floor 8)

**Action**
- Attempt to register an account with a password shorter than the
  configured minimum (e.g., 6 characters)

**Expected**
- Registration rejected
- Error message indicates minimum length requirement
- No account is created

## Scenario 2: Signup accepts long memorable passphrase

**Preconditions**
- Application configured per substrate guidance

**Action**
- Attempt to register an account with a 40-character memorable
  passphrase composed of common words (e.g.,
  "correct-horse-battery-staple-with-extra-spice")

**Expected**
- Registration succeeds
- The long passphrase is not truncated silently
- Authentication with the passphrase works on subsequent login

## Scenario 3: Signup rejects breach-corpus passwords

**Preconditions**
- Breach corpus screening enabled (HaveIBeenPwned API or
  equivalent)
- Known-breached password available (e.g., "password123" appears
  in the corpus with millions of occurrences)

**Action**
- Attempt to register an account using the known-breached password

**Expected**
- Registration rejected
- Error message indicates the password appears in a breach corpus
- No account is created

## Scenario 4: Signup accepts non-breached strong password

**Preconditions**
- Application configured per substrate guidance

**Action**
- Generate a cryptographically random password that does NOT
  appear in the breach corpus (use a passphrase generator
  producing a 40-character output)
- Attempt to register an account with that password

**Expected**
- Registration succeeds

## Scenario 5: Password change applies the same policy

**Preconditions**
- Account exists with a valid password
- User is authenticated

**Action**
- Attempt to change password to a too-short value
- Attempt to change password to a breach-corpus value
- Attempt to change password to a valid value

**Expected**
- First two attempts rejected with appropriate error messages
- Third attempt succeeds
- The new password works for login

## Scenario 6: No composition rules enforced

**Preconditions**
- Application configured per substrate guidance

**Action**
- Attempt to register an account with a password meeting length
  requirements but containing no uppercase, no numbers, and no
  symbols (e.g., "thisisalonglowercasepassphrase")

**Expected**
- Registration succeeds (composition rules absent per
  authentication.password-policy)
- Authentication with the password works

## Scenario 7: Maximum length permits long passwords

**Preconditions**
- Application configured per substrate guidance (max length 64+)

**Action**
- Attempt to register an account with a 64-character password
- Attempt to register an account with a 100-character password

**Expected**
- 64-character password accepted
- 100-character password accepted (unless application uses bcrypt
  which truncates at 72 bytes; in that case, the application
  should communicate the limit clearly)

## Scenario 8: Breach corpus query uses k-anonymity

**Preconditions**
- Network traffic capture available for the test environment

**Action**
- Attempt to register with any password
- Inspect outbound traffic to the breach corpus service

**Expected**
- The application sends only the first 5 characters of the
  password's SHA-1 hash to the breach corpus service
- The full password is never transmitted
- The full hash is never transmitted

## Cross-reference

- Substrate rule: authentication.password-policy in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Good examples: examples/authentication/password-policy-good.md
- Anti-patterns: examples/authentication/password-policy-anti-pattern.md
