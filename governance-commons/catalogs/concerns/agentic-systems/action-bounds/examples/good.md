<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.action-bounds action bounds (good pattern)

Substrate-original illustration.

```python
# Destructive actions require confirmation; quantitative actions carry limits;
# execution is sandboxed with scoped credentials.
@agent.tool(scope=["files:delete"], requires_confirmation=True)
def delete_path(path: str): ...

@agent.tool(scope=["payments:send"], per_run_limit_usd=500)
def send_payment(to: str, amount_usd: float): ...
```

## Why this satisfies the rule

The irreversible delete requires confirmation, the payment carries a per-run
magnitude limit, and the agent runs with scoped credentials so the blast radius
is contained. The bounds are proportionate: routine reversible actions are not
burdened. The human gate on the most consequential class is agentic-systems.human-action-gating and the
definition of consequential is the agentic-systems.human-action-gating-policy policy, cross-referenced.
