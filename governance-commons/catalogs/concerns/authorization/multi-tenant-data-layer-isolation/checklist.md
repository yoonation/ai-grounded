---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.multi-tenant-data-layer-isolation-multi-tenant-data-layer-isolation"
title: "authorization.multi-tenant-data-layer-isolation review checklist: multi-tenant data layer isolation"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add a resource model in a multi-tenant system"
  - "Code changes that touch queries against tenant-scoped data"
  - "Code changes that introduce a new way to access data (background job, ETL pipeline, admin tooling)"
  - "Code changes that touch the tenant-context-acquisition path (connection pool, session setup, middleware)"
---

# authorization.multi-tenant-data-layer-isolation review checklist: multi-tenant data layer isolation

## How to use this binding

This checklist applies only to multi-tenant systems where
multiple customers' data co-resides in shared logical storage.
Single-tenant systems and per-tenant-deployment systems do not
need this rule.

Reviewers answer every question below when reviewing pull
requests that match the triggers. Tenant boundary violation is
a categorical failure (per the catalog's severity rationale);
the checklist is conservative and reviewers are encouraged to
escalate concerns rather than wave findings through.

## Review questions

### 1. Tenant model: per-table, per-database, or RLS-enforced?

Identify the tenant model in use. The substrate-recognized
shapes: per-table tenant column (every tenant-scoped table
has a tenant_id, workspace_id, or organization_id column;
isolation is enforced by filtering on the column);
per-database tenant separation (each tenant has its own
database or schema; isolation is by physical separation);
per-row isolation via RLS (tenant-scoped tables have
PostgreSQL row-level security policies; isolation is enforced
at the database boundary); hybrid (high-volume tables in
shared schema with tenant column; high-sensitivity tables in
per-tenant schemas).

What good looks like: the model is explicit, documented, and
consistent across the application; new tenant-scoped tables
follow the established model; the model selection appears in
the application's authorization MADR.

What needs follow-up: the model is implicit; new tables follow
inconsistent conventions; the application has multiple models
partially-applied without documentation.

### 2. Enforcement: mechanism, not discipline?

The tenant scope is applied by mechanism (RLS, tenant-aware
ORM default, tenant-scoped connection), not by developer
discipline (remembering to add a tenant filter to every
query).

What good looks like: mechanism-based enforcement. The
mechanism makes cross-tenant queries impossible or makes
them require explicit override. Examples: PostgreSQL RLS;
Django default manager scoped to current tenant via
threadlocal; Rails ActiveRecord default scope on every
TenantScoped model; tenant-scoped database connection
acquired from a per-tenant connection pool.

What needs follow-up: every query manually filters on
tenant_id; the application "should" add the filter
everywhere; review relies on catching missing filters
case-by-case.

### 3. Tenant context acquisition: is the source authoritative?

The tenant context is acquired once per request and is
unambiguous. The substrate-recommended source: the
authenticated principal's tenant claim (JWT claim, session
attribute, IdP federation claim).

What good looks like: the request's tenant context is
established by middleware before any handler runs; handlers
never look up the tenant from request headers or parameters;
the tenant context is immutable for the request lifetime.

What needs follow-up: the tenant is read from a query
parameter (the attacker can change it); the tenant is
derived from the resource being accessed (circular); the
tenant context can be mutated mid-request.

### 4. Query coverage: does every tenant-scoped query inherit the scope?

Every query against tenant-scoped data carries the tenant
scope. The mechanism enforces this; the review verifies the
mechanism is active.

What good looks like: for RLS, every tenant-scoped table has
the policy; the session variable is set at connection
acquisition; the integration tests confirm cross-tenant
queries return empty. For tenant-aware ORM, every tenant-
scoped model inherits from the tenant-aware base; the default
scope is non-bypassable.

What needs follow-up: some tenant-scoped tables lack the RLS
policy; some models do not inherit from the tenant-aware
base; the ORM allows queries that bypass the default scope
via low-level interfaces (raw SQL, escape hatches, unscoped
blocks).

### 5. Background jobs and async workers: do they carry tenant context?

Async workers, background jobs, scheduled tasks, and ETL
pipelines acquire tenant context the same way request
handlers do. The tenant is not implicit in the job's
arguments.

What good looks like: jobs carry the tenant identity in
their argument set; job execution sets the session variable
before any database work; the tenant scope is the same as a
request handler would have.

