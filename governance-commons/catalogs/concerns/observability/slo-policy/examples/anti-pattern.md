<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.slo-policy SLO and error budget policy (anti-patterns)

Substrate-original anti-pattern examples for observability.slo-policy.

## Anti-pattern A: Aspirational SLO with no numeric target

```markdown
# ADR-009: payments-api SLO

We aim for high availability of the payments-api service.
The team will work to keep error rates low and response
times fast. When customer-facing issues occur, we will
respond promptly.

## SLI
The service should be reliable.

## SLO target
High availability and good performance.

## Error budget policy
We will be careful when reliability is at risk.
```

Why this violates observability.slo-policy: every required section is
present in name only. The SLI is not specified ("be
reliable" is not a signal). The target is not numeric
("high availability" is not measurable). The budget policy
is aspirational ("be careful"). Engineers cannot compute
whether the SLO is being met; on-call cannot invoke a
burndown response because there is no threshold to cross.

Remediation: see the good-pattern ADR for the substrate-
required content. Every section needs substantive
operational content.

## Anti-pattern B: SLI reflects operator convenience not customer experience

```markdown
## SLI for payments-api
- Database connection pool utilization stays below 80 percent
- p99 query latency in the payments-database stays below 100ms
- API server CPU utilization stays below 70 percent
```

Why this violates observability.slo-policy: every SLI is an operator-
convenience metric, not a customer experience signal. A
service can have healthy connection pool utilization and
healthy CPU utilization while customers experience failed
payments (the SLIs miss the customer-facing failure modes).
The SLO passes; customers are unhappy; executives lose
confidence in the SLO mechanism when they discover the gap.

Remediation: select SLIs that reflect what customers
observe. The good-pattern ADR uses request success ratio
and p99 latency, both directly customer-felt. Operator-
convenience metrics belong on dashboards, not in the SLI.

## Anti-pattern C: Error budget without burndown response

```markdown
## Error budget
We have a budget of 43 minutes per month at 99.9 percent
availability.

## Budget burndown response
The team is aware of the budget and considers it when
planning reliability work.
```

Why this violates observability.slo-policy: the error budget exists as a
number on a dashboard but is not operationally binding. No
threshold triggers a documented action. Feature work
continues at the same pace regardless of budget consumption;
in retrospect, the team discovers the budget was exhausted
and "considered" did not translate into changed work
allocation.

Remediation: the burndown response must be a graduated
table with explicit actions at explicit thresholds (good-
pattern Pattern B example). The substrate-recommended
escalation: the team should be able to point to past
quarters where the policy was invoked.

## Anti-pattern D: SLI computation not connected to instrumentation

```markdown
## SLI for payments-api: request success ratio

Computed from the payments service health check.

## Target: 99.9 percent monthly
```

Why this violates observability.slo-policy: the SLI is theoretically
specified but no actual instrumentation produces the data.
The "payments service health check" is a once-per-minute
ping that returns 200 if the process is running; it does
not reflect request success ratio. The ADR's SLI definition
and the actual telemetry are disconnected; the SLI metric
on the dashboard is a fiction.

Remediation: cross-reference specific metrics with names
and label sets; verify the metrics exist via observability.metric-naming-convention
naming and observability.semantic-convention-coverage semantic-convention coverage; verify
the metrics' cardinality is stable via observability.cardinality-discipline. The
good-pattern ADR shows the explicit cross-reference.

## Anti-pattern E: Measurement window mismatched with alerting

```markdown
## SLO target
99.9 percent over the calendar month.

## Alerting
- Page on error rate above 1 percent for 5 minutes.
```

Why this violates observability.slo-policy: the SLO uses calendar-month
windows, but the alerting uses a fixed threshold (1 percent
for 5 minutes) that is not derived from the SLO. The result:
the alert fires whenever error rate exceeds 1 percent
regardless of budget state. Late-month low traffic produces
high noise; high-traffic mid-month allows substantial budget
consumption without firing.

Remediation: derive burn-rate alerting from the SLO and
window (good-pattern Pattern B example in observability.alerting-discipline).
The substrate-recommended pattern is multi-window burn-
rate alerts whose thresholds are derived from the SLO
target and budget consumption math.

## Anti-pattern F: ADR predates substrate framework, never reviewed against it

The team authored an SLO ADR in 2024 (before the substrate
v0.3.0 release that includes the observability concern).
The ADR has not been updated; it does not reference the
substrate framework; it does not address several substrate-
required sections (no explicit burn-rate alerting integration;
no review cadence documented).

Why this violates observability.slo-policy: the ADR was acceptable at
the time of authoring but has not been reconciled with the
substrate's current requirements. The annual review (or
the new-substrate-version trigger) should have caught this.

Remediation: review the ADR against the current substrate
framework; update missing sections; document the version
of the substrate framework the ADR now aligns to. Future
substrate framework version updates are review triggers.

## Anti-pattern G: Burndown policy never invoked despite budget burndown

The ADR documents a graduated burndown response policy
(feature freeze at 10 percent budget remaining). The
service exhausted its budget in three consecutive months
last quarter. The feature freeze was never invoked; feature
work continued at the same pace. The team's quarterly
retrospective did not address the gap.

Why this violates observability.slo-policy: the policy exists but is not
authoritative. The SLO mechanism's credibility is undermined
when the documented response is not followed. Future
authoring of SLO ADRs in the consumer's catalog inherits
the same credibility gap: engineers learn that the burndown
policy is decorative rather than binding.

Remediation: re-establish the policy as authoritative;
invoke it explicitly on the next budget pressure event;
include policy-invocation status in the consumer's
operational reporting so the gap cannot reproduce silently.

## Cross-reference

- Substrate rule: observability.slo-policy in catalogs/concerns/observability.oscal.yaml
- Decision framework: decision-frameworks/observability-slo-policy.madr.md
- Review checklist: checklist.md
- Good-pattern examples: examples/observability/slo-policy-good.md
