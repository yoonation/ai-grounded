---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: reliability.reliability-strategy
title: "Reliability Strategy: Failure Modes, Dependency Criticality, Delivery Semantics, Isolation, Health, and Degradation"
lifecycle-status: stable
commons-version: "0.6.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M4 close consolidation (2026-06-01) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M4 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-01. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with reliability.reliability-strategy substrate rule. Portfolio-of-sub-decisions structure mirroring the code-organization-strategy and error-handling-strategy MADR precedents: six sub-decisions (failure-mode catalog, dependency-criticality classification, delivery and idempotency semantics, resource-isolation model, health-and-recovery model, degradation policy) plus a review cadence, rather than a single option pick. Draft lifecycle per M4 Session 3; stable promotion at M4 close."
authoritative-sources:
  - "https://en.wikipedia.org/wiki/Fault_tolerance"
  - "https://en.wikipedia.org/wiki/Reliability_engineering"
  - "https://en.wikipedia.org/wiki/Bulkhead_(software)"
  - "https://en.wikipedia.org/wiki/Idempotence"
  - "https://en.wikipedia.org/wiki/Graceful_degradation"
  - "https://en.wikipedia.org/wiki/Circuit_breaker_design_pattern"
  - "https://en.wikipedia.org/wiki/Health_check"
  - "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.error-handling-strategy
  - decision-frameworks.observability-slo-policy
---

# Reliability Strategy: Failure Modes, Dependency Criticality, Delivery Semantics, Isolation, Health, and Degradation

## Context and Problem Statement

Every networked service has a reliability strategy. The only choice is
whether it is decided and written down or left to accrete from whatever
resilience each author happened to remember to add. reliability.reliability-strategy requires
that the strategy be explicit, because it is the anchoring decision the
rest of the reliability concern depends on: the four L2 rules are each
conformance checks, and what they conform to is precisely this strategy.
Idempotency (reliability.idempotency) is judged against the declared delivery
semantics; graceful degradation (reliability.graceful-degradation) against the dependency-
criticality classification; failure isolation (reliability.failure-isolation) against the
failure-domain map; health signaling (reliability.health-signaling) against the health-
and-recovery model. The three L1 rules are sized and shaped by the same
decision: a queue bound (reliability.bounded-buffers) follows from how much in-flight
work the strategy tolerates, and background-task supervision (reliability.tracked-async-tasks)
follows from whether a task's loss is survivable.

This framework is also where the boundary with error-handling is held.
Error-handling governs the per-call-site resilience triad of bounded
retry, timeout, and circuit breaker (error-handling.retry-and-circuit-breaker). Reliability does not
restate those mechanisms; it governs the system-level properties that
make them survivable: that the operations the retries target are safe to
repeat, that a tripped breaker degrades a feature rather than the
request, that one slow dependency cannot exhaust shared resources, and
that the orchestrator can tell whether an instance should receive
traffic. The strategy records the decisions; the mechanisms implement
them. A service whose reliability is the unplanned sum of scattered
reflexes survives only the failures its authors happened to anticipate.

The substrate does not prescribe a single reliability target. It requires
that the target be chosen, written down, and propagated into the rules
that hold the service to it. The sub-decisions below structure that
choice.

## Decision Drivers

The reliability target is driven by the cost of unavailability (a payment
path and an internal analytics job warrant different investment), the
tolerance for data loss (whether a dropped or duplicated message is
acceptable), latency sensitivity (whether a slow degraded response beats
a fast error), the operational maturity of the team (what they can run
and observe), the reliability of the dependencies themselves (a flaky
third party forces decisions a rock-solid internal one does not), and the
deployment topology (a single instance, a replicated fleet, an
orchestrated platform). These drivers are weighed per service rather than
fixed by the substrate.

## Considered Options

The strategy is not a single pick from a menu; it is a portfolio of six
sub-decisions, each with its own option space. The substrate analyzes
each; the consumer's ADR records the choices and their drivers.

### Sub-decision 1: Failure-mode catalog (what the service survives)

The first decision is which failures the service is designed to survive
and which it explicitly is not. The option space ranges from minimal
(survive a single dependency timeout and a single instance loss) through
moderate (survive a zone outage, a dependency being down for minutes,
a traffic spike of some multiple) to extensive (survive a region loss, a
prolonged dependency outage, correlated failures). The substrate's
guidance is that the out-of-scope list matters as much as the in-scope
one: naming the failures the service is not built to withstand is what
prevents false confidence and tells operators where manual response is
the plan. Each in-scope failure is paired with its designed-for response,
which the later sub-decisions detail.

### Sub-decision 2: Dependency-criticality classification

Each cross-process dependency is labeled critical (the request cannot
succeed without it), degradable (the request can return a useful partial
result without it), or optional (its loss is invisible to the user). The
option space is not the labels but the discipline: classify every
dependency explicitly, or classify none and treat all as critical by
default. The substrate strongly favors explicit classification, because
the default-critical posture is the single most common cause of a minor
dependency taking down a major path, and because this classification is
the reference that reliability.graceful-degradation degradation checks against. The
classification records, per dependency, the request-level consequence of
its loss and the chosen response.

### Sub-decision 3: Delivery and idempotency semantics

