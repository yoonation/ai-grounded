---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authorization.object-level-authorization-object-level-authorization"
title: "authorization.object-level-authorization test template: object-level authorization"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authorization.object-level-authorization test template: object-level authorization

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework (pytest, Jest, RSpec, JUnit, Go test, etc.) against
the application's resource-access endpoints.

These are integration tests, not unit tests: they exercise the
authorization layer in combination with the resource fetch
code path. They run against a deployed test environment or a
representative local stack with real-looking data.

The test corpus must include at least two test principals
(Alice and Bob) and a set of resources owned by each. The
scenarios verify that Alice cannot access Bob's resources even
when Alice authenticates successfully and constructs a request
with Bob's resource identifier.

The substrate-recommended coverage target is: every endpoint
that accepts a resource identifier in path, query, or body has
at least one positive scenario (owner accesses their resource)
and at least one negative scenario (non-owner is denied).

## Scenario 1: Owner accesses their own resource (positive)

**Preconditions**
- Test user Alice authenticates and obtains a session
- A resource R_alice exists with Alice as owner
- The endpoint under test is GET /resources/{id}

**Action**
- Alice submits GET /resources/{R_alice.id} with her session

**Expected**
- HTTP 200 with the resource body
- The application's authorization audit event records a
  decision of "allow" with principal=Alice, resource=R_alice,
  action=read

## Scenario 2: Non-owner is denied another user's resource (the IDOR case)

**Preconditions**
- Test user Alice authenticates and obtains a session
- A resource R_bob exists with Bob as owner; Alice has no
  permission to access R_bob through any role grant, share,
  or other mechanism
- The endpoint under test is GET /resources/{id}

**Action**
- Alice submits GET /resources/{R_bob.id} with her session
  (constructing the request body or URL with Bob's resource
  identifier despite no UI affordance)

**Expected**
- HTTP 403 (Forbidden) or 404 (Not Found); substrate accepts
  either, with 404 preferred when leaking the resource's
  existence is itself a concern (existence inference)
- The response body does not contain any portion of R_bob's
  content; if 404, the body does not reveal that R_bob exists
- An authorization audit event records a decision of "deny"
  with principal=Alice, resource=R_bob, action=read

## Scenario 3: IDOR via numeric identifier enumeration

**Preconditions**
- Resources are identified by sequential numeric IDs
- Resource IDs 1 through 1000 exist with various owners
- Test user Alice owns resources with IDs 1, 5, 9 (every
  fourth ID); other IDs belong to other users

**Action**
- Alice submits GET /resources/{id} for IDs 1 through 10 in
  sequence

**Expected**
- IDs 1, 5, 9: HTTP 200
- IDs 2, 3, 4, 6, 7, 8, 10: HTTP 403 or 404
- No body of any non-owned resource is leaked to Alice in
  any response
- Audit events record deny decisions for IDs 2, 3, 4, 6, 7,
  8, 10

Notes: this scenario exercises the most common IDOR shape (a
sequential ID space discoverable by enumeration). Even when
the production application uses non-sequential identifiers
(UUIDs), the authorization rule must hold for cases where an
attacker discovers an identifier through any means.

## Scenario 4: IDOR via resource identifier in request body

**Preconditions**
- Test user Alice authenticates
- The endpoint POST /transfers accepts a JSON body with a
  source_account_id field
- Alice owns account A_alice; Bob owns account A_bob

**Action**
- Alice submits POST /transfers with body
  {"source_account_id": A_bob.id, "destination": A_alice.id,
  "amount": 100}

**Expected**
- HTTP 403 (Forbidden)
- The transfer is NOT executed
- A_bob's balance is unchanged
- An audit event records a deny decision with principal=
  Alice, resource=A_bob, action=transfer-source

Notes: this scenario verifies that the authorization check
applies to resource identifiers in request bodies, not only
identifiers in URL paths.

## Scenario 5: IDOR via stale or guessed identifier

**Preconditions**
- A resource R_deleted previously existed with Bob as owner;
  the resource has since been soft-deleted
- Alice authenticates and somehow possesses R_deleted's
  identifier (e.g., from cached search results or shared
  URL)

**Action**
- Alice submits GET /resources/{R_deleted.id}

**Expected**
- HTTP 403 or 404
- The response does not reveal that the resource ever existed
  or that it was previously owned by Bob
- An audit event records the access attempt

## Scenario 6: Authorization check happens before resource fetch is exposed

**Preconditions**
- Test instrumentation can observe whether the resource fetch
  query reached the database
- Alice authenticates with no access to R_bob

**Action**
- Alice submits GET /resources/{R_bob.id}

**Expected**
- HTTP 403 or 404
- The application's behavior is consistent with the
  authorization check being decisive: either the resource
  fetch did not execute (preferred), or the fetch executed
  but the result is not returned and is not used for any
  further side effects (acceptable when the fetch is required
  for the authorization decision itself, as in attribute-
  based access control)

Notes: this scenario verifies the L2-001 semantic counterpart
to L1-002 (authorization decision precedes resource access).
The mechanical ordering check (L1-002) is the static analog;
this scenario is the integration-test counterpart.

## Scenario 7: Side-effect endpoints are also protected

**Preconditions**
- The application has both read endpoints (GET) and write
  endpoints (POST, PUT, PATCH, DELETE) for resources
- Alice authenticates with no access to R_bob

**Action**
- Alice submits the following sequence:
  - GET /resources/{R_bob.id}
  - PUT /resources/{R_bob.id} with arbitrary body
  - DELETE /resources/{R_bob.id}

**Expected**
- All three requests return HTTP 403 or 404
- R_bob is unchanged in all material respects (content,
  state, lifecycle)
- Three audit events record three deny decisions with the
  three different actions

## Scenario 8: Bulk endpoints check authorization per resource

**Preconditions**
- The application has a bulk-fetch endpoint such as POST
  /resources/batch accepting a list of resource IDs
- Alice authenticates and owns R1 and R3 but not R2 and R4

**Action**
- Alice submits POST /resources/batch with body
  {"ids": [R1, R2, R3, R4]}

**Expected**
- The response includes R1 and R3 (Alice's owned resources)
- The response does NOT include R2 or R4 content
- The response does not reveal that R2 and R4 exist (or, if
  the response includes a per-ID status, the status for R2
  and R4 is "forbidden" or "not found", consistent with the
  single-resource case)
- Four audit events record allow for R1 and R3, deny for R2
  and R4

Notes: bulk endpoints are a common source of authorization
gaps because reviewers often verify the single-resource path
and not the bulk path. The substrate requires per-resource
authorization in the bulk path.

## Test scaffold: principal and resource setup

Tests require at least two principals (Alice and Bob) and a
set of resources distributed between them. The substrate
recommends:

- A dedicated test fixture that creates Alice, Bob, a third
  user Carol (uninvolved control), and 10 to 20 resources
  distributed across owners
- The fixture resets between scenarios to a known starting
  state
- The fixture exposes helpers for "authenticate as Alice",
  "authenticate as Bob", and "obtain resource X"

The test scaffold is consumer-implemented; the substrate
specifies the requirement but not the mechanism.

## Cross-reference

- Substrate rule: authorization.object-level-authorization in catalogs/concerns/authorization.oscal.yaml
- Review checklist binding: checklist.md
- Good examples: examples/authorization/object-level-authorization-good.md
- Anti-patterns: examples/authorization/object-level-authorization-anti-pattern.md
- Related mechanical rule: authorization.authz-before-resource-access (authorization decision precedes resource access)
