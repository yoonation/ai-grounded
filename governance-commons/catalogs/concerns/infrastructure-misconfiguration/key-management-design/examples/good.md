<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.key-management-design key-management design (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.key-management-design. Each
shows the substrate's pattern of CMK declaration, scoped key
policies, rotation, separation of administrator and user roles,
and lifecycle protection.

## Terraform: AWS KMS key with scoped policy and rotation

```hcl
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "payments_data_key" {
  # Root grant retained for recovery (substrate-recommended; do
  # not remove the root grant or the key becomes unrecoverable
  # by the account owner)
  statement {
    sid     = "EnableRootAccountRecovery"
    effect  = "Allow"
    actions = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  # Key administrator role: can manage the key but cannot
  # cryptographically use it
  statement {
    sid    = "AllowKeyAdministrator"
    effect = "Allow"
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion",
    ]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.kms_admin.arn]
    }
  }

  # Key user role: can use the key cryptographically but cannot
  # manage its lifecycle
  statement {
    sid    = "AllowKeyUsage"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
    ]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.payments_app.arn]
    }
  }
}

resource "aws_kms_key" "payments_data" {
  description             = "Payments data-at-rest CMK"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.payments_data_key.json
  tags = merge(local.common_tags, {
    "data-sensitivity" = "confidential"
  })
}

resource "aws_kms_alias" "payments_data" {
  name          = "alias/payments-data-at-rest"
  target_key_id = aws_kms_key.payments_data.key_id
}
```

## Terraform: Per-workload, per-region, per-environment keys

```hcl
# Production payments has its own key
module "kms_payments_prod" {
  source      = "./modules/cmk"
  description = "Payments data-at-rest CMK (production)"
  alias       = "payments-data-prod"
  tags = merge(local.common_tags, {
    workload    = "payments"
    environment = "production"
  })
}

# Staging payments has a separate key
module "kms_payments_staging" {
  source      = "./modules/cmk"
  description = "Payments data-at-rest CMK (staging)"
  alias       = "payments-data-staging"
  tags = merge(local.common_tags, {
    workload    = "payments"
    environment = "staging"
  })
}
```

## Azure: Key Vault with purge protection and rotation policy

```hcl
resource "azurerm_key_vault" "payments" {
  name                       = "kv-payments-prod"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "premium"
  purge_protection_enabled   = true
  soft_delete_retention_days = 30
  enable_rbac_authorization  = true
  tags                       = local.common_tags
}

resource "azurerm_key_vault_key" "payments_data" {
  name         = "payments-data-at-rest"
  key_vault_id = azurerm_key_vault.payments.id
  key_type     = "RSA"
  key_size     = 4096
  key_opts     = ["decrypt", "encrypt", "sign", "unwrapKey", "verify", "wrapKey"]

  rotation_policy {
    automatic { time_before_expiry = "P30D" }
    expire_after = "P90D"
  }
}
```

## GCP: Cloud KMS with rotation period and IAM scoping

```hcl
resource "google_kms_key_ring" "payments" {
  name     = "payments-prod"
  location = "us-west1"
}

resource "google_kms_crypto_key" "payments_data" {
  name            = "data-at-rest"
  key_ring        = google_kms_key_ring.payments.id
  rotation_period = "7776000s"  # 90 days
  purpose         = "ENCRYPT_DECRYPT"

  lifecycle {
    prevent_destroy = true
  }

  labels = local.common_labels
}

resource "google_kms_crypto_key_iam_binding" "encrypter" {
  crypto_key_id = google_kms_crypto_key.payments_data.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members = [
    "serviceAccount:${google_service_account.payments_app.email}",
  ]
}
```

## What the L2 review verifies

- Customer-managed keys (CMK) for resources classified at the
  tier requiring it.
- Key policies scope non-root principals to specific role ARNs.
- Key administrator and key user roles are separated.
- Rotation is configured (automatic for symmetric; documented
  procedure for asymmetric).
- Keys are scoped per workload, per region, per environment.
- Deletion protection: 30-day deletion window (AWS),
  purge_protection_enabled (Azure), IaC lifecycle
  prevent_destroy (GCP).

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