What needs follow-up: jobs run as a "system" tenant with
visibility across tenants; jobs accept tenant_id as an
argument but do not actually enforce the scope; jobs use raw
SQL to bypass the ORM tenant scope.

### 6. Admin tooling and operator flows: is cross-tenant access gated?

Admin tooling (support tools, operator consoles, internal
dashboards) requires operator-mode authorization to access
cross-tenant data. The operator-mode authorization is
distinct from the standing tenant-scoped session.

What good looks like: operator-mode is a separate
authorization path; it requires step-up (per authorization.step-up-and-audit-for-privilege-changes);
it emits audit events with the operator identity and the
tenants accessed; it is heavily logged.

What needs follow-up: admin tooling runs without tenant
context; the operator role implicitly grants cross-tenant
read; cross-tenant operations are silent.

### 7. Analytics and reporting: are cross-tenant aggregations explicit?

Analytics queries against the production database respect
the same tenant scope as the application or run against a
separated analytics store with explicit cross-tenant access
controls.

What good looks like: analytics use a read replica or a
separate warehouse with deliberate cross-tenant access
controls; per-tenant reports use the tenant scope; cross-
tenant aggregations are aggregate-only (no row-level data
exposure).

What needs follow-up: analytics use a "service account" that
bypasses tenant scope; the same database connection is used
for tenant-scoped and cross-tenant queries.

### 8. Test coverage: do tests exercise cross-tenant attempts?

Tests include cross-tenant attempts: a principal in tenant A
attempts to read a resource owned by tenant B and the
response is empty (or 404).

What good looks like: the test template binding scenarios
are implemented in the project's test framework; tests run
in CI; failure blocks merge; both API-level and data-layer
cross-tenant tests exist.

What needs follow-up: tests only cover within-tenant cases;
no regression test exists for cross-tenant attempts; cross-
tenant tests run only manually and not in CI.

### 9. New tenant-scoped tables: model conformance?

New tables introduced in the change conform to the tenant
model (column, inheritance, RLS policy).

What good looks like: the new table inherits from the tenant-
scoped base; the RLS policy is included in the migration; the
migration is reviewed for tenant-model conformance before
merge.

What needs follow-up: the new table has a tenant_id column
but no RLS policy; the migration omits the policy; the table
is added to the ORM without inheriting from the tenant-scoped
base.

### 10. Cross-tenant references: prohibited or explicit?

Foreign-key references that cross tenant boundaries (resource
A in tenant A references resource B in tenant B) are
prohibited by default. Explicit cross-tenant references
exist only for the global resources (the tenant directory
itself, the global subscription catalog) and are documented
as such.

What good looks like: cross-tenant references are absent;
the schema review catches accidental cross-tenant foreign
keys; global resources are clearly marked and have
documented cross-tenant access patterns.

What needs follow-up: foreign keys cross tenant boundaries
without consideration; the application logic "trusts" the
foreign key to point at the right tenant without checking.

## Reviewer attestation

When all ten questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review:

```
authorization.multi-tenant-data-layer-isolation review checklist: complete
- Tenant model: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Mechanism enforcement: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Tenant context acquisition: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Query coverage: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Background jobs: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Admin tooling: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Analytics: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Test coverage: PASS / FOLLOW-UP / EXEMPT-with-rationale
- New table conformance: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cross-tenant references: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge until resolved. EXEMPT items
require documented rationale in the pull-request thread. If
the review identifies cross-tenant leakage in the running
system, the response is incident response, not code review;
the substrate does not prescribe incident response, but
remediation is gated until the leak is contained.

## Cross-reference

- Substrate rule: authorization.multi-tenant-data-layer-isolation in catalogs/concerns/authorization.oscal.yaml
- Related rule: authorization.step-up-and-audit-for-privilege-changes (step-up for operator cross-tenant access)
- Related rule: authorization.authorization-model-selection (authorization model selection includes tenant architecture)
- Test binding: test-template.md
- Good examples: examples/authorization/multi-tenant-data-layer-isolation-good.md
- Anti-patterns: examples/authorization/multi-tenant-data-layer-isolation-anti-pattern.md
- OWASP ASVS v5.0.0 V8.5.1
- NIST SP 800-53 AC-4 Information Flow Enforcement
- PostgreSQL Row Level Security documentation
