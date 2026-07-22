<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.guarded-destructive-operation guarded destructive operation (anti-patterns)

Substrate-original anti-pattern examples for backup-recovery.guarded-destructive-operation. An irreversible
destruction runs unconditionally with no interposed guard.

## SQL: an unscoped delete that removes every row

```sql
-- no predicate: deletes the entire table, unrecoverable without a backup
DELETE FROM orders;
```

## Python: an ORM drop with no guard or snapshot

```python
# runs on import or deploy; no confirmation, no snapshot, no dry run
Base.metadata.drop_all(bind=engine)
```

## Bash: a recursive force-delete of a data root

```bash
# force-removes the live data directory unconditionally
rm -rf /var/lib/app/data
```

Each operation destroys durable data with no point of control. Interpose a
guard, a snapshot precondition, or a recognized safe wrapper, or scope the
operation to non-durable data.
