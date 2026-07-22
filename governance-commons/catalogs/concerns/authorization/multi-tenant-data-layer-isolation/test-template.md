---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authorization.multi-tenant-data-layer-isolation-multi-tenant-data-layer-isolation"
title: "authorization.multi-tenant-data-layer-isolation test template: multi-tenant data-layer isolation"
substrate-rule: "authorization.multi-tenant-data-layer-isolation"
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

# authorization.multi-tenant-data-layer-isolation test template: multi-tenant data-layer isolation

## How to use this binding

Multi-tenant isolation must hold at the data layer, not only
at the application layer. The substrate-recommended pattern
is database-level enforcement (PostgreSQL Row-Level Security,
or equivalent mechanism in other databases). Application-
layer filtering alone is insufficient because a single
forgotten WHERE clause leaks tenant data.

These scenarios verify the property at the data layer: even
if the application layer's tenant filter is bypassed (forgotten
clause, raw SQL, ORM escape hatch), the data layer still
enforces isolation.

The substrate-recommended test approach is to construct
scenarios that DELIBERATELY bypass the application layer's
filter and verify the data layer's enforcement holds.

The scenarios assume two tenants T_alpha and T_beta, each
with at least one principal and several resources. The test
suite verifies cross-tenant access fails through every
plausible path.

## Scenario 1: Application-layer cross-tenant query is blocked

**Preconditions**
- Tenant T_alpha contains principal P_alpha and resource R_alpha
- Tenant T_beta contains principal P_beta and resource R_beta
- P_alpha authenticates and receives a session bound to T_alpha
- The application endpoint GET /resources/{id} normally
  applies a tenant filter through the ORM

**Action**
- P_alpha submits GET /resources/{R_beta.id}

**Expected**
- HTTP 403 or 404
- R_beta is not returned in any form
- An audit event records the cross-tenant access attempt

## Scenario 2: Bypass test: direct database query without app-layer filter

**Preconditions**
- Test infrastructure can connect to the database using the
  application's database role (the role the application
  process uses at runtime)
- T_alpha and T_beta exist with resources as in Scenario 1
- A test query is constructed that SELECTs resources WITHOUT
  any tenant_id filter clause

