---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: monitoring-alerting.alerting-strategy
title: "Alerting Strategy: Coverage Philosophy, the Severity-to-Routing Matrix, the Escalation and On-Call Model, the Alert Lifecycle, Meta-Monitoring, and the Post-Incident Feedback Loop"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with monitoring-alerting.alerting-strategy. Portfolio-of-sub-decisions structure mirroring the privacy, responsible-ai, and observability decision-framework precedents: the detection-coverage philosophy, the severity-to-routing matrix, the escalation and on-call model, the alert lifecycle, the meta-monitoring approach, the post-incident feedback loop, and ownership and review cadence, rather than a single option pick. Draft lifecycle per M5 Session 5; stable promotion at M5 close."
authoritative-sources:
  - "https://sre.google/sre-book/monitoring-distributed-systems/"
  - "https://sre.google/sre-book/practical-alerting/"
  - "https://sre.google/sre-book/being-on-call/"
  - "https://sre.google/workbook/alerting-on-slos/"
  - "https://prometheus.io/docs/practices/alerting/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.observability-slo-and-error-budget-policy
---

# Alerting Strategy: Coverage Philosophy, the Severity-to-Routing Matrix, the Escalation and On-Call Model, the Alert Lifecycle, Meta-Monitoring, and the Post-Incident Feedback Loop

## Context and Problem Statement

Any operated service has an alerting posture. The only choice is whether it is
decided and written down or left to accrete from whatever each alert author
happened to wire up. monitoring-alerting.alerting-strategy requires the strategy be explicit, because a
coherent on-call experience is a system property that emerges from how coverage,
routing, escalation, lifecycle, and meta-monitoring cohere, not from any one
alert rule. The mechanical rules (every route resolves to a real receiver,
monitoring-alerting.alert-route-resolves-to-receiver; every suppression carries an expiry, monitoring-alerting.silence-carries-expiry) and the semantic
rules (coverage, monitoring-alerting.detection-coverage; routing and escalation, monitoring-alerting.routing-and-escalation; lifecycle,
monitoring-alerting.alert-lifecycle; pipeline liveness, monitoring-alerting.pipeline-liveness-and-runbook-reachability; on-call coverage, monitoring-alerting.on-call-rotation-coverage) are
each local conformance checks; what they conform to is this policy.

The failure this prevents is the pile of locally reasonable alerts that do not
cohere: rules that individually pass hygiene but collectively page the wrong
people at the wrong severity, with no lifecycle and no backstop, until on-call
becomes something engineers dread and learn to tune out. This strategy builds
on the observability concern (which owns the signals, the per-alert-rule
hygiene in observability.alerting-discipline, and the SLO and error-budget policy in observability.slo-policy) and
adds the operations layer observability explicitly defers to monitoring-
alerting. It consumes the severity label observability.alerting-discipline defines and the SLOs
observability.slo-policy chooses rather than redefining either, and it references the
liveness and readiness health signals reliability owns (reliability.health-signaling) as one
input it may alert on.

## Decision Drivers

- Real incidents must be detected internally before users report them, which is
  a coverage question, not an alert-hygiene one.
- A detected incident must reach a human who can act, with a backstop when the
  first human does not.
- Alerts must be operable: acknowledged, silenced without creating permanent
  blind spots, and resolved when the condition clears, or the team learns to
  ignore them.
- The alerting pipeline must itself be watched, or its failure is silent by
  construction.
- The strategy must improve: incidents that were missed or alerts that were
  noise must feed back into the rules.
- The substrate provides the structure and the conformance check; the
  organizational decisions (which SLOs, which rotation, how aggressive the
  escalation) belong to the consumer.

## Considered Options

The decision is not a single pick but a portfolio of sub-decisions, each of
which the consumer records in the ADR monitoring-alerting.alerting-strategy requires. For each, the
substrate states the recommended default and the trade-offs.

### Sub-decision 1: The detection-coverage philosophy

