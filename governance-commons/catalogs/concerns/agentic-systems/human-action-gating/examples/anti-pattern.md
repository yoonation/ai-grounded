<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.human-action-gating human action gating (anti-pattern)

Substrate-original illustration.

```python
# The high-impact action executes autonomously; a sibling path has no gate.
def execute(action, ctx):
    return perform(action)   # no gate on any consequential action

def sub_agent_execute(action, ctx):
    return perform(action)   # and delegation bypasses even an intended gate
```

## Why this violates the rule

Gate-warranting actions execute autonomously with no human approval, and even
where a gate exists on one path a delegated sub-agent reaches the action
ungated, so the last line that should keep an autonomous loop from committing an
irreversible high-impact act is absent or bypassable. Halting gate-warranting
actions for a meaningful, non-bypassable approval is the fix.
