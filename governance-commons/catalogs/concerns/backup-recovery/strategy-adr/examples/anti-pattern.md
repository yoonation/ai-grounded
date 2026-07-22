<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.strategy-adr backup-and-recovery strategy ADR (anti-pattern)

Substrate-original anti-pattern example for backup-recovery.strategy-adr. The ADR leaves
core decisions open, contradicts itself, and blurs the sibling boundaries.

## ADR excerpt (illustrative)

```markdown
# ADR-031: Backups

Status: Accepted   Owner: (unassigned)

- We take nightly backups of the databases.
- Retention: TBD.
- RPO/RTO: to be determined per service later.
- Restore testing: we will test restores when we have time.
- Encryption keys are stored in the backup bucket alongside the backups
  for convenience.
- Ransomware: backups are in the same account and region as production.
```

Sub-decisions are missing or "to be determined", so there is no standard the
lower-layer rules can enforce. The decisions that exist contradict the goal:
keys colocated with the backups are a single point of compromise and a
recovery risk, and same-account same-region copies do not survive the
deletion or ransomware they are meant to protect against. There is no owner
and no review cadence. Resolve each sub-decision, make them consistent, and
defer keys to secrets-management.
