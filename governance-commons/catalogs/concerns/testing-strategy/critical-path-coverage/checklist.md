---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.testing-strategy.critical-path-coverage-critical-path-coverage"
title: "testing-strategy.critical-path-coverage review checklist: critical path coverage"
substrate-rule: "testing-strategy.critical-path-coverage"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-25"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that touch authentication, authorization, payment, or state-changing flows"
  - "Code changes that introduce new critical business paths"
  - "Code changes that modify error-handling on critical paths (per ERR-L2-* rules)"
  - "Periodic critical-path-coverage audit (substrate-recommended: per release cycle)"
  - "Detection of low coverage on security-sensitive modules"
---

# testing-strategy.critical-path-coverage review checklist: critical path coverage

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with the substrate's adjacent-concern L1 rules
(AUTH-L1-*, AUTHZ-L1-*, INPUT-L1-*, ERR-L1-*). Those L1 rules catch
the mechanical antipatterns at the boundary; this L2 review confirms
the test suite exercises the critical paths beyond the happy case.

## Review questions

### 1. Critical path catalog: does the application document its critical business paths?

Confirm that the application maintains a documented catalog of
critical business paths. Substrate-recommended categories:
authentication flows (login, logout, password reset, session
refresh), authorization decisions (role assignment, permission
checks, ownership verification), payment and state-changing
operations (transactions, write APIs, bulk actions), data export
(personal data, audit logs), security-sensitive boundary points
(token validation, signature verification).

The catalog lives in the testing-strategy.testing-strategy ADR or in a discoverable
companion document (substrate-acceptable: /docs/critical-paths.md
referenced from the ADR).

### 2. Catalog completeness: are all substrate-recommended categories represented?

Confirm that the catalog includes every category that applies to
this application. An application that handles money but has no
payment-flow critical path entry has an incomplete catalog;
remediate by adding the entry and tracking the coverage gap as a
finding.

For categories that genuinely do not apply (e.g., a stateless
read-only API does not have state-changing operations), the
catalog documents the non-applicability explicitly.

### 3. Per-path test matrix: for each catalogued path, are happy-path, error-path, edge-case, and security-probe tests present?

For every entry in the critical path catalog, confirm the existence
of dedicated tests for each of:

- **Happy path:** the call succeeds with valid inputs. This is
  typically present; absence is the first finding.

- **Error paths:** the call fails when the substrate's recommended
  failure conditions are exercised (network failure, downstream
  dependency unavailable, input validation rejection, authorization
  denial).

- **Edge cases:** boundary values (empty string, empty list, max
  length input, just over limit, just under limit), nulls or
  undefined handling, character set boundaries (Unicode, control
  characters), numeric overflow at integer boundaries.

- **Security probes:** attempts to bypass the substrate's L1
  mechanical rules from adjacent concerns. For authentication
  paths: tests asserting authentication.password-hashing password-hashing strength,
  authentication.token-expiration token expiration enforcement, authentication.generic-failure-responses generic-
  error-messaging (no user enumeration). For authorization paths:
  tests asserting authorization.protected-route-declares-authz route protection, authorization.authz-before-resource-access
  authz-before-access. For input paths: tests asserting
  input-validation.parameterized-queries parameterized queries, input-validation.no-shell-injection shell-injection
  prevention. For error paths: tests asserting error-handling.no-stack-trace-in-response no-stack-
  trace-in-response.

### 4. Test matrix gaps: are gaps tracked and prioritized?

Confirm that the matrix of (critical path × test type) has known
gaps documented as remediation items. Substrate-recommended
prioritization for gap remediation: security probes first, error
paths second, edge cases third.

Empty cells with no tracking are findings. Documented gaps with
remediation owners and target dates are substrate-acceptable
interim states.

### 5. Coverage metric reconciliation: does the line-coverage report agree with the matrix completeness?

Confirm that the line-coverage report on critical-path modules is
consistent with the matrix. A critical-path module with 95% line
coverage that has no security probe tests indicates the matrix
is incomplete or the coverage tool is measuring uninteresting code
paths. Reviewer flags the inconsistency for investigation.

The substrate's L2 review uses the matrix as the authoritative
signal of critical path coverage; the line coverage metric is
secondary and confirms structural exercise.

### 6. Cross-concern security probe alignment: do the security probe tests align with the substrate's L1 rules across concerns?

For each security probe test, confirm it exercises a substrate L1
rule from an adjacent concern. The substrate's compositional
discipline expects critical path security probe tests to be
visible enforcement of the cross-concern L1 rules. Tests that
don't align with any L1 rule signal either an application-specific
critical path beyond the substrate's recommended categories
(substrate-acceptable; document in the catalog) or a security
concern not yet captured in the catalog.

### 7. Test isolation per path: do critical path tests run in isolation, or do they depend on global test ordering?

Confirm that critical path tests are written to run in any order
(see testing-strategy.deterministic-execution determinism). Critical path tests with order
dependencies are flaky on the most important paths; remediation
takes precedence over other determinism work.

### 8. Test ownership: who maintains the critical path tests for each cataloged path?

Confirm that the catalog identifies owners for each path's tests.
The substrate-recommended pattern is the team that owns the
underlying code owns the tests for the critical path through that
code; the security-engineering function reviews the catalog and
the security probe tests on a periodic cadence.

## Escalation to testing-strategy.testing-strategy ADR revision

If review of these questions reveals systemic gaps (most critical
paths have no security probe tests; the catalog itself is missing
or incomplete), the finding escalates to a testing-strategy.testing-strategy ADR revision
or initial authoring rather than tactical remediation.
