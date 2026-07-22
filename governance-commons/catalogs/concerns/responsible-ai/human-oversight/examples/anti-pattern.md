<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.human-oversight human oversight (anti-pattern)

Substrate-original illustration.

```text
Every decision the model makes is applied automatically. There is no chosen
oversight model; the high-impact decline path is fully automated by default,
and the "review" team can see decisions but has no authority or time to overturn
them.
```

## Why this violates the rule

No oversight model was chosen, so the question defaulted to full automation
exactly where the high-impact, person-affecting decision most needed a human, and
the nominal reviewers are a rubber stamp with no authority. An oversight mode
matched per decision class to risk and genuinely implemented with an empowered
reviewer is the fix; the per-action agent gate is owned by agentic-systems.
