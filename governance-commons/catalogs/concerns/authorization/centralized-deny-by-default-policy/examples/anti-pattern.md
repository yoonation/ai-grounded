<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.centralized-deny-by-default-policy centralized deny-by-default policy (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Inline authz at every call site (Python)

```python
# FORBIDDEN: each endpoint reimplements its own authz logic.
# No central policy point.
@app.route("/invoices/<id>")
def get_invoice_BAD(id):
    user = current_user()
    invoice = Invoice.objects.get(pk=id)
    if user.role == "admin" or invoice.owner_id == user.id:
        return JsonResponse(invoice.to_dict())
    return HttpResponseForbidden()


@app.route("/reports/<id>")
def get_report_BAD(id):
    user = current_user()
    report = Report.objects.get(pk=id)
    if user.role == "admin" or report.owner_id == user.id or report.is_public:
        return JsonResponse(report.to_dict())
    return HttpResponseForbidden()


@app.route("/comments/<id>")
def get_comment_BAD(id):
    user = current_user()
    comment = Comment.objects.get(pk=id)
    # Subtle differences across endpoints. Bug: missing
    # is_admin shortcut means admins cannot delete comments.
    if comment.author_id == user.id:
        return JsonResponse(comment.to_dict())
    return HttpResponseForbidden()
```

Why this violates authorization.centralized-deny-by-default-policy:
- Authorization logic distributed across endpoints
- Subtle inconsistency (the comment endpoint omits the admin
  override; possibly intentional, possibly a bug, impossible
  to tell from code review)
- Adding a new role requires editing every endpoint
- The substrate's L2-005 finding fires precisely because
  there is no centralized policy point

## Anti-pattern B: Centralized function but allow-by-default (Python)

```python
# FORBIDDEN: a single function, but its default is allow.
# Unknown subjects, actions, or resources fall through to
# allow.
def is_authorized_BAD(user, action, resource):
    if user.role == "blocked":
        return False
    if action == "delete" and resource.is_locked:
        return False
    return True  # ALLOW-BY-DEFAULT
```

Why this violates authorization.centralized-deny-by-default-policy:
- Centralization is present, but the default is wrong
- An action not anticipated (newly added feature, typo in
  action name) returns True
- A new attacker-controlled action string defaults to allow
- The substrate's L2-005 requirement is deny-by-default; the
  function must return False unless an explicit allow rule
  matches

## Anti-pattern C: Configuration object treated as policy (Node.js)

```javascript
// FORBIDDEN: "policy" is a config object hard-coded in the
// application. Changes to "policy" require code deploys.
const POLICY = {
  admin: { canDo: ["everything"] },
  editor: { canDo: ["read", "write"] },
  viewer: { canDo: ["read"] },
};


function canPerform_BAD(user, action) {
  const perms = POLICY[user.role]?.canDo || [];
  if (perms.includes("everything")) return true;
  return perms.includes(action);
}
```

Why this violates authorization.centralized-deny-by-default-policy:
- "everything" wildcard defeats deny-by-default (any future
  action defaults to allowed for admin)
- The config is data in the sense of being a JavaScript
  object, but it lives in code and ships with deploys
- Policy is not testable as data because it is intertwined
  with the canPerform function
- Substrate-required pattern: external policy engine (Cedar,
  OPA) or data-backed policy classes (Pundit)

## Anti-pattern D: Default-to-allow when policy engine fails (Python)

```python
# FORBIDDEN: when the policy engine is unreachable, the code
# falls back to allow.
def decide_BAD(principal, action, resource):
    try:
        return opa_client.decide(principal, action, resource)
    except requests.RequestException:
        # FALL OPEN
        log.warning("opa unavailable; allowing")
        return Decision(allow=True, reason="opa-down")
```

Why this violates authorization.centralized-deny-by-default-policy:
- "Fail open" on policy-engine failure makes the policy
  engine optional
- An attacker who can make OPA unreachable (DOS, network
  partition) bypasses authorization
- Substrate-required behavior: deny-by-default on policy
  engine failure, with operational alerting for engine
  outages

## Anti-pattern E: Policy embedded in ORM queries (Python)

```python
# FORBIDDEN: authorization "rules" implemented as ORM filter
# clauses scattered across the codebase.
def list_visible_reports_BAD(user):
    return Report.objects.filter(
        Q(owner_id=user.id) |
        Q(is_public=True) |
        Q(shared_with=user) |
        (Q(team_id__in=user.team_ids) & Q(team_visible=True))
    )


def list_visible_invoices_BAD(user):
    # SIMILAR LOGIC, SUBTLY DIFFERENT
    return Invoice.objects.filter(
        Q(owner_id=user.id) |
        Q(visible_to=user) |
        (Q(department_id=user.department_id) & Q(department_visible=True))
    )
```

Why this violates authorization.centralized-deny-by-default-policy:
- The authorization rules live in ORM query construction
- The rules are not testable independent of the database
- Adding a new "visibility" concept requires changes across
  every list endpoint
- The substrate-recommended pattern is Row-Level Security
  (data-layer enforcement) plus a centralized policy point
  for action-level decisions; ORM-embedded rules satisfy
  neither layer
