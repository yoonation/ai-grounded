<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.delegation-authority delegation authority (good pattern)

Substrate-original illustration.

```python
# Delegation narrows authority and propagates caller identity.
def delegate(caller_ctx, subtask, needed_scope):
    if needed_scope not in caller_ctx.grant:
        raise Denied("cannot delegate authority the caller lacks")
    sub_ctx = Context(
        agent_grant=caller_ctx.grant & needed_scope,   # subset, never wider
        caller_identity=caller_ctx.identity,            # attribution propagates
        delegation_of=caller_ctx.request_id,
    )
    return run_sub_agent(subtask, sub_ctx)
```

## Why this satisfies the rule

The delegated authority is the intersection of the caller's grant and the
subtask's need, never an expansion, and the caller's identity and the delegation
context propagate so the sub-agent's action stays attributable in the audit
record. Because the grant only narrows, the caller's bounds and gate are
preserved across the boundary. The trust topology framing this is agentic-systems.multi-agent-trust.
