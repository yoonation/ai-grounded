---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.observability.slo-policy-slo-policy"
title: "observability.slo-policy review checklist: SLO and error budget policy ADR"
substrate-rule: "observability.slo-policy"
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
  - "Significant architecture change affecting reliability characteristics"
  - "Major customer commitments implying specific reliability targets"
  - "Substrate-recommended annual SLO review"
  - "Error budget burndown event requiring policy invocation"
---

# observability.slo-policy review checklist: SLO and error budget policy ADR

## How to use this binding

Reviewers answer every question below when reviewing the
consumer's SLO ADR, either at initial authoring or during the
annual review. The ADR's purpose is to make the service's
reliability commitments and budget policy explicit and
debatable; the checklist verifies the ADR carries the content
that makes that debate possible.

The substrate provides the decision framework MADR at
decision-frameworks/observability-slo-policy.madr.md as the
substrate's analysis of the option space. The consumer's ADR
adapts that framework. Reviewers consult both when answering.

## Review questions

### 1. Does the ADR identify SLIs that reflect customer experience?

SLI choice is the foundation. SLIs that reflect operator
convenience (CPU utilization, request count) rather than
customer experience (success rate, latency, freshness)
produce SLOs that pass while customers are unhappy.

What good looks like: SLIs are drawn from customer-facing
signals (request-success ratio over a meaningful customer
operation set; latency at a percentile users actually feel;
freshness for data-pipeline services); each SLI cites the
customer experience it measures; the ADR documents why these
SLIs were chosen over alternatives.

What needs follow-up: SLIs are operator-convenience metrics
(server CPU, queue depth); SLIs measure components rather
than user-facing operations; the ADR does not connect the
SLI to a customer experience.

### 2. Are SLO targets numerically specific?

A target like "high availability" is unmeasurable. A target
like "99.9 percent of HTTP requests succeed over a rolling
28-day window" is measurable, debatable, and operational.

What good looks like: each SLI has a numeric target; the
target's denominator (the request set, the time window) is
specified; the target rationale is documented (customer
commitment, competitive baseline, internal aspirational
target with acknowledged stretch).

What needs follow-up: targets use qualitative language
("high", "appropriate", "industry standard") without numerics;
target denominator is implicit (the reader must guess what
counts toward the success rate); rationale is missing or
generic.

### 3. Is the measurement window appropriate to the alerting cadence?

The SLO measurement window interacts with the burn-rate
alerting configuration (observability.alerting-discipline). A 28-day rolling window
supports multi-window burn-rate alerts at 1-hour and 6-hour
windows; a calendar-month window has different burn-rate
implications.

What good looks like: the measurement window is justified
(rolling 28 days is the substrate-default; calendar month
aligns with executive reporting; custom windows have explicit
rationale); the window's interaction with burn-rate alerting
is documented; the observability.alerting-discipline alert configuration cross-
references the window choice.

What needs follow-up: window is unstated (the SLO is "99.9
percent" without indicating over what period); window does
not match the burn-rate alerting configuration; window choice
was inherited from an unrelated service without analysis.

### 4. Is the error budget computation documented?

The error budget operationalizes the SLO. Without an explicit
computation, the budget is unauditable.

What good looks like: the budget computation is documented
formula-precisely (e.g., "error budget = (1 - SLO target) ×
total events in window"); the data source for total events
and error events is specified (which metrics, with which
labels); the computation is verifiable against the consumer's
metrics backend.

What needs follow-up: budget computation is described
qualitatively without a formula; the data source is unclear;
the computation cannot be reproduced from the consumer's
metrics.

### 5. Does the ADR document the budget burndown response policy?

The policy is what the team does when the budget is being
consumed faster than planned. Without it, the SLO is a number
without operational consequence.

What good looks like: the policy specifies actions at defined
budget consumption thresholds (e.g., "at 50 percent budget
remaining with 25 percent of window elapsed, feature work
slows and reliability work prioritizes; at 25 percent budget
remaining, feature work pauses; at 0 percent budget, escalate
to leadership for SLO renegotiation or extraordinary
remediation"); the policy is authoritative for the team's
work allocation.

What needs follow-up: policy is aspirational without
thresholds; thresholds exist but actions are unclear; the
team has informally agreed to a policy but the ADR does not
document it; the policy has never been invoked despite budget
burndown (the policy is not actually authoritative).

### 6. Is the ADR consistent with the substrate decision framework?

The substrate's decision framework provides the option space
analysis. The consumer's ADR adapts that framework. Deviations
from substrate-preferred options should be justified rather
than asserted.

What good looks like: the ADR explicitly references the
substrate framework (decision-frameworks/observability-slo-
policy.madr.md) and documents how the consumer's choices map
to or deviate from the substrate options; deviations cite the
consumer's specific context (regulatory regime, customer
commitment, organizational maturity).

What needs follow-up: the ADR does not reference the substrate
framework; the consumer's choices deviate without rationale;
the ADR predates the substrate framework and has not been
reviewed against it.

### 7. Is the SLO data flow connected to instrumentation?

The SLO and budget must be computable from emitted telemetry.
Without that connection, the SLO is aspirational rather than
operational.

What good looks like: each SLI's computation is connected to
specific metrics (with names, label sets, queries);
instrumentation for those metrics is verified in code
(observability.no-sensitive-data-in-telemetry, observability.trace-context-propagation, observability.metric-naming-convention, observability.semantic-convention-coverage, observability.cardinality-discipline
cross-references); the dashboard panels (observability.dashboard-discipline) and
alerts (observability.alerting-discipline) reference the same data source.

What needs follow-up: SLI computation references metrics that
do not exist or are not currently emitted; cardinality
discipline (observability.cardinality-discipline) prevents stable SLI computation
because labels are unbounded; the dashboard and alert
configurations do not match the SLO's data definition.

### 8. Has the ADR been reviewed in the substrate-recommended cadence?

SLOs age as the service and customer base evolve. Annual
review is the substrate default; significant events may
trigger off-cycle review.

What good looks like: the ADR has been reviewed in the past
year; the review documents the reviewer, date, and outcome;
review confirms the SLO still reflects customer experience
and the budget policy is still authoritative.

What needs follow-up: ADR has not been reviewed since
authoring; review confirms the ADR is current but does not
inspect whether SLI choices still reflect customer experience
(the most common review failure mode); the ADR is reviewed
without invoking the budget policy review even when
significant budget burndown has occurred.

## Reviewer attestation

```
observability.slo-policy review checklist: complete
- Customer-experience SLIs: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Numeric targets: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Measurement window: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Budget computation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Burndown response policy: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Substrate framework alignment: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Instrumentation connection: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Reviewed in cadence: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: observability.slo-policy in catalogs/concerns/observability.oscal.yaml
- Decision framework: decision-frameworks/observability-slo-policy.madr.md
- Good examples: examples/observability/slo-policy-good.md
- Anti-patterns: examples/observability/slo-policy-anti-pattern.md
- Related: observability.alerting-discipline (burn-rate alerting depends on this ADR); observability.dashboard-discipline (SLI dashboard depends on this ADR); observability.semantic-convention-coverage, observability.cardinality-discipline (instrumentation discipline supplies SLI data)
