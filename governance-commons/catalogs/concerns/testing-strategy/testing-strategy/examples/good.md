<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.testing-strategy filled-in consumer ADR

Substrate-original good pattern. Adapt to your stack.

This is a representative consumer ADR adapting the substrate's
framework MADR (`decision-frameworks/testing-strategy.madr.md`)
to a specific application context. The ADR would live at
`/docs/decisions/ADR-019-testing-strategy.md` in the consumer's
repository.

---

# ADR-019: Testing Strategy

**Status:** Accepted

**Date:** 2026-05-20

**Deciders:** Platform Engineering Team, Security Engineering
(advisory)

**Supersedes:** none

## Context

OrderService is a backend REST API serving 200 RPS in production
with peak bursts to 800 RPS. The application has:

- **D1 Architecture:** monolithic backend service in Python
  (FastAPI), no UI rendering layer.
- **D2 Integration topology:** PostgreSQL primary, Redis cache,
  Stripe API (payment), SendGrid (email), SQS (work queue). Five
  external service integrations.
- **D3 Risk profile:** processes payment authorization; PCI DSS
  in-scope; security-sensitive paths are auth, charge, refund,
  and webhook ingestion.
- **D4 CI runtime budget:** PR feedback target is under 5
  minutes; unit + integration tiers must complete within this
  budget.
- **D5 Team capacity:** 6 engineers, all comfortable with test-
  authoring; 2 with strong fixture and mocking discipline.
- **D6 Regulatory context:** PCI DSS requires test coverage of
  cardholder data flows; SOC 2 Type II requires evidence of test
  execution.
- **D7 Observability surface:** observability.slo-policy ADR declares latency
  P99 < 200ms on /charge, error rate < 0.1% on auth flows.
  Tests must verify the instrumentation that surfaces these.

## Decision

We adopt the substrate-preferred default (Option 1: classic
pyramid with per-test isolation, documented floors, quarantine-
based flake management).

### Decisions C1 through C9

- **C1 Pyramid shape:** classic pyramid.
- **C2 Per-tier targets:** 70% unit / 20% integration / 10% e2e.
  Per-module floor: 70% line coverage; critical-path modules
  (auth, charge, refund) elevated to 80%.
- **C3 CI gate composition:** unit + integration fail PR merge;
  e2e runs post-merge on main; PR runtime budget is 5 minutes
  enforced per tier (unit < 60s, integration < 4min).
- **C4 Flakiness policy:** quarantine on second flake within 30
  days; tracking issue required; sunset 8 weeks.
- **C5 Environment management:** testcontainers for PostgreSQL
  and Redis at integration tier; mocked Stripe via stripe-mock
  container; mocked SendGrid via local SMTP capture.
- **C6 Performance budget:** as in C3; current actual: unit 42s,
  integration 3min 12s.
- **C7 Mutation testing:** scoped to critical-path modules (auth,
  charge, refund). 70% mutation kill rate gates PR merge for
  changes to these modules.
- **C8 Property-based testing:** scoped to the amount-arithmetic
  module and the webhook signature verifier. Hypothesis library.
- **C9 Determinism:** pytest-randomly enabled; pytest-xdist
  parallel with 4 workers; freezegun for time-dependent tests;
  flake metrics published weekly to engineering Slack.

## Decision Drivers

| Driver | Finding | Implication |
| ------ | ------- | ----------- |
| D1 Architecture | Backend service, no UI | Classic pyramid suits |
| D2 Integration | 5 external services | Mid-size integration tier; mock externals |
| D3 Risk | PCI DSS scope | Elevated coverage on auth/charge/refund; mutation testing on these |
| D4 CI budget | 5 min PR target | Unit < 60s, integration < 4min budgets |
| D5 Team | 6 engineers, mixed discipline | Substrate default fits |
| D6 Regulatory | PCI + SOC 2 | Evidence-of-execution via JUnit XML in CI artifact retention |
| D7 Observability | P99 < 200ms claims | Tests verify metric emission on /charge path |

