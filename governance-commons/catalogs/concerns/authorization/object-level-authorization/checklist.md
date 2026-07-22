---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.object-level-authorization-object-level-authorization"
title: "authorization.object-level-authorization review checklist: object-level authorization"
substrate-rule: "authorization.object-level-authorization"
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
  - "Code changes that add, modify, or remove API endpoints accepting object identifiers"
  - "Code changes that touch resource fetch or authorization logic on existing endpoints"
  - "Code changes adding new resource types with associated CRUD endpoints"
  - "Periodic API security self-assessment"
---

# authorization.object-level-authorization review checklist: object-level authorization

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling (GitHub PR template, GitLab MR
approval rules, Gerrit code-review labels).

The checklist pairs with authorization.authz-before-resource-access's mechanical detection. L1
catches "no authz call before resource access"; this L2 review
confirms "the authz call evaluates the right subject-resource
pair." This is the OWASP API Security Top 10 API1:2023 Broken
Object Level Authorization concern.

## Review questions

### 1. Identifier source: where does the resource identifier come from?

Confirm whether the resource identifier in question reaches the
handler from a client-supplied source (URL path parameter, query
string field, request body field, GraphQL argument, header). If
the identifier is server-derived (looked up from the principal's
session, computed from a context the principal does not control),
per-object authorization is not required at this call site;
class-level authorization is sufficient.

What good looks like: identifier source is documented in the
handler's docstring or adjacent comment; the reviewer can trace
the identifier from request to fetch in two reads.

What needs follow-up: identifier source is implicit; the handler
mixes server-derived and client-supplied identifiers without
documentation; the reviewer cannot determine the source without
running the handler.

### 2. Authorization subject: against whom is the authz check performed?

The subject of the authorization check must be the authenticated
principal: request.user, session.principal, the validated JWT
subject claim, or the framework's equivalent. The subject must
NOT come from a request field the client controls (a request
body field carrying user_id, an X-User header, a JWT claim not
verified against the application's signing key).

What good looks like: subject sourced from authoritative session
state; one-line code reference clearly identifies the source.

What needs follow-up: subject sourced from request fields; the
JWT is decoded without signature verification; the application
trusts a header value the upstream load balancer is supposed to
set but does not guarantee.

### 3. Authorization resource: against what is the authz check performed?

The resource of the authorization check must be the specific
resource named by the client-supplied identifier, not a generic
resource class. The check fetches or references the specific
resource and evaluates the principal against it.

What good looks like: the authz call passes the resource ID (or
resource object) explicitly; the call evaluates "can principal X
access resource Y?", not "can principal X access resources of
type Z?".

What needs follow-up: the authz call only confirms the principal
has any access to the resource class; the per-object check is
silently delegated to the data layer "because the query will
return nothing if access is denied" (assumes data-layer
enforcement that may not exist).

### 4. Failure mode: what happens on authz denial?

On authorization denial, the handler must return a generic
not-found or forbidden response without leaking object existence.
The response must not contain the resource's contents in any
field. The substrate-recommended pattern is for the response to
be the SAME for "object does not exist" and "object exists but
you cannot access it" to prevent identifier enumeration.

What good looks like: the same HTTP status and response body for
both nonexistence and unauthorized cases; no resource-specific
fields in error responses.

What needs follow-up: different responses leak existence (404
for missing, 403 for forbidden); error response includes the
object's owner identifier, organization name, or other fields
the unauthorized principal should not learn.

### 5. Coverage: are all CRUD operations covered?

Read, update, delete, and any application-specific actions that
touch the resource (export, share, archive, restore, transfer)
must all enforce object-level authz. Partial coverage allows
the unauthorized action to be reached through the uncovered
endpoint.

What good looks like: a table or comment in the resource's
controller listing each operation and the authz call that
covers it; reviewer can confirm coverage in one scan.

What needs follow-up: read enforces authz but update or delete
does not; bulk operations bypass per-object checks; admin or
internal endpoints share the resource handler but skip the
authz call.

### 6. Test coverage: does the test suite include negative cases?

Tests must exercise the negative case: a principal who should
NOT have access attempts to access the resource and receives
the denial response. Tests covering only the positive case do
not verify object-level authorization.

What good looks like: each object-level authz endpoint has at
least one positive-case test (authorized principal accesses
authorized resource) and one negative-case test (unauthorized
principal attempts unauthorized resource). The negative case
asserts the denial response shape.

What needs follow-up: only happy-path tests exist; negative
tests check denial status but not response shape (allowing
existence leak to regress silently); cross-tenant or cross-
owner cases are absent from the test suite.

## Reviewer attestation

When all six questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review:

```
authorization.object-level-authorization review checklist: complete
- Identifier source: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Authorization subject: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Authorization resource: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Failure mode: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Coverage: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Test coverage: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge until resolved. EXEMPT items
require documented rationale in the pull-request thread.

## Cross-reference

- Substrate rule: authorization.object-level-authorization in catalogs/concerns/authorization.oscal.yaml
- Paired mechanical rule: authorization.authz-before-resource-access (authorization decisions precede resource access)
- Test binding: test-template.md
- Good examples: examples/authorization/object-level-authorization-good.md
- Anti-patterns: examples/authorization/object-level-authorization-anti-pattern.md
- OWASP API Security Top 10 2023 API1:2023 Broken Object Level Authorization
