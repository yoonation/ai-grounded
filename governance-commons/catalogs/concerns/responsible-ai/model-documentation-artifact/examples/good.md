<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.model-documentation-artifact model documentation artifact (good pattern)

Substrate-original illustration.

```yaml
# model_card.yaml accompanies the deployed model in the registry.
model: fraud-scorer
version: "4.2.0"
owner: risk-platform-team
intended_use: >
  Scores card-not-present transactions for review routing. Advisory only;
  a human adjudicates declines.
known_limitations:
  - "Under-tested for merchant categories added after 2026-01."
  - "Not validated for transactions above 50k; routed to manual review."
evaluation_summary:
  dataset: eval-2026-q1-snapshot
  aggregate_auc: 0.94
  disaggregated: see eval-report/2026-q1 (per-region, per-merchant-tier)
```

## Why this satisfies the rule

The deployed model carries a machine-checkable documentation artifact with every
required field populated: intended use, known limitations, an evaluation
summary, an owner, and a version. The conformance rules (fitness evaluation,
oversight, record-keeping) now have something to anchor to. Whether the stated
limitations are complete is the responsible-ai.fitness-evaluation review; this rule asserts the
documentation exists.
