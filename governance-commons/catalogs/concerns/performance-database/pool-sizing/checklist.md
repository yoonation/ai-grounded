---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.performance-database.pool-sizing-pool-sizing"
title: "performance-database.pool-sizing review checklist: connection pool sizing"
substrate-rule: "performance-database.pool-sizing"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 4 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "Initial deployment of a service that connects to a datastore"
  - "Any change to instance count or autoscaling policy"
  - "A migration to or from a serverless runtime"
  - "An incident showing connection-acquisition timeouts or database connection refusals"
---

# performance-database.pool-sizing review checklist: connection pool sizing

## How to use this binding

Pool sizing is a two-sided constraint: too small serializes an instance's
concurrency, too large (summed across instances) breaches the database
ceiling. The review checks both sides plus the safety valves. The two
diagnostic signals from incident history are acquisition timeouts (pool too
small) and connection refusals (aggregate pools too large).

## Review questions

### 1. Does aggregate pool capacity stay within the database ceiling?

What good looks like: pool max times peak instance count, plus headroom for
admin and replica connections, is within the datastore's configured
connection limit.

What needs follow-up: a pool size that is fine per instance but, multiplied
by the autoscaling maximum, can exceed the database ceiling and cause
connection refusals.

### 2. Is a single instance's pool large enough for its concurrency?

What good looks like: an instance has enough connections to serve its
concurrent in-flight requests without excessive queueing on pool
acquisition, sized toward active concurrency rather than maximal.

What needs follow-up: a pool so small that requests serialize on connection
acquisition, presenting as database slowness that is really a starved pool.

### 3. Are the acquire timeout and max connection lifetime set?

What good looks like: a bounded acquire timeout (so pool starvation fails
fast and visibly) and a maximum connection lifetime (so connections recycle
and rebalance after a failover or scaling event) are configured.

What needs follow-up: no acquire timeout (starvation hangs rather than
errors) or no max lifetime (connections pin to a single node indefinitely).

### 4. Does a serverless or high-fan-out deployment use an external pooler?

What good looks like: where instance count is elastic and large, an external
pooler (PgBouncer or the managed equivalent) multiplexes many client
connections onto few database connections, and per-instance application
pools are small.

What needs follow-up: a serverless deployment connecting directly to the
database with per-instance pools and no external pooler, so instance churn
can breach the ceiling.

## When to escalate to L3

Escalate to performance-database.data-access-strategy when connection topology becomes architectural:
the deployment model forcing an external-pooler decision, the database
ceiling constraining the scaling plan, or pool sizing that must be
coordinated with a read-replica routing strategy (performance-database.replica-routing).
