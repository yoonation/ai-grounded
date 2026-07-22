---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: testing-strategy.testing-strategy
title: "Testing Strategy"
lifecycle-status: stable
commons-version: "0.5.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-25"
entered-status-at: "2026-05-26"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention. Promoted to stable at M2 close consolidation (Path A precedent) on 2026-05-26 alongside the four other M2 draft MADRs and the five M2 draft catalogs they pair with."
ai-assistance: "AI drafted from substrate-author intent. Pairs with testing-strategy.testing-strategy substrate rule; mirrors the error-handling-strategy.madr.md, input-validation-strategy.madr.md, and observability-slo-policy.madr.md precedents for L3-as-pre-build-gate. Draft lifecycle per M2 Session 4; promotion to stable deferred to M2 close per Path A precedent."
authoritative-sources:
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x22-V14-Config.md"
  - "https://www.iso.org/standard/79428.html"
  - "https://www.istqb.org/certifications/certified-tester-foundation-level"
  - "https://martinfowler.com/articles/practical-test-pyramid.html"
  - "https://martinfowler.com/bliki/TestPyramid.html"
  - "https://martinfowler.com/articles/nonDeterminism.html"
  - "https://google.github.io/eng-practices/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.error-handling-strategy
  - decision-frameworks.observability-slo-policy
  - decision-frameworks.logging-architecture
  - decision-frameworks.input-validation-strategy
  - decision-frameworks.auth-strategy
  - decision-frameworks.authorization-model-selection
---

# Testing Strategy

This decision framework provides the substrate's analysis of
testing strategy options. Consumers reference this framework when
authoring their own ADR documenting their application's testing
strategy choice (substrate-recommended location for the consumer's
ADR: `/docs/decisions/ADR-XXX-testing-strategy.md`).

The framework is referenced by substrate rule testing-strategy.testing-strategy, which
requires applications to have an explicit, documented testing
strategy decision before substantive test-suite implementation
begins. Consumers satisfy testing-strategy.testing-strategy by authoring an ADR that
adapts the analysis in this framework to their application
context.

This framework is the testing counterpart to the substrate's
existing decision frameworks for error-handling, observability,
logging, input-validation, authentication, and authorization. The
testing strategy is the cross-cutting concern that exercises the
others; the test suite verifies that the application implements
the substrate's L1 and L2 rules from adjacent concerns correctly.
The relationship is asymmetric: the testing strategy depends on
the adjacent concerns being decided first (the test suite tests
something, and that something is partly determined by the
adjacent ADRs); the adjacent concerns do not depend on the
testing strategy. Authoring order is substrate-recommended:
adjacent ADRs first, testing strategy after.

The framework is non-binding: it surveys options and consequences
without prescribing the consumer's choice beyond the substrate-
preferred default. Where the substrate has a preference, it is
stated; where the choice depends on application context, the
framework provides decision drivers rather than recommendations.

## Context

The testing strategy decision determines how the application's
test suite is structured, how confident the team can be in
unfailed builds, and how expensive the suite is to maintain.
The decision is structural: changing the strategy after
significant test-suite work has been done requires either
rewriting a meaningful fraction of the tests or accepting drift
between the documented strategy and the running suite.

The substrate identifies seven application-context factors that
inform the testing strategy choice. Each is discussed in the
Decision Drivers section below. The substrate-acceptable
strategies all address these factors; they differ in how they
balance the trade-offs the factors introduce.

The substrate-preferred default for new applications is the
classic test pyramid with per-test isolation, documented per-
tier ratios, and quarantine-based flake management. The default
suits backend services, command-line tools, libraries, and
moderately interactive applications. Alternative shapes (testing
trophy for frontend-heavy applications, diamond / honeycomb for
integration-heavy systems, small / medium / large for
heterogeneous systems) are substrate-acceptable when chosen
with documented rationale referencing the decision drivers.

Two shapes are substrate-discouraged: the ice cream cone (end-to-
end heavy, unit-light) and the ad-hoc strategy (no documented
structure). The ice cream cone has well-understood cost and
flakiness consequences that compound over time; ad-hoc structures
produce divergent module-level discipline that is hard to
reconcile.

The testing strategy interacts with the substrate's other
concerns in specific ways:

- **Error-handling (error-handling.error-response-contract through error-handling.observable-response-discrepancy):** the
  substrate ships paired test templates for each L2 error-
  handling rule. The testing strategy commits to running those
  test templates and integrating them into the per-tier test
  organization.

