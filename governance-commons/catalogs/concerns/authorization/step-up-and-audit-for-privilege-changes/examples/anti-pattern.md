<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.step-up-and-audit-for-privilege-changes step-up authentication and audit for privilege changes (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Grant role with standard session, no step-up (Python)

```python
# FORBIDDEN: any authenticated session can grant any role
# given role.assign permission. A stolen session cookie
# extends to all privilege-changing operations.
@app.post("/admin/roles")
def grant_role_BAD(payload):
    actor = current_principal()
    if not actor.has_permission("role.assign"):
        abort(403)

    target = User.get(payload["target_user_id"])
    RoleGrant.create(user=target, role=payload["role"])
    return "", 201
```

Why this violates authorization.step-up-and-audit-for-privilege-changes:
- No step-up requirement; a stolen session can grant admin
  roles to attacker-controlled accounts
- No audit event recording the change

## Anti-pattern B: Audit event missing critical fields (Node.js)

```javascript
// FORBIDDEN: grant happens, audit event emitted but content
// is insufficient for investigation.
app.post("/admin/roles", async (req, res) => {
  const grant = req.body;
  await db.roleGrants.insert({
    userId: grant.userId,
    role: grant.role,
  });
  console.log(`role grant happened`);  // useless audit
  res.sendStatus(201);
});
```

Why this violates authorization.step-up-and-audit-for-privilege-changes:
- The audit "event" is a plaintext log line with no actor,
  no target, no role, no timestamp, no correlation ID
- logging.structured-format (structured format) violated
- The investigation question "who granted what role to whom
  and when" cannot be answered
- No step-up requirement

## Anti-pattern C: Revoke without audit (Python)

```python
# FORBIDDEN: revocations are not audited because "they only
# reduce access". Investigation of "who lost access during
# the incident" is impossible.
@app.delete("/admin/roles/<user_id>/<role>")
def revoke_role_BAD(user_id, role):
    actor = current_principal()
    if not actor.has_permission("role.revoke"):
        abort(403)
    RoleGrant.objects.filter(user_id=user_id, role=role).delete()
    return "", 204
    # NO AUDIT
```

Why this violates authorization.step-up-and-audit-for-privilege-changes:
- Revocation is privilege-changing and must be audited
- An attacker who has compromised an admin can revoke
  legitimate user roles during an attack, locking out the
  defender; absence of audit makes this undetectable
- The substrate treats revocation and grant symmetrically

## Anti-pattern D: Step-up cached for session lifetime (Python)

```python
# FORBIDDEN: step-up state stored on the session and never
# refreshed. One step-up at login extends to every privilege
# change for the rest of the session.
def requires_step_up_BAD(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("did_step_up_at_login"):
            return fn(*args, **kwargs)
        return JsonResponse({"error": "step_up_required"}, status=401)
    return wrapper
```

Why this violates authorization.step-up-and-audit-for-privilege-changes:
- The step-up freshness window is the entire session length
  (often hours or days)
- An attacker with the session can perform any privilege
  change long after the original step-up
- The substrate-recommended window is 5-15 minutes; longer
  windows are documented exceptions

## Anti-pattern E: Bulk operation as single audit event (Python)

```python
# FORBIDDEN: one audit event covers a batch of grants. Per-
# change accountability is lost.
@app.post("/admin/roles/batch")
def grant_batch_BAD(payload):
    actor = current_principal()
    for assignment in payload["assignments"]:
        RoleGrant.create(
            user_id=assignment["user_id"],
            role=assignment["role"],
        )

    # ONE audit event for the whole batch
    audit_log.emit(
        event_type="role_grant_batch",
        actor=actor.subject_id,
        batch_size=len(payload["assignments"]),
        severity="WARN",
    )
```

Why this violates authorization.step-up-and-audit-for-privilege-changes:
- The audit event records "batch happened with N items" but
  not which items or which roles
- Investigation of "did Alice get the admin role on Tuesday"
  cannot be answered from the audit log
- The substrate-required pattern is one event per change,
  with a shared batch_id field for correlation
