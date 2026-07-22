---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.rate-limiting-rate-limiting"
title: "authentication.rate-limiting review checklist: rate limiting on authentication endpoints"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove authentication endpoints"
  - "Code changes that touch rate-limiting middleware or configuration"
  - "Code changes to login, password reset, MFA challenge, or token-endpoint code paths"
  - "Periodic security self-assessment of authentication code"
---

# authentication.rate-limiting review checklist: rate limiting on authentication endpoints

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling (GitHub PR template checkbox
list, GitLab merge-request approval rules, Gerrit code-review
labels, etc).

The checklist is also useful for periodic self-assessment outside
the pull-request flow.

## Review questions

### 1. Coverage: are all authentication endpoints rate limited?

Rate limiting should cover every authentication endpoint in the
application, not just the login form. Common gaps to check for:

- Login endpoint (the obvious one)
- Password reset request endpoint
- Password reset confirmation endpoint
- MFA challenge submission endpoint
- MFA enrollment endpoint
- Email verification endpoint
- Magic link request endpoint
- OAuth or OIDC token endpoint
- Refresh token endpoint
- Account recovery endpoint
- API key creation or rotation endpoint

What good looks like: rate limiting applies to all auth endpoints
via shared middleware or per-endpoint declarative configuration;
every endpoint has visible rate-limit configuration.

What needs follow-up: only login is rate-limited; password reset
or token endpoints lack rate limiting; rate-limit middleware exists
but is conditionally bypassed for certain endpoints.

### 2. Granularity: are both per-IP and per-account limits in place?

Rate limiting must operate at two granularities:

- Per-source (per-IP, per-user-agent fingerprint, etc.) bounds
  total authentication attempts from one source
- Per-target (per-account, per-credential identifier) bounds
  total authentication attempts against one target

Per-IP-only allows distributed attacks against single accounts.
Per-account-only allows single-IP attacks across many accounts
before any single account hits its limit.

What good looks like: both granularities present; failure of
either triggers rate limit response.

What needs follow-up: only one granularity present; per-account
counter is per-process in memory; per-IP counter ignored when
account counter is present.

### 3. Thresholds: are the limits appropriate for this risk profile?

Substrate-recommended starting points (consumers tune by risk
profile):

- Login: 5 to 10 failed attempts per IP per 15 minutes;
  5 failed attempts per account before lockout
- Password reset request: 3 to 5 requests per IP per hour
- MFA challenge: 5 attempts per challenge before challenge
  invalidation
- Token endpoint: 10 to 30 requests per IP per minute

Higher-risk applications (banking, healthcare, regulated
industries) use stricter limits. Lower-risk applications with
high legitimate traffic may relax limits but never above
threshold that defeats brute-force protection.

What good looks like: thresholds are within or stricter than
the substrate-recommended ranges; thresholds are documented
in the rate-limit configuration with rationale.

What needs follow-up: thresholds significantly looser than the
substrate-recommended ranges without documented rationale;
unlimited retries permitted on any auth endpoint; thresholds
documented as comments but not enforced.

### 4. Storage backend: is rate-limit state shared across replicas?

Rate-limit counters must live in a shared backend (Redis,
database, dedicated rate-limit service) when the application
runs as multiple replicas. Per-process in-memory rate limiting
allows attackers to distribute their attack across replicas and
multiply their effective rate by the replica count.

What good looks like: rate-limit middleware reads and writes
state to Redis, a database, or a dedicated rate-limit service;
the storage is consistent across all application replicas.

What needs follow-up: rate-limit state is in-process memory
(typical of "for now" implementations that ship and never get
revisited); rate-limit state is in a per-replica file or local
cache.

### 5. Response shape: is the rate-limit response uniform with auth outcome?

The rate-limit response must not reveal whether the rejected
request would have authenticated successfully. The rate-limit
response is identical regardless of whether the credentials
were correct.

A common subtle bug: the rate-limit check happens after the
authentication check, so the response varies based on whether
the credentials matched (rate-limit message implies "you
authenticated but were rate limited" vs another rate-limit
message implying "you failed auth and were rate limited").

What good looks like: rate-limit check happens before any
credential verification; rate-limit response is identical
regardless of credential validity; internal logging captures
cause for monitoring without leaking to client.

What needs follow-up: rate-limit response differs based on
authentication outcome; rate-limit check happens after
authentication; rate-limit logs surface to the response body.

### 6. Bypass surface: are there legitimate bypasses, and are they safe?

Some applications need bypasses for legitimate retry traffic
(user typing password slowly), trusted internal services, or
testing. Bypasses are a common attack target.

What good looks like: bypasses are explicit and narrow (single
internal service IP range with documented purpose; admin
override behind privileged session); bypasses are logged when
triggered; bypasses do not extend to credential-stuffing
patterns (large request volume from one source).

What needs follow-up: blanket bypass for "trusted" IPs without
narrow scope; bypass triggered by header that client can set
(X-Forwarded-For trust without verification); bypass for
"testing" that survives in production.

### 7. Account lockout integration: does failure trigger appropriate lockout?

Per-account rate limiting transitions to account lockout when
the threshold is reached. Lockout behavior is part of this rule.

What good looks like: lockout duration is bounded (15 to 30
minutes typical) and self-clearing; lockout is signalled via
the same generic auth failure response to preserve authentication.generic-failure-responses;
lockout state is recorded in audit log; user can recover via
password reset that itself is rate-limited.

What needs follow-up: lockout is permanent and requires
administrative unlock for ordinary accounts (denial-of-service
risk); lockout response leaks state to client; lockout cleared
by any successful authentication (allowing the attacker to
clear lockout by guessing one correct credential).

### 8. Telemetry: are rate-limit events captured for security monitoring?

Rate-limit events are valuable security telemetry. They
indicate active attempts to brute-force or credential-stuff
the authentication. Capture is part of the rule.

What good looks like: rate-limit events recorded with IP,
target account (if applicable), endpoint, timestamp; events
flow to security monitoring (SIEM, log aggregator with alert
rules); anomalous patterns (large spike in rate-limit events,
unusual IP geo-distribution) trigger alerts.

What needs follow-up: rate-limit events not logged; events
logged at DEBUG level only and lost in production; events not
integrated with security monitoring.

## Reviewer attestation

When all eight questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review:

```
authentication.rate-limiting review checklist: complete
- Coverage: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Granularity: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Thresholds: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Storage: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Response shape: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Bypass surface: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Account lockout: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Telemetry: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge until resolved. EXEMPT items
require documented rationale in the pull-request thread.

## Cross-reference

- Substrate rule: authentication.rate-limiting in catalogs/concerns/authentication.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/authentication/rate-limiting-good.md
- Anti-patterns: examples/authentication/rate-limiting-anti-pattern.md
