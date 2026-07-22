<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.human-action-gating human action gating (good pattern)

Substrate-original illustration.

```python
# A gate-warranting action halts for explicit human approval, with context, on
# every path including delegation.
def execute(action, ctx):
    if gating_policy.is_gated(action):
        approval = request_approval(
            action=action.summary, target=action.target, rationale=action.why,
        )
        if not approval.granted:
            return Halted(action)
    return perform(action)   # same gate applies to sub-agent-initiated actions
```

## Why this satisfies the rule

An action the agentic-systems.human-action-gating-policy policy classifies as gate-warranting halts and
requires explicit approval before it takes effect, the approver is shown the
action, target, and rationale so the decision is meaningful, and the gate is
applied centrally so a delegated sub-agent cannot route around it
(cross-referencing agentic-systems.delegation-authority). The system-level oversight model is
responsible-ai's responsible-ai.human-oversight.
