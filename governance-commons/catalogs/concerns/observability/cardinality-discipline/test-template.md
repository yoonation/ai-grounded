---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.observability.cardinality-discipline-cardinality-discipline"
title: "observability.cardinality-discipline test template: cardinality discipline"
substrate-rule: "observability.cardinality-discipline"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-21"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# observability.cardinality-discipline test template: cardinality discipline

## How to use this binding

Cardinality discipline tests verify that metric label values
stay within bounded vocabularies. The tests have two complementary
forms: a load-generation test that drives the service with
known input variety and asserts the resulting series count
matches expectations, and an inventory test that queries the
metrics backend for actual cardinality and compares against
documented bounds. Substrate-recommended cadence: CI on every
new metric registration; weekly inventory in production.

## Scenario 1: Metric registration documents bounded vocabulary

**Preconditions**
- Service has at least one labeled metric
- Documentation discipline (observability.cardinality-discipline question 4) is in
  effect

**Action**
- Parse the metric registration site (source code)
- Verify a documentation comment or vocabulary reference
  exists for each label

**Expected**
- Every label key has an associated vocabulary specification
- The vocabulary specification is either a substrate-recognized
  value (tenant_id, region, environment, etc.) or a consumer-
  documented vocabulary with explicit cardinality bound
- Registration sites without documentation fail the test

## Scenario 2: Load-generation produces expected series count

**Preconditions**
- A controlled load generator with known input variety (e.g.,
  drives 3 tenant_ids, 2 environments, 5 endpoint templates,
  3 status codes)
- A test metrics backend or in-process registry that exposes
  the resulting series

**Action**
- Drive the service with the controlled load
- Query the resulting series count for each labeled metric

**Expected**
- The series count is the cartesian product of the documented
  vocabularies (for the example above: 3 × 2 × 5 × 3 = 90
  series per metric)
- No additional series exist that the load did not exercise
- The test fails if series count exceeds the expected product

## Scenario 3: Unbounded vocabulary as label value is rejected

**Preconditions**
- A test fixture registers a metric with a label whose
  documented vocabulary is unbounded (e.g., a label named
  user_id)
- The substrate-recognized unbounded vocabulary list is
  enforced

**Action**
- Run the registration-discipline check (Scenario 1 framework)
  on the fixture

**Expected**
- The check fails on the unbounded label key
- The failure message identifies the label, the source
  location, and the substrate-recognized alternative
  (substrate-recommended: tenant_id rather than user_id)

## Scenario 4: Backend cardinality matches expected bounds

**Preconditions**
- Service has been running in production or a representative
  staging environment for a substrate-recommended observation
  period (at least one week)
- Metrics backend exposes per-metric series count

**Action**
- Query the backend for series count per metric
- Compare against the consumer-documented bounds for each
  label vocabulary

**Expected**
- For each metric, actual series count is at or below the
  bound implied by the documented vocabulary cartesian
  product
- Metrics exceeding bounds are flagged for investigation
- The query produces a report suitable for inclusion in the
  consumer's weekly cardinality review

## Scenario 5: Pipeline-level metric_relabel drops are documented

**Preconditions**
- The consumer has applied Prometheus metric_relabel rules
  (or vendor equivalent) to drop high-cardinality labels at
  the ingestion boundary

**Action**
- Inventory the metric_relabel rules in the Prometheus
  configuration (or vendor pipeline)
- Cross-reference each rule with the consumer's documented
  remediation backlog

**Expected**
- Every metric_relabel drop has a corresponding remediation
  ticket
- The remediation ticket targets source-side fix within a
  documented timeline
- Drops that have been in place beyond the documented timeline
  are flagged

## Scenario 6: SLI computation is stable under cardinality growth

**Preconditions**
- The service has an SLO (observability.slo-policy) and an SLI computation
  query
- Load generator can vary cardinality of the SLI-driving
  metric's labels

**Action**
- Drive the service with two loads at different cardinality
  levels (e.g., 5 tenant_ids vs. 50 tenant_ids)
- Measure SLI query response time and result stability

**Expected**
- SLI query response time stays within the consumer's
  documented acceptable range across both load profiles
- SLI result is stable (the query returns the same
  computational result modulo the underlying availability
  difference)
- Backend resource use (query memory, storage) scales
  within the consumer's capacity plan

## Scenario 7: Negative test: emergency cardinality cut triggers correctly

**Preconditions**
- Substrate-recommended monitoring exists for the metrics
  backend's cardinality threshold
- A test fixture deliberately introduces high cardinality

**Action**
- Introduce the high-cardinality fixture
- Verify the cardinality-threshold monitor fires
- Apply the substrate-recommended emergency response
  (metric_relabel drop at the pipeline boundary)

**Expected**
- The cardinality-threshold monitor fires within the
  consumer's documented detection window
- The emergency response succeeds (cardinality returns to
  acceptable bound)
- A remediation ticket is created automatically (or
  manually within the response procedure)

## L1-promotion contribution log

Substrate-author note recorded 2026-05-21: when this test
template is executed in real consumer projects, the failure
modes observed contribute to the substrate's evaluation of
whether observability.cardinality-discipline can promote to L1. Specifically:

- Scenario 3 (unbounded vocabulary as label) failures that
  match the substrate's documented unbounded list confirm
  the mechanical pattern holds
- Scenario 3 failures that surface unbounded values outside
  the substrate's list inform vocabulary expansion
- False positives (the test rejects a documented bounded
  vocabulary that is actually fine) inform the substrate-
  recognized bounded list

Patterns recorded contribute to the substrate-author's
decision on L1 promotion timing.

## Cross-reference

- Substrate rule: observability.cardinality-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Good examples: examples/observability/cardinality-discipline-good.md
- Anti-patterns: examples/observability/cardinality-discipline-anti-pattern.md
