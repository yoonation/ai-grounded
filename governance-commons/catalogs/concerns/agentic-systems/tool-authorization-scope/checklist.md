---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: agentic-systems.tool-authorization-scope
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether every tool or skill registered to an agent declares an authorization scope depends on the agent framework's registration shape and is a coverage property a static tool cannot universally resolve; it is review-decidable.
review-triggers:
  - A tool or skill is registered to an agent, or its permissions change
---

# Review checklist: registered tools declare an authorization scope

## Review questions

- Does every registered tool or skill declare an authorization scope: the actions or resources it may touch?
- Is the scope least-privilege for the tool's purpose rather than broad by default?
- Is the scope enforced at invocation, not merely documented?
