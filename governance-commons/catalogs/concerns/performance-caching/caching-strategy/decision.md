---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: performance-caching.caching-strategy
title: "Caching Strategy: What Is Cached, Topology, Keys, Invalidation, Staleness, Failure Posture, and Sizing"
lifecycle-status: stable
commons-version: "0.6.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M4 close consolidation (2026-06-01) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M4 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-01. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with performance-caching.caching-strategy substrate rule. Portfolio-of-sub-decisions structure mirroring the data-access-performance-strategy and reliability-strategy MADR precedents: seven sub-decisions (what is cached and never cached, cache topology and tiers, key and namespace conventions, invalidation model per data class, staleness budget per data class, failure posture, sizing and eviction) plus a review cadence, rather than a single option pick. Draft lifecycle per M4 Session 5; stable promotion at M4 close."
authoritative-sources:
  - "https://redis.io/docs/latest/develop/use/patterns/"
  - "https://redis.io/docs/latest/develop/reference/eviction/"
  - "https://redis.io/docs/latest/develop/use/keyspace/"
  - "https://www.rfc-editor.org/rfc/rfc9111.html"
  - "https://en.wikipedia.org/wiki/Cache_stampede"
  - "https://aws.amazon.com/builders-library/caching-challenges-and-strategies/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.data-access-performance-strategy
---

# Caching Strategy: What Is Cached, Topology, Keys, Invalidation, Staleness, Failure Posture, and Sizing

## Context and Problem Statement

Any application that caches has a caching strategy. The only choice is
whether it is decided and written down or left to accrete from whatever
each author happened to cache. performance-caching.caching-strategy requires that the strategy be
explicit, because caching correctness is a system property that emerges
from how a set of decisions cohere, not from any one of them. The
mechanical rules (a bounded time-to-live on every write, no per-item cache
call in a loop, namespaced keys) and the semantic rules (invalidation
correctness, stampede protection, cache-as-optional, staleness tolerance,
bounded eviction) are each local conformance checks; what they conform to
is this strategy. The failure this prevents is the pile of locally
reasonable caching decisions that do not cohere: a value cached by one
path and invalidated by none, a key convention that differs per module so
the same data is cached twice, a sensitive value cached in a shared tier
because no one recorded that it must not be.

This framework is the deliberate complement to the data-access performance
strategy (decision-frameworks.data-access-performance-strategy). That
framework governs using the datastore well; this one governs avoiding the
datastore via a cache. The two cross-reference rather than restate: a
cache does not excuse an unbounded or unindexed query behind it.

## Decision Drivers

- The read-to-write ratio and the recomputation cost of the cached values
  (caching pays off for read-heavy, expensive-to-compute values).
- The freshness requirements of each value, which set the staleness budget.
- The data classification of each value, which constrains what may be
  cached and in which tier (a private in-process cache, a shared
  distributed cache, an edge or CDN cache that replicates widely).
- The deployment topology and the operational maturity for running a cache
  tier (a distributed cache is infrastructure to run and fail over).
- The cost of staleness and of a stampede against the source of record.

## Considered Options

The strategy is a portfolio of seven sub-decisions. Each is recorded with
the option chosen and the drivers that selected it.

### Sub-decision 1: What is cached and what is never cached

This is the premise the other six rest on. Inventory the values that are
expensive enough and read enough to be worth caching, and, just as
important, record what is never cached and why. The drivers are the
read-to-write ratio, the recomputation cost, and the data classification:
some values must not be cached at all (a value that must always be fresh,
or sensitive data whose classification forbids the available tiers). The
options are depth levels rather than alternatives: an informal list for a
small system, a measured inventory keyed to the hot paths for a larger
one. Recording the never-cached set explicitly is what keeps a later
contributor from caching a value the strategy deliberately excluded.

### Sub-decision 2: Cache topology and tiers

Decide where values are cached. Options are an in-process cache (the
simplest, fastest, and least consistent across instances, suited to small
hot values that tolerate per-instance staleness), a shared distributed
cache such as Redis or Memcached (the default for values that must be
consistent across instances and survive a deploy), an edge or CDN cache
(for cacheable responses served to many clients), and a multi-tier
hierarchy combining them. The drivers are the consistency requirement
across instances, the data classification (a shared or edge tier
replicates the value more widely), and the operational maturity to run the
tier. This topology is what performance-caching.cache-as-optional (fallback per tier) and
performance-caching.bounded-eviction (bounding per backend) are assessed against.

### Sub-decision 3: Key and namespace conventions

Decide the project-wide cache key conventions: the namespace prefix scheme
(a data-type or domain prefix so unrelated values do not collide), the
versioning rule (a version component in the key for values whose shape can
change across deploys, so a deploy does not serve a value computed under an
old shape), and the rule that a key must include every input that varies
the value. The driver is the need to avoid collision and stale-across-
deploy serving. These conventions are what performance-caching.namespaced-keys checks the
mechanical key shape against and what performance-caching.invalidation-strategy relies on to know which
keys a write must invalidate.

### Sub-decision 4: Invalidation model per data class

Decide, per class of cached data, how the cached copy is kept correct when
the underlying data changes. Options are write-through or write-around with
explicit invalidation on every write that affects the value (the answer for
values that must be fresh), time-to-live-only with deliberate bounded
staleness (the answer for values that tolerate staleness), and event-driven
invalidation off a change stream (the answer at scale where many consumers
cache derived views). The driver is the staleness budget from sub-decision
5 and the set of writes that affect each value. This model is what
performance-caching.invalidation-strategy checks, with the performance-caching.ttl-on-write time-to-live as the floor that
bounds a missed invalidation.

