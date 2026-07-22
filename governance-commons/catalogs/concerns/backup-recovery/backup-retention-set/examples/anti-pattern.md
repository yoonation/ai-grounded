<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.backup-retention-set backup retention set (anti-patterns)

Substrate-original anti-pattern examples for backup-recovery.backup-retention-set. A declared backup
resource whose retention is absent, zero, or disabled keeps no recoverable
copy when it is needed.

## Terraform: backup retention disabled

```hcl
resource "aws_db_instance" "orders" {
  identifier              = "orders"
  backup_retention_period = 0   # backups disabled; the job looks present, the copy is not kept
}
```

## Terraform: a snapshot schedule with no retention, expiring the only copy

```hcl
resource "aws_backup_plan" "primary" {
  name = "primary-daily"
  rule {
    rule_name         = "daily"
    target_vault_name = aws_backup_vault.primary.name
    schedule          = "cron(0 5 * * ? *)"
    # no lifecycle block: retention defaults are provider-dependent and may keep nothing
  }
}
```

Both declarations pass a casual review (a backup resource exists) while
providing no recoverable copy. Set an explicit non-zero retention sized to the
data tier.