What it covers: what conditions the service alerts on at all. The substrate-
recommended philosophy is symptom-based and SLO-burn-based: alert on the
symptoms a user would feel (error rate, latency, unavailability of a core flow)
and on the rate at which the error budget for an SLO (observability.slo-policy) is burning,
rather than on every cause-level signal. The trade-off is that cause-based
alerting (a single host, a single saturated queue) catches problems earlier but
produces the noise that drives fatigue; symptom-based alerting is quieter and
catches what actually matters but can miss a slow-building cause before it
surfaces. The recommended resolution is to page on symptoms and SLO burn and to
keep cause-level signals as dashboard context and ticket-tier alerts, not pages.
This is the philosophy monitoring-alerting.detection-coverage coverage conforms to.

### Sub-decision 2: The severity-to-routing matrix

What it covers: how each severity maps to a destination. The substrate-
recommended matrix consumes the severity vocabulary observability.alerting-discipline defines (a
paging tier for human-now conditions, a ticket tier for work-soon conditions, a
record-only tier for log-only conditions) and routes each to a destination of
matching urgency: paging tier to a paging integration that notifies the on-call
responder, ticket tier to a work-item queue, record-only to a log sink. The
trade-off is granularity versus simplicity: more tiers express intent more
precisely but are harder to keep consistent. The recommended resolution is the
three-tier matrix unless the consumer has a demonstrated need for more. This is
the matrix monitoring-alerting.routing-and-escalation routing conforms to and monitoring-alerting.alert-route-resolves-to-receiver requires resolve to
real receivers.

### Sub-decision 3: The escalation and on-call model

What it covers: what happens when a page is not acknowledged, and who is on the
other end. The substrate-recommended model is a primary on-call with a defined
secondary, a bounded acknowledgement window after which an unacknowledged page
escalates to the secondary, and a documented rotation (monitoring-alerting.on-call-rotation-coverage) that covers
every hour with a handoff. The trade-off is responsiveness versus burden: a
short acknowledgement window and aggressive escalation catch a missed page fast
but raise the on-call burden and the risk of waking the secondary
unnecessarily. The recommended resolution is an acknowledgement window matched
to the service's incident-response expectations, with the rotation and handoff
recorded so coverage has no gap. This is the model monitoring-alerting.routing-and-escalation and monitoring-alerting.on-call-rotation-coverage
operate.

### Sub-decision 4: The alert lifecycle

What it covers: how an alert is operated from firing to resolution. The
substrate-recommended lifecycle is acknowledge (so responders do not duplicate
work), silence with a bounded expiry (monitoring-alerting.silence-carries-expiry, so a mute lapses rather than
becoming permanent), auto-resolve when the condition clears, and a resolution
notification to the firing destination. The trade-off is automation versus
control: auto-resolution keeps the alert state honest but can flap if the
condition oscillates around the threshold, which is mitigated by the
deduplication and grouping observability.alerting-discipline owns and by appropriate for-durations on
the rule. The recommended resolution is the full lifecycle with auto-resolution
and dedup. This is the lifecycle monitoring-alerting.alert-lifecycle conforms to.

### Sub-decision 5: The meta-monitoring approach

What it covers: who watches the watcher. The substrate-recommended approach is a
dead-man's-switch: a heartbeat alert that fires continuously under normal
operation and pages a destination external to the monitored pipeline precisely
when it stops arriving, so a pipeline failure is itself an alert rather than
silence. The trade-off is the dependency on an independent delivery path: the
heartbeat is only useful if its absence is delivered by something the failure
cannot also take down, which means a separate provider or a hosted check. The
recommended resolution is a heartbeat routed through an independent path. This
is the approach monitoring-alerting.pipeline-liveness-and-runbook-reachability conforms to.

### Sub-decision 6: The post-incident feedback loop

What it covers: how the strategy improves. The substrate-recommended loop is a
post-incident review that asks two questions of the alerting system: was the
incident detected by an alert (a no is a monitoring-alerting.detection-coverage coverage gap to close), and
did the alerts that fired help or add noise (noise is an observability.alerting-discipline hygiene
correction or a monitoring-alerting.alert-lifecycle lifecycle fix). The trade-off is process weight: a
heavy review per incident is thorough but unsustainable. The recommended
resolution is a lightweight, consistent review that feeds concrete changes back
into the rules. This is the loop the strategy closes and monitoring-alerting.detection-coverage coverage
benefits from.

