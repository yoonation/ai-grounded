---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.observability.alerting-discipline-alerting-discipline"
title: "observability.alerting-discipline review checklist: alerting discipline"
substrate-rule: "observability.alerting-discipline"
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
  - "Every new alert rule"
  - "Post-incident review identifying alert noise or alert gap"
  - "Substrate-recommended quarterly alert rule sweep"
  - "Migration between alerting backends"
---

# observability.alerting-discipline review checklist: alerting discipline

## How to use this binding

Reviewers answer every question below when reviewing pull
requests adding or modifying alert rules, or during the
quarterly alert sweep. Unanswered items block merge or
escalate as findings in the self-assessment.

The reviewer references the alert rule definition, the
runbook the alert links to, and the alert's recent firing
history (substrate-recommended past quarter) when answering.

## Review questions

### 1. Does the alert carry a severity label drawn from a bounded vocabulary?

Severity is the on-call responder's first triage signal. A
missing or ambiguous severity leaves responders unable to
distinguish urgent from informational.

What good looks like: the alert has a severity label drawn
from the consumer's bounded vocabulary (substrate-recommended
starting set: critical for human-paging conditions, warning
for ticket-creating conditions, info for record-only
conditions); the vocabulary is documented in the consumer's
paging policy.

What needs follow-up: severity label missing; severity uses
ad-hoc values outside the consumer's vocabulary; severity
inflation has occurred (everything labeled critical to ensure
notification); the consumer has no documented paging policy.

### 2. Does the alert link to a runbook?

A runbook-less alert is operationally incomplete. The on-call
responder needs documented steps; without them the alert
fires into an investigation rather than a remediation.

What good looks like: alert has a runbook_url annotation
linking to a live document; the runbook describes the alert's
detection logic, common root causes, immediate remediation
steps, escalation criteria, and post-resolution actions.

What needs follow-up: runbook_url missing; runbook_url points
to a 404 or a wiki page that has been deleted; runbook exists
but has not been updated since the alert was authored.

### 3. Does the alert summary distinguish it from related alerts?

Notification UIs display the summary; the on-call responder
sees this before opening the runbook. Ambiguous summaries
slow triage.

What good looks like: summary annotation is concise (fits a
notification body); summary identifies the alerting service,
the symptom, and the severity at-a-glance; related alerts
(same service, different symptom) have distinguishable
summaries.

What needs follow-up: summary is the same as the alert name
(uninformative); summary is identical to a related alert's
summary; summary is verbose to the point of unhelpfulness;
summary contains template variables that did not interpolate
at fire time.

### 4. Does the alert detection logic capture a symptom rather than a cause?

Symptom-based alerts catch the user-visible problem
regardless of underlying cause. Cause-based alerts catch one
specific failure mode and miss others.

What good looks like: the alert fires when the service
violates its SLO (burn-rate alert), or when a user-visible
operation degrades (latency above threshold), or when error
rates exceed a customer-impact threshold; the alert is robust
to different root causes producing the same symptom.

What needs follow-up: the alert fires on a single component's
health (database connection count) without correlation to
user impact; the alert misses cases where the underlying
component is healthy but composition produces user-visible
failure; the alert is part of a "many alerts per service"
pattern where each cause has its own alert.

### 5. Are inhibition or grouping rules configured for dedup?

Multiple symptoms of a single root cause should produce a
single notification, not a cascade. Alertmanager inhibition
rules (or vendor equivalent) are the substrate-recommended
mechanism.

What good looks like: cascading alerts (the database is down
so dependent services emit error alerts) are grouped by
inhibition rules so a single notification covers the root
cause; alert grouping is configured at the Alertmanager (or
equivalent) layer with documented routing.

What needs follow-up: an incident produces ten notifications
when one would suffice; inhibition rules are not configured;
grouping rules group alerts that should be distinct (hiding
genuine separate problems).

### 6. Does the alert rule history show it has been acted on?

Chronically-ignored alerts are operational noise. The
substrate-recommended action is to disable rather than
continue paging.

What good looks like: the alert has fired in the past
quarter and the firings were acted on (responder ticked,
runbook executed, post-incident review when appropriate); or
the alert has not fired in the past quarter because the
condition has not occurred; or the alert has been disabled
with a documented rationale.

What needs follow-up: the alert fires frequently and is
routinely silenced without acting on it; the alert fires and
the response is "ignore until it goes away"; the alert
fires and creates tickets that age out without action.

### 7. Does the alert use burn-rate alerting for SLO-bound conditions?

For alerts that detect SLO violations, burn-rate alerting is
the substrate-recommended pattern. Threshold alerting on raw
error rate produces high noise; burn-rate alerts on the rate
of error budget consumption.

What good looks like: SLO-bound alerts use multi-window burn-
rate alerting (substrate-recommended starting configuration:
1-hour and 6-hour windows with severity tiered by combined
burn rate); the configuration cross-references the observability.slo-policy
SLO documentation.

What needs follow-up: SLO-bound alerts use threshold alerting
on raw error rate (high noise at low traffic, slow detection
at high traffic); burn-rate alerts use a single window
(either too fast and noisy or too slow); the SLO is not
documented (observability.slo-policy violation surfaces here).

### 8. Has the alert been reviewed in the substrate-recommended sweep cadence?

The quarterly sweep ensures alerts stay relevant as the
service evolves. Without the sweep, alerts accumulate as
noise.

What good looks like: each alert was reviewed in the past
quarter against the questions above; the review documents
the reviewer and outcome; the sweep catches alerts to retire,
to amend, or to upgrade to SLO-bound burn-rate.

What needs follow-up: alerts have not been reviewed since
authoring; the sweep happens but is not documented; the
review surfaces an unhealthy alert count (substrate-
recommended escalation: more than three rules requiring
discipline corrections in one quarter triggers a meta-review
on the alert authoring process).

## Reviewer attestation

```
observability.alerting-discipline review checklist: complete
- Severity label: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Runbook link: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Distinguishable summary: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Symptom-based detection: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Inhibition or grouping: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Alert acted on: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Burn-rate where applicable: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Reviewed in sweep cadence: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: observability.alerting-discipline in catalogs/concerns/observability.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/observability/alerting-discipline-good.md
- Anti-patterns: examples/observability/alerting-discipline-anti-pattern.md
- Related: observability.slo-policy SLO policy (anchors burn-rate alerting); monitoring-alerting concern (Milestone 5; deeper alert operations questions)
