<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.no-client-side-only-authz no client-side-only authorization on privileged actions (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: SPA route guard with no server enforcement (Angular)

```typescript
// FORBIDDEN: route guard hides the admin page from non-admins
// but the admin API endpoint has no server-side authz check.
@Injectable()
export class AdminRouteGuard implements CanActivate {
  canActivate(): boolean {
    return this.authService.user.role === "admin";
  }
}
```

```python
# FORBIDDEN: the admin endpoint trusts the client to have done
# the check. A direct curl request bypasses the route guard.
@app.route("/admin/api/delete-user/<id>", methods=["POST"])
def admin_delete_user_BAD(id):
    User.query.filter_by(id=id).delete()  # NO AUTHZ
    return "", 204
```

Why this violates authorization.no-client-side-only-authz:
- A malicious user with non-admin credentials can curl
  POST /admin/api/delete-user/{id} and delete any user
- The client-side guard provides no security; it provides
  only UX
- Static analysis fires on the unguarded server endpoint;
  the client-side guard does not satisfy L1-001 or L1-004

## Anti-pattern B: Hidden form field as "authorization" (HTML)

```html
<!-- FORBIDDEN: the form includes a hidden field indicating
     the user's role. The server "trusts" this field. -->
<form action="/api/admin-action" method="POST">
  <input type="hidden" name="user_role" value="admin">
  <input type="text" name="target_user_id" placeholder="User ID">
  <button type="submit">Delete User</button>
</form>
```

```python
# FORBIDDEN: server reads the role from the form field.
@app.route("/api/admin-action", methods=["POST"])
def admin_action_BAD():
    if request.form.get("user_role") == "admin":  # CLIENT-CONTROLLED INPUT
        target = request.form.get("target_user_id")
        User.query.filter_by(id=target).delete()
        return "", 204
    return "", 403
```

Why this violates authorization.no-client-side-only-authz:
- The "user_role" is supplied by the client (the HTML form)
  and trusted by the server
- An attacker submits the form with user_role=admin in any
  browser or with curl
- The pattern is functionally equivalent to no authorization
  at all
- Static analysis fires on the client-supplied authz input

## Anti-pattern C: JavaScript-only feature flag (React)

```jsx
// FORBIDDEN: feature only "available" if the JavaScript bundle
// decides the user is on the beta list. No server check.
function BetaFeaturePage() {
  const isBetaUser = localStorage.getItem("isBetaUser") === "true";
  if (!isBetaUser) {
    return <div>Beta access required</div>;
  }
  return <BetaFeatureContent />;
}
```

```python
# FORBIDDEN: server endpoint trusts the client to have done
# the beta-user check.
@app.route("/api/beta-feature-data")
def beta_data_BAD():
    return jsonify(load_sensitive_beta_data())  # NO AUTHZ
```

Why this violates authorization.no-client-side-only-authz:
- The localStorage value is fully controllable by the user
  (browser dev tools, console)
- The pattern is common in early-stage product development
  and often persists into production
- Substrate-recommended fix: the server endpoint enforces
  beta-list membership via the policy point regardless of
  what the client claims

## Anti-pattern D: JWT claim trusted without verification (Node.js)

```javascript
// FORBIDDEN: the server reads the role claim from the JWT
// payload without verifying the JWT signature, OR the JWT
// was issued without the server controlling its claims.
app.post("/api/admin-action", (req, res) => {
  const token = req.headers.authorization?.split(" ")[1];
  const payload = JSON.parse(Buffer.from(token.split(".")[1], "base64").toString());
  if (payload.role === "admin") {  // NO SIGNATURE VERIFICATION
    performAdminAction();
    return res.status(204).end();
  }
  return res.status(403).end();
});
```

Why this violates authorization.no-client-side-only-authz (with overlap to authentication concerns):
- An attacker can craft a JWT with role=admin and base64-
  encode it; without signature verification, the server
  trusts it
- Even with signature verification, if the JWT is issued by
  a client-controlled identity provider or with client-
  controlled claims, the role field is client-supplied
- The substrate-required pattern is server-issued tokens whose
  claims are populated by the server-side policy point at
  authentication time, with mandatory signature verification
  on every request
