---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: authorization.protected-route-declares-authz
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Deciding which routes are protected versus intentionally public is an
  application-policy judgment, and confirming that every protected route declares
  a server-side authorization check is a coverage property across all routes. A
  static tool can assist where the framework and a public-marker convention are
  fixed, but the property as written is review-decidable.
review-triggers:
  - New route handler or change to route registration
  - A route's public-or-protected status changes
  - Changes to the authorization middleware, decorator, or attribute scheme
---

# Review checklist: protected routes declare server-side authorization

## Review questions

- Is every route that is not explicitly public covered by a declarative
  server-side authorization check (decorator, middleware, attribute, or
  controller metadata)?
- Is the public set explicit and intentional, so a new route does not default to
  unprotected by omission?
- Is the check declared in a way that new handlers inherit by default rather than
  requiring each author to remember it?

## Mechanical assist

Where the framework and a public-marker convention are fixed, a sast rule can
flag a route handler that declares neither an authorization check nor a public
marker. Treat a clean run as necessary, not sufficient.
