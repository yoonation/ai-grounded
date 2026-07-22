<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.guarded-destructive-operation guarded destructive operation (good patterns)

Substrate-original good-pattern examples for backup-recovery.guarded-destructive-operation. An irreversible
data destruction passes through a guard, a snapshot precondition, or a
recognized safe wrapper.

## SQL migration: snapshot precondition before a drop

```sql
-- guarded: a verified snapshot exists before the irreversible drop
-- snapshot: orders_pre_v42 taken and verified by the migration runner
DROP TABLE orders_legacy;
```

## Python: a recognized safe-delete wrapper with confirmation

```python
# safe_destroy snapshots, requires an explicit confirm token, and logs
safe_destroy(
    target=orders_archive,
    confirm=os.environ["DESTROY_CONFIRM_TOKEN"],
    snapshot_first=True,
)
```

## Bash: a scoped delete, not a recursive force-delete of a data root

```bash
# scoped to a dated, ephemeral export dir, not the data root
rm -rf "/var/exports/tmp/${RUN_ID}"
```

Each destruction is deliberate and recoverable or scoped to non-durable data.
The guard is the point of control at the place loss originates.
