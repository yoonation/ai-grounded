<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.protected-route-declares-authz protected route declares server-side authorization (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Route handler with no authorization at all (Python / Flask)

```python
# FORBIDDEN: route returns resource content with no authz check.
# Any authenticated principal can access any report.
@app.route("/reports/<id>")
def get_report_BAD(id):
    return fetch_report(id).to_json()
```

Why this violates authorization.protected-route-declares-authz:
- No declaration of who may access; authentication alone is
  treated as authorization
- Cannot be detected by reviewing the route in isolation
- Static analysis fires authorization.protected-route-declares-authz because the route lacks
  the substrate-recommended decorator

## Anti-pattern B: Authorization in the wrong layer (Node.js / Express)

```javascript
// FORBIDDEN: authorization buried inside the resource fetch,
// after the resource is loaded from the database.
app.get("/reports/:id", async (req, res) => {
  const report = await fetchReport(req.params.id); // resource fetched first
  if (req.user.role !== "admin" && report.ownerId !== req.user.id) {
    return res.status(403).end();
  }
  res.json(report);
});
```

Why this violates authorization.protected-route-declares-authz (and authorization.authz-before-resource-access):
- The authorization construct is not at the route declaration
  level; reviewers scanning the route table cannot tell which
  routes are protected
- Authorization happens after resource fetch (per authorization.authz-before-resource-access,
  this is the IDOR ordering bug; the L1-001 finding is
  separate: the route declaration itself does not declare
  authz)
- Hardcoded role string "admin" is a separate authorization.no-hardcoded-role-strings
  finding

## Anti-pattern C: Conditional authorization (Java / Spring)

```java
// FORBIDDEN: authorization happens only when the feature flag
// is enabled. If the flag is off, the route is unprotected.
@GetMapping("/reports/{id}")
public Report getReport_BAD(
    @PathVariable String id,
    Authentication authentication
) {
    if (featureFlags.isAuthzEnabled()) {
        if (!policyPoint.canRead(id, authentication)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN);
        }
    }
    return reportService.findById(id);
}
```

Why this violates authorization.protected-route-declares-authz:
- Authorization is not unconditional; a runtime flag can
  silently disable it
- Common failure: the flag's "off" state was intended for
  development but ships to production
- The substrate's L1 rule requires the authorization construct
  to be present in the route declaration; feature flags can
  control policy content, not policy presence

## Anti-pattern D: Comment in place of authorization (Python / Flask)

```python
# FORBIDDEN: comment claims authorization happens; code does
# not enforce it.
@app.route("/admin/users/<id>", methods=["DELETE"])
def delete_user_BAD(id):
    # TODO: add authz check here
    User.query.filter_by(id=id).delete()
    return "", 204
```

Why this violates authorization.protected-route-declares-authz:
- A TODO comment is not authorization
- This pattern is the substrate's most-common L1 finding in
  real codebases: development scaffolding shipped to production
- Static analysis catches the absence of the substrate-
  recommended construct regardless of intent expressed in
  comments
