---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.error-handling.observable-response-discrepancy-observable-response-discrepancy"
title: "error-handling.observable-response-discrepancy test template: observable response discrepancy"
substrate-rule: "error-handling.observable-response-discrepancy"
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

# error-handling.observable-response-discrepancy test template: observable response discrepancy

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework against the application's resource-access endpoints
to verify the response for "not found" and "unauthorized" cases
is indistinguishable to clients.

These tests are enumeration-probe tests: paired requests that
attempt to enumerate valid resource IDs by observing response
differences. The tests would fail if a regression introduced a
discrepancy.

## Scenario 1: Status code uniformity for read endpoint

**Preconditions**
- A read endpoint accepts a resource ID parameter
- The test fixture has two resource IDs: ID-A is a known
  non-existent resource; ID-B is a known existing resource
  owned by a different principal than the test principal
- The test principal authenticates correctly but is not
  authorized to read ID-B

**Action**
- Submit GET requests for both IDs as the test principal
- Capture both response status codes

**Expected**
- Both responses return the same status code (substrate-
  recommended: 404 Not Found for both)
- No 403 Forbidden response on the ID-B case

## Scenario 2: Response body shape uniformity for read endpoint

**Preconditions**
- Same as Scenario 1

**Action**
- Capture both response bodies
- Compare the JSON structures (field names, field count,
  field types)

**Expected**
- Both response bodies have identical JSON structure
- Field names are identical (no extra fields on the ID-B
  case)
- The Problem Details type URI is identical
- The detail field is the same phrasing (or follows a
  deliberate phrasing pattern that does not leak existence)

## Scenario 3: Response size uniformity (within jitter)

**Preconditions**
- Same as Scenario 1

**Action**
- Measure the byte size of both response bodies

**Expected**
- The response sizes are within a small jitter range (a few
  bytes, accounting for any per-request unique identifier
  like the instance URI from RFC 7807 / 9457)
- The sizes are NOT systematically different (e.g., 80 bytes
  vs 200 bytes indicates different shapes)

## Scenario 4: Response timing uniformity

**Preconditions**
- Same as Scenario 1
- The test runs a sufficient number of trials to characterize
  timing distribution (substrate-recommended: 1000 trials per
  case)

**Action**
- Submit 1000 GET requests for ID-A and 1000 for ID-B
- Record response time for each

**Expected**
- The distributions overlap substantially
- The mean response times differ by less than 5ms (or by less
  than the standard jitter of the network and test environment)
- No systematic timing signal allows distinguishing the two
  cases at high confidence

### Scenario 4a: Cache-warmed timing

**Preconditions**
- The application caches authorization decisions or resource
  metadata
- The cache is warmed before measurement (run several requests
  for each ID, then begin recording)

**Action**
- Repeat Scenario 4 with the cache warm

**Expected**
- Timing uniformity holds even with cache warm
- Cache-cold cases also pass the uniformity check, or the
  application documents the cache-cold-warm transition as an
  enumeration-resistant warm-up phase

## Scenario 5: Update and delete endpoints follow the same discipline

**Preconditions**
- Update (PUT/PATCH) and delete (DELETE) endpoints exist for
  the resource type from Scenario 1
- The test fixture and principal setup is the same

**Action**
- Submit PUT (or PATCH) requests for ID-A and ID-B
- Submit DELETE requests for ID-A and ID-B
- Capture status codes and response bodies for each

**Expected**
- PUT/PATCH for ID-A returns the same status code as PUT/PATCH
  for ID-B (substrate-recommended: 404)
- DELETE for ID-A returns the same status code as DELETE for
  ID-B
- Response bodies have the same shape for paired cases
- Attackers cannot enumerate IDs through write methods

## Scenario 6: List endpoint does not differentiate empty cases

**Preconditions**
- A list endpoint exists for the resource type
- The list can be filtered by owner
- ID-C is a known non-existent owner; ID-D is a known
  existing owner whose resources the test principal is not
  authorized to see

**Action**
- Submit list requests filtered by ID-C and ID-D
- Capture both response bodies

**Expected**
- Both responses are equivalent (empty list with the same
  shape, or both filtered to an empty result with consistent
  pagination metadata)
- The "empty because owner does not exist" case is
  indistinguishable from "empty because principal cannot see
  owner's resources"

## Scenario 7: Server log preserves distinction

**Preconditions**
- The application's logging captures resource-access outcomes
- The log entries include a structured field for the access
  outcome (not-found vs unauthorized)

**Action**
- Trigger the ID-A (not found) and ID-B (unauthorized) cases
  from Scenario 1
- Inspect the server log

**Expected**
- The log entry for ID-A is tagged outcome=not-found (or
  substrate-equivalent)
- The log entry for ID-B is tagged outcome=unauthorized (or
  substrate-equivalent)
- An operator querying logs by outcome can distinguish the
  cases for forensic analysis
- The principal's identity is captured for the unauthorized
  case
- The client-facing response remains indistinguishable per
  Scenarios 1-3

## Coverage notes

- Test scenarios above are the minimum coverage; consumers
  exercise every resource-access endpoint with the paired
  fixtures.
- Timing tests (Scenario 4) may be flaky in environments with
  high jitter; substrate-recommended approach is to run them
  in dedicated timing-isolated environments or to use
  statistical confidence intervals rather than fixed
  thresholds.
- Tests should run in CI against every PR that modifies
  resource-access endpoints, authorization decision logic,
  or the central error handler.
- The substrate also recommends penetration-testing
  enumeration probes against the production-like surface as
  a complementary verification.
