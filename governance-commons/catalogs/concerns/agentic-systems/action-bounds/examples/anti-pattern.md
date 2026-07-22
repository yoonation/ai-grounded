<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.action-bounds action bounds (anti-pattern)

Substrate-original illustration.

```python
# Destructive and quantitative actions with no bound, run at loop speed.
@agent.tool(scope=["files:delete"])
def delete_path(path: str): ...        # no confirmation

@agent.tool(scope=["payments:send"])
def send_payment(to: str, amount_usd: float): ...   # no limit
```

## Why this violates the rule

The delete fires in one autonomous step with no confirmation and the payment has
no magnitude limit, so a single wrong or subverted decision can delete data or
drain funds at machine speed before anyone notices. Unbounded consequential
actions are the runaway-agent failure. Requiring confirmation for irreversible
actions and limits for quantitative ones, in a sandbox, is the fix.
