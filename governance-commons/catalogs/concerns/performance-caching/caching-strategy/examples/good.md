<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.caching-strategy caching strategy (good pattern)

Substrate-original illustration.

```markdown
# ADR 0031: Caching Strategy

## 1. What is cached / never cached
Cached: product summaries, rendered marketing fragments, author article
lists. Never cached: account balances, permissions, anything classified
PII-sensitive (forbidden in the shared tier per data classification).

## 2. Topology and tiers
Shared Redis for cross-instance values; in-process LRU for hot render
fragments. No edge/CDN tier yet.

## 3. Key and namespace conventions
`<type>:v<schema>:<id>[:<variant>]`. Version bumped on serialized-shape
changes. Keys include every result-varying input.

## 4. Invalidation model per class
Write-through invalidation on product and article entities (and their list
and count keys). Time-to-live-only for marketing fragments.

## 5. Staleness budget per class
Balances/permissions: must-be-fresh (not cached). Product summary:
minutes. Marketing fragment: hours.

## 6. Failure posture
Cache-aside helper with a 50ms timeout, source fallback on any failure,
single-flight locks on the three hottest keys.

## 7. Sizing and eviction
Redis maxmemory 2gb, allkeys-lru. In-process LRU maxsize 1024 per worker.
```

## Why this satisfies the rule

The ADR is short but covers all seven sub-decisions, each with its drivers,
and records the data-classification constraints (what may not be cached and
where). A new contributor can make a local caching choice that fits the
whole, and a scale change updates this document rather than rediscovering
the decisions after an incident.
