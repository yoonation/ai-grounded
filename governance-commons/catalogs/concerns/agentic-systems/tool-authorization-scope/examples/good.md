<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.tool-authorization-scope tool authorization scope (good pattern)

Substrate-original illustration.

```python
# Every tool registered to the agent declares a scope the call-time check
# can enforce.
@agent.tool(scope=["crm:contacts:read"])
def lookup_contact(contact_id: str) -> Contact:
    return crm.get(contact_id)

@agent.tool(scope=[])  # explicit empty scope: a genuinely unprivileged tool
def current_time() -> str:
    return now_iso()
```

## Why this satisfies the rule

Each tool registration declares an authorization scope, so the call-time
authorization rule (agentic-systems.tool-use-authorization) has a stated boundary to enforce against. The
unprivileged tool declares an explicit empty scope rather than omitting the
declaration, so its lack of authority is a decision rather than an oversight.
Whether `crm:contacts:read` is genuinely least-privilege is the agentic-systems.tool-use-authorization
judgment; this rule asserts a scope was declared.
