---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authorization.least-privilege-role-design-least-privilege-role-design"
title: "authorization.least-privilege-role-design test template: least-privilege role and permission design"
substrate-rule: "authorization.least-privilege-role-design"
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

# authorization.least-privilege-role-design test template: least-privilege role and permission design

## How to use this binding

Least-privilege is a property of role and permission design,
not of any single code path. The scenarios below verify the
property holds end-to-end: a principal granted role R can do
the actions R is intended to permit, and CANNOT do actions R
is not intended to permit.

These scenarios are integration tests structured around the
application's role catalog. The substrate-recommended pattern
is to maintain the role-to-permitted-actions mapping as a
data artifact (CSV, JSON, policy file) and to derive the test
suite from that artifact. Then a change to the role catalog
automatically updates the test suite without code edits.

The substrate-recommended coverage target is: every role
defined in the application's role catalog has at least one
positive scenario per permitted action and at least one
negative scenario per prohibited action.

## Scenario 1: Role grants permitted actions

**Preconditions**
- A role R is defined in the application's role catalog with
  documented permitted actions {A1, A2, A3}
- Test principal P is granted role R and only role R
- The application's resource fixture provides resources of
  the types that actions A1, A2, A3 apply to

**Action**
- P attempts each action A1, A2, A3 on appropriately-scoped
  test resources

**Expected**
- Each of A1, A2, A3 returns success
- Audit events record allow decisions for each

## Scenario 2: Role denies non-permitted actions

**Preconditions**
- Role R is defined with permitted actions {A1, A2, A3}
- Actions A4, A5, A6 exist in the application but are NOT
  permitted by role R
- Test principal P is granted role R and only role R

**Action**
- P attempts each action A4, A5, A6

**Expected**
- Each of A4, A5, A6 returns HTTP 403
- Audit events record deny decisions for each
- The application state is unchanged with respect to A4, A5,
  A6 (no partial effect)

## Scenario 3: Role separation prevents cross-role escalation

**Preconditions**
- Two roles R_reader and R_admin are defined
- R_reader has read-only actions
- R_admin has all actions
- Test principal P_reader is granted R_reader only
- The application's UI exposes admin actions only to admins

**Action**
- P_reader bypasses the UI affordance and submits a direct
  HTTP request for an admin action (e.g., DELETE /users/{id}
  or PUT /system-config)

**Expected**
- HTTP 403 Forbidden
- The admin action does not execute
- An audit event records the deny with principal=P_reader,
  action=<admin action>, decision=deny

Notes: this scenario covers the case where the UI gives
appropriate affordances per role, but the authorization
enforcement must be at the server side regardless of UI
state (per authorization.no-client-side-only-authz prohibition on client-side-only
authz).

## Scenario 4: Permission granularity is action-level, not endpoint-level

**Preconditions**
- The application has an endpoint POST /reports that supports
  multiple actions via a body field (action=draft, action=
  publish, action=archive)
- Role R_editor permits draft and archive but not publish

**Action**
- Test principal P_editor (granted R_editor) submits:
  - POST /reports with body {"action": "draft", ...}
  - POST /reports with body {"action": "publish", ...}
  - POST /reports with body {"action": "archive", ...}

**Expected**
- The draft and archive requests succeed
- The publish request returns HTTP 403
- An audit event records the deny for publish with the
  specific action recorded, not just the endpoint

Notes: this scenario verifies that authorization checks the
action being attempted, not merely the endpoint being hit.
Coarse endpoint-only permissions are an L2-002 finding.

## Scenario 5: Role removal revokes access promptly

**Preconditions**
- Test principal P is granted role R with an active session
- Through the application's role-management mechanism, role
  R is removed from P

**Action**
- P attempts an action permitted by R after the role removal
- The substrate-recommended timeline for revocation effect:
  the next request after role removal must reflect the
  revocation; sessions are not exempt

**Expected**
- The action returns HTTP 403
- An audit event records the deny

Notes: revocation latency is a property of the session and
permission-lookup model. If the application caches role
grants for performance, the cache must respect a revocation
TTL or be invalidated explicitly on role change. Long
revocation latency is an L2-002 finding.

## Scenario 6: Permission grants are auditable

**Preconditions**
- The application supports granting and revoking role
  assignments via a designated admin interface
- An admin principal P_admin has the role-management
  permission

**Action**
- P_admin grants role R to principal P_target
- P_admin revokes role R from principal P_target

**Expected**
- Both the grant and revoke produce audit events at WARN or
  higher severity (these are privilege-changing operations
  per authorization.step-up-and-audit-for-privilege-changes)
- The audit events record: actor (P_admin), target
  (P_target), role granted or revoked, timestamp
- The events appear in the application's audit log within
  one polling cycle

Notes: this scenario pairs with authorization.step-up-and-audit-for-privilege-changes (privilege-
changing operations require audit). A least-privilege design
where grants are unauditable is not actually a least-
privilege design.

## Test scaffold: role catalog as data

The substrate recommends representing the role catalog as data
(JSON, CSV, or policy file) so the test suite can be
parameterized from it:

```python
# Example test scaffold pattern (Python / pytest)
import yaml
import pytest

ROLE_CATALOG = yaml.safe_load(open("policies/roles.yaml"))

@pytest.mark.parametrize("role,permitted_actions",
                         [(r, ROLE_CATALOG[r]["permitted"])
                          for r in ROLE_CATALOG])
def test_role_grants_permitted_actions(role, permitted_actions):
    principal = create_principal_with_role(role)
    for action in permitted_actions:
        response = attempt(principal, action)
        assert response.status_code == 200

@pytest.mark.parametrize("role,prohibited_actions",
                         [(r, ROLE_CATALOG[r]["prohibited"])
                          for r in ROLE_CATALOG])
def test_role_denies_prohibited_actions(role, prohibited_actions):
    principal = create_principal_with_role(role)
    for action in prohibited_actions:
        response = attempt(principal, action)
        assert response.status_code == 403
```

The scaffold is consumer-implemented; the substrate specifies
the requirement (test the role catalog as the source of truth)
but not the framework details.

## Cross-reference

- Substrate rule: authorization.least-privilege-role-design in catalogs/concerns/authorization.oscal.yaml
- Review checklist binding: checklist.md
- Good examples: examples/authorization/least-privilege-role-design-good.md
- Anti-patterns: examples/authorization/least-privilege-role-design-anti-pattern.md
- Related rules: authorization.no-hardcoded-role-strings (no hardcoded role strings), authorization.step-up-and-audit-for-privilege-changes (privilege-change audit), authorization.centralized-deny-by-default-policy (centralized policy)