**Action**
- The test runs `SET app.tenant_id = T_alpha;` (or the
  application's tenant-context-setting mechanism)
- The test then executes `SELECT * FROM resources;` with no
  WHERE clause

**Expected**
- The result set contains ONLY T_alpha's resources
- T_beta's resources are NOT returned even though no
  application-layer filter was applied
- The data-layer mechanism (PostgreSQL RLS policy or
  equivalent) is the enforcement

Notes: this is the substrate-critical scenario. If this test
fails, the application has application-layer filtering only,
and any forgotten filter clause in production code leaks
tenant data. The L2-004 rule is specifically about this case.

## Scenario 3: Bypass test: missing tenant context fails closed

**Preconditions**
- Test connects to the database using the application's
  database role
- T_alpha and T_beta exist
- The test does NOT set the tenant context (omits the SET
  command or equivalent)

**Action**
- The test executes `SELECT * FROM resources;` with no
  tenant context

**Expected**
- The query returns EMPTY result set (substrate-preferred
  deny-by-default behavior), OR
- The query raises an error indicating tenant context is
  required (also substrate-acceptable; deny-by-default is
  satisfied either way)
- The query DOES NOT return cross-tenant data

Notes: deny-by-default at the data layer means absence of
context is treated as no access, not as universal access.

## Scenario 4: Write isolation: cross-tenant write is blocked

**Preconditions**
- P_alpha authenticated bound to T_alpha
- R_beta exists in T_beta with content C_original

**Action**
- P_alpha submits PUT /resources/{R_beta.id} with arbitrary
  content C_attacker

**Expected**
- HTTP 403 or 404
- R_beta's content remains C_original
- An audit event records the cross-tenant write attempt

## Scenario 5: Aggregation isolation: cross-tenant COUNT is blocked

**Preconditions**
- T_alpha contains 5 resources; T_beta contains 100 resources
- P_alpha authenticates bound to T_alpha
- The application has an endpoint GET /resources/count

**Action**
- P_alpha submits GET /resources/count

**Expected**
- The response contains 5 (T_alpha's count)
- The response does NOT contain 105 or 100 in any form
- The response does not leak the existence of T_beta

Notes: aggregation queries (COUNT, SUM, AVG, GROUP BY) are
particularly prone to cross-tenant leakage because reviewers
often check WHERE clauses on SELECT but overlook aggregation.
The data-layer enforcement must cover aggregation.

## Scenario 6: Index and search isolation

**Preconditions**
- The application includes a search index (full-text or
  vector) over resources
- Indexed content includes resources from both T_alpha and
  T_beta
- P_alpha authenticates bound to T_alpha
- A search term matches resources in both tenants

**Action**
- P_alpha submits GET /search?q=<term>

**Expected**
- The result set contains ONLY T_alpha's matches
- T_beta's matching resources are not returned
- The result set does not reveal T_beta's match count
  through total-results metadata

Notes: search indexes often live outside the database and
have their own isolation model. The data-layer-isolation rule
extends to all data layers including secondary indexes.

## Scenario 7: Tenant context is bound to authoritative session

**Preconditions**
- P_alpha authenticates and receives a session bound to
  T_alpha
- The application accepts a tenant_id field in request body
  (anti-pattern for testing purposes)

**Action**
- P_alpha submits a request with tenant_id=T_beta in the
  request body, attempting to spoof the tenant context

**Expected**
- The application IGNORES the request-supplied tenant_id
- The session's authoritative tenant_id (T_alpha) is used
  for all data-layer queries
- Cross-tenant access does not succeed

Notes: tenant context must derive from authoritative session
state, not from request fields the attacker can spoof. This
is the multi-tenant counterpart to the principal-identity-
source rule from authorization.audit-events-on-decisions.

## Scenario 8: SUPERUSER bypass is documented and audited

**Preconditions**
- The application has a documented SUPERUSER role used for
  cross-tenant administrative tasks (substrate-acceptable
  with documentation and audit)
- Test principal P_super has the SUPERUSER role

**Action**
- P_super submits a cross-tenant query

**Expected**
- The query succeeds (SUPERUSER is documented exception)
- An audit event records the cross-tenant access at WARN or
  higher severity
- Security monitoring receives the event
- The application's documentation lists SUPERUSER as the
  only exception path

Notes: many applications need a documented cross-tenant
mechanism for support, migrations, and incident response.
This is substrate-acceptable provided the exception is
documented, audited, and monitored.

## Test scaffold: tenant fixture and database state

The test scaffold creates two tenants with comparable resource
counts:

```python
# Example tenant fixture pattern
@pytest.fixture
def two_tenant_fixture(test_db):
    tenant_alpha = create_tenant("alpha")
    tenant_beta = create_tenant("beta")

    principal_alpha = create_principal(tenant_alpha)
    principal_beta = create_principal(tenant_beta)

    for i in range(5):
        create_resource(tenant_alpha, principal_alpha)
    for i in range(5):
        create_resource(tenant_beta, principal_beta)

    yield {
        "alpha": {"tenant": tenant_alpha, "principal":
                  principal_alpha},
        "beta": {"tenant": tenant_beta, "principal":
                 principal_beta}
    }

    cleanup_tenants(tenant_alpha, tenant_beta)
```

The scaffold is consumer-implemented. The data-layer bypass
scenarios (Scenarios 2 and 3) require direct database access
in the test infrastructure, which the consumer enables for
the test environment.

## Cross-reference

- Substrate rule: authorization.multi-tenant-data-layer-isolation in catalogs/concerns/authorization.oscal.yaml
- Review checklist binding: checklist.md
- Good examples: examples/authorization/multi-tenant-data-layer-isolation-good.md
- Anti-patterns: examples/authorization/multi-tenant-data-layer-isolation-anti-pattern.md
- Related rules: authorization.object-level-authorization (object-level authorization is necessary but not sufficient for multi-tenant), authorization.audit-events-on-decisions (audit events on decisions)
