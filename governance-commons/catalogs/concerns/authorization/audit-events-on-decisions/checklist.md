---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.audit-events-on-decisions-audit-events-on-decisions"
title: "authorization.audit-events-on-decisions review checklist: authorization audit events on decisions"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove authorization-check call sites"
  - "Code changes touching the application's audit pipeline or log emission paths"
  - "Code changes adding new resource types that require authorization event coverage"
  - "Security monitoring configuration changes affecting authz event alerting (SIEM rules, alert thresholds)"
  - "Periodic audit pipeline review (substrate-recommended quarterly alongside policy audit)"
---

# authorization.audit-events-on-decisions review checklist: authorization audit events on decisions

## How to use this binding

The checklist pairs with the logging concern's structural rules
(logging.structured-format structured format, logging.no-sensitive-data-in-logs sensitive-data
exclusion, logging.retention-policy retention). authorization.audit-events-on-decisions adds the
authorization-domain requirements on top: which events are
emitted, with which fields, at which severity. Reviewers verify
both axes: the events exist with the required content, and the
events satisfy the logging concern's structural rules.

The substrate cross-references the logging concern rather than
restating it. If a finding here also indicates a logging-concern
failure (e.g., authz events emitted as unstructured strings),
the logging-concern checklist captures the structural defect
and this checklist captures the authorization-specific gap.

Reviewers answer every question below when reviewing pull
requests that match the triggers or when conducting periodic
audit-pipeline reviews. Unanswered items block merge or close
the review cycle.

## Review questions

### 1. Coverage: does every authz decision call site emit an event?

Authorization decisions (both allow and deny) must produce
audit events. The substrate-recommended emission point is the
centralized policy point established by authorization.centralized-deny-by-default-policy: every
call into the policy point emits one event for the decision
returned. This couples emission discipline to policy
centralization, and a single change to the policy-point
implementation covers every caller.

What good looks like: the centralized policy point emits a
structured event for each call; the event-emission path is
unconditional and not feature-flagged on; allow and deny paths
both produce events; non-policy-point authorization checks
(if any exist for documented reasons) also emit events.

What needs follow-up: emission is conditional on log-level or
feature flag (audit events should be unconditional emission
regardless of operational log level); only deny events are
emitted (allow events are required for completeness and post-
incident reconstruction); call sites that bypass the policy
point exist without emission coverage.

### 2. Required fields: do events contain principal, resource, action, decision, timestamp?

Substrate-required event fields are: principal identity (the
subject identifier), resource identifier (the specific object
or resource class targeted), action attempted (read, write,
delete, or application-specific verb), decision (allow or
deny), and timestamp.

What good looks like: every emitted authz event includes all
five required fields; field names follow a documented
convention (substrate-recommended: align with OpenTelemetry
semantic conventions where applicable); field values are
typed consistently (timestamps in a single standard like
RFC 3339 UTC; principal identifiers as opaque subject IDs).

What needs follow-up: events are missing one or more required
fields; field names vary across emission sites (some events
say "user", others "principal", others "actor"); decision is
encoded inconsistently (boolean in some events, string in
others).

### 3. Principal identity source: is the principal from authoritative session, not request?

The principal field in audit events must derive from
authoritative session state established by the application's
authentication layer, not from request fields the attacker
can spoof. An audit event populated from a request header is
populated by the attacker.

What good looks like: the audit-event emission path reads the
principal from the authenticated session context (the same
source the policy point uses for the authorization decision);
unauthenticated request paths emit a sentinel value (such as
"anonymous") or are excluded from authz events as out-of-scope.

What needs follow-up: principal is read from a request header
(X-User-Id, X-Subject, Authorization-User); principal is read
from a request body field; principal is computed by the audit
layer from a token the audit layer itself does not validate.

### 4. Severity assignment: deny at WARN/ERROR, allow at INFO?

The substrate-recommended severity assignment aligns with
logging.severity-levels severity-level conventions. Deny events surface to
security monitoring at a severity that triggers operator
attention (WARN or ERROR per logging.severity-levels severity semantics).
Allow events are emitted at INFO for completeness without
flooding alert pipelines.

What good looks like: deny events at WARN minimum (or ERROR
where the deny correlates with a high-confidence threat
signal); allow events at INFO; the severity assignment is
applied uniformly across emission sites (no allow at WARN, no
deny at INFO).

What needs follow-up: deny events are at INFO and are
invisible to alerting; severity varies inconsistently across
call sites; allow events are at WARN and saturate alert
channels; logging.severity-levels severity definitions are not referenced.

### 5. Sensitive-data exclusion: do events satisfy logging.no-sensitive-data-in-logs?

Authz audit events are log events; logging.no-sensitive-data-in-logs (no sensitive
data in logs) applies. Principal fields must be identifiers,
not credentials. Resource fields must be identifiers, not
content. Decision context must not contain payloads of
sensitive resources.

