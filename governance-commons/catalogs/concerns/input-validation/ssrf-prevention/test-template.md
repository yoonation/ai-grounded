---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.input-validation.ssrf-prevention-ssrf-prevention"
title: "input-validation.ssrf-prevention test template: SSRF prevention"
substrate-rule: "input-validation.ssrf-prevention"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# input-validation.ssrf-prevention test template: SSRF prevention

## How to use this binding

This binding describes test scenarios for SSRF defenses on
outbound requests with user-influenced URLs. The tests require
infrastructure (a controlled DNS test fixture, a controlled
redirect server) to verify the full defense chain.

The substrate-recommended coverage target is: every endpoint
that makes an outbound request with a user-influenced URL has
all scenarios below covered.

## Scenario 1: Allowlisted external host succeeds

**Preconditions**
- The application has a configured allowlist (e.g., contains
  "api.example.com")
- A request triggers an outbound call to api.example.com

**Action**
- Trigger the request

**Expected**
- The outbound call succeeds
- A log entry records the successful outbound call
- The application uses the response as expected

## Scenario 2: Non-allowlisted external host rejected

**Preconditions**
- Same configuration as Scenario 1
- A request supplies a URL pointing to a host NOT on the
  allowlist (e.g., "evil.example.org")

**Action**
- Trigger the request

**Expected**
- The outbound call is rejected before connection
- HTTP 400 or the endpoint's structured error response
- The error response does not echo the rejected URL (or echoes
  it only with the rejected-host marker)
- A log entry records the rejection with the rejected host

## Scenario 3: Private IP rejected via direct address

**Preconditions**
- Same configuration
- A request supplies a URL with a private IP literal
  (e.g., "http://10.0.0.5/")

**Action**
- Trigger the request

**Expected**
- The outbound call is rejected at the IP-check step
- The application logs the rejection

## Scenario 4: Private IP rejected via DNS resolution

**Preconditions**
- A test DNS fixture is configured: "internal.test.example"
  resolves to 10.0.0.5
- A request supplies "http://internal.test.example/"

**Action**
- Trigger the request

**Expected**
- The application resolves the host name to its IP, checks
  against private ranges, and rejects
- The rejection occurs before the connection attempt

## Scenario 5: Cloud metadata service rejected

**Preconditions**
- A request supplies "http://169.254.169.254/latest/meta-data/"

**Action**
- Trigger the request

**Expected**
- The outbound call is rejected
- The rejection is logged with explicit reference to the
  metadata-service block
- On AWS, the instance is configured for IMDSv2; the application
  cannot reach IMDSv1 endpoints even if validation is bypassed

## Scenario 6: Redirect to private IP rejected

**Preconditions**
- A controlled redirect server is reachable at a public IP
- The redirect server responds with HTTP 302 Location:
  http://10.0.0.5/
- A request supplies the redirect server's URL

**Action**
- Trigger the outbound call

**Expected**
- The application follows the redirect (or has follow-redirects
  disabled, depending on configuration)
- If following redirects, the application re-validates the
  redirect target and rejects the private destination
- If not following redirects, the application receives the 302
  response and treats it as a structured error

## Scenario 7: Timeout enforced on slow connection

**Preconditions**
- A controlled slow-response server is reachable
- The application's outbound client has a documented timeout

**Action**
- Trigger an outbound call to the slow server

**Expected**
- The outbound call returns a timeout error within the
  configured timeout duration plus a reasonable margin
- The application's worker pool is not exhausted by the slow
  call
- The error is reported to the caller as a structured response

## Scenario 8: Logging coverage verified

**Preconditions**
- All scenarios above have been executed

**Action**
- Inspect the application log

**Expected**
- Every rejection appears in the log with the rejected URL,
  the rejection reason, and the request correlation ID
- Successful outbound calls also appear (at appropriate
  severity) for traffic accounting
- An audit dashboard can compute rejection rates by endpoint
