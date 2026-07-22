<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.mass-assignment-allowlist mass-assignment uses allowlist (good patterns)

Substrate-original good-pattern examples for authorization.mass-assignment-allowlist.

## Pattern A: Pydantic model with explicit allowed fields (Python / FastAPI)

```python
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()


class UserUpdateInput(BaseModel):
    """Allowlist: only fields the client may set."""
    display_name: str | None = None
    email: str | None = None
    bio: str | None = None
    # is_admin, password_hash, created_at, etc. are NOT in the
    # model. Even if the client posts them, Pydantic drops them.

    class Config:
        extra = "forbid"  # reject unknown fields outright


@app.patch("/users/{id}")
def update_user(id: str, payload: UserUpdateInput):
    user = User.get(id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    user.save()
    return user.to_dict()
```

The Pydantic model is the allowlist. Adding a sensitive field
to the User model does not automatically expose it to client
input; the model author must explicitly add it to UserUpdateInput.

## Pattern B: Django REST Framework serializer (Python / Django)

```python
from rest_framework import serializers


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["display_name", "email", "bio"]  # explicit allowlist
        # is_admin, password, created_at intentionally excluded


@api_view(["PATCH"])
def update_user(request, id):
    user = User.objects.get(pk=id)
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
```

The substrate-recommended pattern is `fields = [...]` (allowlist),
NOT `exclude = [...]` (denylist). Adding a new model field
defaults to "not exposed" with the allowlist; defaults to
"exposed unless updated" with the denylist.

## Pattern C: Rails strong parameters (Ruby / Rails)

```ruby
class UsersController < ApplicationController

  def update
    @user = User.find(params[:id])
    @user.update!(user_update_params)
    render json: @user
  end


  private

  def user_update_params
    # Strong parameters: only permit the listed keys.
    # :is_admin and :password_digest are not permitted, so
    # they are silently filtered out.
    params.require(:user).permit(:display_name, :email, :bio)
  end
end
```

## Pattern D: Jackson with @JsonView for separate read/write surfaces (Java / Spring)

```java
public class User {
    public interface PublicWrite {}
    public interface InternalOnly {}

    @JsonView(PublicWrite.class)
    private String displayName;

    @JsonView(PublicWrite.class)
    private String email;

    @JsonView(PublicWrite.class)
    private String bio;

    // is_admin, password_hash, created_at have NO @JsonView
    // for PublicWrite, so the JSON binder will not bind them
    // from the request body.
    private boolean isAdmin;
    private String passwordHash;
    private Instant createdAt;
}


@RestController
public class UsersController {
    @PatchMapping("/users/{id}")
    public User update(
        @PathVariable String id,
        @RequestBody @JsonView(User.PublicWrite.class) User input
    ) {
        User existing = userService.findById(id);
        userService.applyPublicUpdate(existing, input);
        return userService.save(existing);
    }
}
```

## Pattern E: Go with explicit struct for input (Go)

```go
type UserUpdateInput struct {
    DisplayName *string `json:"display_name,omitempty"`
    Email       *string `json:"email,omitempty"`
    Bio         *string `json:"bio,omitempty"`
    // IsAdmin, PasswordHash, CreatedAt intentionally absent
}


func UpdateUser(w http.ResponseWriter, r *http.Request) {
    var input UserUpdateInput
    decoder := json.NewDecoder(r.Body)
    decoder.DisallowUnknownFields()  // reject unknown fields
    if err := decoder.Decode(&input); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    user := lookupUser(mux.Vars(r)["id"])
    if input.DisplayName != nil {
        user.DisplayName = *input.DisplayName
    }
    if input.Email != nil {
        user.Email = *input.Email
    }
    if input.Bio != nil {
        user.Bio = *input.Bio
    }
    saveUser(user)
}
```

Why these patterns satisfy authorization.mass-assignment-allowlist:
- The input boundary is an explicit allowlist; sensitive fields
  are not bindable from request data
- Adding a new sensitive field to the persistent model does
  NOT automatically expose it; the developer must consciously
  add it to the input model
- The pattern composes with framework conventions; the
  allowlist is at the same layer the framework binds at, so
  no manual stripping is required at every call site
- Static analysis fires authorization.mass-assignment-allowlist on bind-all patterns
  (User(**request.json), .update(params.permit!), splat-assign
  of request body); these patterns avoid all of them
