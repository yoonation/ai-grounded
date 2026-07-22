<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.session-regeneration session fixation (forbidden patterns)

## Anti-pattern A: Session ID preserved across authentication

```python
# FORBIDDEN: the session ID from pre-auth is kept after auth.
# Attacker who sets the victim's pre-auth session ID retains
# the authenticated session.
def login_BAD(request):
    user = authenticate(request.POST["username"], request.POST["password"])
    if user is None:
        return render_generic_auth_failure()

    # Just set user data on the existing session. No rotation.
    request.session["user_id"] = user.id
    return redirect("/dashboard")
```

Why this violates authentication.session-regeneration:
- The pre-auth session ID continues to authenticate after login
- A fixation attack succeeds: attacker pre-sets victim's session
  ID, victim authenticates, attacker has the authenticated session

## Anti-pattern B: Login completion that creates new session without invalidating old

```javascript
// FORBIDDEN: a new session is created but the old one is not
// invalidated. The pre-auth session ID continues to map to
// some state in the session store.
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body.username, req.body.password);
  if (!user) return renderGenericAuthFailure(res);

  // Create a new session ID but leave the old session record
  // alive in the store.
  req.session = {userId: user.id};  // ← creates new mapping
  res.cookie("sid", generateNewSessionId());  // ← new cookie

  // The old session ID is still in the session store with its
  // pre-auth state. If the attacker had it, they can probe.
  return res.redirect("/dashboard");
});
```

Why this violates authentication.session-regeneration:
- Old session record remains in the store
- Depending on the application's session lookup, the old ID may
  still be partially valid
- Proper rotation invalidates the old record

## Anti-pattern C: MFA completion does not rotate

```python
# FORBIDDEN: primary login rotates the session ID (good) but
# MFA completion does not. Step-up authentication does not
# defeat fixation that targets the MFA-completed state.
def login_BAD(request):
    user = authenticate(request.POST["username"], request.POST["password"])
    if user is None:
        return render_generic_auth_failure()

    login(request, user)  # rotates session - good
    return redirect("/mfa-challenge")


def mfa_complete_BAD(request):
    if not verify_totp(request.user.totp_secret, request.POST["code"]):
        return render_generic_auth_failure()

    request.session["mfa_completed_at"] = timezone.now().isoformat()
    # No cycle_key() call. Session ID remains the same.
    return redirect("/dashboard")
```

Why this violates authentication.session-regeneration:
- MFA completion is a privilege boundary; the session ID should
  rotate
- Without rotation, fixation targeting the post-MFA state can
  succeed if the attacker held the post-login session ID

## Anti-pattern D: Cookie attributes weak on the new session

```javascript
// FORBIDDEN: session is regenerated (good) but the new cookie
// is set without security attributes (bad).
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body.username, req.body.password);
  if (!user) return renderGenericAuthFailure(res);

  req.session.regenerate((err) => {
    if (err) return res.status(500).end();
    req.session.userId = user.id;

    // FORBIDDEN: cookie set without httpOnly, Secure, SameSite.
    res.cookie("sid", req.sessionID, {});
    res.redirect("/dashboard");
  });
});
```

Why this violates authentication.session-regeneration:
- The rotation is correct but the new cookie is vulnerable to
  XSS theft (no httpOnly) and to network observation (no Secure)
- Proper rotation includes setting the cookie with security
  attributes

## Anti-pattern E: JWT login that issues new token without revoking old

```python
# FORBIDDEN: new JWT issued at authentication, but old JWT
# is never revoked. A leaked old JWT (e.g., captured in an
# old log) continues to authenticate.
def login_jwt_BAD(username, password):
    user = authenticate(username, password)
    if user is None:
        return render_generic_auth_failure()

    # New token issued; old one (if any) never invalidated.
    payload = {
        "sub": str(user.id),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()),
    }
    return jwt.encode(payload, signing_key, algorithm="HS256")
```

Why this violates authentication.session-regeneration:
- Old JWTs remain valid until natural expiration
- Token-rotation as a defense requires revocation, not just
  issuance
- Replay of any old JWT still authenticates

## Cross-reference

- Substrate rule: authentication.session-regeneration in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Good examples: examples/authentication/session-fixation-good.md
