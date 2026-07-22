---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authorization.audit-events-on-decisions-audit-events-on-decisions"
title: "authorization.audit-events-on-decisions test template: authorization audit events on decisions"
substrate-rule: "authorization.audit-events-on-decisions"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-22"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authorization.audit-events-on-decisions test template: authorization audit events on decisions

## How to use this binding

This binding verifies that authorization decisions emit
structured audit events with the substrate-required content.
The scenarios test both emission (events exist) and content
(events have the right fields, sourced correctly, at the
right severity).

The tests require a mechanism to capture emitted log events
during the test. The substrate-recommended pattern is a test
log handler attached during fixture setup that captures
structured events into an assertable list. The mechanism is
consumer-implemented.

Scenarios verify the authorization.audit-events-on-decisions content requirements
(principal, resource, action, decision, timestamp, severity)
and cross-reference the logging.structured-format (structured), logging.no-sensitive-data-in-logs
(no sensitive data), and logging.correlation-ids (correlation ID) rules.

## Scenario 1: Allow decision emits structured event

**Preconditions**
- Test log handler is attached and captures structured
  events
- A principal P with permission for action A on resource R
- The application's endpoint that requires authorization for
  A on R

**Action**
- P submits a request that triggers an authorization
  decision (allow)

**Expected**
- The captured log contains an event with structured fields:
  - principal field containing P's subject identifier
  - resource field containing R's identifier
  - action field containing A
  - decision field with value "allow"
  - timestamp field in RFC 3339 UTC
  - severity at INFO
  - request correlation ID matching the request's
    correlation ID
- The event is parseable JSON (or equivalent structured
  format)

## Scenario 2: Deny decision emits structured event at higher severity

**Preconditions**
- Principal P without permission for action A on resource R

**Action**
- P submits a request that triggers a deny decision

**Expected**
- The captured log contains an event with the same field
  structure as Scenario 1
- The decision field has value "deny"
- The severity is WARN or higher (per logging.severity-levels severity
  semantics; substrate-recommended WARN minimum for deny)

## Scenario 3: Event includes deny reason where available

**Preconditions**
- The policy point can return a deny reason (e.g., "role
  insufficient", "resource not in scope", "rate limit
  exceeded")
- A principal whose authorization fails for a specific
  reason R_reason

**Action**
- A request that produces a deny with R_reason

**Expected**
- The audit event includes a deny-reason field (optional but
  substrate-recommended for investigative value)
- The deny-reason field does not contain sensitive data
  (e.g., "insufficient role" is fine; "role does not include
  permission to view medical record content X" is not)

## Scenario 4: Principal field comes from authoritative session

**Preconditions**
- A principal P authenticated and bound to session S
- The application accepts a "user_id" field in the request
  body (this field is anti-pattern for testing purposes)

**Action**
- P submits a request with a body field user_id="attacker
  spoofed value" while authenticated as P

**Expected**
- The audit event's principal field contains P's subject
  identifier from the session
- The audit event's principal field does NOT contain the
  request body's user_id value
- The application IGNORES the request-supplied user_id
  field for authorization purposes

Notes: this scenario tests the authorization.audit-events-on-decisions principal-
identity-source requirement. Failure here is a critical
audit-integrity defect.

## Scenario 5: Event does not contain credential material

**Preconditions**
- Test log handler captures events
- The application accepts an Authorization header (Bearer
  token) on the request under test

**Action**
- A request that produces an authorization decision (allow
  or deny)

**Expected**
- The audit event does NOT contain the Bearer token, session
  cookie value, or any other credential material in any
  field
- The audit event does NOT contain the resource's sensitive
  content (medical record body, financial transaction
  details, PII payload) in any field
- The logging.no-sensitive-data-in-logs redaction rules apply to the audit event

## Scenario 6: Event correlates with request telemetry

**Preconditions**
- The application emits a request-start log line with
  correlation ID C_request when the request begins
- Test log handler captures both request-start events and
  audit events

**Action**
- A request that produces an authorization decision

**Expected**
- The audit event includes a correlation ID field with value
  C_request
- The correlation ID in the audit event matches the
  correlation ID in the request-start event
- Investigators can join audit events to other request
  telemetry by correlation ID

## Scenario 7: Bulk operation emits one audit event per decision

**Preconditions**
- The application has a bulk endpoint that processes N
  resources per request
- The bulk endpoint makes N separate authorization decisions

**Action**
- A request that processes 5 resources, 3 allowed and 2
  denied

**Expected**
- The captured log contains 5 audit events, one per decision
- 3 events have decision="allow" with the resource
  identifiers for the allowed resources
- 2 events have decision="deny" with the resource
  identifiers for the denied resources
- All 5 events share the same request correlation ID

Notes: bulk operations are a common audit-coverage gap.
Emitting a single summary event for the bulk request loses
per-resource accountability.

## Scenario 8: Unauthenticated requests emit events with sentinel principal

**Preconditions**
- The application has an endpoint that requires authorization
  but is sometimes hit without authentication (e.g., the
  middleware emits an audit event before rejecting the
  unauthenticated request)

**Action**
- An anonymous client submits a request without any
  authentication credentials

**Expected**
- An audit event is emitted with principal field containing
  a sentinel value (such as "anonymous" or "unauthenticated")
  rather than null or missing
- The decision field has value "deny"
- The severity is WARN or higher

Notes: this scenario is environment-dependent. Some
applications reject unauthenticated requests at a layer
upstream of the policy point and therefore do not emit authz
events for them. The substrate accepts either pattern provided
the application's design is documented.

## Test scaffold: log capture mechanism

Tests require a log capture mechanism. The pattern depends on
the application's logging stack:

```python
# Example test scaffold (Python with structlog)
import structlog
import pytest

class LogCapture:
    def __init__(self):
        self.events = []

    def __call__(self, logger, method, event_dict):
        self.events.append(event_dict)
        return event_dict

@pytest.fixture
def log_capture():
    capture = LogCapture()
    structlog.configure(processors=[capture])
    yield capture
    structlog.reset_defaults()

def test_allow_emits_event(log_capture, authenticated_alice,
                            owned_resource):
    response = authenticated_alice.get(
        f"/resources/{owned_resource.id}"
    )
    assert response.status_code == 200
    authz_events = [e for e in log_capture.events
                    if e.get("event_type") == "authz_decision"]
    assert len(authz_events) >= 1
    event = authz_events[0]
    assert event["decision"] == "allow"
    assert event["principal"] == authenticated_alice.subject_id
    assert event["resource"] == owned_resource.id
```

The scaffold is consumer-implemented; the substrate specifies
the captured-event content requirements without prescribing
the framework.

## Cross-reference

- Substrate rule: authorization.audit-events-on-decisions in catalogs/concerns/authorization.oscal.yaml
- Review checklist binding: checklist.md
- Good examples: examples/authorization/audit-events-on-decisions-good.md
- Anti-patterns: examples/authorization/audit-events-on-decisions-anti-pattern.md
- Related rules: logging.structured-format (structured format), logging.no-sensitive-data-in-logs (no sensitive data), logging.correlation-ids (correlation IDs), logging.severity-levels (severity levels), logging.retention-policy (retention), authorization.centralized-deny-by-default-policy (centralized policy is the substrate-recommended emission site)
