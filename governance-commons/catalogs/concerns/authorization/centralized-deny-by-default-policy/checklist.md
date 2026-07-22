---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.centralized-deny-by-default-policy-centralized-deny-by-default-policy"
title: "authorization.centralized-deny-by-default-policy review checklist: centralized deny-by-default policy"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that modify the application's authorization policy (policy file changes, policy engine configuration, role-or-permission definitions)"
  - "Code changes that add or modify authorization-check call sites"
  - "Code changes to the policy point itself (policy engine integration, framework authorization abstraction)"
  - "Periodic policy audit (substrate-recommended quarterly)"
---

# authorization.centralized-deny-by-default-policy review checklist: centralized deny-by-default policy

## How to use this binding

The checklist pairs with authorization.no-hardcoded-role-strings's mechanical detection.
L1 catches the "no hardcoded role strings in business logic"
anti-pattern; this L2 review confirms the centralized
replacement satisfies the substrate's quality bar:
centralization, deny-by-default, and testability as data.

Reviewers answer every question below when reviewing pull
requests that match the triggers or when conducting quarterly
policy audits. Unanswered items block merge or close the
audit cycle.

## Review questions

### 1. Centralization: does authz flow through one named entry point?

The application's authorization decisions flow through one
named entry point: a function, a policy engine call site, or
a framework abstraction. Distributed authz logic (multiple
inline checks scattered across handlers) does not satisfy the
rule.

What good looks like: every authorization check in the
application is a call to a single centralized policy point
(or a small number of well-documented entry points covering
distinct concern domains, with documented rationale for the
multi-entry pattern); a reviewer can identify the policy
point in one read of the codebase.

What needs follow-up: authorization checks appear inline in
business handlers as role-string comparisons; multiple
authorization patterns coexist without documentation;
"centralized" exists as a function but is bypassed by
several handlers.

### 2. Policy representation: is the policy expressed as data or as code?

The policy is expressed as data: Cedar policy files, OPA Rego
rule files, Casbin policy CSV, Pundit policy classes, Django
Guardian permission grants, framework-native role-permission
tables. Imperative code paths and inline role comparisons do
not satisfy the rule.

What good looks like: the policy is a set of files, database
rows, or other data artifacts that can be loaded
independently of business code; the policy's content can be
diffed across revisions.

What needs follow-up: the policy is encoded as imperative
function chains and conditional logic distributed across
handlers; the policy is a hardcoded constant in business
code; the policy is a configuration but the actual decision
logic is in code that consults the configuration.

### 3. Default decision: deny-by-default?

The default decision for any unspecified principal-action-
resource combination is deny. New actions are initially
inaccessible to every principal until an explicit allow is
added.

What good looks like: the policy engine's configured default
is deny; the application's authorization call sites trust
the default and do not add their own fallback behavior; the
policy unit tests assert deny-by-default explicitly with an
arbitrary unspecified action.

What needs follow-up: the policy is allow-by-default (every
new action implicitly grants access until an explicit deny);
the deny-by-default property is asserted in documentation
but not in tests; the policy engine's default is deny but
application call sites override it with allow.

### 4. Testability: are policy unit tests present?

Policy correctness is verified by unit tests that load the
policy in isolation and assert principal-action-resource
triples evaluate to expected decisions, without exercising
business handlers.

What good looks like: tests exist for each policy rule
(positive: principal with grant gets allow; negative:
principal without grant gets deny); tests for deny-by-
default (an arbitrary unspecified action gets deny); tests
run in CI and block merge on regression.

What needs follow-up: the policy is tested only through
integration tests that exercise business handlers (policy
bugs conflated with business-logic bugs); the policy tests
do not cover deny-by-default; policy tests exist but do not
run in CI.

### 5. Policy change process: how are changes introduced?

Policy changes go through the same code review process as
code changes. Policy changes that expand access have higher
review scrutiny than policy changes that restrict access.

What good looks like: policy files live in version control;
PRs to policy files follow the application's standard review
process; changes that broaden access (add allows, remove
denies, widen scope) require approval from a designated
authorization-domain reviewer; policy changes are linked to
the operational or business reason that motivated them.

What needs follow-up: policy lives in a database modifiable
without code review; policy changes are exempt from the
standard review process; expansion and restriction changes
get equal scrutiny.

### 6. Conflict resolution: are overlapping rules deterministic?

When multiple rules match the same principal-action-resource
triple, the resolution is deterministic and documented.
Common resolutions: explicit deny overrides explicit allow;
most-specific rule wins; rule ordering defines precedence.

What good looks like: the resolution rule is documented in
the application's authorization MADR; policy unit tests
exercise conflict cases and assert the resolution; the
policy engine's behavior matches the documented resolution.

What needs follow-up: conflicts are not addressed; the
policy engine's default resolution is unknown to the
authors; the resolution differs across the application
(some call sites use deny-overrides, others use allow-
overrides).

### 7. Policy versioning: can policies be rolled back?

Policy is version-controlled and rollbacks are operationally
straightforward. The application can pin to a known-good
policy version if a recent policy change is suspected of
introducing a regression.

What good looks like: policy version is tracked alongside
application version; rollback procedure exists and is
exercised in a runbook; emergency policy rollback can be
performed without a code deploy if the policy is loaded at
runtime.

What needs follow-up: policy is updated in-place without
versioning; rollback requires reverting a database state
that may have moved on; rollback procedure exists in
principle but has never been exercised.

### 8. Policy-engine selection rationale: does it match the model choice?

The selected policy engine or framework abstraction fits the
authorization model chosen in the application's authorization.authorization-model-selection
MADR (RBAC, ABAC, ReBAC, hybrid).

What good looks like: the MADR documents the engine choice;
the engine's idioms match the model (Cedar for ABAC and
ReBAC; OPA Rego for multi-service deployments; Casbin for
RBAC with hierarchical roles; framework-native for
applications staying within one framework's conventions).

What needs follow-up: the engine choice predates the model
decision and is being retrofitted; the engine handles the
declared model but is being stretched into another (RBAC
engine encoding ABAC logic with proliferating roles); no
documented rationale exists for the engine choice.

## Reviewer attestation

When all eight questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review or quarterly audit report:

```
authorization.centralized-deny-by-default-policy review checklist: complete
- Centralization: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Policy representation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Default decision: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Testability: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Policy change process: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Conflict resolution: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Policy versioning: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Engine selection rationale: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or close the audit cycle.
EXEMPT items require documented rationale in the pull-request
thread or the audit report.

## Cross-reference

- Substrate rule: authorization.centralized-deny-by-default-policy in catalogs/concerns/authorization.oscal.yaml
- Paired mechanical rule: authorization.no-hardcoded-role-strings (no hardcoded role strings in business logic)
- Related rule: authorization.authorization-model-selection (authorization model selection drives engine choice)
- Related rule: authorization.audit-events-on-decisions (audit events emitted from the centralized policy point)
- Test binding: test-template.md
- Good examples: examples/authorization/centralized-deny-by-default-policy-good.md
- Anti-patterns: examples/authorization/centralized-deny-by-default-policy-anti-pattern.md
- OWASP ASVS v5.0.0 V8.3.1
- NIST SP 800-53 AC-3 Access Enforcement and AC-25 Reference Monitor
- Cedar policy engine (Amazon, Apache-2.0)
- Open Policy Agent and Rego (CNCF, Apache-2.0)
