<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.no-hardcoded-role-strings no hardcoded role or permission strings in business logic (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Role string comparisons throughout business logic (Python)

```python
# FORBIDDEN: role strings embedded in business logic across
# many call sites. Renaming "admin" to "administrator"
# requires editing every site.
def archive_report_BAD(user, report):
    if user.role == "admin":
        report.archive()
    elif user.role == "editor" and report.status == "draft":
        report.archive()
    else:
        raise PermissionDenied()


def delete_report_BAD(user, report):
    if user.role == "admin":  # SAME STRING IN ANOTHER PLACE
        report.delete()
    else:
        raise PermissionDenied()


def feature_flag_check_BAD(user):
    if user.role == "admin" or user.role == "editor":  # AGAIN
        return True
    return False
```

Why this violates authorization.no-hardcoded-role-strings:
- "admin" and "editor" appear as literal strings across many
  business-logic call sites
- Role renaming requires editing every site (high risk of
  missing one)
- Adding a new role (e.g., "moderator") requires touching every
  site that should permit moderators
- The role concept is encoded in code, not in data

## Anti-pattern B: Role check via string concatenation (Node.js)

```javascript
// FORBIDDEN: role hard-coded, with additional string-
// concatenation cruft that obscures the dependency.
function canEdit_BAD(user, resourceType) {
  const requiredRole = "edit-" + resourceType + "-role";  // builds "edit-report-role"
  return user.roles.includes(requiredRole);
}
```

Why this violates authorization.no-hardcoded-role-strings:
- Role names are constructed from string fragments in business
  logic
- Static analysis can detect the pattern as a string-
  concatenated role reference
- A typo in any fragment produces silent permission denial
  rather than a build-time error

## Anti-pattern C: Role hierarchy hard-coded in code (Python)

```python
# FORBIDDEN: role precedence table in code. Every role change
# requires deploying.
ROLE_PRECEDENCE = ["viewer", "editor", "admin", "superadmin"]


def has_at_least(user_role, required_role):
    return ROLE_PRECEDENCE.index(user_role) >= ROLE_PRECEDENCE.index(required_role)


def archive_report_BAD(user, report):
    if not has_at_least(user.role, "editor"):  # "editor" hard-coded
        raise PermissionDenied()
    report.archive()
```

Why this violates authorization.no-hardcoded-role-strings:
- Role names and their precedence ordering are encoded as a
  hardcoded list in business code
- Adding a new role between editor and admin requires editing
  the list and redeploying
- The pattern fits ABAC or a role-hierarchy table in the policy
  point, not inline business code

## Anti-pattern D: "Just check the role" reasoning (Java)

```java
// FORBIDDEN: developer "just checked the role" because it was
// faster than going through the policy point. This grows into
// the pattern above as more endpoints follow the same
// expedient.
@PostMapping("/reports/{id}/archive")
public void archive_BAD(
    @PathVariable String id,
    Authentication auth
) {
    boolean isAdminOrEditor = auth.getAuthorities().stream()
        .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN") ||
                       a.getAuthority().equals("ROLE_EDITOR"));
    if (!isAdminOrEditor) {
        throw new ResponseStatusException(HttpStatus.FORBIDDEN);
    }
    reportService.archive(id);
}
```

Why this violates authorization.no-hardcoded-role-strings:
- "ROLE_ADMIN" and "ROLE_EDITOR" appear as literal strings in
  business code
- The inline check duplicates what the @PreAuthorize annotation
  (Pattern D in the paired good-example file) would express
  via the policy point
- The "just check the role" reasoning propagates: another
  developer sees this pattern and copies it for a new endpoint
- The substrate pairs L1-003 with L2-005 (centralized policy)
  to make the alternative concrete; without the centralized
  policy point, every endpoint has to re-implement the role
  check inline
