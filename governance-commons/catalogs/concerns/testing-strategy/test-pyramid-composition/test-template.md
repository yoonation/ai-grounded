---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.testing-strategy.test-pyramid-composition-test-pyramid-composition"
title: "testing-strategy.test-pyramid-composition test template: test pyramid composition"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# testing-strategy.test-pyramid-composition test template: test pyramid composition

## How to use this binding

This binding describes a CI gate that counts tests per tier and
verifies the ratios stay within tolerance of the testing-strategy.testing-strategy ADR-
declared target. The gate runs on every pull request and fails
when drift exceeds tolerance.

The template is framework-agnostic and is implemented at the
project level. The substrate provides the test-counting and
ratio-verification scenarios; consumers implement the per-tier
counting mechanism appropriate to their test organization
(directories, markers, projects, categories).

## Scenario 1: per-tier test counts are mechanically observable

**Preconditions**
- The project's test suite has the substrate-recommended
  organization (separate directories, markers, or equivalent)
- The testing-strategy.testing-strategy ADR declares the target per-tier ratios

**Verification**
- The CI gate runs a counting script that emits per-tier counts.
  For directory-based organization: count files matching the
  tier's path pattern. For marker-based organization (pytest):
  use `pytest --collect-only -q -m unit` and parse the count.
  For Jest projects: parse the project configuration.

**Substrate-recommended assertion shape**
- Counts are non-negative integers per tier.
- The set of tiers in the report matches the set declared in the
  ADR (no surprise tier emerging from refactoring).

## Scenario 2: per-tier ratios are within substrate-acceptable tolerance

**Preconditions**
- Scenario 1 has produced per-tier counts
- The testing-strategy.testing-strategy ADR declares target ratios (e.g., 70/20/10
  unit/integration/e2e)
- The substrate-recommended tolerance is 20% absolute deviation

**Verification**
- The CI gate computes the actual ratio (count_tier /
  total_count) for each tier
- The gate compares each ratio against the target ratio in the
  ADR
- The gate fails when any tier exceeds the absolute tolerance

**Substrate-recommended assertion shape**

```
# Pseudocode for the per-tier ratio check
for tier in tiers:
    target = adr_targets[tier]      # e.g., 0.70 for unit
    actual = counts[tier] / total   # e.g., 0.85
    deviation = abs(actual - target)
    if deviation > 0.20:
        fail(
            "Tier "tier" ratio "actual" deviates from target "
            target" by "deviation" (tolerance: 0.20). "
            "Either rebalance the suite or revise the ADR."
        )
```

**Tolerance rationale**
The 20% tolerance accommodates natural variation as the suite
grows; tighter tolerances (10%) produce CI noise without
proportional benefit; looser tolerances (40%) defeat the gate's
purpose. The testing-strategy.testing-strategy ADR may set a project-specific tolerance
with documented rationale.

## Scenario 3: tier-appropriate test characteristics

**Preconditions**
- Tests are classified into tiers per the project's organization

**Verification**
- Unit-tier tests do not create network sockets (verified by
  test runner with network-block fixture or by pytest-socket /
  jest-environment-node-no-network configuration)
- Unit-tier tests do not write outside tmpdir (verified by
  filesystem isolation fixture)
- Integration-tier tests may use testcontainers or per-test
  ephemeral resources but do not depend on shared infrastructure

**Substrate-recommended assertion shape**
- A network-blocked fixture at the unit-tier root that raises on
  any socket creation, with substrate-acceptable allow-list for
  loopback when project-justified
- A tmpdir fixture at the unit-tier root that asserts test
  outputs are within the allocated tmpdir

## Scenario 4: tier execution time within substrate-recommended budget

**Preconditions**
- The CI gate has access to per-tier execution time (from the
  test framework's report)

**Verification**
- Unit-tier suite completes under 60 seconds (substrate-
  recommended; adjust to ADR)
- Integration-tier suite completes under 5 minutes (substrate-
  recommended; adjust to ADR)
- End-to-end-tier suite completes under 15 minutes (substrate-
  recommended; adjust to ADR)

**Substrate-recommended assertion shape**

```
# Pseudocode for the tier execution time check
for tier, budget in adr_budgets.items():
    actual = report.duration_for_tier(tier)
    if actual > budget * 1.5:        # 50% headroom before fail
        fail(
            "Tier "tier" exceeded its budget: actual "actual"
             vs. budget "budget". Either optimize, reclassify
             slow tests, or revise the ADR budget."
        )
    elif actual > budget:
        warn(
            "Tier "tier" approaching budget: actual "actual"
             vs. budget "budget"."
        )
```

## Scenario 5: drift detection across versions

**Preconditions**
- The CI gate persists per-tier counts and ratios per commit
  to a tracked history (substrate-recommended: a CI artifact or
  a metric backend)

**Verification**
- A weekly or monthly report compares the current ratios against
  the ratios from N weeks ago
- Significant trend movement (e.g., the e2e tier growing 50%
  faster than the unit tier) surfaces as a finding for ADR
  review

**Substrate-recommended assertion shape**
- A trend report visible to the team; not a hard CI gate but a
  team-channel notification when trends cross a threshold

## Coverage notes

This test template enforces the structural composition. The
substrate-acceptable form is a CI gate (hard fail on tolerance
breach) supplemented by a trend report (soft signal on drift).

Projects without per-tier observability cannot enforce this rule;
the prerequisite work is to add the organization, then implement
the gate.
