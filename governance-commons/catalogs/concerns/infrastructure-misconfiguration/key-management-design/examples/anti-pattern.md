<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.key-management-design key-management design (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.key-management-design.

## Anti-pattern 1: Provider-managed key on confidential data

```hcl
# Bad: SSE-S3 on a bucket holding confidential data
resource "aws_s3_bucket" "phi_records" {
  bucket = "phi-records-prod"
  tags = {
    "data-sensitivity" = "restricted"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "phi_records" {
  bucket = aws_s3_bucket.phi_records.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"  # provider-managed key
    }
  }
}
```

**Why it matters:** Confidential / restricted data requires a
customer-managed key (CMK) per the consumer's classification-to-
key-tier matrix. SSE-S3 satisfies infrastructure-misconfiguration.data-resource-encryption-at-rest's encryption
declaration but fails the infrastructure-misconfiguration.key-management-design review's first question.

## Anti-pattern 2: Default key policy on shared key

```hcl
# Bad: KMS key with default (account-wide) policy
resource "aws_kms_key" "shared" {
  description         = "Shared key"
  enable_key_rotation = true
  # policy attribute omitted; provider applies the default policy
  # which grants every principal in the account that has appropriate
  # IAM permissions
}
```

**Why it matters:** The default key policy grants
account-wide-via-IAM access; any IAM principal with KMS
permissions can use the key. The substrate requires a scoped
key policy naming specific principals.

## Anti-pattern 3: Key admin and key user are the same principal

```hcl
# Bad: one role manages and uses the key
data "aws_iam_policy_document" "combined" {
  statement {
    effect    = "Allow"
    actions   = ["kms:*"]  # all KMS actions
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.app_and_admin.arn]
    }
  }
}
```

**Why it matters:** A principal that can both manage the key
(disable, schedule deletion) and use it cryptographically can
exfiltrate-then-erase or set up a cipher-oracle attack. The
substrate's bias is separation of duties: distinct admin and
user roles.

## Anti-pattern 4: Rotation disabled

```hcl
# Bad: rotation explicitly disabled
resource "aws_kms_key" "no_rotation" {
  description         = "Long-lived key"
  enable_key_rotation = false  # explicit disablement
}
```

**Why it matters:** Without rotation, key material persists
indefinitely. The blast radius of a compromised key grows with
its lifetime: every encrypted artifact in the key's lifetime
becomes plaintext to anyone who obtains the key. The substrate
requires rotation (automatic for symmetric).

## Anti-pattern 5: Cross-environment key reuse

```hcl
# Bad: production key used by staging workloads
resource "aws_kms_key" "shared_envs" {
  description         = "Shared across all environments"
  enable_key_rotation = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "prod_data" {
  bucket = aws_s3_bucket.prod_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.shared_envs.arn
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "staging_data" {
  bucket = aws_s3_bucket.staging_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.shared_envs.arn
    }
  }
}
```

**Why it matters:** A staging workload's compromise enables
decryption of production data because both share the key.
Substrate-required: per-environment keys; environment-tier
isolation is a primary blast-radius control.

## Anti-pattern 6: Short or absent deletion window

```hcl
# Bad: 7-day deletion window
resource "aws_kms_key" "fast_delete" {
  description             = "Short-window key"
  deletion_window_in_days = 7  # substrate minimum is 30 for production
}

# Bad: Azure Key Vault without purge protection
resource "azurerm_key_vault" "no_purge" {
  name                       = "kv-app"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = false  # bad
  soft_delete_retention_days = 7      # substrate minimum is 30
}
```

**Why it matters:** A short deletion window or absent purge
protection enables a compromised admin to schedule key
deletion fast enough that recovery may not happen. The
substrate's minimum is 30 days for production keys.

## Anti-pattern 7: Key in IaC but referenced via alias name only

```hcl
# Bad: alias-by-name reference without explicit key arn
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = "alias/data"  # name-only; can be redirected
    }
  }
}
```

**Why it matters:** Alias names can be re-pointed to a different
key without re-deploying the IaC. The substrate prefers
explicit `aws_kms_alias.target_key_id` and `aws_kms_key.arn`
references in IaC so the binding is reviewable.

## How each anti-pattern is reviewed

Detected by Checkov (CKV_AWS_7 rotation, CKV_AWS_33 key policy,
CKV_AZURE_42 purge protection, etc.), Trivy, terrascan, and the
infrastructure-misconfiguration.key-management-design review-checklist's seven questions.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired `key-management-design-good.md`
example.
