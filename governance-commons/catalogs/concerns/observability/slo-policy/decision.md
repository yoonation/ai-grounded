---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: observability.slo-policy
title: "SLO Selection and Error Budget Policy"
lifecycle-status: stable
commons-version: "0.4.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-21"
entered-status-at: "2026-05-22"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
ai-assistance: "AI drafted from substrate-author intent following the logging-architecture.madr.md precedent; fourth decision framework authored in the substrate; exercises the established MADR pattern for the observability concern. SPDX header placed as YAML comments inside frontmatter per Section 10 settled decision 15. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft."
authoritative-sources:
  - "https://sre.google/workbook/implementing-slos/"
  - "https://sre.google/workbook/alerting-on-slos/"
  - "https://sre.google/workbook/error-budget-policy/"
  - "https://opentelemetry.io/docs/specs/semconv/"
  - "https://www.w3.org/TR/trace-context/"
  - "https://prometheus.io/docs/practices/alerting/"
  - "https://adr.github.io/madr/"
---

# SLO Selection and Error Budget Policy

This decision framework provides the substrate's analysis of
SLO selection and error budget policy options. Consumers
reference this framework when authoring their own ADR
documenting their service's reliability commitments and budget
policy. The substrate-recommended location for the consumer's
ADR is `/docs/decisions/ADR-XXX-observability-slo-policy.md`.

The framework is referenced by substrate rule observability.slo-policy, which
requires services to have an explicit, documented SLO selection
and error budget policy before exiting their initial reliability
soak period. Consumers satisfy observability.slo-policy by authoring an ADR
that adapts the analysis in this framework to their service
context.

## Context

SLO selection is a service-level concern with four interlocking
decisions: SLI choice (which signals reflect customer
experience), SLO target (the numeric reliability commitment),
measurement window (the rolling period over which SLO is
computed), and error budget burndown response (what the team
does when the budget is consumed). Each decision affects the
others. Choosing the SLI without considering the alerting
cadence forces re-engineering of the alerting strategy
(observability.alerting-discipline); choosing the SLO target without instrumentation
discipline produces an SLI that is not actually computable
(OBS-L1 and OBS-L2 cross-rules); choosing the measurement
window incompatibly with the alerting cadence breaks burn-rate
alerting.

The substrate-recommended pattern is to make all four
decisions together as a single architectural choice, document
the decision in an ADR before the service exits its initial
reliability soak period, and revisit annually or on triggers
(significant architecture change, major customer commitments,
significant budget burndown event).

The choice has implications across every subsequent OBS-L2
rule. Semantic-convention coverage (observability.semantic-convention-coverage) supplies the
attribute set the SLI computation depends on. Cardinality
discipline (observability.cardinality-discipline) keeps the SLI computation stable as
load grows. Alerting discipline (observability.alerting-discipline) implements burn-
rate alerting against the chosen SLI, target, and window.
Dashboard discipline (observability.dashboard-discipline) renders the SLI panel set
the team and stakeholders consume.

Common substrate failure modes:

- Teams adopt aspirational SLOs that never materially affect
  team behavior. The SLO is a number on a dashboard rather
  than a decision input; the error budget burndown response is
  not invoked even when the budget is exhausted.
- Teams choose SLIs that reflect operator convenience (CPU
  utilization, request count) rather than customer experience
  (success rate, latency, freshness). The SLO passes while
  customers are unhappy.
- Teams set SLO targets borrowed from peer services without
  examining the customer commitments and operational maturity
  that justified those targets in the original context.
- Teams treat the error budget as a soft signal, not a budget.
  Feature work continues at the same pace regardless of
  burndown; the budget policy is invoked only in retrospect
  during post-incident review.

The substrate provides analysis of each viable option but does
not prescribe a single answer. Consumers select based on their
context. The substrate requires the choice to be documented
and reasoned; it does not require consumers to choose the
substrate-preferred option for their context.

## Decision Drivers

