---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.observability.semantic-convention-coverage-semantic-convention-coverage"
title: "observability.semantic-convention-coverage test template: semantic convention coverage"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# observability.semantic-convention-coverage test template: semantic convention coverage

## How to use this binding

Semantic convention coverage tests exercise the service's
instrumentation against a controlled load that exercises HTTP,
database, messaging, and RPC code paths. Tests capture the
emitted spans (via an in-process span processor or a test
collector) and assert against the required attribute sets.
Substrate-recommended cadence: CI integration test on every
pull request affecting instrumentation; periodic
(substrate-recommended quarterly) production verification
via the trace backend.

## Scenario 1: HTTP server spans carry required attributes

**Preconditions**
- Service is instrumented for HTTP server (auto-instrumentation
  or explicit interceptor)
- A test span collector or in-process exporter is attached
- The service exposes a representative HTTP route (e.g., a
  health check or a known fixture endpoint)

**Action**
- Issue a single HTTP request to the route
- Capture the resulting server-kind span

**Expected**
- Span kind is SERVER
- Attribute http.request.method is present and matches the
  request method
- Attribute http.route is present and is the templated route
  pattern (not the substituted URL)
- Attribute http.response.status_code is present and matches
  the response
- Attribute server.address is present
- No attribute carries sensitive data (cross-check observability.no-sensitive-data-in-telemetry)

## Scenario 2: HTTP client spans carry required attributes

**Preconditions**
- Service makes outbound HTTP calls to a controlled stub
- The HTTP client is instrumented (cross-check observability.trace-context-propagation)
- Span collector is attached

**Action**
- Issue an HTTP request from the service to the stub
- Capture the resulting client-kind span

**Expected**
- Span kind is CLIENT
- Attribute http.request.method is present
- Attribute url.full or url.scheme + url.host + url.path is
  present
- Attribute http.response.status_code is present
- Attribute server.address is present
- The span is correctly parented to the originating request's
  server span

## Scenario 3: Database spans carry required attributes

**Preconditions**
- Service uses a database client (postgresql, mysql, mongodb,
  redis, etc.)
- The database client is instrumented
- Span collector is attached
- A representative query fixture (a SELECT against a test
  table) is available

**Action**
- Execute the query
- Capture the resulting database span

**Expected**
- Span kind is CLIENT
- Attribute db.system is present and uses an OpenTelemetry
  registry value (postgresql, mysql, mongodb, redis, etc.)
- Attribute db.operation is present and identifies the
  operation kind (SELECT, INSERT, command name)
- Attribute db.namespace or db.name is present
- Attribute db.statement is either absent or carries a
  parameterized form without substituted sensitive values
  (cross-check observability.no-sensitive-data-in-telemetry)

## Scenario 4: Messaging spans carry required attributes

**Preconditions**
- Service publishes to and consumes from a controlled queue
  (kafka, rabbitmq, sqs, etc.) test instance
- Messaging client is instrumented
- Span collector is attached

**Action**
- Publish a test message; consume it
- Capture the producer-kind and consumer-kind spans

**Expected**
- Producer span has kind PRODUCER
- Consumer span has kind CONSUMER
- Both spans carry messaging.system (registry value)
- Both spans carry messaging.destination.name
- Both spans carry messaging.operation matching the operation
- Consumer span is linked to producer span via trace context
  through message headers

## Scenario 5: RPC spans carry required attributes

**Preconditions**
- Service has a gRPC client or server
- The gRPC instrumentation is enabled
- Span collector is attached

**Action**
- Issue a gRPC call (client side, or a server-side fixture
  request)
- Capture the resulting span

**Expected**
- Span kind matches the role (CLIENT for outbound gRPC,
  SERVER for inbound)
- Attribute rpc.system is "grpc"
- Attribute rpc.service is the fully-qualified protobuf
  service name
- Attribute rpc.method is the method name
- The span is correctly parented

## Scenario 6: Convention version is recorded

**Preconditions**
- Service emits the OpenTelemetry semantic conventions
  schema URL on its resource

**Action**
- Capture a sample of resource attributes from the service's
  emitted telemetry

**Expected**
- The resource carries a schema URL identifying the
  OpenTelemetry semantic conventions version the service
  follows
- The schema URL points to a version the consumer's
  instrumentation ADR documents

## Scenario 7: Negative test: span without required attribute fails

**Preconditions**
- A test fixture handler that explicitly omits a required
  attribute (e.g., does not set http.route)

**Action**
- Run the test exercising the fixture handler
- Apply the convention-coverage assertion suite

**Expected**
- The assertion suite fails on the missing http.route
- The failure message identifies the missing attribute, the
  span kind, and the source code location of the emission
- The test catches the case before merge

## Cross-reference

- Substrate rule: observability.semantic-convention-coverage in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Good examples: examples/observability/semantic-convention-coverage-good.md
- Anti-patterns: examples/observability/semantic-convention-coverage-anti-pattern.md
