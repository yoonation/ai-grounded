<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.fairness-objective fairness objective (good pattern)

Substrate-original illustration. A recorded fairness decision (excerpt).

```markdown
# ADR-018: Fairness objective for the fraud-scorer

Criterion: equal opportunity (equal false-negative rate across regions),
  because a missed fraud flag that lets a legitimate-looking fraud through, and
  the inverse review burden, should not fall unequally by region.
Trade-off accepted: demographic parity is not targeted; review volume may differ
  by region where fraud base rates differ.
Groups: region; revisited if a new protected dimension becomes relevant.
Metric and threshold: FPR gap <= 0.05 between any region and the best region.
Mitigation: post-processing threshold adjustment per region; residual gap
  recorded if the threshold cannot be met without unacceptable accuracy loss.
```

## Why this satisfies the rule

The decision names the fairness criterion and why it fits the use, makes the
trade-off against the incompatible criteria explicit, names the groups, sets a
metric and acceptable disparity, and states the mitigation. The responsible-ai.fitness-evaluation
evaluation measures against this objective; fairness is an explicit, measurable,
contestable commitment rather than an accident of the data.
