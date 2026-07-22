---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: agentic-systems.agent-action-audit-record
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Confirming that every agent action and tool-invocation path attaches an audit record is a coverage property across all dispatch paths that a static tool cannot fully resolve; it is review-decidable.
review-triggers:
  - New or changed agent action-dispatch or tool-invocation path
---

# Review checklist: agent actions are auditable

## Review questions

- Does every action-dispatch and tool-invocation path attach an audit record capturing the action taken, its inputs, and its outcome?
- Can the agent's behavior over a session be reconstructed from the audit records alone?
- Are failures and refusals recorded, not only successful actions?
