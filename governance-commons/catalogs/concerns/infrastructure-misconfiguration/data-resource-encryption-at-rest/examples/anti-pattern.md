<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.data-resource-encryption-at-rest data-resource encryption at rest (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.data-resource-encryption-at-rest. Each
shows a common way the rule is violated and explains why the
violation matters even when provider defaults appear to cover
the gap.

## Anti-pattern 1: Encryption attribute omitted entirely

```hcl
# Bad: no encryption configuration in IaC source
resource "aws_s3_bucket" "data" {
  bucket = "data-${var.environment}"
}

resource "aws_ebs_volume" "app" {
  availability_zone = "us-west-2a"
  size              = 100
  # encrypted attribute absent
}

resource "aws_db_instance" "main" {
  identifier        = "main"
  engine            = "postgres"
  instance_class    = "db.t4g.large"
  allocated_storage = 100
  # storage_encrypted attribute absent
}
```

**Why it matters:** Even where the cloud-provider account default
enables encryption (AWS account-default EBS encryption since
2023; S3 default SSE-S3), the IaC source does not declare the
intent. Two consequences follow: (1) the substrate's static
analysis cannot determine encryption posture from source alone,
and (2) account-default changes apply only at resource creation
time, so reverting an account-default leaves existing resources
unaffected without a re-creation. The substrate requires
declaration in source.

## Anti-pattern 2: Encryption explicitly disabled

```hcl
# Bad: encryption explicitly disabled
resource "aws_ebs_volume" "app" {
  availability_zone = "us-west-2a"
  size              = 100
  encrypted         = false  # explicit disablement
}

resource "aws_dynamodb_table" "sessions" {
  name         = "sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"
  attribute {
    name = "session_id"
    type = "S"
  }
  server_side_encryption {
    enabled = false  # explicit disablement
  }
}
```

**Why it matters:** Explicit disablement is the same finding as
omission from the L1 rule's perspective; the substrate treats
both as violations. The motivation for disablement is sometimes
performance (a misconception: KMS-CMK encryption has measurable
but small latency cost; SSE-S3 and provider-managed keys have
no measurable latency cost). The substrate's bias is
encryption-on; performance exceptions require an infrastructure-misconfiguration.key-management-design
review documenting the trade-off.

## Anti-pattern 3: Encryption enabled without CMK on a regulated profile

```hcl
# Bad in regulated profile: provider-managed key on PHI data
resource "aws_s3_bucket" "phi_records" {
  bucket = "phi-records-prod"
  tags = {
    data-sensitivity = "restricted"  # PHI
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "phi_records" {
  bucket = aws_s3_bucket.phi_records.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"  # SSE-S3, provider-managed key
    }
  }
}
```

**Why it matters:** Under a regulated profile (HIPAA, FedRAMP),
data with `data-sensitivity = restricted` typically requires
customer-managed key (CMK) encryption per the consumer's
classification-to-key-tier matrix. SSE-S3 (provider-managed)
satisfies infrastructure-misconfiguration.data-resource-encryption-at-rest mechanically but violates infrastructure-misconfiguration.key-management-design's
key-management design review at regulated tier. The infrastructure-misconfiguration.key-management-design
checklist's Question 1 catches this.

## Anti-pattern 4: Kubernetes PVC without encrypted StorageClass

```yaml
# Bad: StorageClass without encryption parameters
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard-ebs
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  # encrypted parameter absent
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: standard-ebs
  resources:
    requests:
      storage: 50Gi
```

**Why it matters:** The CSI driver provisions an unencrypted
EBS volume because the StorageClass does not request encryption
even though AWS account-default would otherwise encrypt EBS at
creation. The CSI driver's `encrypted: "true"` parameter is the
substrate-required declaration.

## Anti-pattern 5: Encryption enabled at create time only

```hcl
# Bad: relying on account-default for encryption posture
provider "aws" {
  region = "us-west-2"
  # No explicit default-encryption declaration; relies on
  # account-level ec2_default_encryption being enabled.
}

resource "aws_ebs_volume" "app" {
  availability_zone = "us-west-2a"
  size              = 100
  # encrypted attribute absent; relies on account default
}
```

**Why it matters:** Account-default encryption is a deploy-time
flag that can be changed without affecting existing resources;
the IaC source has no record of the assumption. The substrate
requires the IaC source to declare the intent explicitly.

## How each anti-pattern is detected

- Anti-patterns 1, 2, 5: Checkov CKV_AWS_*_ENCRYPTION rule
  family, Trivy AVD-AWS-*-ENCRYPTION, terrascan AC_AWS_*
  encryption policies, Semgrep terraform.aws.security.aws-*-
  unencrypted family.
- Anti-pattern 3: requires CMK-tier policy added to the
  consumer's policy library per infrastructure-misconfiguration.key-management-design (the substrate's
  L1 surface does not detect CMK requirements; that is L2).
- Anti-pattern 4: Checkov CKV_K8S_* encryption family,
  Trivy AVD-KUBERNETES, kube-linter encryption checks.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`data-resource-encryption-at-rest-good.md` example.
