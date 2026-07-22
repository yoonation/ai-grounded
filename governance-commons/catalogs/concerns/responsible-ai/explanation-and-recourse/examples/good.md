<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.explanation-and-recourse explanation and recourse (good pattern)

Substrate-original illustration.

```json
{
  "decision": "application_declined",
  "ai_generated": true,
  "principal_factors": [
    "debt-to-income ratio above threshold",
    "insufficient credit history length"
  ],
  "human_review": {
    "available": true,
    "route": "/appeals",
    "sla_days": 5
  }
}
```

## Why this satisfies the rule

The significant automated decision discloses that it was automated, names the
principal factors that drove it in terms the person can act on, and offers a
reachable human-review route with a service level. The oversight mode behind the
review is the responsible-ai.human-oversight decision; this rule confirms the decision is explained
and contestable.
