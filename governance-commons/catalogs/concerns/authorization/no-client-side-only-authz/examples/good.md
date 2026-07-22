<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.no-client-side-only-authz no client-side-only authorization on privileged actions (good patterns)

Substrate-original good-pattern examples for authorization.no-client-side-only-authz.

## Pattern A: Both server enforces and client hides (React + server)

```jsx
// CLIENT: hides the admin button when the user has no admin
// claim. Pure UI affordance; not an authorization decision.
function ReportToolbar({ report, currentUser }) {
  const canDelete = currentUser.permissions.includes("delete:report");
  return (
    <div>
      <button onClick={() => view(report.id)}>View</button>
      {canDelete && (
        <button onClick={() => deleteReport(report.id)}>Delete</button>
      )}
    </div>
  );
}
```

```python
# SERVER: actually enforces. The button hiding above is
# convenience; even if a malicious client re-enables the
# button or constructs the DELETE request directly, the
# server rejects without the right permission.
@app.route("/reports/<id>", methods=["DELETE"])
def delete_report(id):
    decision = policy_point.decide(
        principal=current_principal(),
        action="delete",
        resource_type="report",
        resource_id=id,
    )
    if decision.allow is not True:
        abort(403)
    delete_report_record(id)
    return "", 204
```

The client hint (the permission claim in the user profile) is
useful for UX; the server is the authority. The same policy
point produces both: the server enforces by calling decide(),
and the user profile claim is populated by querying decide()
for the actions the client cares about hinting.

## Pattern B: GraphQL with field-level server authorization (TypeScript)

```typescript
// CLIENT: query asks for fields the user has permission for.
// If the user lacks permission for a field, the server omits
// the field from the response.
const QUERY = `
  query Report($id: ID!) {
    report(id: $id) {
      id
      title
      content
      auditTrail  # admin-only field
    }
  }
`;
```

```typescript
// SERVER: the auditTrail resolver enforces authorization.
// The client cannot get the field by asking for it; the
// server returns null when the principal lacks permission.
export const reportResolver = {
  Report: {
    auditTrail: async (parent, args, context) => {
      const decision = await context.policyPoint.decide({
        principal: context.principal,
        action: "read",
        resourceType: "report.auditTrail",
        resourceId: parent.id,
      });
      if (!decision.allow) return null;
      return fetchAuditTrail(parent.id);
    },
  },
};
```

The client can request any field; the server decides what to
return. The client-side conditional rendering is a UX nicety
but not the security mechanism.

## Pattern C: SPA route guard with server-enforced API (Angular + server)

```typescript
// CLIENT: route guard prevents the user from navigating to
// the admin page when they lack the admin role hint.
// PURE UI: the API still enforces.
@Injectable()
export class AdminRouteGuard implements CanActivate {
  constructor(private authService: AuthService) {}

  canActivate(): boolean {
    return this.authService.hasRoleHint("admin");
  }
}
```

```python
# SERVER: every API endpoint the admin page calls still
# enforces. The client-side guard is UX only.
@app.route("/admin/api/users")
def admin_list_users():
    decision = policy_point.decide(
        principal=current_principal(),
        action="list",
        resource_type="users",
    )
    if decision.allow is not True:
        abort(403)
    return jsonify([u.to_dict() for u in User.query.all()])
```

Why these patterns satisfy authorization.no-client-side-only-authz:
- Server enforces every privileged action; the client decision
  is convenience and can be bypassed without security impact
- The client-side hint is sourced from server-issued claims
  (token, profile API), not from client-only state
- A malicious client (e.g., crafted curl request) cannot
  perform the privileged action because the server still
  evaluates the policy
- Static analysis fires authorization.no-client-side-only-authz on client-side checks
  without a corresponding server enforcement; these patterns
  pair both, so the rule does not fire
