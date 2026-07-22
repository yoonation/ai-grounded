<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.human-action-gating-policy human-action-gating policy (good pattern)

Substrate-original illustration. A recorded policy ADR (excerpt).

```markdown
# ADR-032: Human-action-gating policy for the support-triage agent

Consequential = irreversible, externally visible, or affecting a customer's
  money or account.
Gated (human approval before effect): sending any customer-facing message;
  any account or billing change; any refund.
Bounded-autonomous (within agentic-systems.action-bounds limits): tagging, routing, internal
  note-taking, drafting (not sending).
Approval path: routed to the on-shift support lead; 30-minute SLA; on timeout
  the action is held, not auto-approved.
```

## Why this satisfies the rule

The ADR defines what counts as consequential for this agent, names the gated set
(the actions where a human must decide before effect) and the
bounded-autonomous set, and sets a concrete approval path with a safe timeout
behavior. The gate implementation (agentic-systems.human-action-gating) fires on exactly this set, and
the policy specializes responsible-ai's responsible-ai.human-oversight oversight model for actions.
