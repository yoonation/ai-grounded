<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.data-access-strategy data-access strategy (anti-pattern)

Substrate-original illustration. Performance decisions made ad hoc per
feature with no recorded strategy, producing choices that do not cohere.

```text
No ADR exists. Observable state of the codebase:
- One team added read replicas for a dashboard; another team's
  read-your-writes flow now intermittently reads stale data because no
  routing policy was written down.
- Indexes were added per feature; three are unused, and the hottest query
  still has no covering index because no one owned the posture.
- Pools were sized per service in isolation; the aggregate breaches the DB
  ceiling under autoscaling, discovered only during an incident.
```

Why this violates the rule: each decision looked reasonable locally, but
with no recorded strategy no one owned the interactions, and they were
discovered at the scale where they are expensive to unwind. The fix is to
author the strategy ADR (the good example) so the interactions surface at
decision time.
