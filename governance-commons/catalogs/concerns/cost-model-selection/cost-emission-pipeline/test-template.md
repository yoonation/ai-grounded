---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.cost-model-selection.cost-emission-pipeline-cost-emission-pipeline"
title: "cost-model-selection.cost-emission-pipeline test template: cost emission pipeline discipline"
substrate-rule: "cost-model-selection.cost-emission-pipeline"
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

# cost-model-selection.cost-emission-pipeline test template: cost emission pipeline discipline

## How to use this binding

Cost emission pipeline tests exercise the consumer's cost pipeline
against a controlled period of known-shape spend (a recent month
for which the provider invoice is finalized) and assert that the
pipeline's attributed view reconciles to the provider invoice
within the substrate-recommended variance threshold. Tests also
exercise the pipeline's drill-down tooling so variance investigation
capability is verified rather than assumed.

Substrate-recommended cadence: quarterly reconciliation test
against the most recent finalized invoice; spot-check after every
significant allocation-rule change; CI gate on the pipeline's
ingestion job (alerts on failed ingestion within the same day).

## Scenario 1: Pipeline ingests provider billing data on schedule

**Preconditions**
- The pipeline's last-ingest timestamp is observable
- The provider billing export has produced data for the prior
  calendar day
- The ingestion job has had at least one expected run cycle

**Action**
- Query the pipeline's last-ingest timestamp
- Compare to the substrate-recommended cadence (daily for the
  primary cloud provider; on-publication for vendor invoices)

**Expected**
- Last-ingest timestamp is within the substrate-recommended
  cadence window (no more than 1 cadence cycle stale)
- The pipeline's ingestion job has a monitored success signal
  (alert on failed run)
- The pipeline does not silently fall behind when the provider's
  export is delayed (the consumer's monitoring catches export-
  delay as a distinct condition from ingestion failure)

## Scenario 2: Allocation rules consume the cost-model-selection.cost-attribution-tags tag floor

**Preconditions**
- A representative service in the consumer's service catalog is
  known to be tagged with the substrate-required floor (cost-
  center, environment, service, owner)
- The pipeline has ingested the service's spend for the prior
  month

**Action**
- Query the pipeline for the service's attributed spend by each
  required tag dimension
- Compare the attributed sums (sum by cost-center, sum by
  environment, sum by service, sum by owner) against the
  pipeline's total view for the service

**Expected**
- Each tag-dimension sum reconciles to the service's total
  within the substrate-recommended variance threshold
- The pipeline's allocation rules reference each substrate-
  required tag (rules can be enumerated and verified to
  consume the tag in question)
- Services with the substrate-required tag floor produce
  attributed spend in every tag dimension; absence of attribution
  in any dimension indicates an allocation rule gap or a tag-
  coverage gap

## Scenario 3: Multi-tenant attribution sums to workload total

**Preconditions**
- The consumer operates at least one multi-tenant workload
- Per-tenant attribution is implemented (OpenCost, cloud-native
  labels, or consumer-custom labeled metrics)
- The workload's spend for the prior month is finalized in the
  pipeline

**Action**
- Query the per-tenant attribution for the workload across all
  tenants
- Sum the per-tenant attributed spend
- Compare to the workload's total attributed spend from the
  pipeline's workload-level view

**Expected**
- The sum of per-tenant attribution reconciles to the workload
  total within the substrate-recommended variance threshold
- Per-tenant attribution covers every active tenant in the
  prior month (no tenant is missing from the attribution view
  while having been active)
- The substrate-recommended variance threshold is documented in
  the consumer's cost-allocation policy and applied consistently

## Scenario 4: Pipeline output reconciles to provider invoice

**Preconditions**
- The provider has issued a finalized invoice for the prior
  calendar month
- The pipeline has ingested all billing data for the same
  month
- The reviewer has the invoice PDF or API export available

**Action**
- Sum the pipeline's attributed spend for the month
- Compare to the invoice total
- Investigate variance source for any divergence above the
  substrate-recommended threshold

**Expected**
- The pipeline total and the invoice total agree within the
  substrate-recommended variance threshold (2 percent absolute
  variance unless the consumer has tightened)
- Variance below threshold is documented as expected (provider
  billing-export latency; allocation-rule rounding; reseller
  invoice timing)
- Variance above threshold triggers a finding and remediation
  per the cost-model-selection.cost-emission-pipeline review

## Scenario 5: Variance investigation drill-down tooling works

**Preconditions**
- The pipeline produces a service-level attributed view for the
  prior month
- The pipeline exposes drill-down by tag, by service, by
  account, and by time window

**Action**
- Select a service with non-trivial spend
- Drill from the service-level view to the resource-level view
  (the underlying provider line items attributing to the service)
- Drill from the resource-level view to the raw billing data
  (the provider's CUR row or equivalent)
- Reverse-traverse from a raw line item back to the service it
  attributes to

**Expected**
- The drill-down produces a consistent attribution chain end-
  to-end (the resource line items in the resource-level view
  sum to the service-level total; the raw line items in the
  detail view sum to the resource-level value)
- The reverse traversal produces a single attributed service
  (or a documented shared-cost allocation rule if the resource
  is intentionally shared)
- The drill-down tooling completes within the consumer's
  performance expectations (sub-second for a single service;
  no longer than a few minutes for a multi-service investigation)

## Scenario 6: Shared-cost allocation rules apply as documented

**Preconditions**
- The consumer's cost-allocation policy documents shared-cost
  allocation rules (e.g., cross-account shared services
  allocated by usage; account-level support fees allocated by
  spend proportion; reseller invoice line items allocated to
  the receiving account)
- The pipeline has applied the rules to the prior month's data

**Action**
- Select a shared cost the policy documents (e.g., the
  consumer's cross-account VPC endpoint fees)
- Query the pipeline's allocation of that cost across the
  receiving accounts or services
- Compare the actual allocation against the policy's
  documented allocation rule

**Expected**
- The pipeline's allocation matches the policy rule
- The allocation is documented in the pipeline's metadata
  (the reviewer can trace from the allocated line item back to
  the policy rule that produced the allocation)
- Shared-cost allocation rules that have been amended since the
  prior review have updated their documented rule in the policy

## Scenario 7: Pipeline feeds anomaly alerting and budget computation

**Preconditions**
- The pipeline produces the per-service attributed view
- cost-model-selection.cost-anomaly-alerting anomaly alerting is configured against
  per-service budgets
- The cost-model-selection.cost-model-selection-policy ADR documents the budget computation method

**Action**
- For a service with a documented cost SLO in the ADR, derive
  the budget-status from the pipeline's output following the
  ADR's documented computation method
- Compare against the budget-status reported by the cost-model-selection.cost-anomaly-alerting
  alerting configuration

**Expected**
- The pipeline-derived budget-status and the alerting-reported
  status agree
- The cost-model-selection.cost-anomaly-alerting alert thresholds were configured against
  the same pipeline data path the ADR references
- A divergence between the two indicates either alerting is
  running off a different data path (a substrate finding) or
  the ADR's documented computation has fallen out of sync with
  the operational implementation
