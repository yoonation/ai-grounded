<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.deletion-protection-and-drift deletion protection and drift monitoring (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.deletion-protection-and-drift.

## Anti-pattern 1: Production RDS without deletion protection

```hcl
# Bad: production database with destroy enabled
resource "aws_db_instance" "payments_prod" {
  identifier          = "payments-prod"
  engine              = "postgres"
  instance_class      = "db.r6g.xlarge"
  allocated_storage   = 500
  # deletion_protection absent (defaults to false)
  skip_final_snapshot = true  # also bad; no final snapshot
}
```

**Why it matters:** A single `terraform destroy` or an
accidental refactor that removes the resource block (Terraform
treats removal as deletion) destroys the production database
irrecoverably (skip_final_snapshot true means no final
snapshot is taken). Substrate-required for production: both
deletion_protection and lifecycle prevent_destroy.

## Anti-pattern 2: Production DynamoDB without deletion_protection_enabled

```hcl
# Bad: missing deletion_protection_enabled
resource "aws_dynamodb_table" "sessions_prod" {
  name         = "payments-sessions-prod"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"
  attribute {
    name = "session_id"
    type = "S"
  }
  # deletion_protection_enabled absent (defaults to false)
}
```

**Why it matters:** Same as Anti-pattern 1, applied to DynamoDB.
The attribute is recent (introduced March 2023) but
substrate-required for production tables.

## Anti-pattern 3: Production stateful resource without lifecycle prevent_destroy

```hcl
# Bad: provider-tier protection but no IaC-tier
resource "aws_db_instance" "payments_prod" {
  identifier          = "payments-prod"
  engine              = "postgres"
  instance_class      = "db.r6g.xlarge"
  allocated_storage   = 500
  deletion_protection = true   # provider tier present
  # No lifecycle prevent_destroy
}
```

**Why it matters:** Provider-tier `deletion_protection` blocks
the cloud API delete; IaC-tier `prevent_destroy` blocks
Terraform's plan-time delete. They guard different layers:
provider-tier catches operator console deletes; IaC-tier
catches accidental code removals at PR time. Substrate
requires both for production.

## Anti-pattern 4: No drift detection at all

```yaml
# Bad: no scheduled drift-detection workflow
# .github/workflows/ directory has CI but no recurring
# terraform plan against production workspaces.
```

**Why it matters:** Out-of-band changes accumulate silently
between deploys. By the time a substrate-author next runs
`terraform plan`, the drift may have hidden a malicious
modification or a recovery-impacting manual change. The
substrate requires scheduled drift detection.

## Anti-pattern 5: Drift detection job with write credentials

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    # Bad: drift detection assumes the deploy role with write
    # permissions
    role-to-assume: arn:aws:iam::111122223333:role/tf-deploy
    aws-region: us-west-2
```

**Why it matters:** A compromised drift-detection workflow with
write credentials can apply unauthorized changes. The job is
detection-only; credentials must be read-only.

## Anti-pattern 6: Drift findings posted nowhere

```yaml
# Bad: drift detected, no alert
- name: terraform plan -detailed-exitcode
  run: |
    terraform plan -detailed-exitcode -out=plan.tfplan
  # Exit code 2 = drift; no alert step follows
  continue-on-error: true
```

**Why it matters:** Drift detection that produces logs nobody
reads is theater. The substrate requires alerts to the on-call
channel mapped from the owner tag.

## Anti-pattern 7: terraform destroy of production permitted without out-of-band approval

```yaml
# Bad: deploy workflow permits destroy on production
- name: terraform apply
  run: |
    terraform apply -auto-approve  # whatever the plan says
# No policy-as-code or manual approval gate prevents a destroy
# action against production workspaces.
```

**Why it matters:** A malicious or mistaken PR removing a
resource block translates to `terraform apply` deleting the
resource without human review. Substrate-required: a
policy-as-code rule (Sentinel, OPA Conftest, Checkov custom
check) blocking destroy actions on production unless an
explicit out-of-band approval token is present.

## Anti-pattern 8: Ephemeral resources without explicit intent tag

```hcl
# Bad: ephemeral resource that looks like production
resource "aws_db_instance" "test" {
  identifier          = "test-db"
  engine              = "postgres"
  instance_class      = "db.t4g.micro"
  allocated_storage   = 20
  deletion_protection = false
  skip_final_snapshot = true
  # No environment or intent tag distinguishing this from production
}
```

**Why it matters:** Without a clear environment / intent tag,
the L2 reviewer cannot distinguish whether the missing
protections are an anti-pattern or a deliberate ephemeral
choice. Substrate's bias: explicit-omission-with-rationale.

## How each anti-pattern is reviewed

The L2 review surfaces these via IaC inspection and CI workflow
review per the infrastructure-misconfiguration.deletion-protection-and-drift checklist's six questions. Drift-
detection coverage is verified by inspecting the consumer's
CI / CD configuration.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`deletion-protection-and-drift-good.md` example.
