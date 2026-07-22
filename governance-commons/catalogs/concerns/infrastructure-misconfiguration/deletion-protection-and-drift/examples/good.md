<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.deletion-protection-and-drift deletion protection and drift monitoring (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.deletion-protection-and-drift. Each
shows the substrate's three-tier layered protection: provider
deletion-protection attribute, IaC lifecycle prevent_destroy,
and scheduled drift detection.

## Terraform: Stateful resources with layered protection

```hcl
resource "aws_db_instance" "payments_prod" {
  identifier              = "payments-prod"
  engine                  = "postgres"
  instance_class          = "db.r6g.xlarge"
  allocated_storage       = 500
  deletion_protection     = true   # provider tier
  skip_final_snapshot     = false
  final_snapshot_identifier = "payments-prod-final"
  backup_retention_period = 30
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.data_at_rest.arn

  lifecycle {
    prevent_destroy = true  # IaC tier
  }

  tags = merge(local.common_tags, {
    environment = "production"
  })
}

resource "aws_dynamodb_table" "sessions_prod" {
  name                        = "payments-sessions-prod"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "session_id"
  deletion_protection_enabled = true  # provider tier

  attribute {
    name = "session_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true  # IaC tier
  }

  tags = merge(local.common_tags, {
    environment = "production"
  })
}

resource "aws_s3_bucket" "audit_records_prod" {
  bucket = "audit-records-prod"

  lifecycle {
    prevent_destroy = true
  }

  tags = merge(local.common_tags, {
    environment = "production"
  })
}

resource "aws_s3_bucket_versioning" "audit_records_prod" {
  bucket = aws_s3_bucket.audit_records_prod.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_object_lock_configuration" "audit_records_prod" {
  bucket = aws_s3_bucket.audit_records_prod.id
  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = 2557  # 7 years for regulated audit records
    }
  }
}
```

## Terraform: Ephemeral resources explicitly opt out

```hcl
# Ephemeral test fixture; protections deliberately omitted
resource "aws_db_instance" "test_fixture" {
  identifier          = "ci-test-${var.run_id}"
  engine              = "postgres"
  instance_class      = "db.t4g.micro"
  allocated_storage   = 20
  deletion_protection = false      # deliberate; ephemeral
  skip_final_snapshot = true
  storage_encrypted   = true       # encryption still required (L1)

  # No lifecycle prevent_destroy; this resource is meant to be
  # torn down at end of CI run

  tags = merge(local.common_tags, {
    environment = "ephemeral"
    "governance-commons.intent" = "ci-fixture"
  })
}
```

## GitHub Actions: Daily drift detection

```yaml
# .github/workflows/drift-detect.yml
name: drift-detect

on:
  schedule:
    - cron: "0 7 * * *"  # daily 07:00 UTC
  workflow_dispatch:

permissions:
  id-token: write   # for OIDC to AWS
  contents: read

jobs:
  detect:
    strategy:
      matrix:
        workspace: [payments-prod, identity-prod, billing-prod]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111122223333:role/tf-drift-readonly
          aws-region: us-west-2

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.12.0

      - name: terraform init
        run: terraform init -input=false
        working-directory: workspaces/${{ matrix.workspace }}

      - name: terraform plan -detailed-exitcode
        id: plan
        continue-on-error: true
        run: |
          terraform plan -input=false -detailed-exitcode \
            -out=plan.tfplan
        working-directory: workspaces/${{ matrix.workspace }}

      - name: post drift alert
        if: steps.plan.outcome == 'failure' || steps.plan.outcome == 'success'
        run: |
          if [ "${{ steps.plan.conclusion }}" = "success" ] && \
             [ "${{ steps.plan.outputs.exitcode }}" = "2" ]; then
            curl -X POST "$SLACK_WEBHOOK" -d @- <<EOF
            {
              "text": "Drift detected in ${{ matrix.workspace }}",
              "link": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
EOF
          fi
        env:
          SLACK_WEBHOOK: ${{ secrets.DRIFT_ON_CALL_WEBHOOK }}
```

The CI role `tf-drift-readonly` carries IAM permissions that
exclude any write operation; the role can only read resource
state via `terraform plan`.

## Sentinel: terraform destroy gate on production workspaces

```hcl
# .terraform/policies/no-destroy-on-prod.sentinel
import "tfplan/v2" as tfplan

is_production = tfplan.variables.environment.value == "production"
has_destroy_action = length(filter tfplan.resource_changes as _, rc {
    contains(rc.change.actions, "delete")
}) > 0

main = rule {
    not (is_production and has_destroy_action)
}
```

## What the L2 review verifies

- Production stateful resources declare provider-tier deletion
  protection (deletion_protection_enabled, prevent_destroy
  semantics).
- Production stateful resources declare IaC-tier lifecycle
  prevent_destroy.
- Scheduled drift detection runs at the substrate-required
  cadence (daily for production, hourly for regulated).
- Drift findings emit alerts to the on-call channel mapped from
  the owner tag (infrastructure-misconfiguration.governance-tagging).
- Ephemeral resources explicitly opt out and document the
  intent.
- A `terraform destroy` policy-as-code gate is in place per the
  consumer's infrastructure-misconfiguration.infrastructure-security-baseline enforcement-model choice.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