For each retryable path or message flow, the strategy declares the
delivery guarantee: at-most-once (a failure may drop the operation, never
duplicate it), at-least-once (a failure may duplicate it, never drop it),
or exactly-once-in-effect (at-least-once delivery made safe by idempotent
effects). The substrate's guidance is to prefer at-least-once delivery
with idempotent consumers over relying on a broker's exactly-once claim,
because exactly-once delivery is a strong guarantee few systems truly
provide end to end, whereas idempotent effects are achievable locally and
compose. This sub-decision is what reliability.idempotency checks conformance to, and
it determines where idempotency keys are required.

### Sub-decision 4: Resource-isolation model

The strategy names the failure domains and the boundaries between them:
which work shares a thread pool, connection pool, or concurrency limit,
and where bulkheads separate critical from non-critical or fast from
slow. The option space ranges from a single shared pool (simplest, but a
slow dependency can starve everything) through per-criticality pools
(critical work isolated from degradable) to per-dependency pools
(maximum isolation, more capacity to manage). The substrate's guidance is
that the isolation investment should track the failure-mode catalog: a
service designed to survive a slow dependency must isolate that
dependency's resource consumption. This model is what reliability.failure-isolation checks
against, and it is where the reliability.bounded-buffers buffer-bound sizes and
reliability.tracked-async-tasks supervision shapes are justified.

### Sub-decision 5: Health-and-recovery model

The strategy decides, for orchestrated services, what liveness and
readiness each gate on and how the service recovers after a dependency
heals. The settled substrate position, reflecting broad orchestrator
guidance, is that liveness checks only process responsiveness and never
dependencies (so a dependency outage cannot trigger a restart storm),
while readiness gates on the critical dependencies from sub-decision 2
(so traffic routes away from an instance that cannot serve) and recovers
automatically when they return. Slow startup is signaled distinctly from
failure. This model is what reliability.health-signaling checks the probes against. For
non-orchestrated deployments the sub-decision records the equivalent
self-healing and traffic-control mechanism, or records that it is out of
scope.

### Sub-decision 6: Degradation policy

For each degradable dependency from sub-decision 2, the strategy records
the user-visible behavior when it is unavailable: serve a cached value,
serve a default, omit a section, disable a feature. The option space is
the choice of fallback per dependency and whether the fallback triggers
on failure only or on slowness as well. The substrate's guidance is that
degradation must be bounded in time (a hung optional dependency is worse
than a failed one, so fallbacks trigger on slow as well as failed) and
observable (a silent degradation hides an ongoing outage). This is the
behavior reliability.graceful-degradation checks; it is the product-level complement to the
circuit breaker that error-handling.retry-and-circuit-breaker provides as the mechanism.

## Decision Outcome

The consumer's ADR records, for the specific service: the failure-mode
catalog with in-scope and out-of-scope failures; the dependency-
criticality classification with a response per dependency; the delivery
and idempotency semantics per retryable path; the resource-isolation
model with named failure domains; the health-and-recovery model; and the
degradation policy per degradable dependency. The substrate does not
dictate the choices; it requires that each sub-decision be made
explicitly and propagated into the L1 and L2 rules. A complete ADR is one
from which a reviewer applying the RELY-L2 and RELY-L3 checklists can
verify that the enforced gates match the recorded decisions.

## Substrate Alignment

This framework pairs with reliability.reliability-strategy and is the reference the rest of
the reliability concern conforms to. Sub-decision 2 is the classification
reliability.graceful-degradation checks; sub-decision 3 is the semantics reliability.idempotency checks;
sub-decision 4 is the map reliability.failure-isolation checks and the justification for the
reliability.bounded-buffers bound sizes and reliability.tracked-async-tasks supervision shapes; sub-decision
5 is what reliability.health-signaling checks the probes against; sub-decision 6 is the
behavior reliability.graceful-degradation checks. The framework holds the error-handling
boundary explicitly: error-handling.retry-and-circuit-breaker owns the per-call-site retry, timeout,
and circuit-breaker mechanisms, and this strategy owns the system-level
properties (idempotency, isolation, degradation, health) that make those
mechanisms survivable. It holds the observability boundary too: the
health probe contract and its control-plane effect are reliability, while
the metrics and alerts derived from health belong to the observability
SLO policy, with which this framework is a related decision.

## Consequences

A documented reliability strategy makes the L1 and L2 reviews concrete
and turns reliability from an aspiration into a checkable property. The
cost is the up-front analysis: classifying every dependency, naming
failure domains, and deciding delivery semantics is real work that a
small service may feel is heavy. The substrate's position is that the
analysis is cheaper than the incident it prevents, and that for a genuinely
trivial service the ADR is correspondingly short (few dependencies, a
short failure-mode catalog) rather than absent. A risk is that the ADR is
written once and drifts from the code; the review cadence below and the
question-6 enforcement check in the reliability.reliability-strategy checklist exist to keep
the recorded decision and the enforced gates in agreement.

## References

The authoritative sources in the frontmatter cover fault tolerance and
reliability engineering as the discipline, the bulkhead and circuit-
breaker patterns, idempotence and graceful degradation as the techniques,
health-check and container-probe semantics for the health-and-recovery
model, and MADR as the record format. The substrate references these by
URL and reproduces none of their text.

## Decision Review Schedule

The reliability strategy is reviewed when a new service is created or an
existing one crosses into traffic whose loss carries real cost; when a
new critical dependency is added or an existing dependency's criticality
changes; on a topology shift (adding a queue, splitting a service, adding
a cache to the request path); after any incident whose post-mortem finds
the system was not designed to survive the failure that occurred; and on
a substrate-recommended annual cadence. A review that changes a
sub-decision triggers re-verification of the L1 and L2 rules that depend
on it.
