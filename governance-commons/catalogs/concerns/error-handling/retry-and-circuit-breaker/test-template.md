---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.error-handling.retry-and-circuit-breaker-retry-and-circuit-breaker"
title: "error-handling.retry-and-circuit-breaker test template: retry and circuit-breaker"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# error-handling.retry-and-circuit-breaker test template: retry and circuit-breaker

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework against the application's retry, timeout, and
circuit-breaker configuration for representative dependencies.

These tests verify the resilience layer's behavior: timeouts
are enforced, retry is bounded, backoff is applied, idempotency
is respected, and circuit-breakers transition correctly.

## Scenario 1: Timeout is enforced

**Preconditions**
- The application has at least one cross-process call with a
  documented timeout
- A test-double simulates a slow downstream that exceeds the
  timeout

**Action**
- Invoke the operation that calls the slow downstream
- Measure the elapsed time

**Expected**
- The operation completes (with an error result) within the
  configured timeout, not the simulated downstream duration
- The error is the application's documented timeout error type
  (an InfrastructureError subclass)
- The infrastructure error propagates correctly to the central
  handler

## Scenario 2: Retry is bounded by attempt count

**Preconditions**
- The application's retry configuration declares a maximum
  attempt count (substrate-recommended: 3 for idempotent
  calls)
- A test-double fails on every attempt

**Action**
- Invoke the operation
- Count the attempt invocations

**Expected**
- The downstream is invoked exactly max_attempts times (3 in
  the substrate-recommended default)
- The final result is the error (after exhausting retries)
- Retry does not continue indefinitely

## Scenario 3: Backoff with jitter applied

**Preconditions**
- The retry configuration declares exponential backoff with
  base 100ms and jitter
- A test-double fails on every attempt

**Action**
- Invoke the operation
- Record the timestamps of each attempt

**Expected**
- The intervals between attempts grow exponentially (approx
  100ms, 200ms, 400ms in the substrate-default base 100ms
  doubling configuration), with jitter applied
- The intervals are NOT constant (constant intervals indicate
  missing backoff configuration)
- The intervals are NOT identical across test runs (identical
  intervals indicate missing jitter)

## Scenario 4: Non-idempotent call is excluded from retry

**Preconditions**
- The application has a non-idempotent operation documented as
  such (payment authorization, order placement, message publish
  without idempotency key)
- The non-idempotent operation has retry disabled or has a
  max_attempts of 1
- A test-double fails on first attempt

**Action**
- Invoke the non-idempotent operation

**Expected**
- The downstream is invoked exactly once (no retry)
- The error propagates to the central handler immediately
- The application's documented response is returned

### Scenario 4a: Idempotency key contract

**Preconditions** (if the application supports idempotency keys)
- The non-idempotent operation accepts an Idempotency-Key
  header (or downstream-specific equivalent)
- The downstream is configured to deduplicate by key

**Action**
- Invoke the operation with the same key twice (simulating
  retry across requests)

**Expected**
- The downstream is invoked exactly once across the two
  attempts (the second request returns the cached response)

## Scenario 5: Circuit-breaker opens on consecutive failures

**Preconditions**
- The application's dependency has a circuit-breaker with a
  documented threshold (substrate-recommended: 5 consecutive
  failures or 50% failure rate in a 30-second window)
- A test-double fails on every attempt

**Action**
- Invoke the operation repeatedly until the breaker opens

**Expected**
- After the threshold is reached, subsequent invocations fail
  fast without calling the downstream (the breaker is open)
- The application returns the documented fallback response
- The downstream is no longer invoked

## Scenario 6: Circuit-breaker half-open trial and recovery

**Preconditions**
- The circuit-breaker is open (from Scenario 5)
- The test-double is reconfigured to succeed
- The breaker's half-open backoff has elapsed (substrate-
  recommended: 60 seconds; test runs may need to fast-
  forward time)

**Action**
- Invoke the operation

**Expected**
- A single trial invocation passes through to the downstream
  (half-open state)
- The trial succeeds; the breaker closes
- Subsequent invocations pass through normally

## Scenario 7: Retry policy stays within SLO budget

**Preconditions**
- The application's observability.slo-policy SLO budget is documented
- The retry configuration multiplies upstream load by up to
  max_attempts under sustained failure
- A load test or simulation exercises the worst-case
  amplification

**Action**
- Simulate sustained downstream failure with realistic
  upstream request volume
- Measure the load on the downstream

**Expected**
- The amplified downstream load is within the SLO budget's
  accommodation for the dependency
- If the amplification exceeds the budget, the test fails (the
  retry configuration must be re-tuned per the ADR)

## Coverage notes

- Test scenarios above are the minimum coverage; consumers add
  dependency-specific scenarios for each external service.
- Time-fast-forwarding (FakeAsync in Dart, mockito's
  ScheduledExecutor, freezegun for Python, timekeeper for Go)
  is substrate-recommended for testing backoff and circuit-
  breaker timing without real-time delays.
- Chaos engineering frameworks (Chaos Monkey, Toxiproxy,
  Gremlin) extend these tests with production-like fault
  injection; the substrate's test template defines the unit-
  test surface, chaos tests extend the production-like
  surface.
- Tests should run in CI against every PR that modifies
  retry, timeout, or circuit-breaker configuration.
