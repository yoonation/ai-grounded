---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.observability.semantic-convention-coverage-semantic-convention-coverage"
title: "observability.semantic-convention-coverage review checklist: semantic convention coverage"
substrate-rule: "observability.semantic-convention-coverage"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-21"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New HTTP routes, new database clients, new message queues, new gRPC services"
  - "Migration between instrumentation libraries"
  - "New tracing backend integration"
  - "Substrate-recommended quarterly span attribute audit"
---

# observability.semantic-convention-coverage review checklist: semantic convention coverage

## How to use this binding

Reviewers answer every question below when reviewing pull
requests matching the review triggers, or during the periodic
self-assessment. Unanswered items block merge or escalate as
findings in the self-assessment.

The reviewer captures a representative trace from a non-
production environment before answering: a single trace
spanning the affected service's typical request path provides
the concrete data the questions ask about.

## Review questions

### 1. Do HTTP server spans carry the required semantic-convention attributes?

The OpenTelemetry HTTP semantic conventions specify the
attribute set every HTTP server span carries. Cross-service
tooling depends on the convention being followed.

What good looks like: spans of kind SERVER for HTTP requests
carry http.request.method, http.route (the templated route
pattern, not the substituted URL), http.response.status_code,
and server.address. Attribute names match the OpenTelemetry
spelling exactly (http.request.method, not http.method or
http_method). Auto-instrumentation packages provide these by
default; the review confirms the packages are active.

What needs follow-up: span kinds are unset or wrong (e.g.,
INTERNAL where SERVER is required); http.route is set to the
substituted URL (which inflates trace explorer cardinality);
attribute names use local conventions (path, method, status)
instead of OpenTelemetry conventions; auto-instrumentation is
not active and manual setters use ad-hoc names.

### 2. Do HTTP client spans carry the required attributes?

What good looks like: spans of kind CLIENT for outbound HTTP
calls carry http.request.method, url.full (or
url.scheme/url.host/url.path equivalents), http.response.status_code,
server.address. Auto-instrumentation provides these for the
client libraries the consumer uses.

What needs follow-up: outbound spans missing url attributes
(reviewers cannot identify the downstream system); url.full
carries query parameters with sensitive data (a separate
observability.no-sensitive-data-in-telemetry violation surfaces here); auto-instrumentation
omits the response status because exception paths skip the
status setter.

### 3. Do database spans carry the required attributes?

What good looks like: spans of kind CLIENT for database
operations carry db.system (one of postgresql, mysql,
mongodb, redis, etc. per the OpenTelemetry registry),
db.operation (SELECT, INSERT, UPDATE, DELETE, command name
for non-SQL), db.namespace or db.name where applicable. The
db.statement attribute is set only when the consumer has
verified the statement does not contain sensitive parameter
values (cross-reference observability.no-sensitive-data-in-telemetry).

What needs follow-up: db.system uses a non-registry value
(e.g., "postgres" instead of "postgresql"); db.operation is
missing; db.statement contains substituted parameter values
(observability.no-sensitive-data-in-telemetry cross-violation); separate spans for connection
pool acquisition and query execution are not distinguished by
their attributes.

### 4. Do messaging spans carry the required attributes?

What good looks like: spans of kind PRODUCER and CONSUMER
for messaging operations carry messaging.system (kafka,
rabbitmq, sqs, etc.), messaging.destination.name (topic,
queue, exchange), messaging.operation (publish, receive,
process). Message-specific attributes (messaging.message.id,
messaging.kafka.partition) follow OpenTelemetry conventions
where applicable.

What needs follow-up: messaging operations modeled as INTERNAL
or CLIENT spans instead of PRODUCER/CONSUMER; destination
attribute missing or set to a vendor-specific opaque
identifier instead of the destination name; consumer-side
spans not linked to producer-side spans via trace context
through message headers.

### 5. Do RPC spans carry the required attributes?

What good looks like: spans for gRPC operations carry rpc.system
(grpc, apache_dubbo, etc.), rpc.service (the fully-qualified
service name), rpc.method (the method name within the service).
gRPC client and server spans are both annotated; the
opentelemetry-instrumentation-grpc package provides these by
default.

What needs follow-up: gRPC spans modeled as generic HTTP spans
(losing the rpc.* attribute structure); rpc.service set to a
local name rather than the fully-qualified protobuf service
name; rpc.method missing.

### 6. Are span kinds correctly assigned across the service?

What good looks like: span kinds follow the OpenTelemetry
specification: SERVER for inbound requests being processed by
the service; CLIENT for outbound calls the service makes;
INTERNAL for service-internal operations; PRODUCER for
emitting messages to a queue; CONSUMER for receiving messages
from a queue. The kind assignment is consistent across the
service.

What needs follow-up: spans default to INTERNAL because the
instrumentation library does not set the kind explicitly;
SERVER spans appear in places where CLIENT was expected
(misconfigured instrumentation order); INTERNAL spans wrap
what should be CLIENT spans, hiding the downstream dependency.

### 7. Are deviations from the OpenTelemetry conventions documented?

The substrate accepts deviation from the conventions when the
consumer's service has a structural reason (a protocol
OpenTelemetry does not yet cover; a domain-specific attribute
set the consumer's tooling depends on). The deviation must be
documented.

What good looks like: deviations are recorded in the
consumer's instrumentation ADR (or equivalent service-level
documentation); the deviation cites the structural reason; a
periodic review (substrate-recommended quarterly) confirms
the reason still applies.

What needs follow-up: deviation exists without documentation;
the deviation was driven by a one-time fix that became the
permanent state; the consumer's tooling depends on the
deviation and migrating to OpenTelemetry conventions is
deferred indefinitely.

### 8. Are span attribute names verified against an upgrade-stable convention?

OpenTelemetry semantic conventions have a lifecycle; some
attributes are at stable lifecycle, others at experimental.
Consumers should depend on stable conventions where possible
and document use of experimental ones.

What good looks like: the consumer's instrumentation uses
attributes from the stable convention set where stable
versions exist; use of experimental attributes is documented
with awareness of upgrade risk; the consumer reviews
convention updates on a substrate-recommended quarterly
cadence.

What needs follow-up: instrumentation uses experimental
attributes broadly without awareness; convention updates
break instrumentation periodically because no review process
exists; the consumer has not tracked OpenTelemetry releases.

## Reviewer attestation

```
observability.semantic-convention-coverage review checklist: complete
- HTTP server attributes: PASS / FOLLOW-UP / EXEMPT-with-rationale
- HTTP client attributes: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Database attributes: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Messaging attributes: PASS / FOLLOW-UP / EXEMPT-with-rationale
- RPC attributes: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Span kinds: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Deviations documented: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Convention stability tracked: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: observability.semantic-convention-coverage in catalogs/concerns/observability.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/observability/semantic-convention-coverage-good.md
- Anti-patterns: examples/observability/semantic-convention-coverage-anti-pattern.md
