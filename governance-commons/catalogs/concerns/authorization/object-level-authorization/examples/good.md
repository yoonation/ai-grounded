<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.object-level-authorization object-level authorization (good patterns)

Substrate-original good-pattern examples for authorization.object-level-authorization.

## Pattern A: Ownership check via centralized policy point (Python)

```python
# Every per-resource access flows through the policy point.
# The policy point evaluates ownership, sharing, and admin
# overrides in one place.
def get_invoice(request, invoice_id):
    decision = policy_point.decide(
        principal=request.user,
        action="read",
        resource_type="invoice",
        resource_id=invoice_id,
    )
    if decision.allow is not True:
        return HttpResponseForbidden()

    invoice = Invoice.objects.get(pk=invoice_id)
    return JsonResponse(invoice.to_dict())
```

```python
# The policy point's decision uses a database lookup to check
# ownership. The policy is data: changing ownership rules
# does not require changing get_invoice.
class PolicyPoint:
    def decide(self, principal, action, resource_type, resource_id):
        if action == "read" and resource_type == "invoice":
            return self._check_invoice_read(principal, resource_id)
        ...

    def _check_invoice_read(self, principal, invoice_id):
        invoice = Invoice.objects.filter(pk=invoice_id).first()
        if invoice is None:
            return Decision(allow=False, reason="not-found")
        if invoice.owner_id == principal.id:
            return Decision(allow=True, reason="owner")
        if Share.objects.filter(
            invoice=invoice, grantee=principal
        ).exists():
            return Decision(allow=True, reason="shared")
        if principal.is_admin:
            return Decision(allow=True, reason="admin")
        return Decision(allow=False, reason="no-grant")
```

## Pattern B: PostgreSQL Row-Level Security on the resource table

```sql
-- Policy: a principal may SELECT an invoice if they own it,
-- it is shared with them, or they have the admin role.
CREATE POLICY invoice_read_policy
ON invoices
FOR SELECT
USING (
    owner_id = current_setting('app.principal_id')::uuid
    OR EXISTS (
        SELECT 1 FROM invoice_shares
        WHERE invoice_id = invoices.id
          AND grantee_id = current_setting('app.principal_id')::uuid
    )
    OR EXISTS (
        SELECT 1 FROM role_grants
        WHERE principal_id = current_setting('app.principal_id')::uuid
          AND role = 'admin'
    )
);

ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
```

```python
def get_invoice(request, invoice_id):
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.principal_id = %s",
                       [str(request.user.id)])
        cursor.execute("SELECT * FROM invoices WHERE id = %s",
                       [invoice_id])
        row = cursor.fetchone()
        if row is None:
            return HttpResponseNotFound()  # avoid existence inference
        return JsonResponse(row_to_dict(row))
```

The data layer enforces. A forgotten WHERE clause in the
application code still results in only-authorized rows being
returned because the RLS policy filters at the storage layer.

## Pattern C: Pundit object-level policy (Ruby / Rails)

```ruby
class InvoicePolicy < ApplicationPolicy
  def show?
    user.admin? ||
      record.owner == user ||
      record.shares.exists?(grantee: user)
  end
end


class InvoicesController < ApplicationController
  def show
    @invoice = Invoice.find(params[:id])
    authorize @invoice  # calls InvoicePolicy#show?
    render json: @invoice
  end
end
```

The authorize call uses the specific record. ActionController
raises Pundit::NotAuthorizedError on deny, which the
application handles globally as 403.

## Pattern D: GraphQL with per-resource field resolver authorization (TypeScript)

```typescript
export const invoiceResolver = {
  Query: {
    invoice: async (parent, { id }, context) => {
      const decision = await context.policyPoint.decide({
        principal: context.principal,
        action: "read",
        resourceType: "invoice",
        resourceId: id,
      });
      if (!decision.allow) {
        throw new ForbiddenError("not authorized");
      }
      return context.dataSources.invoices.findById(id);
    },
  },
};
```

## Pattern E: Bulk endpoint with per-resource authorization (Python / FastAPI)

```python
@app.post("/invoices/batch")
def batch_get_invoices(
    payload: BatchRequest,
    principal=Depends(current_principal_dep),
):
    """Bulk fetch with per-resource authorization. Returns
    only invoices the principal may access; denied invoices
    are silently excluded from the response (substrate-
    preferred for bulk shape) OR included with a 'forbidden'
    status field (substrate-acceptable, preserves per-ID
    feedback)."""
    results = []
    for invoice_id in payload.ids:
        decision = policy_point.decide(
            principal=principal,
            action="read",
            resource_type="invoice",
            resource_id=invoice_id,
        )
        if decision.allow is True:
            invoice = Invoice.get(invoice_id)
            results.append(invoice.to_dict() if invoice else None)
        # else: silently skip
    return results
```

Why these patterns satisfy authorization.object-level-authorization:
- Per-resource authorization at every access site, not just at
  list endpoints
- Ownership, sharing, and admin override are evaluated by the
  policy point or RLS policy, not inline in business handlers
- The 404 versus 403 ambiguity is resolved consistently to
  avoid existence inference
- Bulk endpoints check authorization for each resource, not
  just the bulk operation as a whole