The substrate identifies the following drivers that should
inform the SLO selection. Consumers may add service-specific
drivers but should address each substrate driver in their ADR.

- **D1. Customer commitments.** Whether the service has
  external commitments (SLAs in customer contracts, regulatory
  requirements implying specific reliability, product
  positioning statements about reliability). External
  commitments tighten the SLO target floor and may dictate
  the measurement window (regulatory reports often use
  calendar-month windows).

- **D2. Customer experience signals.** Which signals the
  customer actually feels: latency for synchronous APIs,
  success rate for transactional operations, freshness for
  data pipelines, availability for dependencies the customer
  observes. The SLI choice must reflect signals the customer
  experiences, not signals the operator finds convenient to
  measure.

- **D3. Operational maturity.** Whether the team can sustain
  an SLO commitment with the team's current operational
  capacity. Tight SLOs require fast incident response, deep
  instrumentation, mature on-call rotation, and rigorous
  post-incident review. Teams without these capabilities
  produce aspirational SLOs that erode the credibility of the
  SLO mechanism.

- **D4. Service criticality tier.** Where the service sits in
  the consumer's service catalog by criticality. Top-tier
  customer-facing services warrant the strictest SLOs and the
  most disciplined budget policies. Internal supporting
  services warrant looser SLOs with proportional policy.

- **D5. Architectural dependency depth.** Services with many
  upstream dependencies have ceiling reliability bounded by
  the product of dependency reliabilities. SLOs that exceed
  the ceiling are mathematically impossible. The SLO target
  must respect the dependency structure.

- **D6. Cost of reliability investment.** Each additional
  9 of availability typically requires substantial investment
  (redundancy, failover, capacity headroom). The SLO target
  should reflect a deliberate cost-benefit analysis, not an
  aspirational round number.

- **D7. Alerting cadence requirements.** The measurement
  window interacts with burn-rate alerting configuration
  (observability.alerting-discipline). A 28-day rolling window pairs with substrate-
  recommended multi-window burn-rate alerts; a calendar-month
  window has different burn-rate implications. The two must
  be designed together.

## Considered Options

The substrate-recognized options span SLI selection patterns,
SLO target shapes, measurement window choices, error budget
computation methods, and budget burndown response policies.

### SLI selection options

#### Option A1: Request success ratio

**Substrate preference:** Substrate-preferred for synchronous
request-driven services (HTTP, gRPC).

**Applicable when:** Service handles discrete user-facing
operations whose success or failure is observable per
operation; the success criterion is unambiguous (a non-5xx
status code; an absence of explicit error markers in gRPC
trailers).

**Pros:**
- Maps directly to a customer observation (their request
  worked or did not)
- Computable from RED-organized dashboard data
  (observability.dashboard-discipline)
- Pairs cleanly with burn-rate alerting (observability.alerting-discipline)

**Cons:**
- Defines "success" requires care; some 5xx responses are
  consumer errors miscategorized; some 2xx responses carry
  application-level failures in payload
- Does not capture latency: a service that returns successful
  responses at 30-second p99 latency passes a success-ratio
  SLO while failing customer experience
- Requires composition with latency for full coverage of
  customer experience

#### Option A2: Latency at chosen percentile

**Substrate preference:** Substrate-preferred as a companion
to request success ratio for synchronous request-driven
services where latency is part of customer experience.

**Applicable when:** Latency is a material customer experience
signal (the customer feels the difference between 100ms and
2000ms response time); the service can be instrumented to
capture per-request latency.

**Pros:**
- Captures user-felt time that success ratio does not
- Computable from histogram metrics (cross-reference
  observability.metric-naming-convention metric naming convention with _seconds suffix)
- Percentile choice (p95, p99, p99.9) lets the consumer
  tune sensitivity to tail behavior

**Cons:**
- Percentile choice is opinionated; the substrate does not
  prescribe a default percentile because the right choice
  depends on the service's customer expectations
- Histogram bucket boundaries affect measurement accuracy at
  the percentile of interest; choosing the wrong bucket
  layout produces a percentile that is mathematically
  imprecise
