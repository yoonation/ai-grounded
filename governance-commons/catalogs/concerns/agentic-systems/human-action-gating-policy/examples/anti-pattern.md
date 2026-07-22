<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.human-action-gating-policy human-action-gating policy (anti-pattern)

Substrate-original illustration.

```text
There is no policy on which agent actions are consequential. A human gate was
implemented on one path because a developer happened to add it, while sending
customer emails and issuing refunds run autonomously. No one decided which
actions warrant a human.
```

## Why this violates the rule

With no gating policy, the gate is pointed arbitrarily: it sits in front of an
action that happened to get one while genuinely consequential actions (customer
emails, refunds) run autonomously, so the gate implementation protects the wrong
things. Defining consequential for this agent and recording the gated and
bounded-autonomous sets is the fix; the gate (agentic-systems.human-action-gating) then fires on the
right set.
