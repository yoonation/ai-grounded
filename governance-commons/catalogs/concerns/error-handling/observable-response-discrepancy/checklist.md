---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.error-handling.observable-response-discrepancy-observable-response-discrepancy"
title: "error-handling.observable-response-discrepancy review checklist: observable response discrepancy"
substrate-rule: "error-handling.observable-response-discrepancy"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-24"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove resource-access endpoints"
  - "Code changes that touch authorization decisions tied to resource existence"
  - "Code changes that modify error response shapes for \"not found\" or \"forbidden\" cases"
  - "Code review of new endpoints that return information about resource existence"
  - "Periodic enumeration-resistance self-assessment"
---

# error-handling.observable-response-discrepancy review checklist: observable response discrepancy

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with authentication.generic-failure-responses (generic error messages on
authentication failure, the credential-specific case) and
authorization.object-level-authorization (object-level authorization, the authorization
decision side). error-handling.observable-response-discrepancy covers the broader resource-existence
case where the response differential between "not found" and
"unauthorized" enables enumeration.

## Review questions

### 1. Status uniformity: do "not found" and "unauthorized" return the same status?

Confirm that resource-access endpoints return the same HTTP
status code for "resource does not exist" and "resource exists
but principal is not authorized to see it." Substrate-
recommended: 404 Not Found for both, treating the response
from the unauthorized principal's perspective as "the resource
is not visible."

What good looks like: the endpoint's response branch returns
404 regardless of whether the underlying cause was missing
resource or failed authorization; the response body shape is
the same; the Problem Details type URI is the same.

What needs follow-up: the endpoint returns 404 for missing
and 403 for unauthorized; clients can enumerate valid
resource IDs by probing for 403 vs 404; the response shape
differs (different fields, different sizes).

### 2. Shape uniformity: is the response body identical across the two cases?

Confirm that the response body shape is byte-equivalent (or
near-byte-equivalent) for the two cases. The detail field,
instance field, and any other shape variations are identical.

What good looks like: both cases produce the same JSON
structure; the detail field uses the same phrasing; the
response size is the same within a small jitter range.

What needs follow-up: the unauthorized response includes
additional fields (the principal's role, the missing
permission); the not-found response includes fewer fields;
response sizes differ noticeably.

### 3. Timing uniformity: are response timings within a similar range?

Confirm that response timings for "not found" and "unauthorized"
are within a range that does not enable timing-based
enumeration. Sub-millisecond differences are acceptable; tens-
of-milliseconds differences (caused by short-circuiting the
authorization check, by different database query paths, by
different cache behavior) are enumeration vectors.

What good looks like: the response timing for both cases is
within 5ms (typical) or within the standard jitter range; the
authorization check runs after the existence check (so the
existence check does not short-circuit), or the response is
explicitly normalized to constant time.

What needs follow-up: the unauthorized case is consistently
slower than the not-found case (because authorization
involves additional database queries); the not-found case is
faster (because it does not run the authorization check);
timing measurements during testing show systematic
differences.

### 4. Ordering: does the authorization check sequence avoid leak?

Confirm that the ordering of existence-check and authorization-
check does not produce observable differences. Substrate-
preferred ordering: existence check first, authorization check
second, with both contributing to the same response branch;
alternative: constant-time response regardless of path.

What good looks like: the endpoint's code path executes both
checks before constructing the response; the response is
constructed from the combined result; no early-return
shortcut bypasses either check.

What needs follow-up: the endpoint short-circuits to 403
when authorization fails (before the existence check); the
endpoint short-circuits to 404 when the resource is missing
(before the authorization check); the short-circuits
produce different response paths.

### 5. Application coverage: is the discipline applied across the surface?

Confirm that the discipline is applied across all endpoints
exposing resource existence (read endpoints, update endpoints,
delete endpoints, list endpoints). The list-endpoint case is
particularly subtle: a list filtered by a non-existent owner
should not differ from a list filtered by an owner whose
resources the principal is not authorized to see.

What good looks like: every endpoint follows the same
discipline; reviews verify across the surface; the ADR
documents the discipline.

What needs follow-up: read endpoints follow the discipline
but update and delete endpoints do not (because the
attacker can probe via PUT and DELETE); list endpoints
distinguish empty-because-missing from empty-because-
unauthorized.

### 6. Log differentiation: do server-side logs preserve the distinction?

Confirm that server-side logs preserve the distinction (the
operator needs to know whether the request was missing-
resource or unauthorized for forensic analysis), even though
the client-facing response does not. The log entry is at the
LOG-L2 layer per the logging concern; error-handling.observable-response-discrepancy references
this expectation.

What good looks like: the log entry distinguishes the two
cases via a structured field (outcome=not-found vs
outcome=unauthorized); the principal's ID is logged for the
unauthorized case; correlation IDs flow through per logging.correlation-ids.

What needs follow-up: the log entry has the same shape as
the client response; the operator cannot distinguish the two
cases from logs; forensic analysis requires reconstructing
the case from auxiliary signals.

### 7. Test coverage: are enumeration-probe tests in place?

Confirm that the application has integration tests that
exercise the enumeration-probe surface: paired requests for
a missing resource and an existing-but-unauthorized resource,
with assertions that the responses are equivalent.

What good looks like: a test suite explicitly exercises the
discrepancy surface; tests would fail if a future change
introduced a discrepancy; tests cover read, update, delete,
and list endpoints.

What needs follow-up: no enumeration-probe tests exist;
discrepancies could be reintroduced without detection in
CI; the test suite covers only positive paths.

## Output

Each question receives one of three answers: GOOD (the rule's
expectation is met), NEEDS FOLLOW-UP (the rule's expectation is
not met; remediation required before merge), or NOT APPLICABLE
(the question does not apply to this change; the reviewer
documents why).

NEEDS FOLLOW-UP answers block merge until resolved. NOT APPLICABLE
answers require a one-line justification in the review thread.
