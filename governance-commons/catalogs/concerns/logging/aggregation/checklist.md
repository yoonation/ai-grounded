---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.logging.aggregation-aggregation"
title: "logging.aggregation review checklist: log aggregation and search readiness"
substrate-rule: "logging.aggregation"
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
  - "New service brought into production"
  - "Changes to log shipping infrastructure"
  - "Substrate-recommended quarterly aggregation readiness check"
  - "Incident retrospectives identifying aggregation gaps"
---

# logging.aggregation review checklist: log aggregation and search readiness

## How to use this binding

Reviewers answer every question below when reviewing pull
requests that match the review triggers, or during the periodic
readiness check.

## Review questions

### 1. Are all production log streams shipped to the centralized aggregator?

Host-local logs die with the host. Centralization is the
prerequisite for incident response across the fleet.

What good looks like: every production service ships its
logs to the central aggregator; new services are required to
ship as part of the production-readiness checklist; the
aggregator's source inventory matches the production service
inventory.

What needs follow-up: some services do not ship logs (gap in
incident response capability); shipping is configured but
fails silently (logs do not arrive); host-local logs are
retained as the primary record (operationally fragile).

### 2. Does the aggregator support full-text or structured-field search?

Search readiness is the minimum useful capability. An
aggregator that retains logs but does not allow query against
them is operationally useless.

What good looks like: search across the hot retention tier
returns results in sub-second time for typical queries;
indexed fields include severity (logging.severity-levels), correlation IDs
(logging.correlation-ids), and service identifiers; the substrate-
recommended aggregator capability list is met.

What needs follow-up: search is supported but slow (multi-
minute query times that defeat incident response under
pressure); only some fields are indexed (operational fields
indexed, security-relevant fields not); search is supported
only on a small recent window (the hot tier is small).

### 3. Does the aggregator support time-ranged queries?

Incident response works in time windows. An aggregator that
cannot answer "what happened between 14:32 and 14:35?" is
operationally insufficient.

What good looks like: time-range queries with sub-second
response on the hot tier; time-range queries against cold
storage are supported, with longer response times accepted;
the aggregator's time-range UI is exercised in incident
drills.

What needs follow-up: time-range queries require full-text
scan (slow); time-range queries against cold storage are not
supported or require ad-hoc retrieval procedures; the time-
range tooling is not exercised, so its limits surface during
incidents.

### 4. Does the aggregator support cross-service join on correlation IDs?

Cross-service correlation is the question incident response
asks most often: "what else happened during this user's
request?"

What good looks like: queries joining records by trace_id,
request_id, or session_id return results across services;
joins span the full hot retention; the join syntax is
documented in the operational runbook.

What needs follow-up: join is technically possible but
operationally painful (no documented syntax, slow); join
requires per-service queries followed by manual correlation
(the aggregator does not handle the join itself); the join
fails when services have inconsistent correlation field
names.

### 5. Is access control configured with separation from application admins?

Per logging.integrity integrity, log access should be governed by
roles distinct from application administrative access.

What good looks like: aggregator access uses a separate role
or group from application admin access; the security team has
read access without application admin privilege; the
aggregator audit log captures access events and is itself
protected.

What needs follow-up: application admins inherit aggregator
admin access through group nesting; security team must
request access ad hoc through application admins;
aggregator audit log is missing or accessible to the people
it is supposed to audit.

### 6. Is per-stream latency monitored and bounded?

Log shipping that batches with hour-scale delay produces an
effective operational blackout during incidents. The
substrate-recommended bound for security-event streams is
sub-minute.

What good looks like: per-stream latency from producer to
aggregator is monitored; latency alerts fire when it exceeds
the documented bound; security-event streams have stricter
bounds than operational streams.

What needs follow-up: latency is unmeasured; "logs arrive
eventually" is the implicit SLA; batched ingestion windows
exceed the time scale of typical incidents (multi-hour delay
is normal).

### 7. Is the shipping pipeline operationally monitored?

The shipping pipeline itself is a service whose failure
silently breaks logging. It needs operational monitoring.

What good looks like: log shippers (Vector, Fluent Bit,
OpenTelemetry Collector, cloud-native agents) emit
operational metrics; alerts fire on shipper failure or
backpressure; failed shipments are queued or retried.

What needs follow-up: shipper health is not monitored; a
shipper failure goes undetected until incident response
notices missing logs (delayed by definition); failed
shipments are dropped silently.

### 8. Are query examples documented for common incident-response patterns?

Aggregator queries are easy to author at scale but hard to
remember under incident pressure. Documented examples reduce
time to insight.

What good looks like: an operational runbook contains
templates for common queries (authentication failures by
user, 5xx responses by endpoint, errors during a deploy
window); the templates are exercised in incident drills;
new query patterns are added after each incident as part of
the retrospective.

What needs follow-up: queries exist only as tribal knowledge;
incident response involves on-the-fly query authoring under
pressure; queries from past incidents are not preserved for
reuse.

## Reviewer attestation

```
logging.aggregation review checklist: complete
- All streams shipped: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Search capability: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Time-range queries: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cross-service join: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Access control separation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Latency monitoring: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Shipping pipeline monitoring: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Documented query examples: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: logging.aggregation in catalogs/concerns/logging.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/logging/aggregation-good.md
- Anti-patterns: examples/logging/aggregation-anti-pattern.md
