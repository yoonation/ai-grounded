<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.fairness-objective fairness objective (anti-pattern)

Substrate-original illustration.

```text
The model is "tested for bias" by checking overall accuracy is high. No fairness
criterion is named, no groups are defined, no disparity threshold is set, and no
trade-off among the incompatible fairness definitions is acknowledged.
```

## Why this violates the rule

No fairness objective is chosen, so the system's fairness is whatever the data
and training produced, measured against no agreed standard, and the responsible-ai.fitness-evaluation
disaggregated evaluation has no target. Leaving the objective unmade does not
avoid the choice; it defaults it. Naming the criterion, the groups, the metric
and threshold, and the mitigation, with the trade-off made explicit, is the fix.
