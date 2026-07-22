<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.least-privilege-role-design least-privilege role and permission design (good patterns)

Substrate-original good-pattern examples for authorization.least-privilege-role-design.

## Pattern A: Role catalog as data with documented permitted actions

```yaml
# policies/roles.yaml - role definitions external to code
roles:
  viewer:
    description: "Read-only access to public reports"
    permitted_actions:
      - report.read
      - report.list
    prohibited_actions:
      - report.write
      - report.delete
      - report.archive
      - user.manage

  editor:
    description: "Draft and edit own reports"
    permitted_actions:
      - report.read
      - report.list
      - report.draft
      - report.edit-own
      - report.archive-own
    prohibited_actions:
      - report.delete
      - report.publish
      - user.manage

  publisher:
    description: "Publish reports authored by editors"
    permitted_actions:
      - report.read
      - report.list
      - report.publish
    prohibited_actions:
      - report.write
      - report.delete
      - user.manage

  admin:
    description: "User and system administration"
    permitted_actions:
      - user.read
      - user.manage
      - report.read
      - report.list
      - role.assign
    prohibited_actions:
      # Admin does NOT include report.write; the substrate
      # recommends separating administrative actions from
      # content actions
      - report.write
      - report.publish
```

The role catalog is data. Test code (per the authorization.least-privilege-role-design test
template) iterates over this YAML to generate test scenarios
for each role's permitted and prohibited actions.

## Pattern B: Permissions at action granularity, not endpoint granularity

```python
# Action names describe what the user is doing, not which
# HTTP endpoint they hit. A single endpoint can dispatch
# different actions based on request content.
@app.post("/reports/<id>/transition")
def transition_report(id):
    target_state = request.json["target_state"]
    action = f"report.{target_state}"  # report.publish, report.archive, etc.

    decision = policy_point.decide(
        principal=current_principal(),
        action=action,
        resource_type="report",
        resource_id=id,
    )
    if decision.allow is not True:
        abort(403)

    apply_state_transition(id, target_state)
```

A user with permission to archive but not publish hits the
same endpoint; the action-level authorization differentiates.

## Pattern C: Role grants are auditable and revocable

```python
# Grant operations are themselves privileged actions (per
# authorization.step-up-and-audit-for-privilege-changes) and produce audit events.
@app.post("/admin/role-grants")
@requires_step_up
def grant_role(payload: RoleGrantInput):
    actor = current_principal()
    decision = policy_point.decide(
        principal=actor,
        action="role.assign",
        resource_type="user",
        resource_id=payload.target_user_id,
    )
    if decision.allow is not True:
        abort(403)

    target = User.get(payload.target_user_id)
    before_roles = list(target.roles)

    RoleGrant.create(
        user=target,
        role=payload.role,
        granted_by=actor,
        granted_at=now(),
    )

    audit_log.emit(
        event_type="role_granted",
        actor=actor.subject_id,
        target=target.subject_id,
        role=payload.role,
        before_state=before_roles,
        after_state=list(target.roles),
        severity="WARN",
        correlation_id=current_correlation_id(),
    )
```

## Pattern D: Revocation latency is bounded by session refresh

```python
# Sessions cache role grants for performance, with a short
# TTL so revocation takes effect within the TTL.
class SessionCache:
    PERMISSION_TTL = timedelta(minutes=5)

    def get_permissions(self, principal_id):
        cached = self.cache.get(f"perms:{principal_id}")
        if cached and (now() - cached["fetched_at"]) < self.PERMISSION_TTL:
            return cached["permissions"]

        # Refresh from authoritative source
        permissions = self._fetch_from_db(principal_id)
        self.cache.set(f"perms:{principal_id}", {
            "permissions": permissions,
            "fetched_at": now(),
        })
        return permissions

    def invalidate(self, principal_id):
        """Called by the role-grant mutation paths to flush
        cache immediately on grant or revoke."""
        self.cache.delete(f"perms:{principal_id}")
```

Grant and revoke mutations call invalidate to drop cached
permissions; this bounds revocation latency to the next
request after the grant change.

Why these patterns satisfy authorization.least-privilege-role-design:
- Role catalog is data: changes happen in YAML, not in code
- Role definitions document both permitted and prohibited
  actions so reviewers and tests can verify the boundary
- Action granularity is fine enough that role separation is
  meaningful (admin does not also have content-write)
- Grants and revocations are auditable; revocation takes
  effect promptly
- The role catalog as data enables data-driven testing of the
  least-privilege property per the test-template binding
