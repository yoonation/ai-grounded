<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.no-credentials-in-urls credentials in URLs (good patterns)

Substrate-original examples demonstrating correct credential
transmission for authentication.no-credentials-in-urls. Per the E1 examples strategy, all
code is substrate-original.

## Pattern A: Bearer token in Authorization header (Python)

```python
import requests

# Token is passed via the Authorization header, never in the URL.
response = requests.get(
    "https://api.example.com/users/me",
    headers={"Authorization": f"Bearer {access_token}"},
)
```

Why this satisfies authentication.no-credentials-in-urls:
- Credential is in a header, not in the URL
- Header values are not logged by default in web server access logs
- Header values do not appear in browser history
- Header values are not sent in Referer headers to third parties

## Pattern B: API key in dedicated header (JavaScript / Node.js)

```javascript
const response = await fetch("https://api.example.com/data", {
  method: "GET",
  headers: {
    "X-API-Key": apiKey,
    "Accept": "application/json",
  },
});
```

Why this satisfies authentication.no-credentials-in-urls:
- API key is in a custom header
- Same protections as Pattern A

## Pattern C: Credentials in POST body for login (Python)

```python
import requests

# Login credentials are submitted in the POST body, not the URL.
response = requests.post(
    "https://api.example.com/login",
    json={"username": username, "password": password},
)
```

Why this satisfies authentication.no-credentials-in-urls:
- Credentials in request body, not URL
- POST bodies are not logged by default
- POST bodies are not stored in browser history

## Pattern D: HttpOnly Secure session cookie (Express / Node.js)

```javascript
// Server sets a session cookie that the browser attaches
// automatically on subsequent requests. The cookie value
// (the session token) never appears in URLs.
res.cookie("session_id", sessionToken, {
  httpOnly: true,
  secure: true,
  sameSite: "lax",
  maxAge: 3600 * 1000,
});
```

Why this satisfies authentication.no-credentials-in-urls:
- Session token is in a cookie, not in URLs
- httpOnly prevents JavaScript access (defense in depth for XSS)
- secure ensures cookie only sent over HTTPS
- sameSite limits CSRF risk

## Pattern E: OAuth 2.0 authorization code flow with PKCE (Python)

```python
# Step 1: Application redirects user to authorization server.
# The redirect URI itself does not carry credentials, only the
# state and code_challenge for PKCE.
authorization_url = (
    "https://auth.example.com/oauth/authorize"
    f"?response_type=code"
    f"&client_id={client_id}"
    f"&redirect_uri={redirect_uri}"
    f"&state={state}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)

# Step 2: Authorization server redirects back with a short-lived
# authorization code (NOT a token). The code in the URL is
# protocol-defined and acceptable; it is single-use and
# short-lived (typically 60 seconds).

# Step 3: Application exchanges code for access token via POST
# to the token endpoint. The access token is returned in the
# response body, NEVER in the URL.
response = requests.post(
    "https://auth.example.com/oauth/token",
    data={
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    },
)
access_token = response.json()["access_token"]
```

Why this satisfies authentication.no-credentials-in-urls:
- Authorization code in URL is protocol-defined exception
- Access token never appears in URL (returned in POST response body)
- PKCE protects the code-to-token exchange even if the code leaks

## What good patterns have in common

- Credentials live in headers, request bodies, or cookies
- The URL itself is safe to log, share, and store in browser history
- Defense in depth: TLS protects the channel; secure attributes on
  cookies prevent additional leakage

## Cross-reference

- Substrate rule: authentication.no-credentials-in-urls in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Anti-patterns: examples/authentication/credentials-in-urls-anti-pattern.md
