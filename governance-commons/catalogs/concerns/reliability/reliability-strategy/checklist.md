---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.reliability.reliability-strategy-reliability-strategy"
title: "reliability.reliability-strategy review checklist: reliability strategy ADR"
substrate-rule: "reliability.reliability-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 3 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new service, or an existing service crossing into traffic whose loss carries real cost"
  - "A new critical dependency, or a change in an existing dependency's criticality"
  - "A topology shift (adding a queue, splitting a service, putting a cache in the request path)"
  - "Any incident whose post-mortem finds the system was not designed to survive the failure that occurred"
  - "Repeated RELY-L2 escalations tracing to an absent or ambiguous strategy"
  - "Substrate-recommended annual reliability-strategy review"
---

# reliability.reliability-strategy review checklist: reliability strategy ADR

## How to use this binding

The reviewer applies this checklist to the consumer's reliability-
strategy ADR (substrate-recommended location /docs/decisions/ADR-XXX-
reliability-strategy.md). The L3 rule is satisfied when the ADR exists,
addresses every required sub-decision substantively, and is enforced by
the L1 and L2 mechanisms of this concern. This is the anchoring decision
the four L2 rules and three L1 rules take their meaning from, so the
review confirms not only that the ADR is complete but that the rest of
the concern is wired to it.

## Review questions

### 1. Does the failure-mode catalog name specific failures, in and out of scope?

What good looks like: the ADR lists the failures the service is designed
to survive (a dependency timing out, an instance dying, a traffic
spike) and, explicitly, the ones it is not (a full regional outage, a
correlated failure of all replicas), each with the designed-for
response. The out-of-scope list is as important as the in-scope one.

What needs follow-up: the catalog gestures at "high availability"
without naming failures, so no one can tell what the service is actually
built to withstand.

### 2. Is every cross-process dependency classified by criticality with a decided response?

What good looks like: each dependency is labeled critical, degradable,
or optional, with the request-level consequence of its loss and the
chosen response (fail the request, degrade the feature, drop it
silently). This is the classification reliability.graceful-degradation checks against.

What needs follow-up: a dependency is missing from the classification, or
every dependency is implicitly critical because criticality was never
decided.

### 3. Are delivery and idempotency semantics stated, and is idempotency real where redelivery is possible?

What good looks like: the ADR states the delivery guarantee for each
retryable path or message flow (at-least-once, at-most-once, exactly-
once-in-effect) and how idempotency is achieved wherever the semantics
permit redelivery. This is what reliability.idempotency checks conformance to.

What needs follow-up: semantics are unstated, or the ADR claims
exactly-once delivery from a broker rather than designing for at-least-
once with idempotent effects.

### 4. Does the resource-isolation model identify real failure domains?

What good looks like: the ADR names the failure domains and the
bulkheads, pools, or concurrency limits separating them, so that a slow
dependency cannot starve unrelated work. This is the map reliability.failure-isolation
checks against, and it is also where the reliability.bounded-buffers bound sizes and
reliability.tracked-async-tasks supervision shapes are justified.

What needs follow-up: isolation is asserted in the abstract with no
named domains, or unrelated work demonstrably shares a pool the ADR
does not acknowledge.

### 5. Does the health-and-recovery model say what readiness gates on and how recovery works?

What good looks like: the ADR states what liveness and readiness each
check, which critical dependencies readiness gates on, and how the
service recovers after a dependency heals. This is what reliability.health-signaling
checks the probes against.

What needs follow-up: health behavior is undecided, so probe semantics
are left to whoever wrote the endpoint, and recovery after an outage is
untested.

### 6. Are the L1 and L2 rules configured consistently with the strategy?

What good looks like: the reliability.bounded-buffers buffer bounds reflect the
strategy's tolerance for in-flight work; the reliability.tracked-async-tasks supervision
matches the failure-survival design; the reliability.graceful-degradation degradation paths
match the criticality classification; the reliability.failure-isolation bulkheads match
the failure-domain map; and the reliability.health-signaling readiness gates on the
dependencies the strategy calls critical. The recorded decision and the
mechanical and semantic gates agree.

What needs follow-up: the ADR declares one reliability model while the
enforced gates implement another, or no gates are wired to the strategy
at all.

## What counts as a finding

A missing ADR, or an ADR missing any sub-decision in questions 1 through
5, is a finding: pause new dependency integrations and failure-domain-
crossing changes until the ADR is authored or amended (per the rule's
remediation guidance). An ADR that exists but is not enforced (question
6 failing) is a finding requiring the enforcement to be wired. For an
existing service, a retrospective ADR documenting the reliability
behavior already in place satisfies the rule provided it then drives
convergence and names the failures the service is not yet designed to
survive.
