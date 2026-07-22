<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.least-privilege-access least-privilege access (good patterns)

Substrate-original good-pattern examples for secrets-management.least-privilege-access.

## Pattern A: Per-secret Vault policy

```hcl
# vault-policies/app-payment-service.hcl
# This policy grants the payment service exactly the
# secrets it needs.

path "secret/data/payment-service/stripe-key" {
  capabilities = ["read"]
}

path "secret/data/payment-service/db-password" {
  capabilities = ["read"]
}

# No wildcards. No write or rotate. No access to other
# services' secrets.
```

Why this satisfies secrets-management.least-privilege-access: explicit per-secret
grants; no blanket access; read-only operations only;
each service has its own policy.

## Pattern B: IAM policy with resource-level scoping (AWS)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:111122223333:secret:prod/payment-service/stripe-key-*",
        "arn:aws:secretsmanager:us-east-1:111122223333:secret:prod/payment-service/db-password-*"
      ]
    }
  ]
}
```

Why this satisfies secrets-management.least-privilege-access: the policy enumerates
specific secret ARNs; the action is limited to
GetSecretValue (no put, no rotate, no delete); the
resource scoping uses the secret's full ARN.

## Pattern C: Workload identity per service (Kubernetes + AWS IRSA)

```yaml
# Each service has its own service account with its own
# IRSA-mapped IAM role. No shared identities.

apiVersion: v1
kind: ServiceAccount
metadata:
  name: payment-service
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/payment-service-role
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: notification-service
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/notification-service-role
```

Why this satisfies secrets-management.least-privilege-access: each service has a
distinct identity; the IAM role per identity has its own
policy; audit logs identify the specific workload that
accessed each secret.

## Pattern D: Just-in-time elevation for human production access

```yaml
# Teleport role definition for break-glass production
# access. Default is no access; humans request elevation.

kind: role
metadata:
  name: prod-secrets-emergency-access
spec:
  options:
    max_session_ttl: 1h
    require_session_mfa: yes
  allow:
    request:
      roles:
        - prod-secrets-read
      thresholds:
        - approve: 2  # two human approvals required
      max_duration: 1h
```

Why this satisfies secrets-management.least-privilege-access: humans have no
standing production secret access. Access is requested,
approved by two reviewers, time-bounded to one hour, and
recorded in the audit log.

## Pattern E: Quarterly access review evidence

```markdown
# /security/access-reviews/2026-Q2-secrets-access-review.md

Date: 2026-04-15
Reviewer: myoung
Scope: All Vault policies and AWS Secrets Manager IAM
       policies in production.

## Findings

1. Service "legacy-reports" has read access to secrets
   it no longer uses (last access 2025-11). Removed.
2. Engineer "X" still has break-glass access from a
   2025-12 incident. Revoked.
3. New service "ml-training" was added without an access
   review. Confirmed via the ADR; access scoped per the
   service's documented needs.

## Outcome
8 policies reviewed; 2 grants revoked; 1 new grant
confirmed; access state is now current.

Next review: 2026-07-15.
```

Why this satisfies secrets-management.least-privilege-access: review is documented,
produces evidence, results in remediation. Access drift
is caught and corrected before it becomes a finding.

## Pattern F: Dynamic database credentials with role-scoped permissions

```hcl
# Vault database role: per-session credential with
# scoped database permissions.

resource "vault_database_secret_backend_role" "app_readonly" {
  backend = vault_database_secrets.postgres.path
  name    = "app-readonly"
  db_name = "production"
  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'",
    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";",
    "GRANT USAGE ON SCHEMA public TO \"{{name}}\";",
  ]
  default_ttl = 3600
  max_ttl     = 7200
}
```

Why this satisfies secrets-management.least-privilege-access: each session gets a
unique database user with role-scoped permissions
(SELECT only, no INSERT/UPDATE/DELETE); credentials
expire automatically; an audit log identifies which
session did what.

## Cross-reference

- Anti-patterns: examples/secrets-management/least-privilege-access-anti-pattern.md
- Substrate rule: secrets-management.least-privilege-access
- Review checklist: checklist.md
