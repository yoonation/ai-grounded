<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.caching-strategy caching strategy (anti-pattern)

Substrate-original illustration.

```text
There is no caching ADR. Caching grew per feature:

- Team A cached product summaries in Redis with a 10-minute TTL and a key
  "product:{id}".
- Team B cached a product's price separately under "price_{id}" with no TTL,
  and invalidates it on price changes but does not know about Team A's
  summary, which embeds the price and is never invalidated on a price change.
- Team C cached a user's full profile, including their email and address, in
  the same shared Redis used by an edge worker, with no record that this data
  class should not leave the private tier.
```

## Why this violates the rule

With no recorded strategy, the local decisions collide. Two key conventions
coexist (`product:{id}` and `price_{id}`), the same data is cached twice, and
a price change invalidates one copy but not the summary that embeds it, so a
corrected price is served stale indefinitely. A sensitive data class lands in
a shared tier reachable from an edge worker because no one wrote down that it
must not. A caching strategy ADR covering the seven sub-decisions makes these
interactions visible and owned before they become incidents.