- **Observability (observability.slo-policy):** the SLO policy declares which
  failure modes the application observes. The testing strategy
  commits to exercising the instrumentation that delivers that
  observation; tests verify that emissions occur on expected
  failures.

- **Logging (the logging mechanical L1 rules):** logging-related
  tests verify the substrate's logging rules (correlation IDs
  present, sensitive data not logged, severity levels accurate)
  through dedicated test fixtures.

- **Input validation (the input-validation mechanical (L1) rules):** the
  testing strategy's critical-path coverage section commits to
  security-probe tests that exercise each L1 input rule.

- **Authentication and authorization (AUTH-L1-* and AUTHZ-L1-*):**
  the testing strategy's critical-path coverage section commits
  to security-probe tests for authentication and authorization
  flows.

## Decision Drivers

The substrate identifies the following drivers that should inform
the testing strategy. Consumers may add application-specific
drivers but should address each substrate driver in their ADR.

- **D1. Application architecture.** Is the application a backend
  service, a CLI, a library, a frontend application, a mobile
  app, a serverless function set, or a hybrid? Different
  architectures suit different shapes. Backends and CLIs suit the
  classic pyramid; frontends with significant UI logic suit the
  trophy; integration-heavy systems suit the diamond.

- **D2. Integration topology.** How many cross-module and cross-
  service interfaces does the application have? More interfaces
  shift the pyramid toward integration tests; fewer interfaces
  allow more unit-heavy ratios. The integration count is a
  proxy for how much of the application's value lives at
  boundaries rather than within modules.

- **D3. Risk profile.** What are the application's highest-risk
  modules (security-sensitive code, payment logic, data-handling
  primitives)? Higher-risk modules require elevated per-module
  coverage floors, deeper critical-path coverage, and possibly
  mutation testing application.

- **D4. CI runtime budget.** How long can the test suite run on
  every pull request without blocking developer feedback?
  Smaller budgets favor unit-heavy ratios and fewer integration
  tests; larger budgets allow broader coverage. The
  substrate-recommended targets per tier (unit < 60s,
  integration < 5min, e2e < 15min) are starting points the
  ADR adapts.

- **D5. Team capacity.** How much test-authoring discipline can
  the team sustain? Lower capacity favors lighter coverage
  floors and simpler fixture mechanisms; higher capacity
  supports elevated floors and more sophisticated test
  infrastructure. The substrate's L2 rules apply regardless of
  capacity; the ADR documents what the team commits to deliver
  given current capacity.

- **D6. Regulatory context.** Do regulatory frameworks (PCI DSS,
  HIPAA, SOC 2, GDPR) require specific testing characteristics
  (security test coverage, data-handling test isolation, audit
  trail testing)? Compliance requirements layer onto the
  substrate strategy and may impose tier-specific requirements
  the substrate-preferred default does not.

- **D7. Observability surface coverage.** What failure modes does
  the observability ADR (observability.slo-policy) require visibility into?
  The test suite verifies each surfaces correctly; the testing
  strategy commits to that verification.

In addition to the seven application-context drivers above, the
substrate's testing-strategy decision involves nine concrete
choices the ADR makes:

- **C1. Pyramid shape choice.** Classic pyramid, trophy, diamond,
  small/medium/large, or documented custom.

- **C2. Per-tier coverage targets.** Numeric ratios across tiers
  (e.g., 70/20/10 unit/integration/e2e) and per-module floors
  if applicable.

- **C3. CI gate composition.** Which tiers fail merge, which
  produce warnings, which run nightly.

- **C4. Flakiness handling policy.** Quarantine mechanism, sunset
  window, team responsibility for fixing flakes vs deleting.

- **C5. Test environment management.** Hermetic isolation
  strategy, fixture lifecycle, test data sensitivity handling.

- **C6. Performance budget.** Suite execution time targets per
  tier; how budget overruns surface.

- **C7. Mutation testing inclusion.** Yes/no/scoped (e.g., only
  on critical-path modules); how mutation scores gate.

- **C8. Property-based testing inclusion.** Yes/no/scoped; which
  modules use property-based tests.

- **C9. Determinism enforcement.** Randomization, parallelism,
  mock-time policy; flake observability and reporting.

## Considered Options

