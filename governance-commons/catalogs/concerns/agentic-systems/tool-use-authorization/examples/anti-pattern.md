<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.tool-use-authorization tool-use authorization (anti-pattern)

Substrate-original illustration.

```python
# The agent holds standing broad authority and calls are never checked.
agent = Agent(tools=ALL_TOOLS, credentials=admin_token)

def dispatch(tool, args, ctx):
    return tool.invoke(args)   # no call-time check against any grant or user
```

## Why this violates the rule

The agent holds standing admin authority over every tool and its calls are never
checked at call time, so a wrong or subverted agent acts with full authority in
real systems, the excessive-agency failure. A declared scope would be inert here
because nothing enforces it on the call path. Checking each call against a
least-privilege grant and the acting user's permissions is the fix.
