<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.encryption-per-class encryption per class (anti-pattern)

Substrate-original illustration.

```hcl
# Confidential data in a store with encryption disabled and plaintext allowed.
resource "aws_db_instance" "customer_data" {
  storage_encrypted = false           # at-rest encryption off
  tags = {
    data-sensitivity = "confidential"
  }
  # no rds.force_ssl: plaintext connections permitted
}
```

## Why this violates the rule

The store holds confidential data but has at-rest encryption disabled and
permits plaintext connections, so the data is exposed by any backup leak or
disk disposal and readable on any network path it crosses. The
data-sensitivity tag declares the class, but the encryption does not meet what
that class requires. Enabling at-rest encryption with a managed key and
forcing TLS is the fix.