### Option 1: Classic pyramid with per-test isolation, documented floors, and quarantine-based flake management (substrate-preferred default)

**Substrate preference:** Substrate-preferred default for new
applications. Provides the most direct path to satisfying L1 and
L2 rules; aligns with the test templates the substrate ships
across other concerns.

**Description**
- C1. Classic pyramid (broad unit base, narrower integration
  middle, narrow end-to-end top).
- C2. Substrate-recommended targets 70/20/10 (unit/integration/
  e2e); per-module floor of 60% line coverage on critical-path
  modules.
- C3. Unit and integration tiers fail PR merge; e2e tier runs
  post-merge and surfaces failures to the team channel,
  blocking deploy where applicable.
- C4. Tests that flake twice within 30 days are quarantined into
  a non-blocking tier and tracked with an issue; quarantined
  tests not fixed within two sprints are deleted.
- C5. Hermetic isolation via testcontainers or per-test
  ephemeral resources at integration tier; per-test tmpdir and
  per-test database transaction at unit tier; no shared
  external state.
- C6. Per-tier execution time budgets: unit < 60s, integration
  < 5min, e2e < 15min on CI.
- C7. Mutation testing optional; recommended for critical-path
  modules with elevated coverage floors.
- C8. Property-based testing optional; recommended for data-
  handling primitives and parsing code.
- C9. Order randomization and parallel execution enabled by
  default; mock-time required for time-dependent behavior;
  flake metrics published weekly.

**Pros**
- Aligns with the substrate's test templates from adjacent
  concerns; minimal adaptation work.
- Well-understood cost-to-confidence ratio; mature tooling
  across languages.
- Unit-heavy base provides fast feedback for the common case;
  integration coverage catches boundary defects.

**Cons**
- Requires test-authoring discipline to maintain the pyramid
  shape; without ratchets, the suite drifts toward inverted
  shapes.
- The 70/20/10 default may not fit applications heavy on
  integration or frontend logic; alternative shapes are
  substrate-acceptable for those cases.
- The unit-heavy emphasis can mask integration defects when the
  unit tests use mocks that diverge from real boundary behavior;
  contract testing or integration coverage closes the gap.

### Option 2: Testing trophy (frontend-heavy applications)

**Description**
- C1. Trophy shape (static analysis at the base, then unit tests,
  then integration / component tests as the largest layer,
  then a narrow end-to-end top).
- C2. Substrate-recommended targets 10/30/50/10 (static-analysis
  coverage / unit / integration-component / e2e); per-component
  coverage rather than per-module.
- C3-C9. Same as Option 1 except per-tier emphasis shifts.

**Pros**
- Better fit for frontend applications where most logic lives at
  the component-composition layer rather than in isolated unit-
  testable functions.
- Integration / component tests exercise the rendering layer
  that unit tests cannot cover meaningfully.

**Cons**
- Slower per-tier feedback compared to unit-heavy options;
  developers wait longer for signal.
- Higher fixture complexity; component tests need realistic DOM,
  state, and routing context.
- Less mature ratchet tooling for the trophy shape compared to
  the classic pyramid; CI gate construction is more bespoke.

**When to choose:** frontend-heavy applications (Next.js, Vue,
React Native) where component composition is the dominant
behavior surface; applications where unit-isolation produces
poor signal because most logic is integration of UI primitives.

### Option 3: Diamond / honeycomb (integration-heavy systems)

**Description**
- C1. Diamond or honeycomb shape (narrow unit base, large
  integration middle, narrow e2e top).
- C2. Substrate-recommended targets 20/60/20 (unit / integration
  / e2e).
- C3-C9. Same as Option 1 with adjusted ratios.

**Pros**
- Suits systems where the value lives at service boundaries
  rather than within services (orchestration layers, BFFs,
  integration platforms).
- Integration tests catch the real defects in this category of
  system.

**Cons**
- Higher per-tier execution cost; CI runtime budget pressure.
- Higher fixture complexity at integration tier.
- Unit-light base provides limited fast feedback; developers
  may wait minutes for signal on a localized change.

**When to choose:** integration platforms, orchestrators,
service composition layers, applications where boundary
correctness dominates internal-logic correctness.

### Option 4: Ice cream cone (e2e-heavy, unit-light) — substrate-discouraged

**Description**
- C1. Inverted pyramid (narrow unit base, slightly wider
  integration, broad end-to-end).
