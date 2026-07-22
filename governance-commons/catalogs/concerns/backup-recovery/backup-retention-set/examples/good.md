<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.backup-retention-set backup retention set (good patterns)

Substrate-original good-pattern examples for backup-recovery.backup-retention-set. Every declared
backup or snapshot resource sets an explicit, non-zero retention sized to the
data tier's recovery objectives.

## Terraform: an AWS Backup plan with an explicit retention

```hcl
resource "aws_backup_plan" "primary" {
  name = "primary-daily"
  rule {
    rule_name         = "daily"
    target_vault_name = aws_backup_vault.primary.name
    schedule          = "cron(0 5 * * ? *)"
    lifecycle {
      # explicit, non-zero retention sized to the tier RPO/RTO in the ADR
      delete_after = 35
    }
  }
}
```

## Terraform: an RDS instance with a non-zero backup retention period

```hcl
resource "aws_db_instance" "orders" {
  identifier              = "orders"
  backup_retention_period = 14   # days; never 0 for a protected store
  backup_window           = "03:00-04:00"
}
```

Each backup resource keeps its copy long enough to use. The retention value
is set deliberately and is reviewable against the tier's recovery objectives.
