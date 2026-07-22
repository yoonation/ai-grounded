<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.delegation-authority delegation authority (anti-pattern)

Substrate-original illustration.

```python
# The sub-agent is spun up with its own broad standing authority.
def delegate(caller_ctx, subtask):
    sub_ctx = Context(agent_grant=ALL_SCOPES, credentials=service_admin_token)
    return run_sub_agent(subtask, sub_ctx)   # no narrowing, no attribution
```

## Why this violates the rule

The sub-agent runs with broad standing authority unrelated to the caller's, so a
delegation amplifies authority rather than narrowing it, and with no caller
identity propagated the resulting action cannot be traced to who authorized it.
This is the multi-agent privilege-amplification and lost-accountability failure.
Constraining delegated authority to a subset of the caller's and carrying
identity is the fix.
