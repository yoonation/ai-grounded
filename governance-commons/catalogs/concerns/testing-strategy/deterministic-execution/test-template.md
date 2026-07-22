---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.testing-strategy.deterministic-execution-deterministic-execution"
title: "testing-strategy.deterministic-execution test template: deterministic execution"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# testing-strategy.deterministic-execution test template: deterministic execution

## How to use this binding

This binding describes verification scenarios that check the test
suite for determinism along five axes: order independence,
parallel safety, repeated-run consistency, time control, and
fixture isolation. The scenarios run as scheduled CI jobs (not
on every PR; they are slower than the standard suite) and
surface flakiness vectors before they accumulate.

The template is framework-agnostic. Consumers implement each
scenario using their test framework's introspection and execution
controls.

## Scenario 1: repeated-run consistency

**Purpose:** confirm that the same test on the same code produces
the same result across runs.

**Preconditions**
- A clean checkout of the application at a specific commit
- The standard test suite that runs in PR CI

**Verification**
- Execute the test suite N times consecutively (substrate-
  recommended N: 10) without rebuilding the artifact
- Record the per-test pass/fail outcome for each iteration
- Aggregate: any test that produces non-identical outcomes
  across the N iterations is flagged

**Substrate-recommended assertion shape**

```
# Pseudocode for the repeated-run check
results = []
for iteration in range(10):
    results.append(run_suite_and_collect_outcomes())

flaky = set()
for test_id in all_test_ids:
    outcomes = {results[i][test_id] for i in range(10)}
    if len(outcomes) > 1:
        flaky.add(test_id)

if flaky:
    fail("Tests with non-deterministic outcomes: " + ", ".join(flaky))
```

**Substrate-recommended cadence:** nightly on main; on demand
before release.

## Scenario 2: order randomization stress

**Purpose:** confirm that the test suite passes under any
execution order.

**Preconditions**
- The test framework supports test order randomization (pytest-
  randomly, Jest test sequencer, Go test -shuffle, RSpec
  --order random)

**Verification**
- Execute the test suite N times (substrate-recommended N: 5)
  with random seeds that produce distinct orderings
- Record the per-test outcome per iteration
- Aggregate: any test that fails under at least one ordering but
  passes under at least one other ordering is order-dependent
  and is flagged

**Substrate-recommended assertion shape**
- A failing test should fail under every ordering (deterministic
  failure)
- A passing test should pass under every ordering (deterministic
  success)
- Tests that flip under different orderings indicate ordering
  dependency, surfaced as findings with the failing seed
  attached

**Recovery**
- Record the failing seed
- Reproduce locally with the same seed
- Identify the test that produced the dependency (often the
  preceding test in the failing ordering)
- Remediate the shared mutable state

## Scenario 3: parallel execution stress

**Purpose:** confirm that the test suite passes under parallel
execution at the substrate-recommended parallelism level.

**Preconditions**
- The test framework supports parallel execution (pytest-xdist,
  Jest workers, Go test -parallel, JUnit 5 parallel execution)
- The project's CI runner has multiple cores

**Verification**
- Execute the test suite with parallelism = 1 (baseline), then
  with parallelism = 4, then with parallelism = 8
- Record per-test outcome at each parallelism level
- Aggregate: tests that pass at parallelism = 1 but fail at
  higher parallelism levels indicate shared-state interference

**Substrate-recommended assertion shape**
- All tests pass at all parallelism levels for substrate-
  acceptable determinism
- Differences across levels surface as findings with the failing
  parallelism level attached

**Recovery**
- Identify the failing test(s) under parallelism
- Inspect for shared mutable state: global variables, shared
  database state, shared filesystem paths, hard-coded ports
- Isolate per-test: tmpdir fixture, per-test schema or
  transaction, dynamic port allocation

## Scenario 4: mock-time discipline check

**Purpose:** confirm that tests with time-dependent behavior use
mock time rather than wall-clock.

**Preconditions**
- The application has time-dependent behavior (TTL eviction,
  scheduled jobs, rate limiting, token expiration)
- The test framework supports mock time (freezegun, sinon fake
  timers, Jest jest.useFakeTimers, Awaitility fake clock)

**Verification**
- A linter rule (or grep-based check) identifies tests that
  import time-related functions (datetime.now, Date.now,
  System.currentTimeMillis, time.Now) without a corresponding
  mock-time fixture import
- Tests in the audit list are reviewed and either justified or
  remediated

**Substrate-recommended assertion shape**

```
# Pseudocode for the mock-time audit
suspicious = []
for test_file in test_files:
    uses_realtime = uses_realtime_imports(test_file)
    uses_mock_time = uses_mock_time_imports(test_file)
    has_time_assertions = has_time_assertions(test_file)
    if uses_realtime and has_time_assertions and not uses_mock_time:
        suspicious.append(test_file)

if suspicious:
    warn("Tests with potential wall-clock dependence: " + ...)
```

**Substrate-recommended cadence:** quarterly; on every release
that introduces time-dependent behavior.

## Scenario 5: fixture isolation check

**Purpose:** confirm that tests do not leak state across each
other through shared fixtures.

**Preconditions**
- The test framework supports per-test or per-class fixtures
  with explicit scope (pytest fixtures with function/class/
  module/session scope; Jest beforeEach/beforeAll)

**Verification**
- A test that mutates a fixture must declare appropriate scope
  (function scope for mutating tests; session scope only for
  read-only fixtures)
- An audit identifies fixtures with broader-than-function scope
  that are mutated in tests; these are findings

**Substrate-recommended assertion shape**
- Mutable fixtures are function-scoped by default
- Broader-scope fixtures are read-only in tests; mutation
  attempts produce test errors

**Substrate-recommended cadence:** at PR time for tests that
introduce new fixtures; quarterly for full-suite audit.

## Aggregated determinism report

The substrate-recommended pattern is to aggregate the outputs of
scenarios 1, 2, 3, 4, 5 into a per-week determinism report visible
to the team. Trends in per-test flakiness, order-dependence count,
parallelism issues, time-dependence audit count, and fixture
isolation findings provide a leading indicator of suite-quality
drift.

## Coverage notes

These scenarios complement the testing-strategy.no-flaky-sleep (no-flaky-sleep)
mechanical check. L1 catches the most common single antipattern;
L2 review and L2 test template cover the structural surface where
determinism can fail beyond the literal sleep call.

Projects that do not yet have the prerequisite tooling (order
randomization, parallel execution support, mock-time libraries)
implement the tooling first; the scenarios are predicated on the
tooling being available.
