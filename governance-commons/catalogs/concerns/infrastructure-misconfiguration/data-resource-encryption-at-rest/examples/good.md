<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.data-resource-encryption-at-rest data-resource encryption at rest (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.data-resource-encryption-at-rest. Each shows
the substrate-recommended pattern of declaring encryption at rest
explicitly on data-bearing IaC resources, so the encryption posture
is reviewable at IaC source rather than inferred from cloud-provider
defaults that the static analyzer cannot see.

## Terraform: S3, EBS, RDS, DynamoDB with explicit encryption

```hcl
resource "aws_kms_key" "data_at_rest" {
  description             = "Data-at-rest CMK for payments workload"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  tags = local.common_tags
}

resource "aws_kms_alias" "data_at_rest" {
  name          = "alias/payments-data-at-rest"
  target_key_id = aws_kms_key.data_at_rest.key_id
}

resource "aws_s3_bucket" "payments_data" {
  bucket = "payments-data-${var.environment}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "payments_data" {
  bucket = aws_s3_bucket.payments_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.data_at_rest.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_ebs_volume" "app_data" {
  availability_zone = "us-west-2a"
  size              = 100
  encrypted         = true
  kms_key_id        = aws_kms_key.data_at_rest.arn
  tags              = local.common_tags
}

resource "aws_db_instance" "payments" {
  identifier              = "payments"
  engine                  = "postgres"
  instance_class          = "db.t4g.large"
  allocated_storage       = 100
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.data_at_rest.arn
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.data_at_rest.arn
  tags                    = local.common_tags
}

resource "aws_dynamodb_table" "sessions" {
  name           = "payments-sessions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"
  attribute {
    name = "session_id"
    type = "S"
  }
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.data_at_rest.arn
  }
  tags = local.common_tags
}
```

## Kubernetes: StorageClass with explicit encryption parameters

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-csi-encrypted-cmk
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:us-west-2:111122223333:key/abc-def-123"
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
  namespace: payments
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: ebs-csi-encrypted-cmk
  resources:
    requests:
      storage: 50Gi
```

## CloudFormation: S3 + RDS with explicit encryption

```yaml
Resources:
  PaymentsDataKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Payments data-at-rest CMK
      EnableKeyRotation: true
      PendingWindowInDays: 30

  PaymentsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "payments-data-${Environment}"
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !GetAtt PaymentsDataKey.Arn
            BucketKeyEnabled: true

  PaymentsDB:
    Type: AWS::RDS::DBInstance
    Properties:
      Engine: postgres
      DBInstanceClass: db.t4g.large
      AllocatedStorage: 100
      StorageEncrypted: true
      KmsKeyId: !GetAtt PaymentsDataKey.Arn
```

## What the L1 binding catches in PR review

- An `aws_s3_bucket` declared without an accompanying
  `aws_s3_bucket_server_side_encryption_configuration` resource.
- An `aws_ebs_volume` with `encrypted = false` or omitted.
- An `aws_db_instance` with `storage_encrypted = false` or
  omitted, or set true without `kms_key_id` for CMK profiles.
- A Kubernetes StorageClass referencing a CSI driver without an
  `encrypted` parameter, paired with PVCs that bind to it.
- A CloudFormation `AWS::S3::Bucket` without
  `BucketEncryption` Properties.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging; encryption examples without governance tags would
violate infrastructure-misconfiguration.governance-tagging separately.