- C2. No formal targets; tests gravitate to e2e because they
  feel "more realistic."

**Pros**
- Tests look like the way the system actually runs in production.
- High initial confidence from broad e2e coverage.

**Cons**
- Slow PR feedback; e2e tests run for minutes per change.
- High flakiness rate; e2e tests have many failure modes
  (network, environment, timing) that unit tests do not have.
- Poor failure diagnostics; an e2e failure could indicate any
  layer being broken.
- Substrate-discouraged: well-understood as a cost-to-
  confidence anti-pattern in the testing literature.

**When to choose:** never as a deliberate design choice for a
new application. Existing applications stuck in this shape work
toward Option 1 incrementally.

### Option 5: Unit-only (no integration or e2e coverage) — substrate-discouraged

**Description**
- C1. Only unit tests; no integration tier; no e2e tier.

**Pros**
- Fastest possible PR feedback.
- Minimal fixture complexity.

**Cons**
- Boundary defects (integration mismatches, contract drift,
  serialization issues) ship to production.
- The unit-mock-based confidence is structurally misleading;
  unit tests pass while the integrated system fails.
- Substrate-discouraged: no application that interacts with
  external systems is well-served by unit-only.

**When to choose:** pure libraries with no external dependencies
and no integration surface; even then, contract testing against
consumers is substrate-recommended.

### Option 6: Ad-hoc (no documented strategy) — substrate-rejected

**Description**
- C1-C9. No explicit decisions; tests accumulate as
  contributors decide what to write where.

**Pros**
- No upfront design cost.

**Cons**
- Module-level divergence: one team writes heavy unit tests,
  another writes only integration tests, another writes none.
- No ratchet against drift; the suite shape evolves randomly.
- Substrate-rejected as the explicit anti-pattern testing-strategy.testing-strategy
  prevents.

**When to choose:** never; this is the failure mode testing-strategy.testing-strategy
exists to prevent.

## Substrate-recommended defaults for other drivers

This section captures the substrate's recommended approach to
the C4 through C9 decisions for consumers adopting Option 1
(classic pyramid). Consumers adopting other options may inherit
these defaults or document alternative choices.

### C4. Flakiness handling policy

The substrate-recommended flake policy: a test that fails non-
deterministically twice within 30 days is quarantined (moved to
a quarantine tier that does not gate the build) and tracked with
an issue. The issue is owned by the team that owns the underlying
code (substrate-recommended; alternative ownership models are
acceptable when documented). Quarantined tests not fixed within
two sprints are deleted.

"Rerun until green" is forbidden as policy. Automatic retry-on-
failure in CI configuration is forbidden for test assertions;
conditional retries on infrastructure errors (DNS lookup
failures, transient container startup) are substrate-acceptable
when documented.

The flake rate is published as a weekly metric visible to the
team. Substrate-recommended threshold for raising the issue at
team review: more than 1% of tests appear in the flake report
in a given week.

### C5. Test environment management

The substrate-recommended environment model:

- **Unit tier:** in-process, no external dependencies, tmpdir
  fixture for filesystem isolation, mocked external services.
- **Integration tier:** per-test or per-session ephemeral
  resources (testcontainers, dockertest, embedded servers); no
  shared development environment.
- **End-to-end tier:** ephemeral deployment per CI run
  (preview environment, Kubernetes namespace, Docker Compose)
  with seed data initialized per test or per suite.

Test data sensitivity (PHI, payment card data, GDPR-protected
data) drives synthetic-fixture strategies: production data is
never copied into test environments; synthetic data is generated
to match production data shape without containing real PII.

### C6. Performance budget

The substrate-recommended per-tier budgets:

- Unit tier: full suite under 60 seconds on a developer laptop;
  full suite under 30 seconds in CI with parallelism.
- Integration tier: full suite under 5 minutes in CI.
- End-to-end tier: full suite under 15 minutes in CI.

Budgets are guidance for the substrate-preferred default;
applications with substantively different scale needs document
alternatives in the ADR with rationale.

Budgets are enforced by the testing-strategy.test-pyramid-composition test template's tier
execution time check, which warns at the budget and fails at
1.5x the budget.

### C7. Mutation testing inclusion

The substrate-recommended approach:

- Mutation testing is optional for the suite as a whole.
- Mutation testing is recommended for critical-path modules
  with elevated coverage floors (substrate-recommended floor:
  80% line coverage on critical-path modules).
