<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.least-privilege-role-design least-privilege role and permission design (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Two-role design (admin and everyone-else) for complex application

```python
# FORBIDDEN: a real application with reports, users, payments,
# and configuration collapsed to two roles. The "admin" role
# can do everything; everyone else can do nothing privileged.
def is_authorized_BAD(user, action):
    if action.startswith("admin."):
        return user.role == "admin"
    return user.is_authenticated  # everything else is "regular user"
```

Why this violates authorization.least-privilege-role-design:
- A user who needs to do ONE privileged thing (e.g., archive
  reports) is granted the admin role and acquires everything
- Role inflation: the admin role becomes a security-team
  catch-all because no other privilege boundaries exist
- The substrate-required pattern is role granularity that
  matches the application's actual privilege boundaries

## Anti-pattern B: Permission strings constructed in business code

```javascript
// FORBIDDEN: permissions assembled by concatenating strings
// at the call site. The role catalog is impossible to audit
// because permissions are not stable identifiers.
function canPerform_BAD(user, resource, verb) {
  const required = `${verb}-${resource.type}-${resource.tenant}`;
  // produces "edit-report-tenant_alpha", "delete-user-tenant_beta", etc.
  return user.permissions.includes(required);
}
```

Why this violates authorization.least-privilege-role-design:
- The permission identifier space is unbounded
- A code change that changes the concatenation breaks every
  existing grant
- Role catalogs cannot be reviewed as data because permissions
  are computed; reviewers cannot see what permissions exist
- The substrate-recommended pattern is a fixed action vocabulary
  (Pattern A in the paired good-example file)

## Anti-pattern C: Roles defined as code constants (Python)

```python
# FORBIDDEN: role-to-permission mapping in Python code. Adding
# a permission to a role requires a code change and deploy.
ROLE_PERMISSIONS_BAD = {
    "admin": ["*"],  # everything; substrate strongly discourages wildcards
    "editor": [
        "report.read",
        "report.write",
        "report.delete",  # editor with delete; common over-grant
        "report.publish",  # AND publish; separation of duties lost
    ],
    "viewer": ["report.read"],
}


def has_permission_BAD(user, action):
    return action in ROLE_PERMISSIONS_BAD.get(user.role, [])
```

Why this violates authorization.least-privilege-role-design:
- Wildcard permissions ("*") defeat the least-privilege
  principle by definition
- Combining write, delete, and publish in one role removes the
  separation-of-duties that distinguishes editor from publisher
- Role definitions in code require code review and deploy for
  every permission tweak; operational friction discourages
  legitimate cleanup
- The role catalog is not auditable by non-developers (e.g.,
  security or compliance reviewers)

## Anti-pattern D: Role grants permanent and unauditable (Java)

```java
// FORBIDDEN: roles assigned by direct database update via
// admin UI, no audit trail. Revocation is also unauditable.
@PostMapping("/admin/grant-role")
public void grantRole_BAD(@RequestBody RoleGrant grant) {
    User user = userRepo.findById(grant.userId).orElseThrow();
    user.getRoles().add(grant.role);
    userRepo.save(user);  // NO AUDIT EVENT
}


@DeleteMapping("/admin/revoke-role")
public void revokeRole_BAD(@RequestBody RoleGrant grant) {
    User user = userRepo.findById(grant.userId).orElseThrow();
    user.getRoles().remove(grant.role);
    userRepo.save(user);  // NO AUDIT EVENT
}
```

Why this violates authorization.least-privilege-role-design (and authorization.step-up-and-audit-for-privilege-changes):
- No audit event records who granted or revoked the role
- Investigation of "how did this account get the admin role"
  is impossible
- The pattern violates authorization.step-up-and-audit-for-privilege-changes (privilege-changing
  operations require audit) and undermines the verifiability
  property authorization.least-privilege-role-design requires

## Anti-pattern E: Permissions cached without invalidation (Node.js)

```javascript
// FORBIDDEN: permissions loaded at session start and cached
// for the session lifetime (hours). Revocation does not take
// effect until the user logs out and back in.
const sessionPermissions = new Map();


function getPermissions_BAD(sessionId, principalId) {
  if (sessionPermissions.has(sessionId)) {
    return sessionPermissions.get(sessionId);  // STALE FOREVER
  }
  const perms = loadPermissionsFromDb(principalId);
  sessionPermissions.set(sessionId, perms);
  return perms;
}
```

Why this violates authorization.least-privilege-role-design:
- Revocation latency equals session lifetime
- Compromised principal whose access is "revoked" remains
  effective for hours
- Incident response cannot rely on revocation to stop an
  attack
- Substrate-recommended pattern is short TTL (Pattern D in
  the paired good-example file) plus explicit invalidation
  on grant mutations
