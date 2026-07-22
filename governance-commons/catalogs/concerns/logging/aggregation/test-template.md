---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.logging.aggregation-aggregation"
title: "logging.aggregation test template: log aggregation and search readiness"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# logging.aggregation test template: log aggregation and search readiness

## How to use this binding

Aggregation tests verify shipping, indexing, search, latency,
and cross-service join capabilities. Some scenarios run as
integration tests against a real aggregator; others as
production verification exercises (substrate-recommended
quarterly).

## Scenario 1: Production log streams reach the aggregator within latency bound

**Preconditions**
- A production service is producing logs
- The documented latency bound for the stream is recorded (e.g.,
  sub-minute for security streams)

**Action**
- Emit a sentinel log record at the producer with a unique
  identifier
- Time the producer-to-aggregator latency by querying the
  aggregator for the sentinel

**Expected**
- The sentinel appears in the aggregator within the documented
  bound
- Latency is monitored continuously, not just at test time
- Latency alerts fire when the bound is exceeded

## Scenario 2: Full-text or structured-field search returns results in sub-second time

**Preconditions**
- The aggregator hot tier holds a known volume of records
- A search query against a known indexed field is prepared

**Action**
- Execute the search query
- Measure response time

**Expected**
- The search returns results in sub-second time on the hot tier
- Indexed fields include severity, correlation IDs, and service
  identifiers
- The substrate-recommended capability list is satisfied

## Scenario 3: Time-range query returns expected records

**Preconditions**
- Records exist across a known time window
- A time-range query for that window is prepared

**Action**
- Execute the time-range query
- Verify the result set matches expectation

**Expected**
- The time-range query returns all records within the window
- No records outside the window are returned
- Response time is acceptable for the hot tier

## Scenario 4: Cross-service join on correlation ID succeeds

**Preconditions**
- A trace traverses multiple services
- Each service emits log records tagged with the shared
  trace_id

**Action**
- Query the aggregator for all records matching the trace_id

**Expected**
- The query returns records from every service the trace
  traversed
- The records are correlatable in time order
- The join syntax is documented in the operational runbook

## Scenario 5: Access control prevents application admin from accessing audit streams

**Preconditions**
- An application admin account exists
- Audit log streams are configured with access control
  restricting application admins

**Action**
- Using application admin credentials, attempt to query the
  audit log streams

**Expected**
- The query is rejected by the aggregator's access control
- An audit event records the denied access
- The security team's role can query the audit streams

## Scenario 6: Shipping pipeline failure produces an alert

**Preconditions**
- Log shippers are deployed at producing services
- Shipper health metrics are monitored

**Action**
- Simulate a shipper failure (stop the shipper container, block
  network egress, exhaust the shipper's disk)
- Wait for the monitoring system to detect

**Expected**
- A monitoring alert fires for shipper failure
- The alert includes the affected service and stream
- Failed shipments are queued or retried per the shipping
  configuration

## Scenario 7: A new service onboarding produces shipping configuration

**Preconditions**
- A new service is being added to production
- The production-readiness checklist requires log shipping

**Action**
- Follow the new-service onboarding procedure
- Verify the procedure produces shipping configuration

**Expected**
- The new service ships logs to the aggregator after onboarding
- The service appears in the aggregator's source inventory
- Latency and shipping health are monitored for the new stream

## Scenario 8: Common incident-response queries are documented and executable

**Preconditions**
- The operational runbook contains query templates for common
  incident patterns
- The aggregator supports the query language used in the
  templates

**Action**
- Execute each documented query against test data

**Expected**
- Each query executes without error
- Each query returns the expected result on test data
- Queries are kept current as the application's log schema
  evolves

## Test attestation

```
logging.aggregation test suite: PASSING
- Scenario 1 (latency within bound): PASS
- Scenario 2 (search returns sub-second): PASS
- Scenario 3 (time-range query): PASS
- Scenario 4 (cross-service join): PASS
- Scenario 5 (access control restricts application admin): PASS
- Scenario 6 (shipping failure produces alert): PASS
- Scenario 7 (new service onboarding ships logs): PASS
- Scenario 8 (incident-response queries executable): PASS
```

## Cross-reference

- Substrate rule: logging.aggregation
- Review checklist: checklist.md
- Good examples: examples/logging/aggregation-good.md
