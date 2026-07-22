<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.tool-authorization-scope tool authorization scope (anti-pattern)

Substrate-original illustration.

```python
# A tool wired to the agent with no declared scope.
@agent.tool
def run_sql(query: str) -> list:
    return db.execute(query)   # inherits whatever authority the agent's db
                               # connection carries; no scope declared
```

## Why this violates the rule

The tool is registered with no authorization scope, so it inherits whatever
ambient authority the agent's database connection happens to carry, and the
call-time authorization rule has nothing to enforce against. A raw SQL tool with
no scope is the unbounded-authority case the concern most wants to prevent.
Declaring a scope on the registration, however coarse, is the fix.
