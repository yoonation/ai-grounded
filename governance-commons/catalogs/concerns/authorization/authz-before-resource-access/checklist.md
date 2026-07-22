---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: authorization.authz-before-resource-access
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Confirming that every code path operating on a client-identified resource
  performs an authorization decision on that specific object before access is the
  classic broken-object-level-authorization (IDOR) property. It requires data-flow
  and authorization-semantic understanding a static tool cannot supply, so it is
  review-decidable.
review-triggers:
  - New or changed endpoint that reads or mutates a resource by client-supplied id
  - New resource type exposed through an identifier
  - Changes to the authorization decision point or ownership model
---

# Review checklist: authorization precedes resource access

## Review questions

- For each path that takes a client-supplied resource identifier, is an
  authorization decision made on that specific resource before it is read,
  returned, or mutated?
- Is the check on the object instance (does this principal own or have rights to
  this id), not merely on the principal's role or on route reachability?
- Are list and bulk endpoints scoped so a principal sees only resources it is
  entitled to, rather than filtering client-side?
- Do nested or related-resource accesses re-check authorization rather than
  inheriting it from the parent route?
