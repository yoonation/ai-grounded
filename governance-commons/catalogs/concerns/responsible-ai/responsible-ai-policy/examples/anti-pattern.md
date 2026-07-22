<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.responsible-ai-policy responsible-AI policy (anti-pattern)

Substrate-original illustration.

```text
No responsible-AI policy exists. Each feature team decides on its own whether to
document a model, what to evaluate, and how much human review to require. There
is no stated intended use, no risk classification, and no record of the fairness
or oversight commitments.
```

## Why this violates the rule

With no recorded policy, the responsible-AI posture is a pile of locally
reasonable choices that do not cohere: a model documented but with no stated
prohibited use, evaluated against no agreed criteria, deployed at an oversight
level nobody chose for its risk. The conformance rules have no standard to check
against. A recorded policy ADR covering the sub-decisions, current and owned, is
the fix.
