<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.alerting-strategy alerting strategy (anti-pattern)

Substrate-original illustration.

```text
(no alerting-strategy ADR exists)

Each engineer adds alerts ad hoc:
  - one team pages on every cause-level signal; another pages on nothing
  - severity labels are inconsistent, so routing is unpredictable
  - no escalation model; no documented rotation; silences never expire
  - the pipeline has no heartbeat; incidents never feed back into the rules
```

## Why this violates the rule

With no strategy, coverage, routing, escalation, and lifecycle are decided per
alert and do not cohere: alerts that individually pass hygiene collectively page
the wrong people at the wrong severity with no backstop and no lifecycle. The
on-call experience degrades until engineers tune alerts out. monitoring-alerting.alerting-strategy requires
the strategy be decided and written down precisely to prevent this pile.
