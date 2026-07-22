---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authentication.rate-limiting-rate-limiting"
title: "authentication.rate-limiting test template: rate limiting on authentication endpoints"
substrate-rule: "authentication.rate-limiting"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.1.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-18"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authentication.rate-limiting test template: rate limiting on authentication endpoints

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework (pytest, Jest, RSpec, JUnit, Go test, etc.) against
their authentication endpoints.

Tests in this suite are integration tests, not unit tests:
they exercise the rate-limit middleware in combination with
the authentication code path. They run against a deployed
test environment or a representative local stack.

Tests must reset rate-limit state between scenarios. Each
scenario assumes a clean slate; one scenario must not leave
state that affects another.

## Scenario 1: Per-IP threshold triggers rate limit on login

**Preconditions**
- Rate-limit state cleared for the test source IP
- Test user account exists in the test environment
- Substrate-recommended per-IP threshold: 5 to 10 failed
  attempts per 15 minutes; the test assumes 10 as the
  ceiling

**Action**
- From a single source IP, submit 11 failed login attempts
  against the login endpoint within 60 seconds
- Use a valid username and an intentionally wrong password

**Expected**
- The first 10 attempts return the application's standard
  failed-authentication response (per authentication.generic-failure-responses, this is
  generic: status 401 with body indicating invalid credentials)
- The 11th attempt returns HTTP 429 Too Many Requests
- The 429 response includes a Retry-After header indicating
  when the IP may retry
- The 429 response body does not reveal whether the
  credentials would have authenticated

## Scenario 2: Per-account threshold triggers account lockout

**Preconditions**
- Rate-limit state cleared
- Test user account exists
- Substrate-recommended per-account threshold: 5 failed
  attempts before lockout

**Action**
- Submit 6 failed login attempts against the test user
  account from different source IPs (one IP per attempt) to
  defeat the per-IP threshold

**Expected**
- The first 5 attempts return the standard failed-auth
  response
- The 6th attempt returns a rate-limit or lockout response
  that does not distinguish between "wrong password" and
  "account locked"
- A subsequent attempt with the CORRECT password from a
  fresh IP also returns the same response (account is
  locked regardless of credential validity)
- Internal logging captures the lockout event with target
  account and triggering IPs

## Scenario 3: Single legitimate request passes normally

**Preconditions**
- Rate-limit state cleared

**Action**
- Submit one login request with correct credentials

**Expected**
- HTTP 200 with the standard successful-authentication
  response (or HTTP 302 redirect, depending on flow)
- No rate-limit response observed
- No rate-limit telemetry event recorded for this request

## Scenario 4: Rate-limit window clears after the configured duration

**Preconditions**
- Rate-limit state cleared
- Substrate-recommended per-IP window: 15 minutes

**Action**
- Submit 10 failed login attempts from one IP (reaching the
  per-IP threshold)
- Wait 16 minutes (or the configured window plus 1 minute)
- Submit one additional login attempt from the same IP

**Expected**
- The 11th attempt during the active window returns 429
- The post-window attempt is processed normally (returns the
  standard auth response based on credential validity)

Notes: this scenario is long-running and may be skipped in
fast-feedback CI; run it as part of nightly or pre-release
regression suite. The window duration is configuration; use
the smallest reasonable value for the test (e.g., 60 seconds
window in test environment) if production uses a longer
window.

## Scenario 5: Password reset endpoint is also rate limited

**Preconditions**
- Rate-limit state cleared
- Substrate-recommended per-IP password-reset threshold:
  3 to 5 requests per hour

**Action**
- Submit 6 password-reset requests from one IP within 60
  seconds

**Expected**
- The first 5 requests return the standard password-reset
  response (per authentication.generic-failure-responses, identical for registered and
  unregistered emails)
- The 6th request returns HTTP 429
- The 429 response does not reveal anything about whether
  the emails were registered

## Scenario 6: Token endpoint is rate limited (if applicable)

**Preconditions**
- Rate-limit state cleared
- Application has an OAuth or JWT token endpoint
- Substrate-recommended per-IP token-endpoint threshold:
  10 to 30 requests per minute

**Action**
- Submit 35 token-refresh or token-issue requests from one
  IP within 60 seconds, using an invalid refresh token or
  credentials

**Expected**
- The first ~30 requests return the standard token-endpoint
  failure response
- Subsequent requests return HTTP 429
- The 429 response does not reveal whether the token would
  have been issued

Skip this scenario if the application does not have a token
endpoint.

## Scenario 7: Rate-limit response does not vary with auth outcome

**Preconditions**
- Rate-limit state cleared
- Test user account exists with a known correct password

**Action**
- Submit 10 failed login attempts from one IP (reaching the
  per-IP threshold)
- Then submit one login request with the CORRECT password
  from the same IP
- Capture the response

**Expected**
- The 11th request returns HTTP 429 with the rate-limit
  response
- The response is BYTE-IDENTICAL to a request that would
  have failed authentication (same status, same body, same
  headers within timing variance)
- The client cannot distinguish "rate limited after correct
  password" from "rate limited after wrong password"

## Scenario 8: Distributed source IPs do not bypass per-account limit

**Preconditions**
- Rate-limit state cleared
- Test user account exists
- The test environment can simulate 10 different source IPs

**Action**
- Submit failed login attempts targeting one account, with
  each attempt from a different source IP, until 10 attempts
  have been made

**Expected**
- The per-IP limit does not trigger (one attempt per IP)
- The per-account limit triggers at the 5th or 6th attempt
  (per the substrate-recommended threshold)
- The 6th and subsequent attempts return the rate-limit or
  lockout response regardless of source IP

## Test scaffold: rate-limit state reset

Tests must reset rate-limit state between scenarios. The
implementation depends on the rate-limit storage:

- Redis: `FLUSHDB` against the rate-limit Redis instance,
  or selective DEL of keys matching the test prefix
- Database: TRUNCATE the rate-limit table or DELETE rows
  with the test prefix
- In-memory (production anti-pattern; should be fixed before
  this test suite is meaningful): restart the application
  between scenarios

The test scaffold is consumer-implemented; the substrate
specifies the requirement (reset state between scenarios)
but does not prescribe the mechanism.

## Cross-reference

- Substrate rule: authentication.rate-limiting in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Good examples: examples/authentication/rate-limiting-good.md
- Anti-patterns: examples/authentication/rate-limiting-anti-pattern.md
