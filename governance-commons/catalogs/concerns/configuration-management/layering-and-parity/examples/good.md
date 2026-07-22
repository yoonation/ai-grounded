<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.layering-and-parity layering and parity (good patterns)

Substrate-original good-pattern example for configuration-management.layering-and-parity. Precedence is
documented and implemented, the required-key set is shared across
environments, and secrets are referenced by indirection.

## Documented precedence (recorded in the configuration ADR)

```
defaults  <  base config file  <  environment-specific file  <  environment variables  <  explicit overrides
```

## Shared required-key schema enforced across environments

```yaml
# required-keys.yaml: the single source of truth for required keys
required:
  - DB_HOST
  - PAYMENTS_BASE_URL
  - HTTP_TIMEOUT_SECONDS
```

## Secret referenced, not inlined

```yaml
# config.production.yaml
db_password_ref: "vault://secret/payments/db#password"   # reference, resolved at runtime
```

Environment-specific files set only the values that legitimately differ; the
parity check fails CI if any environment omits a required key.
