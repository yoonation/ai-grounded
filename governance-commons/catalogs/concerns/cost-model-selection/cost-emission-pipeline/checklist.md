---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.cost-model-selection.cost-emission-pipeline-cost-emission-pipeline"
title: "cost-model-selection.cost-emission-pipeline review checklist: cost emission pipeline discipline"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Cost pipeline initial implementation or platform migration"
  - "New cost-allocation rule (new account, new tenant tier, new vendor outside primary cloud)"
  - "Provider billing-export schema change"
  - "Substrate-recommended quarterly reconciliation audit"
  - "Any unreconciled variance exceeding the substrate-recommended threshold"
---

# cost-model-selection.cost-emission-pipeline review checklist: cost emission pipeline discipline

## How to use this binding

Reviewers answer every question below when reviewing the consumer's
cost emission pipeline, either at initial implementation or during
the periodic reconciliation audit. The pipeline's purpose is to
produce attributed spend that reconciles to the provider's billing
system within a substrate-recommended variance threshold; the
checklist verifies the pipeline meets each substrate requirement.

The reviewer captures a representative month's pipeline output and
the matching provider invoice before answering: the reconciliation
questions depend on having both views available for comparison.

## Review questions

### 1. Does the pipeline ingest provider billing data on the substrate-recommended cadence?

Cost data is time-sensitive. Late-arriving data delays anomaly
detection (cost-model-selection.cost-anomaly-alerting depends on this pipeline) and breaks
reconciliation by misattributing spend to the wrong reporting
period.

What good looks like: the primary cloud provider's billing export
(AWS Cost and Usage Report, Azure Cost Management export, GCP
Billing export to BigQuery) is ingested daily; vendor invoices
outside the primary cloud are ingested on publication; the
pipeline's last-ingest timestamp is observable and alerted on
failure.

What needs follow-up: cost data is loaded manually on an ad-hoc
schedule; the pipeline operates on monthly batches only (forfeiting
intra-month anomaly detection); export failures are silent.

### 2. Do allocation rules consume the cost-model-selection.cost-attribution-tags tags as expected?

The cost-model-selection.cost-attribution-tags tag floor (cost-center, environment, service,
owner) exists to feed this pipeline. Tags that are not consumed
by an allocation rule are tag-discipline overhead with no
operational return.

What good looks like: sample tag values flow through to attributed
spend in the pipeline output; the reviewer can pick a service
known to be tagged and trace its spend from raw billing data
through allocation to the chargeback view; allocation rules
explicitly reference each substrate-required tag.

What needs follow-up: tags collected at IaC time but never
referenced by an allocation rule; allocation rules referencing
deprecated tag names from a prior tag schema; rules that default
all unmatched spend to a generic bucket without surfacing the
default as a finding.

### 3. Is per-tenant attribution implemented where the business model requires it?

A multi-tenant service that does not attribute per-tenant cost
cannot tier its pricing, cannot answer "is tenant X cost-positive,"
cannot detect a single tenant whose usage drives the service's
spend out of band.

What good looks like: multi-tenant services have per-tenant cost
attribution via OpenCost (Kubernetes), cloud-native cost-allocation
labels (non-Kubernetes), or consumer-custom labeled metrics
(application-level tenancy); the per-tenant attribution sums to
the workload's total cost within the substrate-recommended
variance threshold; per-tenant attribution is surfaced in the
consumer's chargeback or showback ledger.

What needs follow-up: multi-tenant workload spend attributed to a
generic shared bucket; per-tenant attribution implemented for
some but not all multi-tenant services; per-tenant attribution
exists but its sum diverges from the workload total without
explanation.

### 4. Does the pipeline output reconcile to the provider invoice?

A pipeline that does not reconcile is not authoritative. Operators
making decisions from a non-reconciled view propagate the
reconciliation gap into financial planning.

What good looks like: the pipeline output and the provider invoice
agree within the substrate-recommended variance threshold (2
percent absolute variance against the monthly invoice; consumers
may tighten); variance sources are documented (provider billing-
export latency, allocation-rule gaps, tag-coverage gaps, reseller
invoice timing); the reviewer can trace a sample service's
attributed spend back through the allocation rules to the raw
billing data and forward to the chargeback ledger.

What needs follow-up: variance exceeds threshold without
documented explanation; variance sources are unknown; the
pipeline output is consumed by stakeholders who are unaware of
the variance.

### 5. Are shared-cost allocation rules documented and reviewed?

Some spend cannot be tagged at the resource level: cross-account
shared services, reseller invoice line items, vendor contracts
negotiated outside the cloud, account-level support fees.
Allocation of this spend depends on consumer-defined policy.

What good looks like: shared-cost allocation rules are documented
in the consumer's cost-allocation policy (typically tied to the
cost-model-selection.cost-model-selection-policy ADR); rules are reviewed at substrate-recommended
annual cadence; rule changes are versioned and announced to
affected teams; the allocation policy includes both the rule and
the rationale.

What needs follow-up: shared cost is split by an undocumented
heuristic; rules have not been reviewed in over a year; rule
changes occur silently and surface as unexplained variance in
the chargeback view.

### 6. Has the pipeline been exercised against a recent variance?

A pipeline that has never been challenged with a variance has
not been exercised. Variance investigation is the operational
discipline that validates the pipeline.

What good looks like: the team has exercised the pipeline against
at least one variance event in the past quarter (either a real
variance or a synthetic drill); the variance investigation
produced a documented root cause; the pipeline's variance-
investigation tooling (drill-down by tag, by service, by
account, by time window) was exercised and worked.

What needs follow-up: no variance events in recent history (the
pipeline may be silently broken); past variances were attributed
generically without root-cause investigation; the pipeline lacks
drill-down tooling sufficient for variance investigation.

### 7. Does the pipeline feed cost-model-selection.cost-anomaly-alerting anomaly alerting and cost-model-selection.cost-model-selection-policy budget computation?

The pipeline is a substrate-recognized data source for two
downstream rules. Where it does not feed them, the downstream
rules operate on a different data path and the substrate's cost-
concern coherence is broken.

What good looks like: the same pipeline output that drives the
chargeback ledger also feeds the cost-anomaly alerts (cost-model-selection.cost-anomaly-alerting)
and the budget-computation method documented in the cost-model
ADR (cost-model-selection.cost-model-selection-policy); a single source of truth exists for "what
this service cost this month."

What needs follow-up: anomaly alerts run off a separate cost
estimate path (the substrate's reconciliation discipline does not
apply to alerts); budget computation in the ADR refers to data
that does not match the pipeline's view; multiple cost-views
exist in the consumer's organization without designated authority.

## Findings disposition

For each question answered with what-needs-follow-up content, the
reviewer records a finding with: question reference; observed
condition; substrate-recommended remediation (or consumer-side
acceptance with documented rationale); owner; target date.

Findings that block the consumer's cost-model-selection.cost-emission-pipeline review are those
where reconciliation variance is unreconcilable, allocation rules
have systemic gaps, or per-tenant attribution is required by the
business model and absent. Findings that surface as advisories
(rather than blocking) are those where the pipeline is adequate
but not substrate-recommended-optimal: monthly-only ingestion
where daily would catch anomalies sooner; manual drill-down
tooling where automated would scale better.
