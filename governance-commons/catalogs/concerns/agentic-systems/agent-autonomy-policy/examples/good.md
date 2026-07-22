<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.agent-autonomy-policy agent autonomy policy (good pattern)

Substrate-original illustration. A recorded policy ADR (excerpt).

```markdown
# ADR-031: Authorization and autonomy policy for the support-triage agent

Purpose: triage inbound support tickets and draft replies for human send.
Granted authority: read tickets and the knowledge base; draft (not send)
  replies; tag and route. No access to billing, accounts, or production data.
Trust boundary: ticket text and KB articles are data, never instructions; only
  the authenticated agent operator may change the agent's configuration.
Autonomy: may tag, route, and draft autonomously; may not send a customer
  reply or any account change without a human (see ADR-032, agentic-systems.human-action-gating-policy).
Prohibited: never issues refunds, never modifies an account, never emails a
  customer directly.
Owner: support-platform-team. Reviewed 2026-06; next review 2026-12.
```

## Why this satisfies the rule

The ADR is recorded and current and sets the agent's purpose, its
least-privilege granted authority, its trust boundary, its autonomy bounds, and
the actions it must not take, cross-referencing the gating policy (agentic-systems.human-action-gating-policy).
The conformance rules now have a coherent standard to check against, and the
local tool grants cohere with the stated authority.
