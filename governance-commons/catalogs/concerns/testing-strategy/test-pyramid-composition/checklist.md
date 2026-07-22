---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.testing-strategy.test-pyramid-composition-test-pyramid-composition"
title: "testing-strategy.test-pyramid-composition review checklist: test pyramid composition"
substrate-rule: "testing-strategy.test-pyramid-composition"
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
  - "Code changes that add new test directories or move tests between tiers"
  - "Code changes that modify CI test execution pipeline structure"
  - "Periodic test-suite composition audits (substrate-recommended: quarterly)"
  - "Review at testing-strategy.testing-strategy ADR adoption or revision"
  - "Detection of significant per-tier ratio drift via the companion test template"
---

# testing-strategy.test-pyramid-composition review checklist: test pyramid composition

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with testing-strategy.testing-strategy (testing strategy ADR). L3
documents the decision; L2 verifies the application's actual test
suite organization matches the documented decision.

## Review questions

### 1. ADR alignment: does the application's testing-strategy.testing-strategy ADR document the chosen pyramid shape?

Confirm that the testing-strategy.testing-strategy ADR explicitly declares the chosen
test shape (classic pyramid, trophy, diamond, small-medium-large,
or documented custom). The shape is not implicit; it is a stated
decision with rationale referencing the application's architecture
(see testing-strategy.testing-strategy substrate framework MADR decision driver D1
application architecture context).

If the ADR is missing or does not declare a shape, the pull request
that introduces this finding should add the missing ADR section
or open a tracking issue.

### 2. Per-tier counts: are the actual tier counts visible to the reviewer?

Confirm that the project's test suite organization makes per-tier
counts mechanically observable. Substrate-acceptable signals
include: separate directory trees per tier (tests/unit/,
tests/integration/, tests/e2e/), pytest markers (@pytest.mark.unit,
@pytest.mark.integration, @pytest.mark.e2e), Jest projects
configuration, JUnit categories, or a CI report that emits per-tier
counts.

If the organization does not surface tier counts, the suite cannot
be governed against the ADR-declared shape. The remediation is
to add the missing organization.

### 3. Ratio adherence: do the actual ratios match the ADR-declared target within tolerance?

Confirm that the actual per-tier counts produce ratios within
substrate-acceptable tolerance of the ADR-declared target. The
substrate-recommended tolerance is 20% absolute deviation (e.g.,
target 70% unit allows actual 50%-90%; outside that range is
drift requiring remediation).

The companion test template (testing-strategy.test-pyramid-composition-test-pyramid-composition.
md) automates this check; the reviewer confirms the CI gate exists
and is current.

### 4. Tier-appropriate coverage: do unit tests test unit-level behavior, integration tests test integration-level behavior?

Confirm that tests classified in each tier actually exercise that
tier's behavior. Substrate-acceptable signals: unit tests do not
spin up Docker containers, do not perform network I/O, do not write
to disk outside tmpdir, do not depend on external services.
Integration tests exercise real boundaries (database, queue, HTTP)
within the substrate-recommended hermetic context. End-to-end
tests exercise the full deployment shape.

Misclassified tests (a "unit test" that hits the real database)
should be reclassified or refactored.

### 5. Tier execution time: does each tier run within its substrate-recommended budget?

Confirm execution time per tier. Substrate-recommended budgets
(adapt to the application's testing-strategy.testing-strategy ADR):
- Unit tier: full suite under 60 seconds on a developer laptop.
- Integration tier: full suite under 5 minutes on CI.
- End-to-end tier: full suite under 15 minutes on CI.

Tiers significantly exceeding their budget signal either
misclassification (slow tests in fast tiers) or scope creep (the
tier has grown beyond its substrate-acceptable shape).

### 6. Cross-tier overlap: do the tiers test distinct behavior, or do they redundantly exercise the same code paths?

Confirm that the suite's tiers complement rather than duplicate.
A test pyramid that exercises the same business logic at unit,
integration, and end-to-end tier wastes execution time without
adding signal. Substrate-acceptable overlap: integration tests
exercise component composition that unit tests cannot exercise
in isolation; end-to-end tests exercise user-facing flows that
integration tests cannot exercise without a deployed environment.

### 7. CI gate composition: which tiers fail the build, which produce warnings, which run nightly?

Confirm the CI gate's tier handling. Substrate-recommended default:
unit and integration tiers fail PR merge; end-to-end tier runs
post-merge on main and surfaces failures to the team channel
(blocking deploy if applicable). Alternative compositions are
substrate-acceptable when documented in testing-strategy.testing-strategy.

### 8. Drift detection: is there a ratchet that prevents the pyramid from inverting silently?

Confirm that the project has a mechanism to catch silent drift
(e.g., gradual addition of end-to-end tests without corresponding
unit-test coverage). Substrate-acceptable mechanisms: CI gate
with ratio check; periodic test-suite audit referenced in
testing-strategy.testing-strategy; PR template question for new test additions.

Without a ratchet, the pyramid composition drifts over months as
contributors add tests at convenient tiers rather than appropriate
ones.

## Escalation to testing-strategy.testing-strategy ADR revision

If review of these questions reveals that the substrate-recommended
default no longer fits the application (e.g., the application has
matured from backend service to frontend-heavy product and the
classic pyramid no longer suits), the finding escalates to a
testing-strategy.testing-strategy ADR revision rather than tactical remediation.
Substrate-recommended trigger: three or more questions in this
checklist consistently surface drift findings across a sprint.
