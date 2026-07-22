---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: authorization.no-client-side-only-authz
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  The violation is the absence of a server-side authorization check behind a
  privileged action, with the client merely hiding UI. Detecting a missing
  server-side enforcement point is not something a static tool can reliably do; it
  is review-decidable.
review-triggers:
  - New privileged action (state mutation, sensitive read, role change, admin op)
  - New client affordance that gates an action by role in the UI
  - Changes to where authorization is enforced
---

# Review checklist: authorization is enforced server-side

## Review questions

- For each privileged action, is authorization enforced on the server, with the
  client UI gating treated only as convenience?
- Would the action be refused if invoked directly against the API, bypassing the
  client entirely?
- Are administrative and role-changing operations protected by a server-side
  check that does not depend on any client-supplied claim of role?
- Are sensitive-data reads authorized server-side rather than filtered in the
  client?
