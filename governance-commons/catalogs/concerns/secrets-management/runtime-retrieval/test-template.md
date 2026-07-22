---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.secrets-management.runtime-retrieval-runtime-retrieval"
title: "secrets-management.runtime-retrieval test template: runtime secret retrieval"
substrate-rule: "secrets-management.runtime-retrieval"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# secrets-management.runtime-retrieval test template: runtime secret retrieval

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework (pytest, Jest, RSpec, JUnit, Go test) against their
application.

Tests in this suite are integration tests. They exercise the
secrets retrieval path in combination with the secrets platform.
They run against a deployed test environment or a representative
local stack (containerized Vault, LocalStack for AWS Secrets
Manager, gcloud-emulator for GCP Secret Manager).

Tests reset state between scenarios. Each scenario assumes a
clean baseline.

## Scenario 1: Cold-start retrieval succeeds against a healthy platform

**Preconditions**
- Secrets platform is reachable with the test workload's identity
- A test secret exists at a known path with a known value
- Application code is configured to retrieve the test secret at
  startup

**Action**
- Start the application
- Trigger the code path that uses the secret

**Expected**
- Application starts successfully without crash
- The code path receives the secret value
- The platform's audit log records a retrieval event tied to the
  workload's identity
- Application logs do not contain the secret value

## Scenario 2: Cached value is reused within the TTL window

**Preconditions**
- Application configured with a cache TTL for the secret (e.g.,
  60 seconds)
- Secret has been retrieved once at startup
- Platform is reachable but the test asserts cache hit count

**Action**
- Within the TTL window, trigger multiple code paths that use
  the secret

**Expected**
- The platform records only the initial retrieval (or the
  initial plus refresh per the cache strategy), not one per
  code path invocation
- Application correctness is identical to a no-cache run

## Scenario 3: Cached value refreshes after TTL elapse

**Preconditions**
- TTL configured for a short duration (e.g., 10 seconds for the
  test)
- Secret has been retrieved once

**Action**
- Wait for the TTL to elapse
- Rotate the secret value at the platform (simulate platform-
  side rotation)
- Trigger the code path that uses the secret

**Expected**
- Application picks up the new value within a bounded window
  after TTL elapse (substrate-recommended ceiling: 2 x TTL)
- Application logs reflect the refresh event
- No application restart was required

## Scenario 4: Platform-unreachable cold-start behavior

**Preconditions**
- Platform configured but unreachable (network error, DNS
  failure, or platform down)
- No cached value exists

**Action**
- Start the application

**Expected**
- Application either fails to start (fail-closed) or starts in
  a degraded mode that surfaces the platform-unreachable state
  through a health-check endpoint
- The specific behavior is documented in the application's
  runbook
- The application does not start with a fallback default
  credential value

## Scenario 5: Platform-unreachable behavior with valid cache

**Preconditions**
- Platform configured but unreachable
- A cached value exists from a prior successful retrieval and
  is still within its TTL window

**Action**
- Trigger the code path that uses the secret

**Expected**
- Application uses the cached value successfully
- Application surfaces the platform-unreachable state through
  monitoring (alert fires, health-check reflects degraded state)
- The application does not silently emit incorrect results

## Scenario 6: Wrong-identity retrieval is rejected

**Preconditions**
- A secret exists at a known path
- Application is configured to use an identity that does NOT
  have read on that path

**Action**
- Start the application
- Trigger the code path that uses the secret

**Expected**
- The platform rejects the retrieval request
- Application code receives the authorization-denied error
- Application either fails to start or fails the code path
  rather than falling back to a default value
- The platform's audit log records the denied attempt

## Scenario 7: Secret value does not appear in error responses

**Preconditions**
- A secret is in use in a code path that may throw an exception
- Exception handlers are configured per application convention

**Action**
- Trigger an exception in the code path that uses the secret
  (e.g., the downstream API the secret authenticates against
  is unreachable)

**Expected**
- The error response returned to the client does not contain
  the secret value
- The error log entry does not contain the secret value (per
  secrets-management.no-secrets-in-logs)
- The exception telemetry (Sentry, Rollbar, error monitor) does
  not contain the secret value

## Scenario 8: Workload-identity rotation continues to work

**Preconditions**
- Workload identity (e.g., IRSA role, GCP workload identity,
  Kubernetes service account token) has been rotated at the
  platform side
- Application is using cached credentials

**Action**
- After identity rotation, trigger a refresh of the cached
  credentials

**Expected**
- Application picks up the new identity automatically (cloud
  SDKs typically handle this)
- Retrieval succeeds with the new identity
- The application does not require a restart to pick up the
  rotated identity

## Test attestation

When all eight scenarios pass, the test suite records the
attestation in the CI artifact:

```
secrets-management.runtime-retrieval test suite: PASSING
- Scenario 1 (cold-start retrieval): PASS
- Scenario 2 (cache hit within TTL): PASS
- Scenario 3 (cache refresh after TTL): PASS
- Scenario 4 (platform unreachable cold-start): PASS
- Scenario 5 (platform unreachable cached): PASS
- Scenario 6 (wrong-identity rejected): PASS
- Scenario 7 (secret not in error responses): PASS
- Scenario 8 (workload-identity rotation): PASS
```

## Cross-reference

- Substrate rule: secrets-management.runtime-retrieval
- Review checklist: checklist.md
- Good examples: examples/secrets-management/runtime-retrieval-good.md
