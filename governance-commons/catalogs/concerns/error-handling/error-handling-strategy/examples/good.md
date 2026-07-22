<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.error-handling-strategy consumer ADR (filled-in)

A substrate-original example of a consumer ADR that adapts the
substrate's error-handling-strategy framework to a concrete
application context. The consumer's ADR satisfies error-handling.error-handling-strategy by
addressing each decision driver and naming the chosen options.

The example below is for a hypothetical "PaymentService"
application: a Go service that processes card-not-present
payment authorizations against a third-party gateway.

---

# ADR-0011: Error-handling strategy

- **Status:** Accepted
- **Date:** 2026-04-22
- **Deciders:** Payments platform team (Dana, Ethan), Site Reliability (Farah), Security (Gomez)
- **References:**
  - Substrate framework MADR: governance-commons/decision-frameworks/error-handling-strategy.madr.md
  - Substrate rule: error-handling.error-handling-strategy
  - Related ADRs: ADR-0003 logging architecture, ADR-0008 observability SLO policy, ADR-0009 retry budget

## Context and Problem Statement

PaymentService authorizes card-not-present payments against the
Acme Payments gateway. The service handles ~3M authorizations/day
at peak, sustained 200 req/s, with bursts to 1.2k req/s during
flash-sale windows. Acme Payments has a published 99.9% SLA with
typical p99 latencies of 400ms.

The 2026-Q1 incident retrospective (INC-2026-0143) identified
that during a 22-minute Acme degradation, PaymentService
produced 940k retry attempts against a degraded gateway, which
contributed to delayed recovery and cascaded into our own
database connection pool exhaustion. We need a documented
error-handling strategy that addresses retry bounding,
circuit-breaking, fallback behavior, and customer-facing error
contracts.

## Decision Drivers

Adapted from the substrate framework's D1-D9. Application-
specific context noted where relevant.

- **D1 Failure-mode classification:** Acme Payments produces
  four observable failure modes: hard decline (4xx terminal),
  soft decline (4xx retryable), gateway timeout (5xx), and rate
  limit (429).
- **D2 Customer expectation:** Card authorizations have a
  business-defined 8-second SLA from "user clicks pay" to
  "outcome shown". This bounds total wall time for all retries
  plus circuit-breaker fallthrough.
- **D3 Cascade risk:** A retry storm caused the INC-2026-0143
  cascade. The strategy must prevent retry amplification.
- **D4 Idempotency:** Acme Payments accepts idempotency keys
  per RFC draft; retries can be safe.
- **D5 Observability:** All errors must flow into the existing
  Datadog SLO dashboards (ADR-0008).
- **D6 Customer error contract:** Payments partners (storefronts)
  consume RFC 7807 Problem Details per their integration spec.
- **D7 Manual operator override:** SRE on-call must be able to
  flip the gateway breaker open manually during planned
  Acme maintenance windows.
- **D8 Compliance:** PCI DSS forbids logging full PAN; error
  logs scrubbing required (already in ADR-0003).
- **D9 Test surface:** Failure-injection tests required for each
  configured failure mode.

## Considered Options

Per the substrate framework's five options.

- **Option 1: Fail-fast only** (substrate Option A). Rejected
  because Acme transient failures are common and a single-shot
  policy would harm customer experience.
- **Option 2: Retry with backoff** (substrate Option B). Rejected
  in pure form because INC-2026-0143 was a retry-with-backoff
  failure mode (the backoff was insufficient and the budget
  unbounded).
- **Option 3: Circuit breaker with degradation** (substrate
  Option C). Rejected because PaymentService has no useful
  degraded mode for the core authorization path.
- **Option 4: Hybrid with service-tier policy** (substrate
  Option D). **Selected.** See decision below.
- **Option 5: Hand-rolled per call site** (substrate Option E).
  Rejected; ADR-0011 cohesion requires a single library and
  shared configuration.

## Decision

We adopt **Option 4: Hybrid with service-tier policy**, with the
following concrete bindings:

- **Library:** `sony/gobreaker` for circuit breaking; `cenkalti/backoff/v4`
  for backoff; both vendored at pinned versions per
  governance-commons dependency-management policy.
- **Idempotency:** Acme Payments idempotency key set to the
  internal authorization request UUID. Per-call.
- **Per-failure-mode policy:**
  - Hard decline (4xx terminal): no retry; map to
    `PaymentDeclined` domain error; HTTP 422 to caller.
  - Soft decline (4xx retryable): up to 2 retries with
    50ms-200ms-450ms exponential backoff + jitter; if all
    exhausted, map to `PaymentRetryExhausted`; HTTP 502 to
    caller.
  - Gateway timeout (5xx): same retry budget as soft decline;
    counts against circuit breaker.
  - Rate limit (429): no retry from this service; map to
    `PaymentBackpressure`; HTTP 429 to caller with
    `Retry-After` derived from the Acme header.
- **Circuit breaker:** opens on 20% error rate over a 30-second
  rolling window with minimum 50 requests; half-open recovery
  at 10-second intervals.
- **Total wall budget:** 6 seconds enforced via `context.Context`
  deadline at the request boundary, leaving 2 seconds of headroom
  against the 8-second customer SLA.
- **Operator override:** SRE-only feature flag `payments.gateway.breaker.force_open`
  via LaunchDarkly (already wired per ADR-0007 feature-flag
  strategy).
- **Observability:** Per-failure-mode counters in Datadog
  (`payments.gateway.{declined,retry_exhausted,backpressure,breaker_open}`)
  feed the existing payment-conversion SLO.

## Consequences

**Positive:**
- INC-2026-0143 cascade pattern is structurally prevented by
  the bounded retry budget plus circuit breaker.
- Customer experience predictable within the 8-second SLA.
- SRE has manual control during planned maintenance.

**Negative:**
- Adds two new library dependencies (gobreaker, backoff/v4)
  vetted per dependency-management policy.
- Operators must understand the breaker state machine; runbook
  RB-PAY-007 documents this.

**Neutral:**
- This ADR supersedes the implicit retry-with-Backoff policy
  used since the service's launch in 2024.

## Compliance

This ADR satisfies error-handling.error-handling-strategy per the substrate-recommended
gate. The decision is captured in code in `internal/payments/gateway/`
with the failure-mode policy as a typed enum and the retry
parameters as configuration constants. Failure-injection tests
exercise each mode under `internal/payments/gateway_test.go`.
