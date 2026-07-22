---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.testing-strategy.critical-path-coverage-critical-path-coverage"
title: "testing-strategy.critical-path-coverage test template: critical path coverage"
substrate-rule: "testing-strategy.critical-path-coverage"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-25"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# testing-strategy.critical-path-coverage test template: critical path coverage

## How to use this binding

This binding ships representative edge-case and security-probe
test scenarios for the substrate-recommended critical path
categories. Consumers translate these scenarios into their test
framework against their application's specific critical paths.

The scenarios are organized by critical path category. Each
scenario represents one cell in the per-path test matrix from
the testing-strategy.critical-path-coverage review checklist. Consumers extend the scenarios
to cover application-specific critical paths beyond the
substrate's recommended categories.

## Authentication critical path scenarios

### Scenario A1: login with wrong password returns generic error

**Substrate-aligned rules:** authentication.generic-failure-responses (generic error
messaging, no user enumeration)

**Preconditions**
- A user account exists in the application's identity store

**Verification**
- Issue a login request with the correct username and an
  incorrect password
- The response is a 4xx status (substrate-recommended: 401)
- The response body contains a generic error ("Invalid
  credentials") and does not distinguish "wrong password" from
  "user not found"
- Timing of the response is within substrate-acceptable variance
  of the response for a non-existent user (to prevent timing-
  based user enumeration)

### Scenario A2: token after expiration is rejected

**Substrate-aligned rules:** authentication.token-expiration (token expiration
enforcement)

**Preconditions**
- A valid token is issued with a known expiration
- The test framework can advance mock time past the expiration

**Verification**
- After advancing time past expiration, an authenticated request
  with the token returns 401
- The application clears or rotates any session derived from the
  expired token

## Authorization critical path scenarios

### Scenario AZ1: cross-tenant data access returns 403

**Substrate-aligned rules:** authorization.authz-before-resource-access (authorization decision
before resource access)

**Preconditions**
- Two tenants exist; tenant A has resource R_A; tenant B has no
  access to R_A

**Verification**
- A user authenticated as tenant B issues a request for R_A
- The response is 403 (or 404, per the application's documented
  enumeration-vs-direct preference)
- No data from R_A leaks in the response body
- No data from R_A leaks in side channels (response timing,
  cache headers, log lines)

### Scenario AZ2: ownership check is enforced on write paths

**Substrate-aligned rules:** authorization.authz-before-resource-access

**Preconditions**
- Resource R has owner user_owner; user_other is not the owner

**Verification**
- A request from user_other to modify R returns 403
- The resource state after the rejected request is unchanged
  (no partial-update side effects)

## Input validation critical path scenarios

### Scenario IV1: SQL injection probe is rejected without execution

**Substrate-aligned rules:** input-validation.parameterized-queries (parameterized queries)

**Preconditions**
- An endpoint accepts a string parameter that flows into a
  database query

**Verification**
- A request with a parameter containing canonical SQL injection
  patterns (`' OR '1'='1`, `'; DROP TABLE`, embedded NUL,
  Unicode-escape variants) is rejected or treated as a literal
  string value
- The database state after the request is unchanged
- The application logs do not contain the unsanitized input
  values (per the logging mechanical (L1) substrate rules)

### Scenario IV2: shell injection probe is rejected

**Substrate-aligned rules:** input-validation.no-shell-injection (shell injection
prevention)

**Preconditions**
- An endpoint accepts a parameter that flows into a system
  command (rare in substrate-aligned applications; the L1 rule
  forbids most cases)

**Verification**
- A request with parameter containing shell metacharacters (`;`,
  `&&`, `|`, command substitution) is rejected or escaped
- The system command, if executed, does not interpret the
  metacharacters

## Error handling critical path scenarios

### Scenario E1: unexpected exception does not leak stack trace

**Substrate-aligned rules:** error-handling.no-stack-trace-in-response (no stack trace in
response)

**Preconditions**
- A test endpoint or an intentional failure injector that can
  raise an unhandled exception

**Verification**
- The response to the unhandled exception is the application's
  standard 5xx error contract per error-handling.error-response-contract
- The response body does not contain stack frames, file paths,
  module names, or other implementation detail
- The internal log (verified separately) contains the full
  context per the logging mechanical (L1) substrate rules

### Scenario E2: error response status code matches the error class

**Substrate-aligned rules:** error-handling.error-status-code (error status code)

**Preconditions**
- Endpoints with documented error responses

**Verification**
- For each documented error class, the response status code
  matches the substrate-recommended mapping (4xx for client
  errors, 5xx for server errors); the 200-OK-with-error-body
  pattern is forbidden

## Payment / state-changing critical path scenarios

### Scenario P1: idempotent write with same idempotency key produces same result

**Preconditions**
- A write endpoint accepts an idempotency key
- The application supports idempotent retries

**Verification**
- Two requests with the same idempotency key and same body
  produce the same result; only one state change occurs
- Two requests with the same idempotency key and different
  bodies produce a substrate-acceptable conflict response

### Scenario P2: write under authorization-denied condition has no side effects

**Preconditions**
- A write endpoint that requires authorization

**Verification**
- A request that fails authorization (403) leaves the application
  state unchanged
- No partial state (audit log entry, side-effect call) is
  produced

## Coverage notes

This test template ships scenarios for the substrate-recommended
critical path categories. Consumers extend the template with
application-specific critical paths; the testing-strategy.critical-path-coverage review
checklist's matrix completeness question covers extension
discipline.

The substrate-acceptable coverage form is: every catalogued
critical path has at least one test from each cell of the matrix
(happy, error, edge, security probe). Gaps are tracked as
remediation items.
