---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authorization.centralized-deny-by-default-policy-centralized-deny-by-default-policy"
title: "authorization.centralized-deny-by-default-policy test template: centralized deny-by-default policy"
substrate-rule: "authorization.centralized-deny-by-default-policy"
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

# authorization.centralized-deny-by-default-policy test template: centralized deny-by-default policy

## How to use this binding

The substrate-critical property tested here is that the
application's policy point is the single decisive authority
for authorization, and that its default verdict is deny.
These properties cannot be observed from any single endpoint
test in isolation; they emerge from the system's overall
behavior under absent, malformed, or unknown policy input.

These scenarios test the policy point as a unit and also
test the system end-to-end with the policy point in place.
The unit scenarios verify policy semantics; the integration
scenarios verify the policy point is actually consulted by
every code path that needs an authorization decision.

The substrate-recommended coverage target is: every plausible
input to the policy point produces a decision (no input
produces an exception, no input is silently dropped), and the
default branch denies.

## Scenario 1: Policy point deny-by-default for unknown subject

**Preconditions**
- The policy point is initialized with the application's
  policy artifact (Cedar policies, OPA Rego files, Casbin
  CSV, Pundit policy classes, etc.)
- A subject identifier that has no associated grants in the
  policy artifact

**Action**
- The test invokes the policy point with
  decide(subject=unknown, action="read", resource=R1)

**Expected**
- The decision returned is "deny"
- No exception is raised
- The decision is consistent across repeated invocations
  with identical inputs

Notes: this is the foundational deny-by-default semantic.
A policy point that returns "allow" or throws an exception
for unknown subjects is an L2-005 finding.

## Scenario 2: Policy point deny-by-default for unknown action

**Preconditions**
- A subject S exists with documented permitted actions
  {read, write}
- The test invokes the policy point with an action that is
  not in the documented action vocabulary (e.g., "execute"
  or "unknown_action")

**Action**
- The test invokes decide(subject=S, action="execute",
  resource=R1)

**Expected**
- The decision returned is "deny"
- The unknown action does not silently map to "read" or
  "write"
- An audit event records the deny

## Scenario 3: Policy point deny-by-default for unknown resource

**Preconditions**
- Subject S has documented permitted actions on resource
  class C1
- The test invokes the policy point with a resource of an
  undocumented class C_unknown

**Action**
- The test invokes decide(subject=S, action="read",
  resource=R_of_class_C_unknown)

**Expected**
- The decision returned is "deny"
- An audit event records the deny

## Scenario 4: Policy point is the only path to a decision

**Preconditions**
- The application's codebase is instrumented to record every
  authorization decision made
- The instrumentation captures: location in code where the
  decision was made, and whether the policy point was
  consulted

**Action**
- The test exercises every authorization-relevant endpoint
  (the substrate-recommended coverage target is the union
  of endpoints in the authorization.object-level-authorization and authorization.least-privilege-role-design test
  scopes)

**Expected**
- Every recorded decision corresponds to a call to the
  centralized policy point
- No decision is made by inline role-string comparison or
  ad-hoc permission check

Notes: this scenario tests that the policy point is decisive.
A common L2-005 failure is a centralized policy point that
exists but is bypassed by some endpoints. The instrumentation
catches the bypass.

## Scenario 5: Policy can be unit-tested in isolation

**Preconditions**
- The policy artifact is loadable independently of the
  application's runtime
- A test harness can initialize the policy point with the
  artifact and submit decision requests

**Action**
- The test loads the production policy artifact into a test
  policy-point instance
- For each role R defined in the policy:
  - For each permitted action A in R: invoke
    decide(subject=R, action=A, resource=appropriate)
    and assert allow
  - For each prohibited action A in R: invoke
    decide(subject=R, action=A, resource=appropriate)
    and assert deny

**Expected**
- All assertions pass
- The test runs without invoking the application's web
  framework, database, or other runtime components

Notes: this scenario is the substrate-specified property that
policy is testable as data. If unit-testing the policy
requires the full application stack, the policy is not
genuinely centralized.

## Scenario 6: Policy change without code change

**Preconditions**
- The application is running with policy version V1
- A policy artifact V2 differs from V1 by adding a permitted
  action to one role

**Action**
- The test deploys V2 by replacing the policy artifact (no
  application code change, no application restart if the
  policy point supports hot reload)
- The test exercises the changed action with a principal
  granted the affected role

**Expected**
- Under V1: the action returned deny
- Under V2: the action returns allow
- The change to behavior is exclusively driven by the policy
  artifact change

Notes: this scenario validates the substrate-required
property that policy is data, not code. If a policy change
requires application code change to take effect, the policy
is encoded in code, which is an L2-005 finding.

## Scenario 7: Policy point handles malformed input safely

**Preconditions**
- The policy point is initialized

**Action**
- The test invokes the policy point with malformed input:
  - decide(subject=None, action="read", resource=R1)
  - decide(subject="", action="", resource="")
  - decide(subject=S, action="read", resource=None)
  - decide(subject=S, action=very_long_string,
    resource=R1)

**Expected**
- Every malformed invocation returns "deny"
- No malformed invocation returns "allow"
- The policy point may log a warning indicating malformed
  input
- No malformed invocation causes the policy point to throw
  an unhandled exception

Notes: malformed input is a substrate-required test case
because attacker-controlled inputs can be malformed. The
policy point's response must be safe regardless of input
shape.

## Test scaffold: policy artifact loading

The scaffold loads the application's actual production
policy artifact for unit testing. The substrate-recommended
pattern:

```python
# Example scaffold (Python / Cedar)
import cedar_engine
import pytest

@pytest.fixture(scope="session")
def production_policy_point():
    policy_files = glob.glob("policies/*.cedar")
    schema_file = "policies/schema.json"
    engine = cedar_engine.Engine(
        policies=policy_files,
        schema=schema_file
    )
    return engine

def test_admin_can_delete(production_policy_point):
    decision = production_policy_point.is_authorized(
        principal="Role::admin",
        action="Action::delete",
        resource="Resource::user_123"
    )
    assert decision == "allow"

def test_admin_cannot_unknown_action(production_policy_point):
    decision = production_policy_point.is_authorized(
        principal="Role::admin",
        action="Action::cosmic_ray_user",
        resource="Resource::user_123"
    )
    assert decision == "deny"
```

The scaffold is consumer-implemented; the substrate specifies
the property (policy unit-testable as data) without
prescribing the engine.

## Cross-reference

- Substrate rule: authorization.centralized-deny-by-default-policy in catalogs/concerns/authorization.oscal.yaml
- Review checklist binding: checklist.md
- Good examples: examples/authorization/centralized-deny-by-default-policy-good.md
- Anti-patterns: examples/authorization/centralized-deny-by-default-policy-anti-pattern.md
- Related rules: authorization.no-hardcoded-role-strings (no hardcoded role strings, the mechanical pairing), authorization.least-privilege-role-design (least-privilege role design), authorization.audit-events-on-decisions (audit events on decisions, the substrate-recommended emission point is the policy point)