- Mutation score targets are documented in the ADR;
  substrate-recommended starting point is 70% mutation kill
  rate for critical-path modules, with the score gating PR
  merge.

Tools: mutmut (Python), Stryker (JavaScript), PIT (Java), go-
mutesting (Go), mutant (Ruby).

### C8. Property-based testing inclusion

The substrate-recommended approach:

- Property-based testing is optional for the suite as a whole.
- Property-based testing is recommended for data-handling
  primitives (parsers, serializers, validators, encoders),
  where the input space is too large for example-based testing
  to cover meaningfully.
- The ADR documents which modules use property-based testing
  and which properties are tested.

Tools: Hypothesis (Python), fast-check (JavaScript), jqwik
(Java), gopter (Go), PropEr (Erlang).

### C9. Determinism enforcement

The substrate-recommended enforcement:

- Order randomization enabled in CI; the randomization seed is
  recorded with each run for reproducibility.
- Parallel execution enabled in CI at parallelism >= 4 by
  default.
- Mock time required for tests with time-dependent behavior;
  wall-clock time in tests is a testing-strategy.deterministic-execution finding.
- Flake metrics published weekly; flake rate above 1% is a team-
  review item.
- The testing-strategy.deterministic-execution test template's scenarios run as scheduled
  CI jobs (nightly for repeated-run; weekly for order and
  parallelism stress; quarterly for mock-time and fixture
  isolation audits).

## Documentation Required

The consumer's ADR documents the following items. Each is
expected to be present and substantive for the ADR to satisfy
the testing-strategy.testing-strategy review checklist.

- **Status, deciders, date.** Status: Accepted (or Superseded);
  Deciders: the people or teams who approved; Date: the
  acceptance date.

- **Context.** The application's facts relevant to D1 through D7
  drivers above. Substrate-recommended structure: a brief table
  mapping each driver to the application's specific fact.

- **Decision.** The chosen pyramid shape (C1) and the chosen
  per-tier targets (C2). The chosen approach to C3 through C9.

- **Decision Drivers.** A discussion of how the application's
  context (D1-D7) led to the chosen option. Substrate-acceptable
  form: a paragraph per driver, or a table with driver/finding/
  implication columns.

- **Considered Options.** At least three options surveyed; the
  substrate-preferred default (Option 1) is always considered
  even if not chosen.

- **Consequences.** The positive and negative consequences of the
  chosen option. At least three of each, phrased as testable
  assertions.

- **Implementation status.** For greenfield applications, the
  status is "to be implemented per this strategy." For existing
  applications, the gap between current and target state, with
  remediation owners and target dates.

- **Cross-concern references.** Explicit references to the
  substrate's adjacent concerns whose tests this strategy
  delivers visibility into: ERR-L2-*, observability.slo-policy, LOG-L1-*,
  INPUT-L1-*, AUTH-L1-*, AUTHZ-L1-*.

- **Review cadence.** When the ADR will be revisited; what
  triggers a revision. Substrate-recommended cadence is annual
  with trigger-based revision.

## More Information

The testing-strategy.test-pyramid-composition, testing-strategy.critical-path-coverage, and testing-strategy.deterministic-execution review checklists
and test templates are the operational instruments of this
strategy. They run at PR time (review checklists) and on
scheduled CI cadence (test templates) to verify the strategy is
being implemented and to detect drift.

The the testing-strategy mechanical (L1) rules mechanical bindings enforce
the floor that the L2 and L3 build on; the L3 strategy assumes
the L1 surface is enforced.

Cross-references to adjacent decision frameworks:
- decision-frameworks.error-handling-strategy: the strategy
  ships paired test templates this framework integrates with.
- decision-frameworks.observability-slo-policy: the SLO instr-
  umentation is exercised by tests this strategy commits to.
- decision-frameworks.logging-architecture: the logging surface
  is exercised by tests this strategy commits to.
- decision-frameworks.input-validation-strategy and
  decision-frameworks.auth-strategy: their L1 rules are
  exercised by critical-path security probe tests this strategy
  commits to.

The substrate's testing-strategy.testing-strategy rule does not prescribe a specific
choice among the options above. The L3 review checklist
verifies that the ADR is present, addresses the substrate's
drivers, considers alternatives, and is operating as a living
document. The choice of option is the consumer's.
