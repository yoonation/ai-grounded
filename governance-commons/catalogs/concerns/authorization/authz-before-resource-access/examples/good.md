<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.authz-before-resource-access authorization decision precedes resource access (good patterns)

Substrate-original good-pattern examples for authorization.authz-before-resource-access.

## Pattern A: Authorization check before database fetch (Python / Django)

```python
from django.http import JsonResponse, HttpResponseForbidden
from app.authz import policy_point


def get_invoice(request, invoice_id):
    # Authorization decision based on the resource IDENTIFIER,
    # not the resource CONTENT. The policy point evaluates
    # whether the principal may access invoice_id without
    # loading the invoice's content.
    decision = policy_point.decide(
        principal=request.user,
        action="read",
        resource_type="invoice",
        resource_id=invoice_id,
    )
    if decision.allow is not True:
        return HttpResponseForbidden()

    # Only after authz allow does the resource fetch happen.
    invoice = Invoice.objects.get(pk=invoice_id)
    return JsonResponse(invoice.to_dict())
```

## Pattern B: Authorization integrated into the query (PostgreSQL Row-Level Security)

```sql
-- Policy at the data layer: the application can issue
-- SELECT * FROM invoices WHERE id = $1 and RLS enforces
-- that only invoices the current principal may access are
-- returned. The authorization decision is implicit in the
-- query and applies before the result row is materialized.
CREATE POLICY invoice_owner_or_admin_read
ON invoices
FOR SELECT
USING (
    owner_id = current_setting('app.principal_id')::uuid
    OR EXISTS (
        SELECT 1 FROM role_grants
        WHERE principal_id = current_setting('app.principal_id')::uuid
          AND role = 'admin'
    )
);
```

```python
# Application code that pairs with the RLS policy.
def get_invoice(request, invoice_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SET LOCAL app.principal_id = %s",
            [str(request.user.id)],
        )
        cursor.execute(
            "SELECT * FROM invoices WHERE id = %s",
            [invoice_id],
        )
        row = cursor.fetchone()
        if row is None:
            # Either the invoice does not exist or the principal
            # is not authorized; RLS does not distinguish.
            # Substrate-recommended: return 404 to avoid
            # existence inference.
            return HttpResponseNotFound()
        return JsonResponse(row_to_dict(row))
```

## Pattern C: Authorization in framework dependency before handler (Node.js / NestJS)

```typescript
import { Controller, Get, Param, UseGuards } from "@nestjs/common";
import { AuthzGuard } from "./authz.guard";


@Controller("documents")
export class DocumentsController {

    @Get(":id")
    @UseGuards(AuthzGuard("read", "document"))
    async getDocument(@Param("id") id: string) {
        // The AuthzGuard ran first and either allowed the
        // request to reach this method or rejected with 403.
        // The handler runs only after the authz decision.
        return this.documentService.findById(id);
    }
}
```

```typescript
import { CanActivate, ExecutionContext, Injectable } from "@nestjs/common";
import { PolicyPoint } from "./policy-point";


export function AuthzGuard(action: string, resourceType: string) {
    @Injectable()
    class AuthzGuardClass implements CanActivate {
        constructor(private readonly policyPoint: PolicyPoint) {}

        async canActivate(context: ExecutionContext): Promise<boolean> {
            const request = context.switchToHttp().getRequest();
            const decision = await this.policyPoint.decide({
                principal: request.principal,
                action,
                resourceType,
                resourceId: request.params.id,
            });
            return decision.allow === true;
        }
    }
    return AuthzGuardClass;
}
```

Why these patterns satisfy authorization.authz-before-resource-access:
- The authorization decision evaluates BEFORE the resource is
  loaded into application memory
- Pattern A makes the ordering explicit at the application
  layer; Pattern B makes the data layer enforce ordering by
  including the policy in the query plan; Pattern C makes the
  framework enforce ordering by running the guard before the
  handler
- Static analysis detects the ordering: the authz call site
  appears textually before the fetch call site, and the fetch
  result does not flow into the authz decision
