<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.state-backend-hardening state-backend hardening (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.state-backend-hardening. Each
shows the substrate's pattern of remote, encrypted, access-
restricted, versioned, locked, and audit-logged state backend.

## Terraform: S3 + DynamoDB backend with full hardening

```hcl
# Backend config in backend.tf (single source of truth)
terraform {
  backend "s3" {
    bucket         = "myco-tfstate-prod"
    key            = "payments/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "myco-tfstate-locks-prod"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-west-2:111122223333:key/abc-def-123"
  }
}
```

## Terraform: Backend bucket configuration

```hcl
# In the separate bootstrap module that creates the backend
resource "aws_s3_bucket" "tfstate" {
  bucket = "myco-tfstate-prod"
  tags = merge(local.common_tags, {
    "data-sensitivity" = "restricted"  # state contains secrets
  })
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.tfstate.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "tfstate" {
  bucket        = aws_s3_bucket.tfstate.id
  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "tfstate/"
}

resource "aws_s3_bucket_lifecycle_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    noncurrent_version_expiration {
      noncurrent_days = 90  # retain old versions 90 days
    }
  }
}

resource "aws_s3_bucket_policy" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  policy = data.aws_iam_policy_document.tfstate_bucket.json
}

data "aws_iam_policy_document" "tfstate_bucket" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = [
      aws_s3_bucket.tfstate.arn,
      "${aws_s3_bucket.tfstate.arn}/*",
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

  statement {
    sid     = "AllowCIRoleOnly"
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.tfstate.arn}/*"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.tf_ci.arn]
    }
  }
}
```

## Terraform: DynamoDB locking table

```hcl
resource "aws_dynamodb_table" "tfstate_lock" {
  name         = "myco-tfstate-locks-prod"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.tfstate.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  deletion_protection_enabled = true

  tags = local.common_tags
}
```

## GCS backend

```hcl
terraform {
  backend "gcs" {
    bucket = "myco-tfstate-prod"
    prefix = "payments"
  }
}

resource "google_storage_bucket" "tfstate" {
  name                        = "myco-tfstate-prod"
  location                    = "US-WEST1"
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.tfstate.id
  }

  logging {
    log_bucket = google_storage_bucket.tfstate_access_logs.name
  }

  lifecycle_rule {
    condition { num_newer_versions = 30 }
    action { type = "Delete" }
  }
}
```

## HCP Terraform / Terraform Cloud workspace

```hcl
resource "tfe_workspace" "payments" {
  name              = "payments-prod"
  organization      = "myco"
  execution_mode    = "remote"  # remote execution; state stored in TFC
  terraform_version = "1.12.0"

  tag_names = ["payments", "production"]
}

resource "tfe_team_access" "payments_writers" {
  team_id      = data.tfe_team.platform.id
  workspace_id = tfe_workspace.payments.id
  access       = "write"
}
```

## What the L2 review verifies

- Remote backend (no local `terraform.tfstate` files).
- Backend storage encrypted (CMK for restricted state).
- Backend access restricted to named CI / break-glass principals.
- State locking configured (DynamoDB for S3 backend; native for
  GCS; lease for Azure; managed-platform locking).
- Versioning enabled with appropriate retention.
- Access logging emitted to a separate, restricted destination.
- Bootstrap procedure documented.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
