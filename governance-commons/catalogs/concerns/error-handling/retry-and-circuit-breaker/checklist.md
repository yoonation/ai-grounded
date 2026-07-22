---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.error-handling.retry-and-circuit-breaker-retry-and-circuit-breaker"
title: "error-handling.retry-and-circuit-breaker review checklist: retry and circuit-breaker"
substrate-rule: "error-handling.retry-and-circuit-breaker"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-24"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove cross-process calls (HTTP, gRPC, database, message queue, cache)"
  - "Code changes that touch retry logic or circuit-breaker configuration"
  - "Code changes that introduce new external dependencies"
  - "Code changes that modify timeout values"
  - "Periodic resilience self-assessment"
---

# error-handling.retry-and-circuit-breaker review checklist: retry and circuit-breaker

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist enforces the substrate's resilience floor for
cross-process calls. The questions reference the application's
observability-slo-policy ADR (observability.slo-policy) for SLO budget
context and the error-handling-strategy ADR (error-handling.error-handling-strategy) for
per-dependency policy decisions.

## Review questions

### 1. Timeout: does every cross-process call have an explicit timeout?

Confirm that every HTTP call, RPC call, database query, message
queue publish, cache fetch, and other cross-process operation
declares an explicit timeout shorter than the caller's own
deadline. Default infinite timeouts (the language or library
default when no timeout is specified) are violations.

What good looks like: HTTP client construction declares a
timeout (requests.get(..., timeout=5), httpx.AsyncClient(
timeout=5), Java HttpClient.newBuilder().connectTimeout(...)
.readTimeout(...)); database connection pools declare statement
timeout; message queue clients declare publish and consume
timeouts.

What needs follow-up: HTTP clients are constructed without
timeout; database queries can hang indefinitely; the application
inherits framework defaults that may be unbounded.

### 2. Retry bound: is retry logic bounded by attempt count and time budget?

Confirm that retry logic is bounded: a maximum attempt count
(substrate-recommended: 3 for idempotent calls, 1 for non-
idempotent), a total time budget shorter than the caller's
deadline, and termination on non-retriable error types.
Unbounded `while True` retry loops are violations.

What good looks like: retry decorators or middleware specify
max_attempts and max_time (tenacity stop_after_attempt,
resilience4j max-attempts); the retry-aware code branches on
the typed error class per error-handling.typed-error-classification to decide whether the
error is retriable.

What needs follow-up: retry loops have no termination
condition; retry libraries are configured with high attempt
counts (10+) without time budgets; retry runs on every error
class without filtering.

### 3. Backoff and jitter: does retry use exponential backoff with jitter?

Confirm that retry between attempts uses exponential backoff
(typically base 100ms doubling per attempt) with jitter applied
to spread retry storms across callers. Constant-interval retry
and unbounded-growth backoff are the antipatterns.

What good looks like: backoff configuration is exponential with
a documented cap (e.g., max 30s); jitter is applied per the
AWS-pattern equal-jitter or full-jitter formulas; the
configuration is documented in the error-handling.error-handling-strategy ADR.

What needs follow-up: retry interval is constant (sleep(1)
between attempts); backoff has no cap and can grow to long
periods; no jitter is applied.

### 4. Idempotency: are non-idempotent calls protected from unsafe retry?

Confirm that non-idempotent calls (payment authorization, order
placement, message publish without idempotency keys) are
excluded from automatic retry or are guarded by an idempotency-
key contract with the downstream. Retrying a non-idempotent
call without the contract produces duplicate side effects.

What good looks like: non-idempotent endpoints use the
Idempotency-Key header pattern (or downstream-specific
equivalent); the application generates a key per request;
duplicate requests with the same key return the original
response.

What needs follow-up: payment, order, or similar calls retry
on transient failure without idempotency keys; the application
relies on the downstream to deduplicate (which may not be
guaranteed); duplicate side effects under retry are
documented as accepted risk.

### 5. Circuit-breaker: are degradation-prone dependencies protected?

Confirm that calls to dependencies with known degradation
modes (third-party APIs with rate limits, shared databases
under contention, message brokers, eventually-consistent
stores) are protected by circuit-breakers. The breaker opens
on consecutive failures or high failure rate, half-opens for
a trial after a backoff period, and closes when the trial
succeeds.

What good looks like: dependency adapters wrap calls in a
circuit-breaker (gobreaker.NewCircuitBreaker, resilience4j
CircuitBreaker, Polly CircuitBreakerPolicy, cockatiel
circuitBreaker); the breaker's open/half-open/closed
transitions are tuned per dependency per the ADR.

What needs follow-up: degradation-prone dependencies have no
circuit-breaker; the breaker is configured but the thresholds
are inappropriate for the dependency; the breaker exists in
code but is not exercised by tests.

### 6. SLO alignment: do retry and circuit-breaker bounds respect the SLO budget?

Confirm that the retry-amplified load on dependencies does not
violate the application's SLO budget per observability.slo-policy. A 3-retry
configuration multiplies upstream load by up to 3 under
sustained failure; the SLO must accommodate the worst-case
amplification.

What good looks like: the error-handling.error-handling-strategy ADR references the
observability.slo-policy SLO budget; retry bounds are sized so that worst-
case amplified load stays within budget; the budget is
periodically reviewed against observed retry rates.

What needs follow-up: the retry policy is set without SLO
context; observed retry rates exceed budgeted error rates;
the ADRs do not reference each other.

### 7. Fallback behavior: what happens when retry exhausts and circuit-breaker opens?

Confirm that the application has a documented fallback path
when retry exhausts and the circuit-breaker is open. The
fallback may be a degraded response (cached, default values,
partial data), a fail-fast response (error to the caller
with appropriate status), or a queue-for-later (background
retry with eventual consistency). The choice depends on D1
client contract from the error-handling.error-handling-strategy ADR.

What good looks like: the fallback is implemented; the
application's response on circuit-open is documented; the
client contract acknowledges the fallback behavior.

What needs follow-up: there is no fallback; the application
returns a generic 500 when the breaker opens; the fallback
is implemented but not documented in the ADR.

## Output

Each question receives one of three answers: GOOD (the rule's
expectation is met), NEEDS FOLLOW-UP (the rule's expectation is
not met; remediation required before merge), or NOT APPLICABLE
(the question does not apply to this change; the reviewer
documents why).

NEEDS FOLLOW-UP answers block merge until resolved. NOT APPLICABLE
answers require a one-line justification in the review thread.