### Sub-decision 7: Ownership and review cadence

What it covers: who owns the strategy and when it is revisited. The substrate-
recommended posture is a named owner for the alerting strategy and a periodic
review (at minimum quarterly, and after any significant incident) that re-checks
coverage, routing, escalation, lifecycle, and meta-monitoring against the
service as it has evolved. The trade-off is overhead versus drift: too frequent
a review is busywork, too infrequent lets the strategy fall behind the service.
The recommended resolution is a quarterly cadence plus an incident trigger.

## Decision Outcome

The consumer records an alerting-strategy ADR that resolves each of the seven
sub-decisions for their service. The substrate does not pick the consumer's
SLOs, rotation, or escalation timing; it requires that each sub-decision be
decided and written down so the L1 and L2 rules have a coherent policy to
conform to. An ADR that resolves sub-decisions 1 through 6 (with 7 as the
governance wrapper) satisfies monitoring-alerting.alerting-strategy. An ADR that leaves a sub-decision the
L2 rules depend on unstated is a monitoring-alerting.alerting-strategy finding: the coverage philosophy
anchors monitoring-alerting.detection-coverage, the routing matrix anchors monitoring-alerting.routing-and-escalation, the escalation and
on-call model anchors monitoring-alerting.routing-and-escalation and monitoring-alerting.on-call-rotation-coverage, the lifecycle anchors
monitoring-alerting.alert-lifecycle, and the meta-monitoring approach anchors monitoring-alerting.pipeline-liveness-and-runbook-reachability.

## Substrate Alignment

This framework is the policy the monitoring-alerting conformance rules conform
to. monitoring-alerting.alert-route-resolves-to-receiver (route resolves to a receiver) and monitoring-alerting.silence-carries-expiry (suppression
carries an expiry) are the mechanical floors beneath the routing matrix and the
lifecycle. monitoring-alerting.detection-coverage through monitoring-alerting.on-call-rotation-coverage are the semantic conformance checks for
coverage, routing and escalation, lifecycle, pipeline liveness, and on-call
coverage. The framework consumes rather than restates the observability
decisions it depends on: observability.alerting-discipline owns the per-alert-rule hygiene (severity
label, runbook link, summary, deduplication) and observability.slo-policy owns the SLO
selection and error-budget policy the coverage philosophy alerts on. It
references the reliability health signals (reliability.health-signaling) as an input it may alert
on. The seam is alerting-operations versus signals-and-hygiene; this framework
owns the operations layer observability defers to it.

## Consequences

Positive: a service with a recorded alerting strategy has a coherent on-call
experience, detects incidents before users do, reaches a human reliably, and
improves its alerts over time. The strategy makes the otherwise-implicit
operational decisions reviewable and gives the conformance rules a policy to
check against.

Negative or costs: authoring and maintaining the ADR is real work, and the
strategy must be kept current as the service evolves or it becomes a stale
document that the rules conform to in name only. The quarterly-plus-incident
review cadence is the mitigation. The strategy also depends on the
observability investment (signals, hygiene, SLOs) being in place; an alerting
strategy on top of poor signals inherits their gaps.

## References

- Google SRE Book, Chapter 6 Monitoring Distributed Systems (the golden signals
  and symptom-based monitoring), referenced as concepts.
- Google SRE Book, Chapter 6 Practical Alerting (routing, escalation, and
  monitoring the monitoring system), referenced as concepts.
- Google SRE Book, Chapter 11 Being On-Call (the rotation, coverage, and
  handoff), referenced as concepts.
- Google SRE Workbook, Alerting on SLOs (burn-rate alerting), referenced as a
  concept.
- Prometheus Alerting Best Practices (the dead-man's-switch heartbeat),
  referenced as a concept.
- MADR (adr.github.io/madr), the decision-record format this framework uses.

All sources are referenced as public concepts; no verbatim text from any source
appears in this framework.

## Decision Review Schedule

The consumer's alerting-strategy ADR is reviewed at minimum quarterly and after
any significant incident, per sub-decision 7. This substrate framework is
reviewed at each milestone close and whenever the observability concern's
observability.alerting-discipline or observability.slo-policy changes in a way that affects the operations layer that
depends on them.
