<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.fitness-evaluation fitness evaluation (good pattern)

Substrate-original illustration.

```python
# Deployment is gated on an evaluation that reports disaggregated performance.
report = evaluate(model, eval_set, subgroups=["region", "age_band"])
assert report.aggregate.auc >= 0.90
for group, metrics in report.by_subgroup.items():
    assert metrics.fpr_gap <= 0.05, f"subgroup {group} exceeds fairness gap"
deploy_if_passing(model, report)  # gate, not a post-hoc report
```

## Why this satisfies the rule

The model is evaluated against acceptance criteria tied to its use, performance
is reported disaggregated across the relevant subgroups (measured against the
responsible-ai.fairness-objective fairness objective), and deployment is gated on meeting the
thresholds. Subgroup failure cannot hide behind a passing aggregate.