- Latency SLOs require the latency distribution be well-
  characterized; novel services may need a soak period before
  setting a meaningful target

#### Option A3: Availability of dependencies

**Substrate preference:** Substrate-preferred for composite
services where customer experience is the product of many
underlying availabilities.

**Applicable when:** The service's customer experience depends
on a known dependency set; the dependencies have their own
observable availability; the composite question (is the
service usable given all required dependencies?) is the
operational question.

**Pros:**
- Captures composition the customer experiences
- Provides a tool for the consumer's service catalog to
  reason about reliability propagation

**Cons:**
- Requires accurate dependency mapping; mapping drifts as
  the service evolves
- Composite SLI computation can be opaque to operators not
  familiar with the composition
- Failure modes in composition (silent dependency degradation
  not affecting availability ratio) escape the SLI

#### Option A4: Freshness for data pipeline services

**Substrate preference:** Substrate-preferred for data
pipeline services where customer experience is driven by data
recency rather than per-request synchronous reliability.

**Applicable when:** The service produces or refreshes data
that downstream consumers query; customer experience depends
on the data being fresh enough.

**Pros:**
- Maps to a customer-observable signal for data services
- Captures the dominant failure mode (stale data) that
  request-driven SLIs miss

**Cons:**
- Freshness definition requires consumer commitment (what
  counts as stale?)
- Instrumentation for freshness requires the service emit
  a freshness signal explicitly (timestamp of last refresh
  per data partition)

### SLO target shape options

#### Option B1: Aspirational target

**Substrate preference:** Substrate-discouraged for production
services.

**Applicable when:** Service is in initial reliability soak
period; the team is calibrating instrumentation; the SLO is
explicitly transitional and will be replaced.

**Pros:**
- Lets the team set a directional target without committing
  to a measurable one

**Cons:**
- Erodes the SLO mechanism's credibility when the aspirational
  target is missed without consequence
- Becomes the de facto SLO if not replaced before the soak
  period ends
- Does not support the error budget burndown response policy

#### Option B2: Commitment-driven target

**Substrate preference:** Substrate-preferred for production
services.

**Applicable when:** The service has external commitments
(SLAs, regulatory, product positioning); the team is prepared
to take operational action when the SLO is at risk.

**Pros:**
- Operationally meaningful: missing the target has
  consequence
- Anchors customer commitment in a measurable form
- Supports rigorous error budget burndown response

**Cons:**
- Requires the team to operationally respect the SLO; a
  commitment-driven SLO without a respected budget policy is
  worse than an aspirational SLO (it creates a credibility
  gap)
- Setting the target requires understanding of the achievable
  reliability ceiling given dependencies and operational
  maturity

#### Option B3: Tiered SLOs by service tier

**Substrate preference:** Substrate-preferred for consumers
with a service catalog with explicit tiers.

**Applicable when:** Consumer has more than one service and
the services have different criticality; the consumer's
operational and engineering practices are differentiated by
tier.

**Pros:**
- Reflects the consumer's actual operational reality
- Avoids the trap of treating every service as top-tier
- Lets internal services run at lower SLOs without erosion
  of the customer-facing SLO discipline

**Cons:**
- Requires the consumer's service catalog to be explicit
  about tier; many consumers operate without an explicit
  tier model
- Tier classification is its own substrate-driver-style
  decision that the consumer must make rigorously

### Measurement window options

#### Option C1: Rolling 28-day window

**Substrate preference:** Substrate-preferred default.

**Applicable when:** The consumer's executive reporting and
incident response cadence both align with a rolling window;
burn-rate alerting at multi-window cadence is the substrate-
recommended alerting pattern.

**Pros:**
- Pairs cleanly with the substrate-recommended burn-rate
  alerting configuration (1-hour and 6-hour windows)
- Smooths short-term variance
- Does not have the calendar-month "fresh budget on the 1st"
  failure mode

