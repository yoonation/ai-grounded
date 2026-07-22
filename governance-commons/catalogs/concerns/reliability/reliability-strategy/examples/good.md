<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.reliability-strategy reliability strategy (good pattern)

Substrate-original illustration: an abbreviated reliability-strategy ADR
that makes each sub-decision explicit and wires it to the L1 and L2
rules. The real document would expand each section.

```markdown
# ADR-021: Reliability strategy for the orders service

## Status
Accepted

## Failure-mode catalog
In scope: single instance loss; one zone outage; payment processor
timeout; a traffic spike up to 5x baseline. Out of scope: full region
loss (manual failover, documented runbook); simultaneous loss of all
database replicas.

## Dependency-criticality classification
- payments-processor: CRITICAL. Loss fails the order; no fallback.
- inventory-service: CRITICAL. Loss fails the order.
- recommendations: OPTIONAL. Loss omits the upsell section.
- pricing-cache: DEGRADABLE. Loss falls back to origin pricing (slower).

## Delivery and idempotency semantics
Order submission is at-least-once from the gateway; consumers are
idempotent on the client-supplied order_id (reliability.idempotency). No reliance on
broker exactly-once.

## Resource-isolation model
Per-dependency concurrency limits; payments and inventory in separate
pools from search (reliability.failure-isolation). Order intake queue bounded at 5000
(reliability.bounded-buffers), sized to one minute of peak intake.

## Health-and-recovery model
Liveness = process only. Readiness gates on payments + inventory + DB
(reliability.health-signaling). Startup probe covers cache warm.

## Degradation policy
recommendations omitted on loss; pricing-cache falls back to origin;
both observable via degraded-mode metrics (reliability.graceful-degradation).

## Decision review schedule
On new critical dependency; after any incident; annually.
```

Why this satisfies the rule: every sub-decision is decided, not assumed,
and each names the L1 or L2 rule it drives, so a reviewer can confirm the
enforced gates match the recorded strategy.
