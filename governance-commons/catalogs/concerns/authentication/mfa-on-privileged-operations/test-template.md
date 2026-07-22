---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authentication.mfa-on-privileged-operations-mfa-on-privileged-ops"
title: "authentication.mfa-on-privileged-operations test template: MFA on privileged operations"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authentication.mfa-on-privileged-operations test template: MFA on privileged operations

## Scenario 1: Privileged operation without recent MFA is rejected

**Preconditions**
- Test user authenticated via standard login (no recent MFA)
- Test endpoint: password change (or any other privileged op)

**Action**
- Submit password change request with valid session

**Expected**
- HTTP 401 or structured response indicating MFA required
- Password is NOT changed
- Audit log records the attempt with "stale" MFA result

## Scenario 2: Privileged operation with stale MFA is rejected

**Preconditions**
- Test user completed MFA challenge T+freshness-window minutes ago
- Test endpoint: privileged operation

**Action**
- Submit privileged operation with valid session

**Expected**
- HTTP 401 with MFA-required indication
- Operation is NOT executed
- Audit log records the attempt with "stale" MFA result

## Scenario 3: Privileged operation with fresh MFA succeeds

**Preconditions**
- Test user completed MFA challenge within the freshness window
- Test endpoint: privileged operation

**Action**
- Submit privileged operation with valid session

**Expected**
- HTTP 200 with successful response
- Operation IS executed
- Audit log records the attempt with "passed" MFA result

## Scenario 4: Freshness timestamp resets on successful MFA

**Preconditions**
- Test user authenticated but no recent MFA
- Test endpoint: privileged operation

**Action**
- Submit privileged operation; expect rejection (per Scenario 1)
- Complete MFA challenge
- Re-submit privileged operation

**Expected**
- Second submission succeeds (freshness timestamp was updated)
- Audit log records both attempts

## Scenario 5: Freshness window does not extend with session activity

**Preconditions**
- Test user completed MFA exactly at the freshness window boundary
- Test endpoint: privileged operation

**Action**
- Make several non-privileged authenticated requests
- After freshness window elapses (since MFA, not since last
  request), attempt privileged operation

**Expected**
- Privileged operation rejected
- Session activity does NOT extend MFA freshness; only successful
  MFA challenge does

## Scenario 6: Different privileged ops can have different windows

**Preconditions**
- Operations configured with different freshness windows (e.g.,
  account deletion 5min, payment change 10min, password change 15min)
- User completed MFA 12 minutes ago

**Action**
- Attempt account deletion (5min window)
- Attempt payment change (10min window)
- Attempt password change (15min window)

**Expected**
- Account deletion rejected (12min > 5min)
- Payment change rejected (12min > 10min)
- Password change succeeds (12min < 15min)

## Scenario 7: Audit log captures all attempts

**Preconditions**
- Audit log accessible via test infrastructure

**Action**
- Perform mix of passed, stale, and failed MFA attempts

**Expected**
- Every attempt appears in audit log with: user identifier,
  operation type, MFA freshness result (passed/stale/failed),
  timestamp, source identifier

## Cross-reference

- Substrate rule: authentication.mfa-on-privileged-operations in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Good examples: examples/authentication/mfa-on-privileged-ops-good.md
- Anti-patterns: examples/authentication/mfa-on-privileged-ops-anti-pattern.md
