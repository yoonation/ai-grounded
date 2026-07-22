<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.agent-autonomy-policy agent autonomy policy (anti-pattern)

Substrate-original illustration.

```text
No authorization or autonomy policy exists for the agent. Tools were added one
at a time as features shipped, autonomy was widened whenever a human approval
felt like friction, and no one recorded the agent's purpose, its authority
bounds, or the actions it must never take.
```

## Why this violates the rule

With no recorded policy, the agent's authority and autonomy were set by default
and accretion, usually toward more capability and less constraint than anyone
deliberately chose, and the conformance rules (tool-use, bounds, gating,
delegation) have no standard to check against. A recorded ADR setting purpose,
granted authority, trust boundary, autonomy, and prohibited actions is the fix.
