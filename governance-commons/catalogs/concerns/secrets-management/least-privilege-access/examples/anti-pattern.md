<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.least-privilege-access least-privilege access (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.least-privilege-access.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Blanket read on all secrets

```hcl
# DO NOT DO THIS
path "secret/data/*" {
  capabilities = ["read"]
}
```

Why this violates secrets-management.least-privilege-access: the wildcard grants
read on every secret in the namespace. A workload needing
one secret has access to all. Substrate-recommended
pattern: enumerate specific paths or use a tight prefix
that matches only this workload's needs.

## Anti-pattern B: Shared service account across workloads

```yaml
# DO NOT DO THIS
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-services-shared
  # Used by payment-service, notification-service,
  # ml-training, and 12 other services.
```

Why this violates secrets-management.least-privilege-access: a shared identity
means audit logs cannot distinguish which workload
accessed which secret. A compromise of any one workload
exposes every secret accessible to the shared identity.
Substrate-recommended pattern: one identity per workload.

## Anti-pattern C: Write capability granted by default

```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:*",
  "Resource": "arn:aws:secretsmanager:*:111122223333:secret:prod/*"
}
```

Why this violates secrets-management.least-privilege-access: `secretsmanager:*`
grants put, delete, rotate, and update in addition to
read. A consumer workload should have GetSecretValue
only. Substrate-recommended pattern: enumerate read-only
actions explicitly.

## Anti-pattern D: Engineers with standing production access

```text
# IAM group: production-engineers
Members: 12 people (the whole team)
Policy: AdministratorAccess on production account
```

Why this violates secrets-management.least-privilege-access: standing access to
production means every engineer's compromised credential
or laptop equals production credential compromise.
Substrate-recommended pattern: no standing human access;
just-in-time elevation with MFA and dual approval for
break-glass.

## Anti-pattern E: Same identity across environments

```yaml
# DO NOT DO THIS
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payment-service
# Used in dev, staging, AND prod with the same IRSA role
# that has access to all three environments' secrets.
```

Why this violates secrets-management.least-privilege-access: a single identity
spanning environments defeats environment isolation. A
dev pod compromise can read production secrets.
Substrate-recommended pattern: per-environment
identities with environment-scoped policies.

## Anti-pattern F: Long-lived "emergency access" credential never revoked

```text
# 2024-03-15: emergency access created for engineer X
# during prod incident. TTL: indefinite.
# 2026-05-20: still active. Engineer X has not used it
# in 14 months. No periodic review revoked it.
```

Why this violates secrets-management.least-privilege-access: emergency-access
credentials should be time-bounded; if they aren't, the
"emergency" became standing access. Substrate-recommended
pattern: just-in-time access with platform-enforced
expiration.

## Anti-pattern G: Database credentials shared across applications

```text
# Single database user "app_user" used by:
- payment-service
- notification-service
- analytics-pipeline
- batch-jobs
- legacy-reports
# All authenticate to the database with the same
# credential.
```

Why this violates secrets-management.least-privilege-access: database audit logs
cannot identify which application performed any
particular query. A compromise of one application
exposes the same credential everywhere. Substrate-
recommended pattern: per-application database users or
dynamic secrets with role-scoped permissions.

## Anti-pattern H: Access review never conducted

```text
# Secrets platform access policy was last reviewed 2024-09.
# Many grants since then are for projects that no longer
# exist, contractors who have left, or services that have
# been retired.
```

Why this violates secrets-management.least-privilege-access: without periodic
review, access drift accumulates. Substrate-recommended
pattern: quarterly review with documented findings and
remediation; revoke access that has not been used in a
defined window.

## Cross-reference

- Good patterns: examples/secrets-management/least-privilege-access-good.md
- Substrate rule: secrets-management.least-privilege-access
- Review checklist: checklist.md
