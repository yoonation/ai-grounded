<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.multi-tenant-data-layer-isolation multi-tenant data-layer isolation (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Application-layer filter is the only enforcement (Python)

```python
# FORBIDDEN: tenant filter applied only in application code.
# A single forgotten WHERE clause leaks cross-tenant data.
class Invoice(models.Model):
    tenant_id = models.UUIDField()
    # ... fields ...


def list_invoices_BAD(request):
    tenant_id = request.user.session_tenant_id
    invoices = Invoice.objects.filter(tenant_id=tenant_id)
    return JsonResponse([i.to_dict() for i in invoices], safe=False)


def export_all_invoices_BAD(request):
    # OOPS: forgot the tenant filter on this code path
    invoices = Invoice.objects.all()  # CROSS-TENANT LEAK
    return CsvResponse(invoices)
```

Why this violates authorization.multi-tenant-data-layer-isolation:
- Tenant isolation depends on every code path remembering to
  filter; one oversight is one data leak
- The data layer has no enforcement; a raw SQL query, ORM
  escape, or background job can leak data
- Substrate-required defense is data-layer enforcement (RLS,
  schema separation, partitioned index) so application bugs
  do not produce data leaks

## Anti-pattern B: Tenant ID from request body or header (Node.js)

```javascript
// FORBIDDEN: tenant_id from request header. Attacker sends
// X-Tenant-Id: <other tenant's id> and reads their data.
app.get("/invoices", async (req, res) => {
  const tenantId = req.headers["x-tenant-id"];  // CLIENT-CONTROLLED
  const invoices = await Invoice.find({ tenantId });
  res.json(invoices);
});
```

Why this violates authorization.multi-tenant-data-layer-isolation:
- Tenant context is client-controlled; an attacker spoofs the
  header to access any tenant
- The tenant ID must derive from authoritative session state
  established at authentication, not from request fields

## Anti-pattern C: SUPERUSER bypass undocumented and unaudited (Python)

```python
# FORBIDDEN: "support mode" bypass that operates cross-tenant
# without audit.
def lookup_invoice_for_support_BAD(invoice_id):
    # Used by support staff. Set in middleware when the user
    # has the support role.
    if current_principal().has_role("support"):
        # Bypass tenant isolation for support tasks
        return Invoice.objects.filter(pk=invoice_id).first()
    abort(403)
```

Why this violates authorization.multi-tenant-data-layer-isolation:
- The bypass is implicit in role membership without explicit
  documentation
- Cross-tenant lookups are not audited; support staff or
  compromised support credentials can read any tenant's data
  invisibly
- The substrate-acceptable pattern is documented SUPERUSER
  role with audit on every cross-tenant access

## Anti-pattern D: Database role not least-privileged (PostgreSQL)

```sql
-- FORBIDDEN: the application connects with a role that has
-- the BYPASSRLS privilege. RLS policies do not apply.
CREATE ROLE app_role WITH LOGIN PASSWORD '...' BYPASSRLS;
```

Why this violates authorization.multi-tenant-data-layer-isolation:
- A BYPASSRLS role makes the RLS policies ornamental
- The substrate's data-layer enforcement requires the
  application role to be subject to RLS
- Migration tooling and DBA tasks should use separate roles
  (substrate-recommended: `app_role` (NOSUPERUSER NOBYPASSRLS)
  for the application; `migrator_role` for schema changes;
  `dba_role` for emergency access with audit)

## Anti-pattern E: Search index unsharded across tenants (Elasticsearch)

```python
# FORBIDDEN: all tenants share one index. Application-layer
# filter is the only isolation.
def search_BAD(query, principal):
    return elasticsearch_client.search(
        index="resources",  # SHARED INDEX
        body={
            "query": {
                "bool": {
                    "must": [{"match": {"content": query}}],
                    "filter": [{
                        "term": {"tenant_id": principal.tenant_id}
                    }],
                }
            }
        },
    )


def admin_dashboard_search_BAD(query):
    # OOPS: admin path forgets the tenant filter
    return elasticsearch_client.search(
        index="resources",
        body={"query": {"match": {"content": query}}},
    )
```

Why this violates authorization.multi-tenant-data-layer-isolation:
- The shared index relies on every query remembering to
  filter; the admin dashboard path does not, and leaks cross-
  tenant search results
- Index storage holds documents from all tenants without
  physical separation; a Elasticsearch RBAC misconfiguration
  exposes everything
- Substrate-recommended pattern is per-tenant index (Pattern
  E in the paired good-example file) so the filter is
  structural, not behavioral
