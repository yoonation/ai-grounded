<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.no-placeholder-documentation no placeholder documentation (good patterns)

Substrate-original good-pattern examples for documentation.no-placeholder-documentation. Shipped
documentation contains real content, or an explicit, visible known-gap
notice rather than a silent stub.

## A reference page with real content

```markdown
## Authentication

Requests authenticate with a bearer token in the Authorization header.
Tokens are issued by the /auth/token endpoint and expire after one hour.
A 401 is returned when the token is missing, expired, or malformed.
```

## An explicit, visible known-gap notice (allowed by configuration)

```markdown
## Rate limiting

> Known gap: rate-limit headers are not yet documented. Tracked in DOC-142.
> This notice is intentional and visible to readers, not a hidden stub.
```

What ships is either real content or a gap the reader can see, never a
placeholder masquerading as complete.
