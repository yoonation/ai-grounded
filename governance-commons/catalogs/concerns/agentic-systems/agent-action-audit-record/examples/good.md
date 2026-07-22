<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.agent-action-audit-record agent action audit record (good pattern)

Substrate-original illustration.

```python
# A shared dispatch wrapper attaches an audit record on every tool call.
def dispatch(tool, args, ctx):
    record = {
        "agent": ctx.agent_id,
        "tool": tool.name,
        "args_hash": sha256(args),
        "caller": ctx.caller_identity,
        "ts": now_iso(),
    }
    audit.write(record)          # audit record on the action path
    return tool.invoke(args)
```

## Why this satisfies the rule

The action path attaches a structured audit record on a shared dispatch wrapper,
so what the agent did can be reconstructed and the delegation, gating, and trust
rules have evidence to rest on. Putting the record on the wrapper means it cannot
be forgotten per tool. Whether the record is sufficient, and how it is retained
and redacted, are owned by the logging concern; this rule asserts a record is
attached.
