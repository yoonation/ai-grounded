<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.responsible-ai-policy responsible-AI policy (good pattern)

Substrate-original illustration. A recorded policy ADR (excerpt).

```markdown
# ADR-017: Responsible-AI policy for the fraud-scorer

Intended use: advisory routing of card-not-present transactions.
Prohibited uses: automated decline without human adjudication; any use outside
  card-not-present fraud.
Risk class: high-impact (affects access to funds), reversible via appeal.
Fairness: equal-opportunity objective; see ADR-018 (responsible-ai.fairness-objective).
Transparency: AI disclosure on all customer-facing output; factor-level
  explanation on declines.
Human oversight: human-in-the-loop on declines; see ADR-020 (responsible-ai.human-oversight).
Evaluation: AUC >= 0.90 aggregate and FPR gap <= 0.05 per region before deploy.
Monitoring: input drift + per-region FPR; see ADR-019 (responsible-ai.drift-monitoring).
Incidents: model incidents route to risk-platform on-call; quarterly review.
Owner: risk-platform-team. Reviewed: 2026-05; next review 2026-11.
```

## Why this satisfies the rule

The policy is recorded, discoverable, and current, and it covers its
sub-decisions: intended and prohibited uses, a risk class that scales the other
commitments, and the fairness, transparency, oversight, evaluation, monitoring,
incident, and ownership commitments, cross-referencing the fairness, drift, and
oversight ADRs rather than restating them. The conformance rules now have a
coherent standard to check against.
