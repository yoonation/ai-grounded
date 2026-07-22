<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.multi-tenant-data-layer-isolation multi-tenant data-layer isolation (good patterns)

Substrate-original good-pattern examples for authorization.multi-tenant-data-layer-isolation.

## Pattern A: PostgreSQL Row-Level Security per tenant

```sql
-- Enable RLS on every tenant-scoped table
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;


-- Tenant isolation policy: principal can only see rows
-- where tenant_id matches the current tenant context.
CREATE POLICY tenant_isolation_select
ON invoices
FOR SELECT
USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_insert
ON invoices
FOR INSERT
WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_update
ON invoices
FOR UPDATE
USING (tenant_id = current_setting('app.tenant_id')::uuid)
WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_delete
ON invoices
FOR DELETE
USING (tenant_id = current_setting('app.tenant_id')::uuid);


-- Deny-by-default for missing context: a connection with no
-- app.tenant_id setting returns empty results, not all rows.
-- PostgreSQL achieves this by treating the cast of an empty
-- string to uuid as an error; a more explicit alternative is
-- a sentinel UUID value never assigned to any tenant.
```

## Pattern B: Application middleware sets tenant context per request

```python
from django.db import connection


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Derive tenant_id from authoritative session, NOT
        # from request header or body
        principal = request.user
        if not principal.is_authenticated:
            return self.get_response(request)

        tenant_id = principal.session_tenant_id  # set at login

        with connection.cursor() as cursor:
            cursor.execute(
                "SET LOCAL app.tenant_id = %s",
                [str(tenant_id)],
            )
            response = self.get_response(request)

        return response
```

The tenant_id is bound to the session at authentication and
cannot be overridden by request fields. Application code can
issue queries without WHERE tenant_id = ... clauses; the RLS
policy enforces.

## Pattern C: ORM-level tenant filter as defense in depth (Python / Django)

```python
# Application layer ALSO filters as defense-in-depth. The
# data layer is authoritative; the application layer reduces
# round-trip data even when the query would also be filtered
# by RLS.
class TenantScopedManager(models.Manager):
    def get_queryset(self):
        request = get_current_request()
        if request and hasattr(request, "tenant_id"):
            return super().get_queryset().filter(
                tenant_id=request.tenant_id
            )
        return super().get_queryset().none()  # deny-by-default


class Invoice(models.Model):
    tenant_id = models.UUIDField()
    # ... other fields ...
    objects = TenantScopedManager()
```

The application filter and the RLS policy are redundant. If
the application filter has a bug or is bypassed (raw SQL,
ORM escape hatch), RLS still enforces.

## Pattern D: Schema-per-tenant isolation (PostgreSQL)

```python
# Alternative isolation: each tenant gets a dedicated schema.
# Queries reference unqualified table names and the schema
# search_path routes them.
def set_tenant_schema(tenant_id):
    with connection.cursor() as cursor:
        schema = f"tenant_{tenant_id.hex}"
        cursor.execute(f"SET search_path TO {schema}, public")


class TenantSchemaMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            set_tenant_schema(request.user.session_tenant_id)
        response = self.get_response(request)
        return response
```

Schema-per-tenant has stronger isolation (separate physical
storage namespace) at the cost of operational complexity
(N schemas to migrate, monitor, back up). Substrate-acceptable
when tenant count is bounded and compliance requirements
favor physical separation.

## Pattern E: Index isolation for search

```python
# Search index is partitioned by tenant. The search query
# always specifies the tenant partition; cross-tenant search
# is structurally impossible.
def search(query: str, principal):
    tenant_id = principal.session_tenant_id
    return elasticsearch_client.search(
        index=f"resources-{tenant_id}",  # tenant-scoped index
        body={"query": {"match": {"content": query}}},
    )
```

Why these patterns satisfy authorization.multi-tenant-data-layer-isolation:
- Data-layer enforcement (RLS, schema separation, partitioned
  index) is the substrate-required mechanism
- Tenant context derives from authoritative session, not
  client-supplied fields
- Missing context fails closed (empty result, not all-tenant
  result)
- Application-layer filters are defense-in-depth, not the
  primary mechanism
- Cross-tenant access by SUPERUSER role is documented and
  audited (per authorization.audit-events-on-decisions)
