<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.data-subject-rights-and-retention DSR and retention architecture ADR (good pattern)

Substrate-original illustration.

```markdown
# ADR: Data-subject-rights and retention architecture

## Store inventory
primary db, redis cache, opensearch index, warehouse, daily backups, email vendor.

## Erasure propagation
Synchronous erase across primary, cache, index, warehouse. Backups: crypto-shred
by destroying the per-subject key; tombstone until backup window expires.

## Portability format
JSON export, documented schema, machine-readable.

## Request handling
Intake -> identity verification -> fan-out to inventory -> completion record.
Statutory window: 30 days.

## Retention schedule
Per category; deletion or irreversible anonymization at expiry. Log retention per logging.retention-policy.

## Owner and review
Owner: privacy lead. Reviewed when a store is added.
```

## Why this satisfies the rule

The architecture decides how erasure propagates across every store including
backups, the portability format, the verified request-handling flow, and the
retention schedule coordinated with logging retention. privacy.data-subject-rights and privacy.retention-limitation
have a designed architecture to rely on rather than improvising per incident. The
store inventory cross-references data-classification.propagation-inheritance rather than duplicating it.
