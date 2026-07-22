<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.human-oversight human oversight (good pattern)

Substrate-original illustration. A recorded oversight decision (excerpt).

```markdown
# ADR-020: Human-oversight model for the fraud-scorer

Per decision class:
  - decline (high impact, reversible): human in the loop; an adjudicator
    approves before the decline takes effect, with the factors and case context.
  - route-to-review (medium impact): human on the loop; the system routes
    autonomously and a queue lead can intervene.
  - allow (low impact, reversible): human in command; bounds set, sampled review
    after the fact.
Implementation: adjudicators have the case context, a target SLA, and authority
  to overturn; overturns feed the responsible-ai.decision-record-keeping record and the responsible-ai.drift-monitoring signals.
```

## Why this satisfies the rule

The oversight mode is matched per decision class to risk, from human-in-the-loop
approval for the high-impact decline to human-in-command sampled review for the
low-impact allow, and the chosen mode is genuinely implemented with an empowered
adjudicator. The per-action gate on an autonomous agent is owned by
agentic-systems; this decision governs the AI system's decisions.
