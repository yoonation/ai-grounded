<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.no-credentials-in-urls credentials in URLs (forbidden patterns)

Substrate-original anti-patterns for authentication.no-credentials-in-urls. Do not copy
into production.

## Anti-pattern A: Password in query string (Python)

```python
import requests

# FORBIDDEN: password as URL parameter. Logged in access logs,
# stored in browser history, leaked to third parties via Referer.
response = requests.get(
    f"https://api.example.com/login?username={user}&password={pwd}"
)

# FORBIDDEN: same pattern with params dict; requests serializes
# them into the URL query string identically.
response = requests.get(
    "https://api.example.com/login",
    params={"username": user, "password": pwd},
)
```

Why this violates authentication.no-credentials-in-urls:
- Password is in URL query string
- Web server access logs capture full URLs by default
- Browser history persists URL
- Referer header sent to next-page resources leaks credential

## Anti-pattern B: API key in query parameter (JavaScript)

```javascript
// FORBIDDEN: API key in query parameter. Same disclosure
// pathways as Anti-pattern A.
const response = await fetch(
  `https://api.example.com/data?api_key=${apiKey}`
);

// FORBIDDEN: same anti-pattern with URLSearchParams.
const params = new URLSearchParams({api_key: apiKey, format: "json"});
const response = await fetch(`https://api.example.com/data?${params}`);
```

Why this violates authentication.no-credentials-in-urls:
- API key in URL has the same leak pathways as password
- "API key" is not less sensitive than "password" for authentication.no-credentials-in-urls

## Anti-pattern C: OAuth implicit flow (token in URL fragment)

```javascript
// FORBIDDEN: OAuth 2.0 implicit grant flow places the access
// token in the URL fragment of the redirect URI. Deprecated
// by OAuth 2.1 for security reasons.
window.location = (
  "https://auth.example.com/oauth/authorize" +
  "?response_type=token" +  // ← implicit grant
  "&client_id=" + clientId +
  "&redirect_uri=" + redirectUri
);

// After authorization, browser receives:
// https://app.example.com/callback#access_token=ya29.xxx&token_type=Bearer
// The token in the fragment is logged by browser extensions,
// captured in browser history, and exposed to any JavaScript
// running on the callback page.
```

Why this violates authentication.no-credentials-in-urls:
- Token in URL fragment is still a token in a URL
- Browser history captures full URL including fragment
- Browser extensions can read fragments
- Migrate to authorization code flow with PKCE

## Anti-pattern D: Token in URL path (Python)

```python
import requests

# FORBIDDEN: session token embedded in URL path.
response = requests.get(
    f"https://api.example.com/users/me/{session_token}"
)

# FORBIDDEN: password reset token in URL path (as a path segment).
# Note: a TOKEN ID is acceptable in a path when it identifies a
# resource but cannot itself authenticate. A token that
# authenticates by its mere presentation must not appear in URLs.
reset_url = f"https://app.example.com/reset/{reset_token}"
```

Why this violates authentication.no-credentials-in-urls:
- URL path is logged by web servers same as query strings
- Password reset tokens are bearer credentials; the holder
  authenticates

Note on password reset emails: the standard pattern is to email
the user a URL containing the reset token. This is a known
exception driven by usability (the user clicks the link); the
substrate-recommended mitigations are short token expiration
(15-60 minutes), single-use enforcement, and POST-only
verification at the receiving endpoint.

## Anti-pattern E: Hardcoded credentials in URL string literal

```python
# FORBIDDEN: credentials in URL string literal in source code.
# Combines violation of authentication.no-credentials-in-urls (credentials in URL) and
# authentication.no-hardcoded-credentials (credentials hardcoded in source).
url = "https://admin:supersecret@internal.example.com/api"
```

Why this violates authentication.no-credentials-in-urls:
- Credentials are in URL
- HTTP basic-auth-in-URL form is a known anti-pattern (RFC
  3986 still permits the syntax but warns against use)

## What anti-patterns have in common

- Credential material in some part of the URL: query string,
  path, fragment, or userinfo segment
- Leak to one or more of: access logs, browser history,
  Referer headers, browser extensions, observability tooling

## Cross-reference

- Substrate rule: authentication.no-credentials-in-urls in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Good examples: examples/authentication/credentials-in-urls-good.md
