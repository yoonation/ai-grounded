---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.logging.integrity-integrity"
title: "logging.integrity review checklist: log integrity controls"
substrate-rule: "logging.integrity"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New log streams added that carry authentication, authorization, or administrative-action events"
  - "Changes to log aggregation pipelines affecting storage tier or access"
  - "Substrate-recommended quarterly integrity verification exercise"
  - "Incident response review identifying suspected log tampering"
---

# logging.integrity review checklist: log integrity controls

## How to use this binding

Reviewers answer every question below when reviewing pull
requests that match the review triggers, or during the periodic
verification. Unanswered items block merge or escalate as
findings.

## Review questions

### 1. Are security-relevant log streams identified?

Not all logs need the same integrity protection. Audit logs
(authentication, authorization, admin actions) need strong
protection; debug logs typically do not.

What good looks like: streams carrying authentication events,
authorization decisions, administrative actions, and security
events are explicitly identified in the logging architecture
ADR (logging.architecture); the identification is reviewed when new
event types are added.

What needs follow-up: all log streams treated identically
(under- or over-protection); identification is implicit ("we
think these are the audit logs"); new high-value event types
added without revisiting the identification.

### 2. Is an integrity mechanism documented and deliberately chosen?

The substrate accepts multiple mechanisms but requires the
choice be explicit.

Substrate-recognized mechanisms:
- Append-only or write-once log stores (cloud-native log
  services with immutability configured, object-lock storage
  with governance or compliance retention)
- Per-record or per-segment hash chains with periodic
  publication of the chain head
- Centralized SIEM with administrative isolation from
  application teams
- Signed log records produced by a trusted shipper

What good looks like: the ADR specifies which mechanism applies
to which streams; the choice is reasoned (threat model, cost,
operational maturity); the substrate-acceptable alternatives
considered are documented.

What needs follow-up: integrity is asserted but no mechanism
is named; multiple mechanisms are claimed but none is fully
configured; the choice is "the aggregator does it" without
verification.

### 3. Is the chosen mechanism actually configured?

Many aggregators support immutability flags or object-lock but
ship with the feature unset. Asserting protection without
verifying configuration is a recurring audit failure.

What good looks like: configuration is inspected (aggregator
console, cloud CLI, Terraform plan output) and confirmed to
match the documented mechanism; an attempted destructive
operation in a test environment is blocked as expected; the
verification is documented.

What needs follow-up: configuration is assumed but not
inspected; configuration is inspected once at deployment but
not re-verified; configuration drifts (e.g., a Terraform
change removes the lock and it is not noticed).

### 4. Is access to modify integrity configuration restricted?

The mechanism is only as strong as the access controls
governing it. If application admins can disable immutability,
the protection is theatrical.

What good looks like: separation of duty between application
teams and the team that controls the integrity configuration;
the security team or platform team owns the configuration;
changes require an out-of-band approval; the approval audit
trail exists separately from the logs being protected.

What needs follow-up: application admins have full control of
the integrity configuration; configuration changes do not
require approval; the audit trail for configuration changes
resides in the same store as the protected logs (which
defeats the purpose).

### 5. Are integrity verification exercises performed periodically?

Configuration drift, software upgrades, and operational
mistakes can silently disable integrity protection. Periodic
exercises catch this.

What good looks like: a documented exercise (substrate-
recommended quarterly) verifies the protection still holds;
the exercise includes an attempted modification and confirms
it is blocked; results are documented; failures trigger
remediation.

What needs follow-up: no documented exercise; exercise exists
but is performed annually with months of unverified drift;
exercise is performed but failures are not tracked to
resolution.

### 6. For hash-chain mechanisms: is the chain head published externally?

Hash chains protect against modification only if the chain
head is published outside the system under attack. Otherwise
an attacker who modifies the log can re-compute the chain.

What good looks like: chain heads are published to an external
attestation service (substrate-acceptable: a write-only
external store, a public blockchain, a separately-administered
notarization service); publication cadence is documented;
verification against the published heads is performed
periodically.

What needs follow-up: chain heads exist but are stored
alongside the logs (no external publication); publication
cadence is unclear or has gapped; verification against
published heads is never performed.

### 7. For SIEM centralization: is administrative isolation real?

SIEM-based integrity depends on application teams not having
administrative access to the SIEM. The substrate's review
asks whether the isolation is configured, not just intended.

What good looks like: SIEM access is governed by a different
IAM root or directory than application access; application
admins cannot grant themselves SIEM access; the SIEM team is
a distinct operational team.

What needs follow-up: application admins have SIEM access via
group membership inheritance; SIEM IAM is in the same
directory as application IAM with weak separation; the SIEM
team is the same as the application team.

### 8. Is the integrity story consistent across stream paths?

A log that travels through multiple hops (application → log
shipper → aggregator → archival) has integrity at each hop or
none. Integrity at the archival tier but not in transit
leaves a tamper window.

What good looks like: integrity is end-to-end (signed at the
producer or TLS plus auth between hops, retained at the
aggregator and archival); the policy documents the end-to-end
chain.

What needs follow-up: integrity protection at one tier but
not others; ad-hoc trust assumptions (e.g., "the network is
isolated, so transit integrity does not matter"); the chain
includes a third-party SaaS hop where the consumer cannot
attest to integrity.

## Reviewer attestation

```
logging.integrity review checklist: complete
- Stream identification: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Documented mechanism: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Configured mechanism: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Access restriction: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Verification exercises: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Hash-chain publication (if applicable): PASS / FOLLOW-UP / NA
- SIEM isolation (if applicable): PASS / FOLLOW-UP / NA
- End-to-end consistency: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: logging.integrity in catalogs/concerns/logging.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/logging/integrity-good.md
- Anti-patterns: examples/logging/integrity-anti-pattern.md
