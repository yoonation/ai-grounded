---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.testing-strategy.deterministic-execution-deterministic-execution"
title: "testing-strategy.deterministic-execution review checklist: deterministic execution"
substrate-rule: "testing-strategy.deterministic-execution"
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
  - "Code changes that introduce new test fixtures, especially shared fixtures"
  - "Code changes that modify CI test execution configuration (parallelism, ordering)"
  - "Code changes that introduce time-dependent behavior in tests"
  - "Detection of test flake events in CI history (substrate-recommended threshold: 2+ flakes in 30 days)"
  - "Periodic determinism audit (substrate-recommended: monthly)"
---

# testing-strategy.deterministic-execution review checklist: deterministic execution

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with testing-strategy.no-flaky-sleep (no flaky sleep) mechanical
detection. L1 catches the most common flakiness vector (literal
sleep); this L2 review confirms the broader determinism surface
(order independence, parallel safety, time control, fixture
isolation, flake quarantine policy).

## Review questions

### 1. Order randomization: can the test suite run in any order and produce the same results?

Confirm that the project's CI configuration enables test order
randomization. Substrate-acceptable mechanisms: pytest with
pytest-randomly plugin, Jest with --randomize (or testSequencer
configuration), Go test with -shuffle=on, RSpec with --order
random, JUnit 5 with @TestMethodOrder(MethodOrderer.Random.class).

If order randomization is disabled or not configured, the project
cannot detect order-dependent tests until they fail in unrelated
PRs. Remediation: enable randomization; surface order-dependent
failures as tickets; fix or quarantine the dependencies.

### 2. Parallel execution safety: can the test suite run in parallel without interference?

Confirm that the project's tests can execute in parallel without
inter-test interference. Substrate-acceptable mechanisms: pytest
with pytest-xdist enabled in CI, Jest with workers > 1 by default,
Go test with -parallel N, JUnit 5 with parallel execution mode.

Tests that fail under parallelism but pass serially indicate
shared mutable state (global variables, shared database state,
shared filesystem paths). Remediation: identify the shared state;
isolate per-test (tmpdir, per-test schema, per-test transaction);
re-enable parallel execution.

### 3. Hermetic isolation: do tests avoid real-world external dependencies?

Confirm that tests at the unit and integration tiers do not depend
on external services not under the test's control. Substrate-
acceptable boundaries: tests may reach out to per-test containers
(testcontainers, dockertest) that are spun up and torn down per
test or per session; tests may not reach out to shared development
environments, third-party APIs, or production-adjacent infrastructure.

The substrate's L2 review confirms the hermetic discipline; tests
that depend on shared external state surface as findings.

### 4. Mock time discipline: do tests that depend on time control time explicitly?

Confirm that tests with time-dependent behavior use mock time
(frozen, advanced deterministically) rather than wall-clock. The
substrate-recommended tools: freezegun, time-machine (Python);
Jest fake timers, sinon useFakeTimers (JavaScript); Awaitility's
fake clock support (Java); golang/mock or a clock interface
abstraction (Go); timecop, Timecop.travel (Ruby).

Tests that use wall-clock time directly fail intermittently when
the clock crosses a boundary (midnight, daylight savings, end of
month). Remediation: introduce a clock abstraction; mock it in
tests.

### 5. Flake quarantine policy: does the project have a documented flake policy?

Confirm that the project has a documented flake-handling policy.
Substrate-recommended policy: a test that fails non-deterministically
twice within 30 days is quarantined (moved to a quarantine tier
that does not gate the build) and tracked with an issue; if not
fixed within a sunset window (substrate-recommended: two sprints),
the test is deleted.

"Rerun until green" without investigation is forbidden as policy
even if technically supported by CI. The flake report should be
visible to the team and tracked as a quality metric.

### 6. Forbidden "rerun until green" practice: are flaky tests investigated rather than retried?

Confirm that the project's CI configuration does not include
unconditional retry-on-failure for tests. Conditional retries
(retry only on infrastructure errors, retry only in nightly
exhaustive runs) are substrate-acceptable when documented.
Automatic retries on test assertions mask flakiness and erode
suite trust over time.

### 7. Observable flake rates: is the flake rate visible to the team?

Confirm that the project surfaces per-test flake rates as a
metric. Substrate-recommended mechanism: a CI report or dashboard
showing tests that have failed and then passed within the same
day, tracked over time. Without observability, flakiness
accumulates silently; with observability, the team has a forcing
function to address it.

### 8. Determinism verification across environments: do tests produce the same results on developer laptops and CI?

Confirm that the project has tooling (or convention) to catch
environment-dependent test behavior. Tests that pass on macOS
laptops but fail on Linux CI (or vice versa) indicate hidden
environmental dependencies. Substrate-acceptable mitigations:
containerized test execution that matches CI exactly;
documented "developer setup" that mirrors CI; per-platform CI
matrix that catches divergence early.

## Escalation to testing-strategy.testing-strategy ADR revision

If review of these questions reveals that the project's determinism
infrastructure is structurally absent (no randomization, no mock
time, no flake tracking), the finding escalates to a testing-strategy.testing-strategy
ADR section addressing determinism enforcement rather than
tactical PR-level remediation.
