<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.encryption-per-class encryption per class (good pattern)

Substrate-original illustration.

```hcl
# A restricted-class store with at-rest encryption enabled and TLS enforced.
resource "aws_db_instance" "health_records" {
  storage_encrypted = true
  kms_key_id        = aws_kms_key.health.arn   # managed key per policy
  tags = {
    data-sensitivity = "restricted"
  }
}

resource "aws_db_parameter_group" "health" {
  parameter {
    name  = "rds.force_ssl"     # reject plaintext connections
    value = "1"
  }
}
```

## Why this satisfies the rule

The store holding restricted data has at-rest encryption enabled with a
policy-managed KMS key, and plaintext connections are rejected so data
crosses only TLS. The data-sensitivity tag binds the store to its class, and
the encryption meets the standard the restricted class requires.
