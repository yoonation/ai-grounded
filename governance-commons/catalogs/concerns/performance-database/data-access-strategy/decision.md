---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: performance-database.data-access-strategy
title: "Data-Access Performance Strategy: Workload, Indexing, Connections, Transactions, Pagination and Bulk IO, and Read Scaling"
lifecycle-status: stable
commons-version: "0.6.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M4 close consolidation (2026-06-01) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M4 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-01. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with performance-database.data-access-strategy substrate rule. Portfolio-of-sub-decisions structure mirroring the reliability-strategy MADR precedent: six sub-decisions (workload characterization, indexing posture, connection topology, transaction and consistency policy, pagination and bulk-IO conventions, read-scaling model) plus a review cadence, rather than a single option pick. Draft lifecycle per M4 Session 4; stable promotion at M4 close."
authoritative-sources:
  - "https://www.postgresql.org/docs/current/performance-tips.html"
  - "https://www.postgresql.org/docs/current/indexes-multicolumn.html"
  - "https://www.postgresql.org/docs/current/transaction-iso.html"
  - "https://www.postgresql.org/docs/current/runtime-config-connection.html"
  - "https://use-the-index-luke.com/"
  - "https://www.pgbouncer.org/"
  - "https://aws.amazon.com/builders-library/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.reliability-strategy
---

# Data-Access Performance Strategy: Workload, Indexing, Connections, Transactions, Pagination and Bulk IO, and Read Scaling

## Context and Problem Statement

Every application that persists data has a data-access performance
strategy. The only choice is whether it is decided and written down or
left to accrete from whatever each author happened to optimize. PERFDB-
L3-001 requires that the strategy be explicit, because data-access
performance is a system property that emerges from how a set of decisions
cohere, not from any one of them. The mechanical rules (no query in a
loop, bounded result sets, explicit projection, pooled connections,
non-blocking migrations) and the semantic rules (index alignment,
transaction scope, pool sizing, keyset pagination, bulk operations,
replica routing) are each local conformance checks; what they conform to
is this strategy. An indexing choice made without the write workload, a
pool sized without the deployment model, or a replica added without a
consistency policy will each undermine the others, and the failure
becomes visible only at the scale where the decisions are expensive to
revisit.

The substrate's position is that the strategy must be recorded, not that
any particular strategy is correct. The right answer for a low-traffic
single-database application differs from the right answer for a
high-traffic replicated or sharded one. What is universal is that the six
sub-decisions below be made explicitly, with their drivers, and revisited
on a stated cadence.

## Decision Drivers

- The workload's read and write mix, its hot access patterns, and its
  current and projected data volume.
- The datastore engine and its constraints (the connection ceiling, the
  isolation semantics, the index types available).
- The deployment model (a fixed fleet, autoscaling, serverless) and its
  effect on connection topology.
- The consistency requirements of each read and write path.
- The scale trajectory: the order of magnitude the system must reach and
  when.
- The cost of revisiting a decision later, which rises sharply with data
  volume and traffic.

## Considered Options

The strategy is a portfolio of six sub-decisions. Each is recorded with
the option chosen and the drivers that selected it.

### Sub-decision 1: Workload characterization and access-pattern inventory

This is the premise the other five rest on. Characterize the workload:
the read-to-write ratio, the handful of hot queries that dominate load,
the largest tables and their growth rate, and the access patterns (lookup
by key, range scan, full-text search, aggregation). The options are not
competing alternatives so much as depth levels: an informal description
for a small system, a measured inventory from the slow-query log and
table statistics for a larger one. The driver is scale: the larger the
system, the more the inventory must be evidence-based rather than assumed.
Recording this first forces the later decisions to rest on facts.

### Sub-decision 2: Indexing posture

Decide how indexing balances read access against write cost. Options range
from index-the-hot-reads (the default for read-heavy OLTP, accepting the
write tax for the read speedup) to minimal-indexing (for write-heavy or
append-only tables where each index is a meaningful write cost) to
specialized approaches (partial, expression, or covering indexes for
specific hot queries). The drivers are the read-to-write ratio from
sub-decision 1 and the selectivity of the hot queries. This posture is
what performance-database.index-alignment checks individual indexes against.

### Sub-decision 3: Connection topology

Decide how the application connects to the datastore. Options are
per-instance pools sized to the fleet (the default for a fixed or modestly
autoscaling fleet), per-instance pools behind an external pooler such as
PgBouncer (the answer for serverless or high-fan-out deployments where
instance count is elastic and would otherwise breach the connection
ceiling), and, at large scale, a connection-multiplexing layer as
infrastructure. The drivers are the deployment model and the datastore's
connection ceiling. This topology is what performance-database.pool-sizing sizes pools
against, and performance-database.pooled-connections enforces that a pool is used at all.