What good looks like: principal is an opaque subject
identifier; resource is an opaque resource identifier (URL,
ID, ARN-style reference, not the resource's contents); event
content does not include access tokens, session tokens,
passwords, or sensitive resource payloads; the application's
redaction layer (per logging.no-sensitive-data-in-logs) covers authz events.

What needs follow-up: events include token or password values
in any field; events include sensitive resource content
(medical records, financial transaction details, PII payload);
events include attacker-controlled fields that bypass
redaction (free-text fields containing arbitrary request data).

### 6. Structured format: do events satisfy logging.structured-format?

Authz audit events must be structured (JSON or equivalent) per
logging.structured-format to support automated downstream consumption (SIEM,
alerting, dashboard).

What good looks like: events are emitted as structured records
(JSON lines or equivalent); the emission path is the same
structured-logging path the application uses for other
operational logs; events are parseable by the application's
log shipper without text-extraction heuristics.

What needs follow-up: events are emitted as free-text strings
("user fred denied access to resource 42"); structured fields
are concatenated into a single message field; events bypass
the application's structured-log pipeline.

### 7. Retention: do events satisfy logging.retention-policy?

Authz events follow logging.retention-policy retention policy. The
substrate-recommended retention is the longest applicable
regulatory requirement; for many regulated applications this
is multi-year.

What good looks like: the audit-event retention is documented;
the retention duration matches or exceeds the longest
regulatory requirement applicable to the application; the
retention configuration is enforced by the storage layer, not
by hope; periodic verification confirms historical events
remain accessible at the retention horizon.

What needs follow-up: retention is the system default for
operational logs (often 7 to 90 days), shorter than regulatory
requirements; retention is undocumented; retention enforcement
relies on operator memory rather than automated policy.

### 8. Security monitoring integration: are deny events consumed by SIEM or equivalent?

Deny events at security-monitoring severity surface anomalous
patterns: spikes of denied attempts on the same resource
(enumeration), denied attempts from one principal across many
resources (compromised principal probing), repeated deny on a
sensitive resource (targeted attack). The deny stream is
useful only when consumed by monitoring tooling.

What good looks like: the application's SIEM (or equivalent
security monitoring platform) ingests the deny event stream;
alert rules are configured for the patterns the application's
threat model identifies; alert rules have documented owners
and runbooks.

What needs follow-up: deny events are written to logs but
never consumed by security monitoring; SIEM ingests events but
no alert rules are configured; alert rules exist but have no
documented response runbook; alert thresholds are at default
values without tuning to the application's traffic baseline.

### 9. Correlation: are events correlated with request context?

Authz events benefit from request-correlation identifiers that
join them to the rest of the application's request telemetry.
logging.correlation-ids (correlation IDs) provides the structural rule;
this question verifies authz events participate.

What good looks like: every authz event includes a request
correlation ID; the correlation ID is the same one the
application's other request telemetry carries; investigators
can join authz events to application logs and traces by
correlation ID.

What needs follow-up: authz events are emitted without
correlation IDs; the correlation ID is present but does not
match the application's other telemetry's correlation
scheme; the correlation ID is generated per emission rather
than per request.

### 10. Testing: is event emission verified by tests?

Audit events must be a tested behavior, not an aspirational
behavior. The paired test-template binding provides scenarios;
this question confirms the consumer has implemented them.

What good looks like: tests assert that allow and deny
decisions produce events with the required fields; tests
assert deny-event severity is WARN or ERROR; tests assert
sensitive-data exclusion (events do not contain credential
material in any field); the test suite is part of the
application's CI gate.

What needs follow-up: no tests assert event emission; tests
assert events exist but do not verify field content; tests
verify allow events but not deny events; tests run only in
local environments and are not part of CI.

## Reviewer attestation

```
authorization.audit-events-on-decisions review checklist: complete
- Coverage at every decision call site: PASS / FOLLOW-UP / EXEMPT
- Required fields present: PASS / FOLLOW-UP / EXEMPT
- Principal from authoritative session: PASS / FOLLOW-UP / EXEMPT
- Severity assignment (deny WARN/ERROR, allow INFO): PASS / FOLLOW-UP / EXEMPT
- Sensitive-data exclusion (logging.no-sensitive-data-in-logs): PASS / FOLLOW-UP / EXEMPT
- Structured format (logging.structured-format): PASS / FOLLOW-UP / EXEMPT
- Retention (logging.retention-policy): PASS / FOLLOW-UP / EXEMPT
- SIEM consumption with alert rules: PASS / FOLLOW-UP / EXEMPT
- Correlation ID present (logging.correlation-ids): PASS / FOLLOW-UP / EXEMPT
- Emission verified by tests: PASS / FOLLOW-UP / EXEMPT
```

When all questions pass, authorization.audit-events-on-decisions is satisfied for the
reviewed code changes. Findings marked FOLLOW-UP block merge
until resolved. Findings marked EXEMPT must reference an
accepted exemption record in the application's risk register.

## Cross-reference

- Substrate rule: authorization.audit-events-on-decisions in catalogs/concerns/authorization.oscal.yaml
- Test template binding: test-template.md
- Good examples: examples/authorization/audit-events-on-decisions-good.md
- Anti-patterns: examples/authorization/audit-events-on-decisions-anti-pattern.md
- Related logging rules: logging.structured-format, logging.no-sensitive-data-in-logs, logging.correlation-ids, logging.severity-levels, logging.retention-policy
- Related authz rule: authorization.centralized-deny-by-default-policy (centralized policy point is the substrate-recommended emission site)
