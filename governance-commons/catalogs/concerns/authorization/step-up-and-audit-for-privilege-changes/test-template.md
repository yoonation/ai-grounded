---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authorization.step-up-and-audit-for-privilege-changes-step-up-and-audit-for-privilege-changes"
title: "authorization.step-up-and-audit-for-privilege-changes test template: step-up authentication and audit for privilege changes"
substrate-rule: "authorization.step-up-and-audit-for-privilege-changes"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-22"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authorization.step-up-and-audit-for-privilege-changes test template: step-up authentication and audit for privilege changes

## How to use this binding

This binding pairs with authentication.mfa-on-privileged-operations (MFA on privileged
operations); the test scenarios extend the authentication.mfa-on-privileged-operations
pattern to privilege-changing operations specifically: role
grants and revocations, permission edits, ownership transfers,
delegation creation, and similar.

Privilege-changing operations are higher-risk than other
authenticated operations because they expand the authorization
surface of one or more principals. Step-up authentication
ensures the actor is recently challenged (not just authenticated
via a session that may have been hijacked), and audit captures
the change for incident investigation.

These are integration tests against the application's privilege-
management endpoints. The substrate-recommended coverage target
is: every endpoint that grants, revokes, or modifies a role,
permission, ownership, or delegation has at least one scenario
each for: step-up required, step-up satisfied, step-up stale,
audit emission.

## Scenario 1: Privilege change without recent step-up is rejected

**Preconditions**
- Test admin principal P_admin authenticated via standard
  session (no recent MFA step-up)
- Target principal P_target exists with role R_basic
- Endpoint POST /admin/roles accepts {principal_id, role}

**Action**
- P_admin submits POST /admin/roles with body
  {"principal_id": P_target.id, "role": "R_admin"} using
  the standard session

**Expected**
- HTTP 401 or structured response indicating step-up required
- The role assignment is NOT made; P_target still has only
  R_basic
- An audit event records the attempt with result=
  "step-up-required" and actor=P_admin
- The response body does not reveal P_target's existing roles

## Scenario 2: Privilege change with stale step-up is rejected

**Preconditions**
- P_admin completed MFA challenge at time T-X minutes ago,
  where X exceeds the substrate-recommended step-up freshness
  window (substrate-recommended: 5 to 15 minutes for
  privilege changes)

**Action**
- P_admin submits the role-grant request

**Expected**
- HTTP 401 with step-up-required indication
- Operation NOT executed
- An audit event records the attempt with result=
  "step-up-stale"

## Scenario 3: Privilege change with fresh step-up succeeds

**Preconditions**
- P_admin completed MFA challenge within the freshness window
- The step-up claim is bound to the session and to the
  intended privileged operation

**Action**
- P_admin submits the role-grant request including the
  step-up token or claim

**Expected**
- HTTP 200 (or 201 for created assignment)
- P_target now has the granted role
- An audit event records: actor=P_admin, target=P_target,
  action="role-grant", role="R_admin", decision="allow",
  step-up-verified=true, severity=WARN minimum

## Scenario 4: Privilege REVOCATION also requires step-up

**Preconditions**
- P_admin authenticated via standard session, no recent step-up
- P_target has role R_admin

**Action**
- P_admin submits DELETE /admin/roles/{P_target}/{R_admin}
  via standard session

**Expected**
- HTTP 401 with step-up-required indication
- The role IS NOT revoked
- P_target retains R_admin
- Audit event records the attempt

Notes: revocations are privilege-changing operations.
Treating revocations as lower-risk is a common failure mode;
revocations can be weaponized (revoking the security team's
access during an attack), so they require the same step-up
protection as grants.

## Scenario 5: Ownership transfer requires step-up

**Preconditions**
- Test principal P_alice owns resource R
- Endpoint POST /resources/{id}/transfer-ownership accepts
  {new_owner_id}

**Action**
- P_alice (no recent step-up) submits a transfer request
  for R to P_bob

**Expected**
- HTTP 401 with step-up-required indication
- Ownership of R does NOT change
- Audit event records the attempted ownership change

## Scenario 6: Audit event includes both old and new state

**Preconditions**
- P_admin with fresh step-up
- P_target has role R_basic

**Action**
- P_admin submits role-grant changing P_target from
  {R_basic} to {R_basic, R_admin}

**Expected**
- HTTP 200
- The audit event records: principal=P_admin, target=P_target,
  action="role-grant", before-state={R_basic},
  after-state={R_basic, R_admin}, decision="allow",
  step-up-verified=true, timestamp, request correlation ID

Notes: the audit event must capture sufficient state for
post-incident reconstruction. Recording only the action and
the principal is insufficient; the before-and-after state
matters for investigations.

## Scenario 7: Step-up token cannot be reused across operations

**Preconditions**
- P_admin completed step-up bound to operation
  "role-grant for P_target1"

**Action**
- P_admin attempts a different privilege operation
  "role-grant for P_target2" reusing the step-up token

**Expected**
- HTTP 401 or 403 with step-up-required indication, OR the
  request succeeds only if the application's step-up model
  is session-scoped (substrate accepts both operation-bound
  and session-scoped step-up provided the freshness window
  is short for session-scoped)
- If session-scoped: the substrate-recommended window is
  shorter (5 minutes) than for non-step-up actions

Notes: this scenario tests the application's documented step-up
binding model. The MFA factor selection MADR (authentication.mfa-factor-selection if
authored) and the application's authentication strategy MADR
(authentication.authentication-strategy) inform the expected behavior.

## Scenario 8: Bulk privilege operations are audited per change

**Preconditions**
- P_admin with fresh step-up
- The application has an endpoint POST /admin/roles/batch
  accepting multiple {principal, role} pairs

**Action**
- P_admin submits a batch of 5 role assignments

**Expected**
- HTTP 200 (or partial-success status if the application
  supports partial failure)
- 5 separate audit events emitted, one per assignment, each
  with the full event content per Scenario 6

Notes: bulk operations must NOT be audited as one event
covering all changes. The audit must permit per-change
reconstruction.

## Test scaffold: step-up state simulation

Tests must simulate both pre-step-up and post-step-up state.
The scaffold depends on the application's step-up mechanism:

- TOTP/HOTP: tests use a known test secret and generate
  current codes; the test scaffold can advance simulated time
  to test stale step-up
- WebAuthn: tests use a virtual authenticator (per WebAuthn
  test infrastructure) bound to the test principal
- Push-based MFA: tests use a deterministic test mode that
  treats the push as approved; freshness is controlled by
  the application's step-up state model

The scaffold is consumer-implemented; the substrate specifies
the requirement (test pre, post, and stale step-up states)
without prescribing the mechanism.

## Cross-reference

- Substrate rule: authorization.step-up-and-audit-for-privilege-changes in catalogs/concerns/authorization.oscal.yaml
- Review checklist binding: checklist.md
- Good examples: examples/authorization/step-up-and-audit-for-privilege-changes-good.md
- Anti-patterns: examples/authorization/step-up-and-audit-for-privilege-changes-anti-pattern.md
- Related rules: authentication.mfa-on-privileged-operations (MFA on privileged operations, the authentication-side counterpart), authorization.audit-events-on-decisions (audit events on decisions)
