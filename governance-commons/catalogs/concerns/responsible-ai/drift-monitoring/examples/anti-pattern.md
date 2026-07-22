<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.drift-monitoring drift monitoring (anti-pattern)

Substrate-original illustration.

```text
The model was evaluated once at launch and deployed. Nothing monitors it in
production: no input-drift signal, no output-distribution check, no performance
or fairness tracking, and no scheduled re-evaluation.
```

## Why this violates the rule

The model operates against a moving world with no monitoring, so the inevitable
drift is invisible until it surfaces as a failure, and a system that was fair and
fit at launch can degrade silently into one that is neither. A recorded strategy
naming the monitored signals, thresholds, triggered responses, and re-evaluation
cadence is the fix; telemetry and alerting are owned by observability and
monitoring-alerting.
