<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.encryption-at-rest encryption at rest (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.encryption-at-rest.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Kubernetes Secret without etcd encryption

```yaml
# DO NOT DO THIS - Kubernetes cluster with no
# EncryptionConfiguration. Secret objects are base64-
# encoded but not encrypted in etcd.
apiVersion: v1
kind: Secret
metadata:
  name: prod-db-credentials
data:
  password: cGFzc3dvcmQxMjM=  # base64, not encrypted
```

Why this violates secrets-management.encryption-at-rest: base64 is not
encryption. Anyone with etcd read access (or an etcd
backup) can decode the value. Substrate-recommended
pattern: configure EncryptionConfiguration with a KMS
provider.

## Anti-pattern B: Encryption key in the same configuration file

```yaml
# DO NOT DO THIS - the key that decrypts encrypted_data
# is in the same file.
encryption_key: "0123456789abcdef0123456789abcdef"
encrypted_data: "abc123def456..."  # encrypted with the key above
```

Why this violates secrets-management.encryption-at-rest: key separation is the
defining property of L2-004. Storing the key alongside
the encrypted data means anyone who can read the file
can decrypt the data. Substrate-recommended pattern: key
in a separate KMS with distinct access policy.

## Anti-pattern C: Backup written unencrypted

```bash
# DO NOT DO THIS
vault operator raft snapshot save vault-backup.snap
scp vault-backup.snap backup-host:/backups/
# The snapshot is in plaintext on backup-host. The
# encryption at rest property is defeated.
```

Why this violates secrets-management.encryption-at-rest: a backup is a copy of
the encrypted data; if the copy is plaintext, the
encryption property is gone. Substrate-recommended:
encrypt the backup at rest in its destination, with a
KMS-held key separate from the production data.

## Anti-pattern D: Single key for both KEK and DEK

```python
# DO NOT DO THIS
def encrypt(plaintext: bytes, key: bytes) -> bytes:
    # Same key used for everything. No envelope, no
    # per-operation freshness.
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, plaintext, None)
```

Why this violates secrets-management.encryption-at-rest (envelope encryption
property): a single long-lived key encrypting all
secrets means a single compromise compromises everything.
Substrate-recommended pattern: per-operation DEK,
wrapped by a KEK held in KMS.

## Anti-pattern E: KMS access policy too broad

```json
{
  "Effect": "Allow",
  "Action": ["kms:Decrypt"],
  "Principal": {
    "AWS": "arn:aws:iam::111122223333:root"
  },
  "Resource": "*"
}
```

Why this violates secrets-management.encryption-at-rest (in spirit): granting
kms:Decrypt to the account root means every principal in
the account can decrypt. The KMS key policy should
enumerate specific services or roles, not the account
root.

## Anti-pattern F: Region mismatch creates failover risk

```text
# Secrets stored in us-east-1
# KMS key in us-west-2
# When us-east-1 is degraded but us-west-2 is not, secrets
# cannot be accessed because of region-crossing failure
# modes in the KMS-Secrets-Manager interaction.
```

Why this violates secrets-management.encryption-at-rest (operational property):
key and data should be deliberately co-located or
deliberately separated based on failover plan. Accidental
cross-region setups produce unexpected unavailability.
Substrate-recommended pattern: explicit region planning
in the consumer's MADR.

## Anti-pattern G: KMS audit logging disabled

```text
# AWS CloudTrail not configured to capture KMS events.
# Decryption operations on the secrets KEK are not
# visible to security operations.
```

Why this violates secrets-management.encryption-at-rest (in spirit): visibility
into KMS usage is part of the L2-004 property. Without
audit, abuse of KMS access cannot be detected.
Substrate-recommended pattern: enable CloudTrail (or
equivalent) for the KMS service; flow the events to the
security log aggregator.

## Anti-pattern H: Hardcoded encryption with weak algorithm

```python
# DO NOT DO THIS
from Crypto.Cipher import DES  # DEPRECATED

def encrypt(plaintext: bytes) -> bytes:
    cipher = DES.new(b"weakkey1", DES.MODE_ECB)
    return cipher.encrypt(pad(plaintext, DES.block_size))
```

Why this violates secrets-management.encryption-at-rest (cryptographic property):
DES is deprecated; ECB mode reveals plaintext patterns;
the key is hardcoded. Substrate-recommended pattern:
AES-256-GCM via a vetted library; key from KMS.

## Cross-reference

- Good patterns: examples/secrets-management/encryption-at-rest-good.md
- Substrate rule: secrets-management.encryption-at-rest
- Review checklist: checklist.md
