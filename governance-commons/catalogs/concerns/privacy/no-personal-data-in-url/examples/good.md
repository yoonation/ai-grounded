<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.no-personal-data-in-url no personal data in URL (good pattern)

Substrate-original illustration.

```python
# The personal identifier travels in the request body or a session-keyed
# lookup, and the route uses an opaque non-personal id.
@app.post("/account/profile")
def update_profile(payload: ProfileUpdate):  # email is in the body
    ...

@app.get("/account/{account_id}")            # opaque surrogate id in the path
def get_account(account_id: AccountId):
    ...
```

## Why this satisfies the rule

The personal value (the email) is carried in the request body, and the path uses
an opaque surrogate identifier rather than a personal one, so nothing personal
reaches the access logs, browser history, or the Referer header. This is the
URL-transport floor; the broader leakage surface is data-classification.no-classified-data-in-logs and logging.redaction,
which this rule cross-references.
