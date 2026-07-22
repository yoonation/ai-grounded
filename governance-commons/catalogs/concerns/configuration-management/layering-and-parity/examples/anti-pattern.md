<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.layering-and-parity layering and parity (anti-patterns)

Substrate-original anti-pattern example for configuration-management.layering-and-parity. Load order is
undocumented, a key exists only in one environment, and a secret is pasted
into committed configuration.

## Undocumented load order and a missing-in-production key

```yaml
# config.staging.yaml
FEATURE_TIMEOUT: 5
PAYMENTS_BASE_URL: https://payments.staging.internal

# config.production.yaml  (PAYMENTS_BASE_URL was never added here)
FEATURE_TIMEOUT: 5
```

## Secret inlined into committed configuration

```yaml
# config.production.yaml
db_password: "S3cr3t-Pa55w0rd"   # committed credential; reclassify to secrets-management
```

Why this is flagged: the workload "works in staging" and fails in production
on the missing key; the committed secret erodes the secrets-management
boundary. The remediation is a shared required-key schema, a documented
precedence, and a secret reference resolved at runtime.