### Sub-decision 5: Staleness budget per data class

Decide, per class of cached data, the maximum acceptable age of a served
value: must-be-fresh, tolerates-minutes, tolerates-hours. The driver is the
product and correctness requirement of the consumer of the value. The
budget is the input that sets the time-to-live duration (performance-caching.ttl-on-write) and
the invalidation aggressiveness (sub-decision 4): a must-be-fresh class is
a candidate for write-through or for the never-cached set, a tolerant class
is a candidate for a long time-to-live and a time-to-live-only model. This
budget is what performance-caching.staleness-tolerance classifies each item against. It is the
caching analogue of the per-path replica-lag-tolerance decision in the
data-access strategy.

### Sub-decision 6: Failure posture

Decide how the application behaves when the cache is unavailable, slow, or
returns an error. The substrate-recommended posture is fixed rather than
open: the cache is optional to correctness, so a miss, an error, and a
timeout all fall back to the source of record, cache calls carry a bounded
timeout, and no authoritative data lives only in the cache. The decision
the strategy records is how this posture is implemented project-wide (a
shared cache-aside helper, a standard timeout, a standard fallback) and the
stampede-protection default for hot keys (a single-flight lock, request
coalescing, or stale-while-revalidate). The drivers are the operational
reality that cache outages happen and the availability cost of a stampede.
This posture is what performance-caching.cache-as-optional and performance-caching.stampede-protection check.

### Sub-decision 7: Sizing and eviction policy

Decide the cache memory budget and the eviction policy per tier: the
maximum memory of the distributed cache and its eviction policy (an LRU or
LFU variant for a general cache), the capacity and eviction of an
in-process cache, and the consideration of key cardinality against the
size so a wide key space does not thrash the cache. The drivers are the
working-set size, the key cardinality, and the memory budget. This sizing
is what performance-caching.bounded-eviction checks the deployment configuration against; the
unbounded in-process collection itself remains a reliability concern
(reliability.bounded-buffers).

## Decision Outcome

The outcome is a recorded ADR that states, for each of the seven
sub-decisions, the option chosen and the drivers that selected it. The ADR
need not be long; it needs to be explicit and current. The
substrate-recommended sequence is to record what is and is not cached
first because it is the premise, then topology, key conventions,
invalidation model, staleness budget, failure posture, and sizing. A small
read-heavy service has a short ADR (cache the few hot expensive reads in a
shared Redis, never cache the session or any value classified sensitive,
namespaced and versioned keys, write-through invalidation on the two hot
entities and time-to-live-only elsewhere, a minutes-scale staleness budget,
cache-aside with a bounded timeout and source fallback, a fixed maxmemory
with allkeys-lru); the value is that even this short version is written
down and can be updated rather than rediscovered after a stale-data
incident or a cache outage.

## Substrate Alignment

This framework is the L3 anchor for the performance-caching concern. The
three L1 rules and five L2 rules are conformance checks against the
sub-decisions here: performance-caching.namespaced-keys against the key and namespace conventions
(sub-decision 3), performance-caching.ttl-on-write and performance-caching.invalidation-strategy against the invalidation
model and its time-to-live floor (sub-decisions 4 and 5), performance-caching.staleness-tolerance
against the staleness budget (sub-decision 5), performance-caching.stampede-protection and
performance-caching.cache-as-optional against the failure posture and stampede default
(sub-decision 6), and performance-caching.bounded-eviction against the sizing and eviction policy
(sub-decision 7), with the topology decision (sub-decision 2) framing where
each applies. performance-caching.no-cache-call-in-loop (no per-item cache call in a loop) is a
round-trip-amortization floor that applies under whatever topology is
chosen. The concern is deliberately scoped to the mechanics of caching;
whether a given data class may be cached in a given tier is a
data-classification decision this ADR consumes as a driver and
cross-references rather than restating, and making the underlying query
efficient is the data-access-performance-strategy sibling's concern.

## Consequences

Recording the strategy forces the interactions between the seven
sub-decisions into view at decision time (most importantly that the
staleness budget drives the invalidation model and the time-to-live, and
that the data classification constrains the topology), gives new
contributors the context to make local caching choices that fit the whole,
and creates the artifact a scale or topology change updates rather than
rediscovers. The cost is the discipline of authoring and maintaining the
ADR, small relative to the failure it prevents: stale data served from a
forgotten cache, a stampede that takes down the source, or sensitive data
cached in a tier that replicates it too widely. The risk is an ADR that
goes stale; the review cadence below is the mitigation.

## References

- Redis caching patterns, key eviction, and keyspace naming (engine
  documentation).
- RFC 9111 HTTP Caching (freshness, age, and stale-while-revalidate as a
  staleness vocabulary).
- Cache stampede (the thundering-herd problem and its mitigations).
- AWS Builders' Library caching challenges and strategies (the strategic
  caching decisions).
- MADR (the decision-record format).

## Decision Review Schedule

Author the strategy when the application first makes meaningful use of
caching. Revisit it at each significant change in cache topology or scale,
at the introduction of a new cache tier, and on a periodic cadence
(annually is a reasonable default). A review confirms the seven
sub-decisions are still current, that the data-classification constraints
still hold, and that the local L1 and L2 choices still cohere with the
recorded strategy.
