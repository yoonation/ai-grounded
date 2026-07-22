---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.cost-model-selection.cost-anomaly-alerting-cost-anomaly-alerting"
title: "cost-model-selection.cost-anomaly-alerting review checklist: cost anomaly alerting configured"
substrate-rule: "cost-model-selection.cost-anomaly-alerting"
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
  - "Cost-budget initial setting on a new service"
  - "Cost-model ADR review (per cost-model-selection.cost-model-selection-policy cadence)"
  - "Budget-burndown event invoking the response policy"
  - "Substrate-recommended annual review of threshold sanity"
  - "Alert routing change in the consumer's on-call rotation"
---

# cost-model-selection.cost-anomaly-alerting review checklist: cost anomaly alerting configured

## How to use this binding

Reviewers answer every question below when reviewing the consumer's
cost anomaly alerting configuration, either at initial setup or
during the periodic review cadence. The alerting's purpose is to
convert the cost pipeline (cost-model-selection.cost-emission-pipeline) from a retrospective
reporting view into a forward-looking control; the checklist
verifies the alerting is configured to do so.

The reviewer captures the consumer's current alert configuration
(thresholds, routing, escalation), the matching cost-model-selection.cost-model-selection-policy ADR
(for the budget targets the alerts are evaluated against), and
the recent alert-firing history before answering.

## Review questions

### 1. Are per-service cost budgets documented and tied to the cost-model-selection.cost-model-selection-policy ADR?

Per-service granularity is what makes alerting actionable.
Account-wide alerts route to teams that do not own the variant
service.

What good looks like: every service with a documented cost SLO
in the cost-model-selection.cost-model-selection-policy ADR has a corresponding per-service budget
configured in the alerting platform; the budget values match the
ADR's documented SLO targets; budget changes are version-controlled
alongside the ADR.

What needs follow-up: only account-wide budgets configured; per-
service budgets exist but do not match the ADR; budget values
were set once and have not been revisited as the service's
profile changed.

### 2. Is the alerting pattern burn-rate (multi-window) rather than single-threshold?

Single-threshold alerts (fire when monthly spend exceeds X) are
either too slow (the threshold fires at month-end when response
is too late) or too noisy (the threshold fires every month-end
on normal spend pattern). Burn-rate alerting evaluates the
trajectory.

What good looks like: alerts use the substrate-recommended multi-
window burn-rate pattern parallel to observability.alerting-discipline: a 1-day window
catches short-burst anomalies (a misconfiguration consuming 10x
baseline for hours); a 7-day window catches sustained burn (a
gradual creep at 1.5x baseline persisting for days); both windows
evaluate against the monthly budget normalized to the window.

What needs follow-up: alerts fire on single-threshold absolute
spend; alerts fire on month-end forecast only; window choices
do not match the substrate-recommended cadence.

### 3. Do alerts route to the service-owning team?

Routing determines whether the alert produces action. An alert
that routes to a generic inbox is triaged-down rather than
acted-on.

What good looks like: per-service alerts route to the service-
owning team's on-call rotation (the same rotation that handles
the service's reliability alerts); account-wide alerts route to
the FinOps or platform-engineering function; routing is
documented in the consumer's runbook; routing has been exercised
in the past quarter (either by a real alert or a synthetic drill).

What needs follow-up: alerts route to a generic inbox; alerts
route to an email list with no on-call accountability; routing
has not been exercised and may be silently broken.

### 4. Is the burndown response policy documented and operationally meaningful?

A burndown response policy that exists only as an aspirational
statement does not invoke when the budget burns. The substrate's
discipline is to predefine the response so the team is not
improvising under fire.

What good looks like: the burndown response is documented in the
cost-model ADR (cost-model-selection.cost-model-selection-policy); the response is operationally
specific (workload-level mitigation steps; service-level rate
limiting parameters; escalation triggers to product owner;
accepted variance with documented rationale); the team has
exercised the response (either by a real burndown event or a
synthetic drill).

What needs follow-up: response policy is aspirational ("we'll
evaluate at that time"); response is documented but has never
been invoked; response references a process owner who is no
longer in role.

### 5. Are threshold values sane against the consumer's spend baseline?

Thresholds set too high (only catastrophic spend fires) or too
low (every minor variance fires) produce alerts that do not
produce signal. Sanity is a function of the service's spend
distribution.

What good looks like: thresholds reflect the consumer's spend
baseline (the 1-day burn-rate threshold fires at the substrate-
recommended multiplier of baseline daily spend; the 7-day
threshold fires at the multiplier of weekly baseline); thresholds
are reviewed annually against the prior year's spend distribution;
threshold changes are documented in the ADR.

What needs follow-up: thresholds set so high they only fire on
runaway spend (the alert exists but does not produce actionable
signal); thresholds set so low they fire on normal variance (the
alert produces noise the team filters out, defeating the alert);
thresholds set once at initial implementation and not revisited.

### 6. Has the alerting fired and been actioned in the past quarter?

An alert that has never fired is either misconfigured or routed
to a non-existent baseline. Either is a finding.

What good looks like: the alert has fired at least once in the
past quarter (either a real variance event or a synthetic drill);
the firing produced documented action (root cause investigation;
remediation; ADR update if the budget needed amendment); the
action loop reflected the documented burndown response.

What needs follow-up: no alert firings in recent history without
explanation; past firings were acknowledged-only without root
cause; past firings were silently dismissed without invoking
the response policy.

### 7. Are per-tenant anomaly alerts configured for multi-tenant services?

Where cost-model-selection.cost-emission-pipeline per-tenant attribution is in place, per-tenant
alerts are the substrate-recommended layer below per-service
alerts. The pattern catches a single tenant whose usage drives
the service into budget burndown.

What good looks like: multi-tenant services with per-tenant
attribution have per-tenant cost anomaly alerts; per-tenant
alerts route to the consumer's customer-success or tenant-
management function (where the response is tenant-facing) or to
the service-owning team (where the response is workload-shaping);
the substrate-recommended pattern is documented in the consumer's
runbook.

What needs follow-up: per-tenant attribution exists but per-
tenant alerts do not; per-tenant alerts route to a function
that lacks authority to respond; alerting is per-service only
for services that have per-tenant attribution available.

## Findings disposition

For each question answered with what-needs-follow-up content, the
reviewer records a finding with: question reference; observed
condition; substrate-recommended remediation; owner; target date.

Findings that block the consumer's cost-model-selection.cost-anomaly-alerting review are those
where alerting is account-wide-only on services that have
documented per-service SLOs, where the burndown response is
aspirational, or where routing has not been exercised. Findings
that surface as advisories are those where the pattern is
substrate-recommended-optimal but the consumer's variant produces
adequate signal: a different burn-rate window choice that fits
the consumer's spend pattern; a per-team routing variant that
matches the consumer's on-call structure.
