<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.multi-agent-trust multi-agent trust (anti-pattern)

Substrate-original illustration.

```text
A swarm of agents can each spawn and delegate to any other agent freely. There
is no recorded model of who may delegate to whom, no narrowing rule, and no
record of which agent authorized an action. A sub-agent can be spun up with
broader authority than the one that created it.
```

## Why this violates the rule

With no recorded trust model, authority accumulates across free delegation
chains, a sub-agent can be trusted as if it were the user, and an action cannot
be traced to the agent that authorized it, the multi-agent amplification and
lost-accountability failures. Mapping roles and a delegation topology, encoding
the narrowing rule, propagating identity, and planning containment is the fix; a
single-agent system instead records non-applicability.
