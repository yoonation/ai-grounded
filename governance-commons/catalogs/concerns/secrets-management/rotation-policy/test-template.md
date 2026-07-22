---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.secrets-management.rotation-policy-rotation-policy"
title: "secrets-management.rotation-policy test template: rotation policy execution"
substrate-rule: "secrets-management.rotation-policy"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# secrets-management.rotation-policy test template: rotation policy execution

## How to use this binding

Rotation tests are typically scheduled rather than per-PR
because they require platform-side rotation execution.
Substrate-recommended cadence for the test suite: weekly in a
staging-equivalent environment.

The tests verify the rotation procedure end-to-end: a scheduled
rotation event occurs, the new credential is issued, the
application picks it up within the documented window, the old
credential is revoked after the dual-key window, and audit
events are recorded.

## Scenario 1: Scheduled rotation produces a new credential

**Preconditions**
- A rotatable secret exists at a known path with a known current
  value
- Rotation is configured at the platform level (Vault rotation,
  AWS Secrets Manager rotation Lambda, GCP rotation policy,
  Azure rotation policy)

**Action**
- Trigger the rotation (manually invoke or wait for scheduled
  execution in a test environment with accelerated schedule)

**Expected**
- The platform produces a new credential value at the same path
- The platform's audit log records the rotation event
- The old credential is recorded in the dual-key state, not
  immediately revoked

## Scenario 2: Application picks up the rotated value

**Preconditions**
- Application is running with the pre-rotation credential
  cached
- Rotation has just executed (Scenario 1 completed)

**Action**
- Wait for the application's refresh interval to elapse
- Trigger the code path that uses the credential

**Expected**
- The application uses the new credential value
- The downstream system (database, API, etc.) accepts
  authentication with the new credential
- The refresh happened automatically; no restart was required

## Scenario 3: Old credential remains valid during the dual-key window

**Preconditions**
- Rotation has just executed
- An application replica (simulating staggered rollout) is
  still using the cached old credential

**Action**
- Trigger the code path on the replica using the old
  credential

**Expected**
- The downstream system accepts the old credential during the
  dual-key window
- Both credentials authenticate successfully during the window
- Service is not disrupted by the staggered rollout

## Scenario 4: Old credential is rejected after the dual-key window

**Preconditions**
- Rotation has executed
- The dual-key window has elapsed
- An application replica is still attempting to use the old
  credential (this is a simulated failure mode)

**Action**
- After the dual-key window, trigger the code path using the
  old credential

**Expected**
- The downstream system rejects the old credential
- The application surfaces the authentication failure
- Monitoring catches the failure and alerts (the replica's
  refresh logic should have caught the rotation; failure here
  indicates a refresh-logic bug)

## Scenario 5: Rotation is recorded in audit and observability

**Preconditions**
- Rotation has just executed

**Action**
- Query the security log aggregator for events in the rotation
  window

**Expected**
- The rotation event appears in the audit log with: secret
  identifier, rotation timestamp, rotation initiator (scheduler
  or human)
- The event correlates with monitoring dashboards showing
  refresh activity on application replicas

## Scenario 6: Manual out-of-band rotation succeeds

**Preconditions**
- The runbook documents a manual rotation procedure for
  incident-driven rotation
- A test secret is targeted for the exercise

**Action**
- Execute the manual rotation procedure end-to-end

**Expected**
- The procedure completes within the documented time bound
- The new credential is in use; the old is revoked
- The procedure works without requiring tribal knowledge not
  in the runbook

## Scenario 7: Inventory matches reality

**Preconditions**
- The project maintains an inventory of rotatable secrets

**Action**
- For each entry in the inventory, query the platform for the
  last rotation timestamp

**Expected**
- Every entry's last-rotation timestamp is within the inventory-
  declared cadence
- No secrets exist on the platform that are not in the inventory
- No inventory entries refer to secrets that no longer exist

## Scenario 8: Cross-environment isolation holds during rotation

**Preconditions**
- The dev and prod environments have separately configured
  rotation
- A dev rotation is initiated

**Action**
- Verify the rotation event affects only dev

**Expected**
- The dev secret is rotated
- The prod secret is unchanged
- Audit logs reflect the scoped change

## Test attestation

```
secrets-management.rotation-policy test suite: PASSING
- Scenario 1 (rotation produces new credential): PASS
- Scenario 2 (application picks up rotated value): PASS
- Scenario 3 (old credential valid during dual-key window): PASS
- Scenario 4 (old credential rejected after window): PASS
- Scenario 5 (rotation recorded in audit): PASS
- Scenario 6 (manual rotation succeeds): PASS
- Scenario 7 (inventory matches reality): PASS
- Scenario 8 (cross-environment isolation): PASS
```

## Cross-reference

- Substrate rule: secrets-management.rotation-policy
- Review checklist: checklist.md
- Good examples: examples/secrets-management/rotation-policy-good.md
