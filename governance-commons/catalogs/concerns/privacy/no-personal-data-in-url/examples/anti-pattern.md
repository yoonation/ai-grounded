<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.no-personal-data-in-url no personal data in URL (anti-pattern)

Substrate-original illustration.

```python
# The personal email is placed directly in the URL path and a query string.
@app.get("/users/{email}/orders")             # email in the path
def orders_for(email: str):
    ...

resp = httpx.get(f"https://api/lookup?ssn={ssn}")  # national id in query string
```

## Why this violates the rule

The email is placed in a URL path segment and a government identifier in a query
string, so both are copied into server access logs, proxy and CDN logs, browser
history, and the Referer header sent to third parties. A single careless route
turns personal data into broadcast data. Moving the value into the request body
or a session-keyed lookup, or using an opaque identifier in the path, is the fix.
