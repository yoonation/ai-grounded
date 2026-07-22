<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.strategy-adr backup-and-recovery strategy ADR (good pattern)

Substrate-original good-pattern example for backup-recovery.strategy-adr. The ADR decides
every required sub-decision, keeps them internally consistent, and draws the
sibling-concern boundaries.

## ADR excerpt (illustrative)

```markdown
# ADR-031: Backup-and-recovery strategy

Status: Accepted   Owner: Platform SRE   Review: annual + post-incident

- Protection inventory and tiers: consumed from data-classification
  (critical, standard, disposable). Disposable stores are not backed up.
- Topology: three copies, two media, one off-site (cross-region) for
  critical; daily full plus hourly incrementals for critical, daily full
  for standard.
- Retention and immutability: 35 days; object-lock (write-once) on critical
  tier copies for ransomware resilience.
- Recovery objectives: critical RPO 1h / RTO 1h; standard RPO 24h / RTO 8h.
- Restore verification: weekly for critical, monthly for standard, into an
  isolated target with integrity checks (backup-recovery.restore-verification).
- Encryption and key custody: keys and restore credentials owned by
  secrets-management; referenced by indirection, rotated without orphaning
  recoverable copies.
- Destructive-operation guard: snapshot-first wrapper `safe_destroy`,
  recognized by the backup-recovery.guarded-destructive-operation allow-list.
- Ownership and review: Platform SRE owns; reviewed annually and after any
  recovery incident or failed restore test.
```

Each sub-decision is resolved; retention supports the RPO, the topology
supports the RTO, and immutability matches the ransomware threat. Keys,
classification, storage hardening, failover, and alerting are deferred to
their owning concerns.