### Sub-decision 4: Transaction and consistency policy

Decide the default isolation level, when to escalate it, how contended
writes are guarded (optimistic version columns versus pessimistic locks
as a system-wide convention), and how cross-service atomicity is handled
(a synchronous distributed transaction, a saga, or an outbox with
post-commit dispatch). The drivers are the correctness requirements of the
write paths and the topology (a single database admits simpler choices
than a distributed one). This policy is what performance-database.transaction-scope checks
transaction scope and isolation against.

### Sub-decision 5: Pagination and bulk-IO conventions

Decide the project's conventions: the default pagination style (offset for
shallow lists, keyset for deeply-navigable or automation-exposed ones),
the page-size defaults and caps, and the batching convention for
high-volume reads and writes (the default batch size, the rule for when a
path must batch). The drivers are how lists are actually navigated and the
existence of high-volume import or sync paths. These conventions are what
performance-database.keyset-pagination (keyset) and performance-database.bulk-operations (bulk) check individual paths
against, and they make performance-database.bounded-result-sets (a bound exists) the floor under a
consistent pagination contract.

### Sub-decision 6: Read-scaling model

Decide whether and how reads scale beyond the primary. Options are a
single primary (no read scaling, the simplest and the right default until
read load demands otherwise), a primary with read replicas plus a per-path
lag-tolerance classification and a read-your-writes mechanism (sticky
primary reads for a window after a write, or lag-aware routing), and, at
the far end, sharding or a separate read store. The drivers are read load
relative to primary capacity and the consistency needs of the read paths.
This model is what performance-database.replica-routing checks replica routing against; until
replicas are adopted, that rule is dormant.

## Decision Outcome

The outcome is a recorded ADR that states, for each of the six
sub-decisions, the option chosen and the drivers that selected it. The
ADR need not be long; it needs to be explicit and current. The
substrate-recommended sequence is to record the workload characterization
first because it is the premise, then indexing, connection topology,
transaction and consistency policy, pagination and bulk-IO conventions,
and the read-scaling model. A small single-database read-heavy service has
a short ADR (index the hot reads, per-instance pools sized to the fleet,
default isolation with optimistic concurrency on the few contended paths,
offset pagination with keyset for the one deep list, single primary); the
value is that even this short version is written down and can be updated
rather than rediscovered at the next scale change.

## Substrate Alignment

This framework is the L3 anchor for the performance-database concern. The
five L1 rules and six L2 rules are conformance checks against the
sub-decisions here: performance-database.pooled-connections and performance-database.pool-sizing against the connection
topology, performance-database.index-alignment against the indexing posture, performance-database.transaction-scope
against the transaction and consistency policy, performance-database.bounded-result-sets and
performance-database.keyset-pagination and performance-database.bulk-operations against the pagination and bulk-IO
conventions, and performance-database.replica-routing against the read-scaling model. The concern
is deliberately scoped to making datastore access efficient; the decision
to avoid the datastore via a cache belongs to the performance-caching
concern, and this ADR cross-references that strategy rather than
restating it. The reliability-strategy framework is the related sibling
that owns the pool as a survival resource, where this framework owns it as
a throughput resource.

## Consequences

Recording the strategy forces the interactions between the six
sub-decisions into view at decision time, gives new contributors the
context to make local choices that fit the whole, and creates the
artifact a scale-change review updates rather than rediscovers. The cost
is the discipline of authoring and maintaining the ADR, which is small
relative to the cost of the failure it prevents: a pile of locally
reasonable choices that do not cohere, discovered at the scale where they
are expensive to unwind. The risk is an ADR that goes stale; the review
cadence below is the mitigation.

## References

- Postgres performance tips, multicolumn indexes, transaction isolation,
  and connection configuration (engine documentation).
- Use The Index, Luke (a public guide to application-developer indexing).
- PgBouncer (external connection pooling for the serverless and
  high-fan-out case).
- AWS Builders' Library (data-access and read-scaling engineering
  guidance).
- MADR (the decision-record format).

## Decision Review Schedule

Author the strategy when the application first takes meaningful production
traffic or persists meaningful data volume. Revisit it at each significant
change in scale (an order of magnitude in traffic or data), at the
introduction of read replicas or sharding, and on a periodic cadence the
team sets (annually is a reasonable default for a stable workload). Treat
a scale-order change or a topology change as a mandatory trigger to update
the ADR rather than a discretionary one.
