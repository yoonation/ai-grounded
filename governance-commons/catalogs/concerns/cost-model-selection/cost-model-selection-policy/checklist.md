---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.cost-model-selection.cost-model-selection-policy-cost-model-selection-policy"
title: "cost-model-selection.cost-model-selection-policy review checklist: cost model selection policy ADR"
substrate-rule: "cost-model-selection.cost-model-selection-policy"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
  - "New service entering production"
  - "Significant architecture change affecting cost characteristics"
  - "Major business model shift affecting unit economics"
  - "Substrate-recommended annual cost-model review"
  - "Substantial budget-burndown event invoking the response policy"
---

# cost-model-selection.cost-model-selection-policy review checklist: cost model selection policy ADR

## How to use this binding

Reviewers answer every question below when reviewing the consumer's
cost-model ADR, either at initial authoring or during the annual
review. The ADR's purpose is to make the service's cost commitments
and trade-off rationale explicit and debatable; the checklist
verifies the ADR carries the content that makes that debate
possible.

The substrate provides the decision framework MADR at
decision-frameworks/cost-model-selection-policy.madr.md as the
substrate's analysis of the option space. The consumer's ADR
adapts that framework. Reviewers consult both when answering.

## Review questions

### 1. Does the ADR identify cost SLIs that reflect the consumer's economic interest?

Cost SLI choice is the foundation. SLIs that reflect operator
convenience (raw monthly spend; provider-defined cost categories)
rather than the consumer's economic interest (cost per customer;
cost per transaction; cost per tenant) produce SLOs that pass
while the business is unsustainable.

What good looks like: cost SLIs are drawn from the consumer's
unit economics (cost per active user per month; cost per
transaction at the consumer's revenue-driving operation; cost
per tenant per tier where the business is multi-tenant); each
cost SLI cites the economic dimension it reflects; the ADR
documents why these cost SLIs were chosen over alternatives.

What needs follow-up: cost SLIs are operator-convenience metrics
(absolute monthly spend without context); cost SLIs measure
provider categories (compute, storage, network) rather than
service or unit dimensions; the ADR does not connect cost SLI
to a unit-economics dimension.

### 2. Are cost SLO targets numerically specific at multiple horizons?

A target like "stay within budget" is unmeasurable. A target
like "monthly compute spend per active user under $0.50" is
measurable, debatable, and operational.

What good looks like: cost SLO targets are numerically specific
(monthly absolute budget; per-unit-economics target; year-over-
year growth target where the consumer's business is in growth
phase); the target denominators (the customer set, the
transaction set, the time window) are explicit; targets at
multiple horizons (monthly for short-term ops; quarterly for
trend; annual for budget planning) are reconciled with one
another.

What needs follow-up: targets are aspirational without numbers;
target denominators are ambiguous; targets at different
horizons contradict (the monthly target implies an annual
amount that contradicts the annual target).

### 3. Is the budget computation method reproducible from the cost-model-selection.cost-emission-pipeline pipeline?

The budget computation must be derivable from the pipeline; an
SLO measured against a pipeline-different data path is two
separate cost views.

What good looks like: the ADR documents the budget computation
formula; the formula references pipeline outputs (the cost-model-selection.cost-emission-pipeline
attributed spend view); the reviewer can run the formula
against the pipeline's recent output and obtain the budget-
status the ADR claims; the pipeline's output and the ADR's
expected status agree.

What needs follow-up: budget computation references a separate
estimate path; budget computation formula is not documented;
the formula references data the pipeline does not produce.

### 4. Is the over-budget response policy operationally meaningful?

