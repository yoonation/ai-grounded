<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.tool-use-authorization tool-use authorization (good pattern)

Substrate-original illustration.

```python
# The dispatch path checks each call against the agent's least-privilege grant
# and against the acting user's permissions.
def dispatch(tool, args, ctx):
    if tool.scope not in ctx.agent_grant:
        raise Denied(f"{tool.name} outside agent grant")
    if not ctx.acting_user.may(tool.scope, args):
        raise Denied("exceeds acting user's permissions")
    return tool.invoke(args)
```

## Why this satisfies the rule

Tool calls are authorized at call time against the authority the agent was
granted, the grant is least-privilege for the agent's purpose, and an
on-behalf-of-user call cannot exceed the user's own permissions. The declared
scope (agentic-systems.tool-authorization-scope) is enforced on the call path rather than merely documented.
The user permission model is owned by authorization and cross-referenced here.