## Considered Options

We surveyed:

- **Option 1 (substrate default):** chosen. Best fit given D1
  (backend service), D2 (moderate integration), D4 (tight CI
  budget).
- **Option 2 (trophy):** rejected. We have no UI; the trophy's
  emphasis on component / integration tests does not apply.
- **Option 3 (diamond):** considered. The integration emphasis
  would suit our 5-service surface, but D4 (tight CI budget)
  makes a wider integration tier infeasible. We accept that
  some boundary defects may slip past unit mocks; we mitigate
  via the contract testing project (issue-2034) tracking.
- **Option 4 (ice cream cone):** rejected. The substrate's
  rationale (slow feedback, high flakiness) aligns with our D4
  constraint.
- **Option 5 (unit only):** rejected. D2's integration surface
  is real and must be tested.

## Consequences

**Positive consequences:**

- PR feedback within target (5 minutes), enabling trunk-based
  development.
- Critical-path security probe tests align with substrate L1
  rules from auth, authz, input, err concerns; the substrate's
  test templates for adjacent concerns ship into the suite with
  minimal adaptation.
- Mutation testing on critical paths provides a defense against
  the structural-coverage gap (high line coverage with missed
  edge cases).

**Negative consequences:**

- Mocked Stripe and mocked SendGrid at integration tier mean
  contract drift between our integration tests and the real
  external APIs. Mitigation: contract testing project tracked
  as issue-2034.
- Property-based testing setup is investment our team has not
  done before; learning curve estimated at 1 sprint per module.
- Quarantine policy with 8-week sunset is aggressive; we accept
  that some flaky tests may be deleted before the root cause is
  found, in exchange for keeping the quarantine tier from
  growing indefinitely.

## Implementation status

Current state (as of 2026-05-20):

- Unit tier: 487 tests, 42s execution time. Within target.
- Integration tier: 142 tests, 3min 12s execution time. Within
  target.
- E2E tier: 71 tests. Currently runs nightly only; PR-time e2e
  blocked on test environment provisioning (issue-2042).
- Critical path matrix: 14 of 17 paths fully covered. Gaps
  tracked as issues 2050-2052.
- Mutation testing: configured for auth and charge modules.
  Refund module pending (issue-2055).

## Cross-concern references

- Decision: error-handling.error-handling-strategy ADR (error-handling-strategy) documents
  the error-response contract this strategy's tests exercise.
- Decision: observability.slo-policy ADR (observability-slo-policy) declares
  SLO commitments this strategy's tests verify instrumentation
  for.
- Substrate rules exercised:
  - authentication.password-hashing (password hashing) via tests/critical-paths/
    auth/test_password_security.py
  - authorization.authz-before-resource-access (authorization before access) via
    tests/critical-paths/authz/test_ownership.py
  - input-validation.parameterized-queries (parameterized queries) via per-endpoint SQL
    injection probes in tests/critical-paths/
  - error-handling.no-stack-trace-in-response (no stack trace in response) via
    tests/integration/test_error_responses.py
  - the logging mechanical rules (correlation IDs, no sensitive data) via
    tests/integration/test_log_capture.py

## Review cadence

- Annual review (next review: 2027-05-20).
- Trigger-based revision: significant architecture change (split
  into services; addition of UI tier), sustained drift detected
  by testing-strategy.test-pyramid-composition weekly reports for 3+ consecutive weeks,
  security incident affecting testing.

---

## Why this ADR satisfies testing-strategy.testing-strategy

- Status is Accepted with explicit date and deciders.
- All seven substrate drivers (D1-D7) are addressed with
  application-specific facts.
- All nine substrate decisions (C1-C9) are made with rationale.
- Three or more alternatives are surveyed before the chosen
  option.
- Consequences are enumerated (3 positive, 3 negative) as
  testable assertions.
- Implementation status documents the gap between current and
  target state with tracking issues.
- Cross-concern references explicitly cite substrate rule IDs
  from adjacent concerns.
- Review cadence is annual with documented trigger events.
