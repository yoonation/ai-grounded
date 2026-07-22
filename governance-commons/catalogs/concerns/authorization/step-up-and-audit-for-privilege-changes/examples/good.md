<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.step-up-and-audit-for-privilege-changes step-up authentication and audit for privilege changes (good patterns)

Substrate-original good-pattern examples for authorization.step-up-and-audit-for-privilege-changes.

## Pattern A: Step-up required on grant or revoke (Python)

```python
from functools import wraps
from datetime import timedelta


STEP_UP_FRESHNESS = timedelta(minutes=10)  # substrate-recommended 5-15


def requires_step_up(fn):
    """Decorator: require recent MFA challenge bound to the
    session before allowing the privilege-changing operation."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        principal = current_principal()
        last_step_up = session_state.get_last_step_up(principal.session_id)
        if last_step_up is None or (now() - last_step_up) > STEP_UP_FRESHNESS:
            return JsonResponse(
                {"error": "step_up_required",
                 "challenge_endpoint": "/auth/step-up"},
                status=401,
            )
        return fn(*args, **kwargs)
    return wrapper


@app.post("/admin/roles")
@requires_step_up
def grant_role(payload: RoleGrantInput):
    actor = current_principal()
    target = User.get(payload.target_user_id)

    # Authorization check that the actor MAY grant this role.
    decision = policy_point.decide(
        principal=actor,
        action="role.assign",
        resource_type="user",
        resource_id=target.id,
    )
    if decision.allow is not True:
        # Audit the failed attempt
        audit_log.emit(
            event_type="role_grant_attempted",
            actor=actor.subject_id,
            target=target.subject_id,
            role=payload.role,
            decision="deny",
            severity="WARN",
            correlation_id=current_correlation_id(),
        )
        abort(403)

    before_roles = list(target.roles)
    RoleGrant.create(user=target, role=payload.role,
                      granted_by=actor, granted_at=now())
    after_roles = list(target.roles)

    audit_log.emit(
        event_type="role_granted",
        actor=actor.subject_id,
        target=target.subject_id,
        role=payload.role,
        before_state=before_roles,
        after_state=after_roles,
        step_up_verified=True,
        severity="WARN",
        correlation_id=current_correlation_id(),
    )
    return jsonify({"status": "granted"})
```

## Pattern B: Step-up also required on revoke (Python)

```python
@app.delete("/admin/roles/<target_id>/<role>")
@requires_step_up  # SAME PROTECTION AS GRANT
def revoke_role(target_id, role):
    actor = current_principal()
    target = User.get(target_id)

    decision = policy_point.decide(
        principal=actor,
        action="role.revoke",
        resource_type="user",
        resource_id=target_id,
    )
    if decision.allow is not True:
        abort(403)

    before_roles = list(target.roles)
    RoleGrant.objects.filter(user=target, role=role).delete()
    after_roles = list(target.roles)

    audit_log.emit(
        event_type="role_revoked",
        actor=actor.subject_id,
        target=target.subject_id,
        role=role,
        before_state=before_roles,
        after_state=after_roles,
        step_up_verified=True,
        severity="WARN",  # revocation is also high-impact
        correlation_id=current_correlation_id(),
    )
    return "", 204
```

Revocation is privilege-changing. Treating it as low-risk
because "it only reduces access" is wrong: revocation can be
weaponized (revoking the security team during an attack).

## Pattern C: Ownership transfer requires step-up (Python)

```python
@app.post("/resources/<id>/transfer-ownership")
@requires_step_up
def transfer_ownership(id):
    actor = current_principal()
    resource = Resource.get(id)

    decision = policy_point.decide(
        principal=actor,
        action="ownership.transfer",
        resource_type="resource",
        resource_id=id,
    )
    if decision.allow is not True:
        abort(403)

    new_owner_id = request.json["new_owner_id"]
    old_owner_id = resource.owner_id
    resource.owner_id = new_owner_id
    resource.save()

    audit_log.emit(
        event_type="ownership_transferred",
        actor=actor.subject_id,
        resource_type="resource",
        resource_id=id,
        before_state={"owner": old_owner_id},
        after_state={"owner": new_owner_id},
        step_up_verified=True,
        severity="WARN",
        correlation_id=current_correlation_id(),
    )
```

## Pattern D: Bulk privilege operations audited per change (Python)

```python
@app.post("/admin/roles/batch")
@requires_step_up
def grant_roles_batch(payload: BatchRoleGrantInput):
    actor = current_principal()
    results = []

    for assignment in payload.assignments:
        # Per-assignment authz check
        target = User.get(assignment.user_id)
        decision = policy_point.decide(
            principal=actor,
            action="role.assign",
            resource_type="user",
            resource_id=target.id,
        )
        if decision.allow is not True:
            results.append({
                "user_id": assignment.user_id,
                "role": assignment.role,
                "status": "denied",
            })
            continue

        before_roles = list(target.roles)
        RoleGrant.create(user=target, role=assignment.role,
                          granted_by=actor, granted_at=now())
        after_roles = list(target.roles)

        # ONE AUDIT EVENT PER ASSIGNMENT (not one for the bulk request)
        audit_log.emit(
            event_type="role_granted",
            actor=actor.subject_id,
            target=target.subject_id,
            role=assignment.role,
            before_state=before_roles,
            after_state=after_roles,
            step_up_verified=True,
            severity="WARN",
            correlation_id=current_correlation_id(),
            batch_id=payload.batch_id,
        )
        results.append({
            "user_id": assignment.user_id,
            "role": assignment.role,
            "status": "granted",
        })

    return jsonify(results)
```

Why these patterns satisfy authorization.step-up-and-audit-for-privilege-changes:
- Step-up freshness window enforced; expired step-up returns
  401 with challenge endpoint
- Step-up is required on grant, revoke, and ownership transfer
- Audit events include before-and-after state for post-
  incident reconstruction
- Bulk operations emit one audit event per change, not one
  for the bulk request
- Audit events at WARN minimum severity so security monitoring
  consumes them (per authorization.audit-events-on-decisions)