**Cons:**
- Does not align with calendar-month executive reporting if
  the consumer's reporting cadence is monthly
- Investigation of historical SLO compliance requires
  rolling-window math

#### Option C2: Calendar month

**Substrate preference:** Substrate-acceptable when the
consumer's executive reporting is calendar-month.

**Applicable when:** Consumer reports SLO compliance to
external parties on a calendar-month basis; the consumer can
accept the "fresh budget on the 1st" pattern.

**Pros:**
- Aligns with calendar-month executive reporting
- Each month produces a clean comparable number

**Cons:**
- "Fresh budget on the 1st" produces a predictable end-of-
  month risk pattern: teams take more reliability risk early
  in the month when budget is full, drive incidents toward
  end of month
- Multi-window burn-rate alerting math is less clean with
  calendar windows

#### Option C3: Custom window

**Substrate preference:** Substrate-acceptable when the
consumer has a specific reporting commitment requiring a
custom window.

**Applicable when:** Regulatory or contractual reporting
requires a window other than rolling 28-day or calendar
month.

**Pros:**
- Matches the consumer's external reporting commitment

**Cons:**
- Burn-rate alerting configuration must be derived for the
  custom window
- Tooling and dashboard templates may not support the custom
  window without configuration

### Error budget computation options

#### Option D1: Simple ratio computation

**Substrate preference:** Substrate-preferred for most
services.

**Applicable when:** The SLI is a ratio of good events to
total events; the SLO is a ratio target; computation is
straightforward.

**Pros:**
- Easy to reason about
- Easy to compute from PromQL or vendor query language

**Cons:**
- Does not weight by event severity or customer impact
- Treats a degraded experience the same as a failed
  experience

#### Option D2: SLI-weighted computation

**Substrate preference:** Substrate-acceptable for services
where different SLI components have different customer impact
weights.

**Applicable when:** The service has multiple SLIs with
materially different customer impact; the consumer can
defensibly assign weights.

**Pros:**
- Aligns budget consumption with customer impact
- Lets the team prioritize remediation by impact rather
  than by frequency

**Cons:**
- Weights are opinionated and require defense
- Computation is harder to explain to non-engineering
  stakeholders
- Weight changes require ADR amendments

### Error budget burndown response policy options

#### Option E1: Strict feature freeze at threshold

**Substrate preference:** Substrate-preferred for top-tier
production services.

**Applicable when:** The team is prepared to operationally
respect the freeze; the engineering culture supports stopping
feature work in response to a budget signal.

**Pros:**
- Strongest possible signal that reliability is the
  consequence of feature work pace
- Aligns engineering effort with the budget mathematically
- Makes the SLO commitment materially binding

**Cons:**
- Requires organizational support; a freeze that is not
  respected damages the credibility of the SLO mechanism
- Can be overcorrective if the budget burndown was driven
  by an external event (a single major incident) rather
  than systemic pace

#### Option E2: Tiered escalation

**Substrate preference:** Substrate-preferred for services
where strict freeze is operationally impractical.

**Applicable when:** The consumer can sustain a tiered
response (slow feature work at 50 percent budget remaining;
significantly slow at 25 percent; pause at 10 percent;
escalate at 0); the team has authority to invoke each tier.

**Pros:**
- Smooth response curve avoids the overcorrection of strict
  freeze
- Lets the team triage between feature work and reliability
  work continuously rather than at a single threshold

**Cons:**
- Less mathematically clean than strict freeze
- Requires more discipline from the team to act on each
  tier rather than only the strictest

#### Option E3: Product owner engaged escalation

**Substrate preference:** Substrate-recommended addition to
either E1 or E2.

**Applicable when:** The service has a product owner; the
product owner is empowered to negotiate scope when budget is
under pressure.

**Pros:**
- Brings the customer commitment owner into the budget
  conversation
- Lets product-side trade-offs (which features can be
  deferred to restore budget) be made explicitly rather
  than by engineering unilaterally