A response policy that is aspirational ("we'll evaluate at that
time") is not a policy. The substrate's discipline is to
predefine the response so the team operates from a documented
position at fire time.

What good looks like: the response policy specifies the response
at concrete burndown thresholds (workload-level mitigation steps
at threshold A; service-level rate limiting at threshold B;
escalation to product owner at threshold C; accepted variance
with documented rationale at threshold D); each response is
operationally meaningful (a documented action rather than an
aspirational statement); the response policy is cross-referenced
from the cost-model-selection.cost-anomaly-alerting alerting configuration.

What needs follow-up: policy is aspirational; thresholds are
named but actions are absent; actions reference processes that
do not exist; escalation targets a role no longer in the
organization.

### 5. Does the trade-off rationale address the cost-vs-reliability boundary?

Cost budgets compete directly with reliability investments. The
substrate's ADR discipline is to document the consumer's
position on the trade-off so the team is not improvising at
the trade-off point.

What good looks like: the ADR documents the consumer's position
on cost-vs-reliability trade-offs at the substrate-recognized
boundaries (an additional 9 of availability costs more than the
current budget allows; a fault-injection program costs recurring
spend; a regulated-region deployment duplicates infrastructure
at full cost); the rationale is substantive (the trade-off is
reasoned with data, not asserted); the ADR cross-references the
observability.slo-policy SLO policy ADR where the two concerns intersect.

What needs follow-up: trade-off rationale is missing; rationale
is asserted without analysis; the ADR commits to reliability
targets that the cost budget cannot fund.

### 6. Are decision drivers from the substrate framework addressed?

The substrate's framework identifies decision drivers (business
model, unit economics, reliability commitments, operational
maturity, multi-tenant constraints, vendor contract structure)
that should inform every cost-model ADR. Coverage of the drivers
is a check on substantive depth.

What good looks like: the ADR addresses each substrate-recognized
driver; coverage is substantive (the driver is engaged, not
referenced and dismissed); consumer-specific drivers are added
where relevant; the connection between drivers and decisions is
explicit.

What needs follow-up: drivers are listed without engagement;
drivers absent from the ADR without justification; consumer-
specific drivers that obviously apply (a multi-tenant SaaS
provider without a multi-tenant-constraints section) are
missing.

### 7. Is the decision-review schedule and trigger set documented?

A cost-model that is not revisited becomes stale as the
consumer's business and infrastructure evolve. The substrate's
discipline is annual review plus trigger-based reviews.

What good looks like: the ADR documents the substrate-recommended
annual review cadence; triggers for earlier review are listed
(architecture change affecting cost; business model shift;
substantial budget-burndown event); the prior review's outcomes
are recorded (where the ADR is on its first review, the next-
review date is explicit).

What needs follow-up: no review schedule; schedule references
"as needed" without triggers; the ADR is past its documented
review date without amendment or extension.

### 8. Does the ADR cross-reference dependent COST rules and the observability.slo-policy SLO policy?

The cost-model ADR is the anchoring decision for the COST-L2
rules. Cross-references make the chain of decisions traceable.

What good looks like: the ADR references cost-model-selection.cost-attribution-tags (the tag
floor whose values feed the pipeline that feeds this ADR's
computation); cost-model-selection.workload-resource-limits (the workload limits that bound the
runtime cost the ADR commits to); cost-model-selection.cost-emission-pipeline (the pipeline
that produces the data the ADR's computation references);
cost-model-selection.cost-anomaly-alerting (the alerting that fires when burndown occurs);
observability.slo-policy (the reliability-budget analog where reliability and
cost trade off).

What needs follow-up: the ADR stands alone without cross-
references; references exist but point to retired or wrong
artifacts; the COST-L2 rules operate against targets the ADR
does not document.

## Findings disposition

For each question answered with what-needs-follow-up content, the
reviewer records a finding with: question reference; observed
condition; substrate-recommended remediation; owner; target date.

Findings that block the consumer's cost-model-selection.cost-model-selection-policy review are those
where the ADR is missing required sections, the over-budget
response is aspirational, or the cost SLI choice does not
connect to a unit-economics dimension. Findings that surface as
advisories are those where the ADR is adequate but not
substrate-recommended-optimal: a different cost SLI composition
that fits the consumer's business model; a different response
policy structure that fits the consumer's organizational shape.

A consumer ADR satisfying cost-model-selection.cost-model-selection-policy references both the
substrate framework (decision-frameworks/cost-model-selection-
policy.madr.md) and the consumer's specific positions on each
section above.
