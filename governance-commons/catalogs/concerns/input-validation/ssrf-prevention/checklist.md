---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.ssrf-prevention-ssrf-prevention"
title: "input-validation.ssrf-prevention review checklist: SSRF prevention"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add or modify outbound HTTP requests with user-influenced URLs"
  - "Code changes that introduce new external service integrations"
  - "Code changes that touch URL parsing or redirect handling"
  - "Periodic input-validation self-assessment"
---

# input-validation.ssrf-prevention review checklist: SSRF prevention

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block
merge.

This checklist enforces server-side request forgery defenses on
outbound requests where the target URL is influenced by user
input. The defenses combine multiple checks because each single
check has known bypasses; partial implementation leaves
exploitable gaps. The 2019 Capital One incident via SSRF and AWS
metadata service is the canonical high-impact case.

## Review questions

### 1. Allowlist policy: is the target host on an explicit allowlist?

Confirm that outbound requests with user-influenced URLs check
the target host against an explicit allowlist of permitted
external services. The allowlist is a closed set (e.g.,
{api.example.com, webhook.thirdparty.example}) rather than a
denylist of internal ranges; a denylist alone is insufficient
because it does not anticipate every internal host.

What good looks like: the application has a configured allowlist
loaded at startup; outbound clients check the requested host
against the allowlist and reject non-matches; the allowlist is
documented in the application configuration and reviewed.

What needs follow-up: the application accepts any external host;
the filter relies on a denylist that may not cover internal
endpoints; the allowlist is implicit in the code's branching.

### 2. IP resolution check: are resolved addresses checked against private ranges?

Confirm that the resolved IP addresses of the target host are
checked against private and link-local ranges (10.0.0.0/8,
172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16 including the
metadata service at 169.254.169.254, 127.0.0.0/8, fc00::/7, ::1,
IPv4-mapped IPv6 forms). If any resolved address is in those
ranges, the request is rejected.

What good looks like: the outbound client performs DNS resolution
before connecting and checks the resolved addresses against the
private-range list; multi-address resolution (a host that returns
multiple IPs) rejects if any is private; the metadata service
URL is explicitly rejected.

What needs follow-up: the application trusts the hostname check
alone; a hostname resolving to a private IP is not detected; DNS
rebinding (the host resolves to a public IP at validation time
and a private IP at request time) is not defended against.

### 3. Redirect handling: are redirects validated?

Confirm that HTTP redirects are either disabled or re-validated
through the same allowlist and IP-resolution checks at each
redirect step. A public host that 302-redirects to a private host
bypasses naive single-check implementations.

What good looks like: the outbound HTTP client is configured with
follow-redirects=false, or with a redirect handler that re-runs
the allowlist and IP-resolution checks on each redirect target;
redirect chains are bounded (typically 3-5 hops max).

What needs follow-up: the client follows redirects without
re-validation; redirect chains can target internal hosts; the
client follows infinite redirect loops.

### 4. Cloud metadata service: is IMDSv2 or equivalent enforced?

Confirm that the AWS metadata service (169.254.169.254) is
protected by IMDSv2 (mandatory session-token requirement on AWS),
or that the equivalent protections are in place on GCP and
Azure. The metadata service is the highest-impact SSRF target
in cloud environments because it surfaces instance credentials.

What good looks like: AWS EC2 instances are configured with
HttpTokens=required at the instance-metadata-options level; GCP
metadata requires Metadata-Flavor: Google header; Azure metadata
requires Metadata: true header; the application's outbound
clients do not send these tokens unintentionally on user-
controlled requests.

What needs follow-up: the AWS instance runs IMDSv1; the metadata
service URL is reachable from user-controlled outbound requests;
the metadata-protection posture is not documented.

### 5. Timeout and connection limits: are slow-connection attacks bounded?

Confirm that the outbound HTTP client has explicit connect and
read timeouts. Slow-connection attacks (slowloris-style or
intentional hangs from internal services) can consume application
worker pool capacity if requests have no timeout.

What good looks like: outbound clients have explicit connect
timeout (typically 1-5 seconds) and read timeout (typically
5-30 seconds); the timeouts are documented per integration; total
request budget is bounded at the handler level.

What needs follow-up: outbound clients use default infinite
timeouts; a slow internal service causes worker exhaustion; the
timeout policy is not documented.

### 6. Test coverage: are SSRF defenses tested?

Confirm that the application's test suite includes specific cases
for SSRF defense: requests to allowlisted hosts succeed; requests
to non-allowlisted hosts are rejected before connection; requests
to hostnames resolving to private IPs are rejected; redirect
chains to private hosts are rejected.

What good looks like: integration tests use a DNS test fixture
or hosts file override to verify the IP-resolution check;
allowlist tests cover positive and negative cases; redirect
chain tests use a controlled redirect server.

What needs follow-up: SSRF defenses are not tested; only unit
tests of the allowlist exist; no test exercises the full chain
of DNS resolution, IP check, and redirect handling.

### 7. Logging: are SSRF rejections logged?

Confirm that rejected outbound requests appear in the application
log per the logging concern (logging.integrity or equivalent). Systematic
SSRF attempts are detectable from log patterns.

What good looks like: rejections include the rejected URL,
resolved IPs, the rejection reason; an audit dashboard surfaces
rejection rates; log volume reflects rejected vs accepted
outbound traffic.

What needs follow-up: rejections are silent; SSRF attempts are
not detectable from logs; the application does not distinguish
between intentional rejections and other outbound failures.

## Output

Each question receives GOOD, NEEDS FOLLOW-UP, or NOT APPLICABLE
per the standard checklist output convention.