**Cons:**
- Requires product owner alignment with the SLO mechanism;
  uninformed product owners may invoke their authority to
  override the budget signal

## Decision Outcome

The substrate-recommended position for a typical request-
driven service in a mature consumer organization:

- **SLI:** Composite of request success ratio (Option A1) and
  latency at p99 (Option A2). Both signals together capture
  customer experience that either alone misses.
- **SLO target shape:** Commitment-driven (Option B2), tiered
  by service tier (Option B3) where the consumer has tiering.
- **Measurement window:** Rolling 28-day (Option C1).
- **Error budget computation:** Simple ratio (Option D1)
  unless the SLI composition requires weighting.
- **Burndown response:** Tiered escalation (Option E2) with
  product-owner-engaged escalation (Option E3) layered on
  top.

This is the substrate's default recommendation. Consumers
should treat it as a starting point and tailor based on the
drivers above.

## Substrate Alignment

The decisions in this framework intersect every other
observability rule:

- observability.no-sensitive-data-in-telemetry (no sensitive data in telemetry) governs the
  span attributes the SLI computation can reference;
  cardinality discipline in observability.cardinality-discipline keeps the SLI metric
  emission stable.
- observability.trace-context-propagation (trace context propagation) enables cross-
  service SLI computation in composite services.
- observability.metric-naming-convention (metric naming convention) and observability.semantic-convention-coverage
  (semantic convention coverage) supply the metric vocabulary
  the SLI queries use.
- observability.alerting-discipline (alerting discipline) implements burn-rate
  alerting against the SLO; the window choice in this
  framework determines the alerting configuration.
- observability.dashboard-discipline (dashboard discipline) renders the SLI dashboard;
  the SLI choice in this framework determines the panel set.

A consumer ADR satisfying observability.slo-policy references both this
framework and the consumer's specific positions on each
section above.

## Consequences

The decisions made under this framework cascade as follows:

- **For instrumentation:** the SLI choice determines which
  metrics and spans must be emitted, with what attributes,
  at what cardinality. Underestimating instrumentation cost
  is a recurring failure mode; the substrate recommends
  treating instrumentation as a first-class cost of the SLO
  commitment.
- **For alerting:** the measurement window choice constrains
  the burn-rate alerting configuration. A 28-day window pairs
  with substrate-recommended 1-hour and 6-hour burn-rate
  alerts; a calendar-month window requires custom alerting
  math.
- **For team operations:** the burndown response policy
  determines what happens to the team's work allocation when
  the budget is consumed. The policy is binding on the
  engineering team and on the product organization; ADR
  authoring should involve both.
- **For executive reporting:** the SLO target and measurement
  window choice determines what the team reports outward.
  Aligning the ADR with the consumer's existing executive
  reporting cadence reduces friction.

## References

- Google SRE Workbook: Implementing SLOs, Alerting on SLOs,
  Error Budget Policy (copyrighted; substrate references
  concepts without reproducing text)
- OpenTelemetry Semantic Conventions
- W3C Trace Context Recommendation
- Prometheus Alerting Best Practices
- MADR (Markdown Any Decision Records) format

## Decision Review Schedule

The substrate-recommended cadence for reviewing the
consumer's ADR derived from this framework:

- **Annual:** full review of SLI choice, SLO target,
  measurement window, error budget computation, and burndown
  response. The annual review reconfirms each choice against
  current drivers.
- **Triggered:** significant architecture change affecting
  reliability characteristics; major customer commitments
  implying specific reliability targets; significant budget
  burndown event requiring policy invocation; substantial
  growth in dependency depth or service criticality tier.
- **Quarterly light-touch:** confirm the SLI computation is
  still producing meaningful data; confirm the alerting
  configuration still matches the measurement window;
  confirm the burndown response policy is still authoritative
  (the team has invoked it, or has not had cause to invoke
  it, as appropriate).

This framework itself is reviewed by the substrate-author on
the substrate's MADR review cadence; framework version
increments propagate to consumer ADRs on the consumer's next
annual review.
