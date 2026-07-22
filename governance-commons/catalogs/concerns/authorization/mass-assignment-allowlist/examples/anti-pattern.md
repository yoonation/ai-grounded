<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.mass-assignment-allowlist mass-assignment uses allowlist (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Splat-assign request body to model (Python / Flask)

```python
# FORBIDDEN: request body unpacked directly into the User
# constructor. An attacker posts {"is_admin": true} and
# becomes admin.
@app.route("/users", methods=["POST"])
def create_user_BAD():
    body = request.get_json()
    user = User(**body)  # MASS ASSIGNMENT
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict())
```

Why this violates authorization.mass-assignment-allowlist:
- The request body's keys map directly to User attributes
- New User fields are automatically exposed
- This is the canonical CWE-915 (improperly controlled
  modification of dynamically determined object attributes)
  pattern

## Anti-pattern B: Update via .update() on full body (Python / Django)

```python
# FORBIDDEN: every field in the request body is assigned to
# the user model. The attacker posts is_admin or is_staff.
def update_user_BAD(request, user_id):
    user = User.objects.get(pk=user_id)
    body = json.loads(request.body)
    for key, value in body.items():
        setattr(user, key, value)  # NO ALLOWLIST
    user.save()
    return JsonResponse(user.to_dict())
```

Why this violates authorization.mass-assignment-allowlist:
- Every key in the body sets a model attribute
- Adding new sensitive fields to User exposes them silently
- Static analysis fires authorization.mass-assignment-allowlist on the setattr loop with
  request data

## Anti-pattern C: Rails .update without strong parameters (Ruby / Rails)

```ruby
# FORBIDDEN: bypasses strong parameters and passes the entire
# params hash. Rails 7+ disables this by default, but legacy
# code paths and explicit .permit! still allow it.
class UsersController < ApplicationController
  def update
    @user = User.find(params[:id])
    @user.update!(params[:user].permit!)  # PERMIT EVERYTHING
    render json: @user
  end
end
```

Why this violates authorization.mass-assignment-allowlist:
- `params.permit!` permits all fields including is_admin,
  password_digest, and any added later
- The strong-parameters mechanism exists specifically to
  prevent this pattern
- Static analysis fires on .permit! call

## Anti-pattern D: Denylist instead of allowlist (Python)

```python
# FORBIDDEN: denylist approach. New sensitive fields default
# to exposed.
SENSITIVE_FIELDS = {"is_admin", "password_hash"}


def update_user_BAD(request, user_id):
    user = User.objects.get(pk=user_id)
    body = json.loads(request.body)
    for key, value in body.items():
        if key in SENSITIVE_FIELDS:
            continue
        setattr(user, key, value)  # ALLOW EVERYTHING ELSE
    user.save()
```

Why this violates authorization.mass-assignment-allowlist:
- Denylist defaults to "exposed unless listed as sensitive"
- A new sensitive field (e.g., "tenant_id" added later)
  defaults to exposed until someone remembers to add it to
  SENSITIVE_FIELDS
- The substrate-required pattern is allowlist (Pattern A in
  the paired good-example file): explicit list of permitted
  fields, default to denied

## Anti-pattern E: Jackson without view restriction (Java)

```java
// FORBIDDEN: full User object bound from request body. Any
// field in User is bindable.
@PostMapping("/users")
public User createUser_BAD(@RequestBody User input) {
    return userService.save(input);  // FULL OBJECT BOUND
}
```

Why this violates authorization.mass-assignment-allowlist:
- Jackson binds every field in User from the request body,
  including is_admin, passwordHash, createdAt
- The pattern fails the substrate's requirement for a
  separate input boundary (DTO with allowlisted fields, or
  @JsonView restriction as in Pattern D of the paired good-
  example file)
- Static analysis fires on @RequestBody binding to a
  persistence-layer model
