<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.agent-action-audit-record agent action audit record (anti-pattern)

Substrate-original illustration.

```python
# The agent calls tools directly with no audit record.
def dispatch(tool, args):
    return tool.invoke(args)   # nothing recorded about the action
```

## Why this violates the rule

The action path records nothing, so a tool call that deleted data or moved money
leaves no trail of who or what initiated it, and the agent cannot be investigated
when it misbehaves. An action path with no audit record is an unaccountable
agent. Attaching an audit record on the action path, preferably on a shared
dispatch wrapper, is the fix; the logging mechanism is owned by logging.
