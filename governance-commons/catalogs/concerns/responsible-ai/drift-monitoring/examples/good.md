<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.drift-monitoring drift monitoring (good pattern)

Substrate-original illustration. A recorded drift strategy (excerpt).

```markdown
# ADR-019: Model-drift monitoring and response for the fraud-scorer

Monitored signals:
  - input feature drift (population stability index per feature)
  - output score distribution shift
  - per-region false-negative rate against confirmed-fraud labels (responsible-ai.fairness-objective)
Thresholds:
  - PSI > 0.2 on any top-10 feature -> alert
  - FNR per region degrades > 0.03 vs baseline -> retrain trigger
Responses: alert to risk-platform on-call; retrain trigger opens a retraining
  task; severe degradation rolls back to the prior version (responsible-ai.model-provenance).
Cadence: full re-evaluation quarterly absent a triggered signal.
Telemetry via the observability concern; alerts via monitoring-alerting.
```

## Why this satisfies the rule

The strategy names the monitored signals (including the fairness metric from
responsible-ai.fairness-objective), the thresholds that constitute meaningful drift, the response each
threshold triggers, and a re-evaluation cadence for slow drift below the
thresholds. Degradation becomes a managed event. The telemetry and alerting
mechanisms are cross-referenced to observability and monitoring-alerting.
