<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.explanation-and-recourse explanation and recourse (anti-pattern)

Substrate-original illustration.

```json
{
  "decision": "application_declined",
  "score": 0.31
}
```

## Why this violates the rule

The consequential automated decision is delivered as a bare score with no
interpretable explanation, no disclosure that it was automated, and no route to
human review. The person cannot understand why or challenge it, so the decision
has placed itself beyond accountability. A meaningful explanation of the
principal factors plus a reachable contestation route is the fix.
