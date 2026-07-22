<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.data-access-strategy data-access strategy (good pattern)

Substrate-original illustration. A short but complete strategy ADR recording
all six sub-decisions with their drivers.

```markdown
# ADR: Data-Access Performance Strategy (Orders service)
1. Workload: read-heavy (20:1), hot query is orders-by-customer; orders
   table ~30M rows, growing ~1M/month.
2. Indexing posture: index the hot reads; composite (customer_id,
   created_at) covering (id, total). Accept the write tax (read-heavy).
3. Connection topology: serverless; small per-instance pools (5) behind
   PgBouncer; DB ceiling 100.
4. Transaction/consistency: default isolation; optimistic version column on
   the order-status update (the one contended path); outbox for the
   payment/messaging effects.
5. Pagination/bulk IO: keyset pagination on the orders list (deeply
   navigated); batched multi-row insert (size 1000) for the nightly import.
6. Read scaling: one read replica; analytics and dashboards route to it;
   read-your-writes and write-gating reads pin to primary.
Revisit: at 10x data or traffic, or when adding a second replica. Reviewed
annually.
```

Why this satisfies the rule: every sub-decision is present with the driver
that selected it, the local choices the L1/L2 rules govern are traceable to
it, and it names a revisit cadence. It is short because the system is
simple, but it is written down and updatable.
