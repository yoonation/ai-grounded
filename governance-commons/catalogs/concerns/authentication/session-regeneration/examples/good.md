<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.session-regeneration session fixation (good patterns)

## Pattern A: Django session cycle (Python / Django)

```python
from django.contrib.auth import authenticate, login

def login_view(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(username=username, password=password)
    if user is None:
        return render_generic_auth_failure()

    # Django's login() function calls cycle_key() internally
    # to rotate the session identifier on authentication. The
    # pre-auth session ID is replaced; subsequent requests use
    # the new ID.
    login(request, user)
    return redirect("/dashboard")


def mfa_complete_view(request):
    if not verify_totp(request.user.totp_secret, request.POST.get("code")):
        return render_generic_auth_failure()

    # Explicitly cycle on MFA completion (separate event from
    # primary login).
    request.session.cycle_key()
    request.session["mfa_completed_at"] = timezone.now().isoformat()
    return redirect("/dashboard")
```

Why this satisfies authentication.session-regeneration:
- Django's login() rotates the session key
- MFA completion explicitly rotates again
- Both are framework-supported primitives

## Pattern B: Express session regenerate (Node.js)

```javascript
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body.username, req.body.password);
  if (!user) return renderGenericAuthFailure(res);

  // Regenerate session ID on authentication. The callback runs
  // with the new session; req.session is the new session.
  req.session.regenerate((err) => {
    if (err) return res.status(500).end();
    req.session.userId = user.id;
    req.session.save(() => res.redirect("/dashboard"));
  });
});


app.post("/mfa/complete", async (req, res) => {
  const ok = await verifyTOTP(req.user.totpSecret, req.body.code);
  if (!ok) return renderGenericAuthFailure(res);

  req.session.regenerate((err) => {
    if (err) return res.status(500).end();
    req.session.userId = req.user.id;
    req.session.mfaCompletedAt = Date.now();
    req.session.save(() => res.redirect("/dashboard"));
  });
});
```

Why this satisfies authentication.session-regeneration:
- regenerate() called at authentication and MFA completion
- Session data copied to new session within callback
- Save before responding so the new cookie is set on response

## Pattern C: Spring Security session fixation strategy (Java)

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .sessionManagement(session -> session
                // Spring Security's built-in fixation protection.
                // newSession creates a fresh session at authentication;
                // pre-auth session attributes are discarded.
                // migrateSession copies attributes to the new session
                // (alternative if pre-auth state matters).
                .sessionFixation().newSession()
                .maximumSessions(1)
            )
            .formLogin(form -> form.loginPage("/login"));
        return http.build();
    }
}
```

Why this satisfies authentication.session-regeneration:
- Spring Security applies fixation protection automatically
- newSession() drops all pre-auth state (defense in depth)
- maximumSessions(1) prevents same user holding multiple sessions

## Pattern D: JWT with token revocation list (Python)

```python
import jwt
import secrets
from datetime import datetime, timezone, timedelta

def login_jwt(username, password):
    user = authenticate(username, password)
    if user is None:
        return render_generic_auth_failure()

    # Revoke previous tokens for this user (if any) by adding
    # their jti values to the revocation list.
    revoke_existing_tokens(user.id)

    # Issue a new token with a fresh jti claim.
    jti = secrets.token_urlsafe(16)
    payload = {
        "sub": str(user.id),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()),
        "jti": jti,
    }
    return jwt.encode(payload, signing_key, algorithm="HS256")


def verify_jwt(token):
    try:
        payload = jwt.decode(token, signing_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

    # Reject revoked tokens.
    if is_revoked(payload["jti"]):
        return None
    return payload
```

Why this satisfies authentication.session-regeneration:
- New JWT issued at authentication (token rotation)
- Old JWT explicitly revoked via jti tracking
- Subsequent presentation of the old JWT is rejected

## What good patterns have in common

- Authentication completion calls the framework's session-rotate
  primitive (or equivalent token issuance + revocation for JWT)
- Rotation happens AFTER authentication validation and BEFORE
  the authenticated response
- All authentication paths (primary login, MFA, OAuth callback)
  apply rotation
- For cookie-based sessions, cookie attributes (httpOnly, Secure,
  SameSite) are set on the rotated cookie

## Cross-reference

- Substrate rule: authentication.session-regeneration in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Anti-patterns: examples/authentication/session-fixation-anti-pattern.md
