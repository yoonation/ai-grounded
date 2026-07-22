<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.encryption-at-rest encryption at rest (good patterns)

Substrate-original good-pattern examples for secrets-management.encryption-at-rest.

## Pattern A: AWS Secrets Manager with customer-managed KMS key

```hcl
resource "aws_kms_key" "secrets_kek" {
  description             = "KEK for production secrets"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  policy = jsonencode({
    Statement = [{
      Sid    = "AllowSecretsManagerUse"
      Effect = "Allow"
      Principal = {
        Service = "secretsmanager.amazonaws.com"
      }
      Action   = ["kms:Decrypt", "kms:GenerateDataKey"]
      Resource = "*"
    }]
  })
}

resource "aws_secretsmanager_secret" "prod_secret" {
  name       = "prod/payment-service/stripe-key"
  kms_key_id = aws_kms_key.secrets_kek.arn
}
```

Why this satisfies secrets-management.encryption-at-rest: customer-managed KMS
key (not the AWS-managed default); annual key rotation
enabled; key policy enumerates Secrets Manager as the
allowed user; the KMS key and the secret are
separately controllable via distinct IAM policies.

## Pattern B: Kubernetes etcd encryption with KMS provider

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - kms:
          name: aws-kms
          endpoint: unix:///var/run/kmsplugin/socket.sock
          cachesize: 1000
          timeout: 3s
      - identity: {}  # fallback only during migration
```

Why this satisfies secrets-management.encryption-at-rest: Kubernetes Secret
objects are encrypted at rest in etcd using an external
KMS provider. The KMS key is held by AWS KMS, separate
from etcd's storage. Without the KMS key, etcd snapshots
are unreadable.

## Pattern C: Vault with auto-unseal via cloud KMS

```hcl
# Vault configuration
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "arn:aws:kms:us-east-1:111122223333:key/abc-123"
}

storage "s3" {
  bucket = "vault-storage-prod"
  region = "us-east-1"
  # Server-side encryption applied via the bucket policy
  # with a separate KMS key.
}
```

Why this satisfies secrets-management.encryption-at-rest: Vault's seal key is
held in AWS KMS; Vault's storage is on S3 with separate
KMS-based encryption; the unseal key and the storage
encryption key are distinct keys; loss of either alone
does not compromise secret data.

## Pattern D: Envelope encryption with explicit DEK and KEK

```python
# Application code that demonstrates envelope encryption
# explicitly. Most platforms abstract this; the example
# is for cases where the application performs its own
# encryption (e.g., a custom secret store).

import boto3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class EnvelopeEncryption:
    def __init__(self, kek_id: str):
        self.kms = boto3.client("kms")
        self.kek_id = kek_id

    def encrypt(self, plaintext: bytes) -> tuple[bytes, bytes]:
        # Generate a fresh DEK for this encryption operation
        data_key = self.kms.generate_data_key(
            KeyId=self.kek_id,
            KeySpec="AES_256",
        )
        dek_plaintext = data_key["Plaintext"]
        dek_ciphertext = data_key["CiphertextBlob"]
        # Encrypt the plaintext with the DEK
        aesgcm = AESGCM(dek_plaintext)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        # Return the encrypted-DEK plus the data ciphertext
        return dek_ciphertext, nonce + ciphertext
```

Why this satisfies secrets-management.encryption-at-rest: each encryption
operation uses a fresh DEK; the DEK is encrypted by the
KEK; only the encrypted DEK is stored alongside the
ciphertext. Compromise of stored data without KMS access
yields no plaintext.

## Pattern E: Backup encryption preserved

```bash
# Vault backup procedure: snapshot is encrypted at rest
# in the backup destination.

# Take Vault snapshot
vault operator raft snapshot save vault-backup.snap

# Upload to S3 with customer-managed KMS encryption
aws s3 cp vault-backup.snap \
  s3://vault-backups/$(date +%Y-%m-%d)/vault-backup.snap \
  --sse aws:kms \
  --sse-kms-key-id arn:aws:kms:us-east-1:111122223333:key/backup-kek
```

Why this satisfies secrets-management.encryption-at-rest: the backup is
encrypted in transit (TLS to S3) and at rest (SSE-KMS
with a customer-managed key). The backup KMS key is
separate from the production KMS key so that backup
restoration access is distinct from production access.

## Cross-reference

- Anti-patterns: examples/secrets-management/encryption-at-rest-anti-pattern.md
- Substrate rule: secrets-management.encryption-at-rest
- Review checklist: checklist.md
