<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.coverage-and-objectives coverage and recovery objectives (anti-pattern)

Substrate-original anti-pattern example for backup-recovery.coverage-and-objectives. A protected store
has no backup, and a backup frequency is looser than the tier tolerates.

## Coverage gap and an unmet objective (illustrative)

```yaml
tiers:
  critical:        # RPO 1h, RTO 1h
    rpo_minutes: 60
    rto_minutes: 60
    stores: [orders, payments]

backups:
  orders:   { interval_minutes: 1440, last_verified_restore_minutes: null }
  # payments: MISSING from the backup set entirely
```

Two failures hide here. `payments` is classified critical but is absent from
the backup set: an unrecoverable gap nobody decided to accept. `orders` is
backed up daily (1440) against a one-hour RPO (60): a recovery would lose up
to a day of orders, far more than the tier tolerates, and its restore time is
unknown because no restore has been verified. Reconcile the backup set against
the inventory and size frequency and restore time to the objectives.
