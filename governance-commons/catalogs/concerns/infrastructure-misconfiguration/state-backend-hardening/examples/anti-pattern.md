<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.state-backend-hardening state-backend hardening (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.state-backend-hardening.

## Anti-pattern 1: Local state committed to the repository

```
# Bad: terraform.tfstate in the repository

$ git ls-files | grep tfstate
terraform.tfstate
terraform.tfstate.backup
```

```hcl
# Bad: no backend block; defaults to local
terraform {
  # backend block absent; state stored locally
}
```

**Why it matters:** `terraform.tfstate` contains every resource's
configuration, often including database passwords, ARNs of
internal-only resources, and principal identities. Committed to
a repository, the state file is visible to anyone with read
access; pushed to a public repository it is visible to the
world. The substrate forbids local state for any non-ephemeral
workspace.

## Anti-pattern 2: Backend without encryption

```hcl
terraform {
  backend "s3" {
    bucket  = "tfstate-prod"
    key     = "payments/terraform.tfstate"
    region  = "us-west-2"
    encrypt = false  # explicit disablement
  }
}
```

**Why it matters:** Unencrypted state files at rest are
plaintext on the backend storage. The substrate requires
encryption at the tier the consumer's classification matrix
specifies (CMK for restricted classification).

## Anti-pattern 3: Backend without locking

```hcl
terraform {
  backend "s3" {
    bucket = "tfstate-prod"
    key    = "payments/terraform.tfstate"
    region = "us-west-2"
    # dynamodb_table absent; no locking
  }
}
```

**Why it matters:** Concurrent `terraform apply` runs without
locking corrupt state: two engineers apply simultaneously, the
later write overwrites the earlier. Recovery requires
restoring an older version from the backend's versioning, which
the next anti-pattern shows missing. Substrate-required: a
DynamoDB lock table for S3 backends; native locking elsewhere.

## Anti-pattern 4: Backend without versioning

```hcl
resource "aws_s3_bucket" "tfstate" {
  bucket = "tfstate-prod"
}

# No aws_s3_bucket_versioning resource
```

**Why it matters:** State corruption, accidental
`terraform destroy`, or malicious modification is unrecoverable
without versioning. Substrate-required: versioning enabled
with at least 30 days of retention for old versions.

## Anti-pattern 5: Backend bucket publicly accessible or with public-access-block missing

```hcl
resource "aws_s3_bucket" "tfstate" {
  bucket = "tfstate-prod"
}

# No public-access-block, no bucket policy denying * principal
```

**Why it matters:** The state file routinely contains secrets;
public exposure is a critical disclosure. Overlaps with
infrastructure-misconfiguration.no-public-access-without-tag detection. Substrate-required: explicit
`aws_s3_bucket_public_access_block` with all four flags true,
plus a bucket policy denying non-CI access.

## Anti-pattern 6: Wide-open backend access policy

```hcl
data "aws_iam_policy_document" "tfstate_open" {
  statement {
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.tfstate.arn,
      "${aws_s3_bucket.tfstate.arn}/*",
    ]
    principals {
      type        = "AWS"
      identifiers = ["*"]  # bad
    }
  }
}
```

**Why it matters:** Wildcard principal on the state bucket
allows any IAM principal in the account (or any account if the
wildcard means anything) to read or write state. Substrate-
required: specific CI role and break-glass role only.

## Anti-pattern 7: Production backend without bootstrap documentation

```
# Bad: no docs/bootstrap.md, no separate bootstrap module
# State is created somehow but the procedure is in someone's
# memory; if the bucket is lost, recovery requires reconstruction.
```

**Why it matters:** The state backend is itself infrastructure.
If the bucket is deleted, the lock table corrupted, or the KMS
key disabled, recovery requires knowing how the backend was
bootstrapped. Substrate-required: a documented bootstrap
procedure exercisable in disaster recovery.

## How each anti-pattern is reviewed

The L2 review surfaces these via inspection of backend
configuration and the supporting IaC for the backend storage.
Static analysis is partial here (the backend configuration is
typically in `backend.tf`); manual review per the infrastructure-misconfiguration.state-backend-hardening
checklist's eight questions is the primary detection.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired `state-backend-hardening-good.md`
example.
