<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.coverage-and-objectives coverage and recovery objectives (good pattern)

Substrate-original good-pattern example for backup-recovery.coverage-and-objectives. The backup set
reconciles against the data-classification protection inventory, and each tier
has defined recovery objectives that backup frequency and restore time meet.

## Coverage and objectives, reconciled (illustrative)

```yaml
# protection inventory (from data-classification) drives the backup set
tiers:
  critical:        # RPO 1h, RTO 1h
    rpo_minutes: 60
    rto_minutes: 60
    stores: [orders, payments]
  standard:        # RPO 24h, RTO 8h
    rpo_minutes: 1440
    rto_minutes: 480
    stores: [catalog, profiles]

backups:
  orders:   { interval_minutes: 30,  last_verified_restore_minutes: 42 }
  payments: { interval_minutes: 30,  last_verified_restore_minutes: 51 }
  catalog:  { interval_minutes: 720, last_verified_restore_minutes: 240 }
  profiles: { interval_minutes: 720, last_verified_restore_minutes: 300 }
```

Every store in the inventory has a backup (no gap). Each interval is at or
below its tier RPO (30 <= 60; 720 <= 1440). Each verified restore time is at
or below its tier RTO (42 and 51 <= 60; 240 and 300 <= 480). Coverage and
objectives are a measured property, not an assumption.
