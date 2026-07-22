<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.rotation-policy rotation policy (good patterns)

Substrate-original good-pattern examples for secrets-management.rotation-policy.

## Pattern A: AWS Secrets Manager native rotation

```hcl
resource "aws_secretsmanager_secret" "db_password" {
  name = "prod/db/password"
}

resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.rotate_db_password.arn
  rotation_rules {
    automatically_after_days = 30
  }
}
```

Why this satisfies secrets-management.rotation-policy: rotation is automated
through a Lambda function that AWS Secrets Manager
invokes on schedule. The Lambda performs the four-step
rotation (create new, set new in service, test new,
finalize); the secret's audit log records each rotation.

## Pattern B: HashiCorp Vault dynamic database secrets

```hcl
# Vault database secrets engine: per-session credentials,
# revoked at lease expiry.
path "database/creds/app-role" {
  capabilities = ["read"]
}

# Application receives a fresh credential at each call;
# database revokes when lease ends. Effective rotation
# cadence: every TTL (substrate-recommended ceiling 1h
# for short-lived workloads).
```

Why this satisfies secrets-management.rotation-policy: dynamic secrets engines
treat every retrieval as a fresh credential issuance.
There is no "rotation event" because there is no long-
lived credential to rotate; each lease expires
automatically. This is the strongest form of rotation
discipline.

## Pattern C: Documented rotation inventory

```yaml
# /security/rotation-inventory.yaml
secrets:
  - name: prod/db/password
    class: database-credential
    cadence-days: 30
    automation: aws-secrets-manager-rotation-lambda
    owner: platform-team
    last-rotation-evidence: cloudwatch-log-group:/aws/lambda/rotate-db
  - name: prod/stripe/api-key
    class: third-party-api-key
    cadence-days: 90
    automation: manual-runbook  # Stripe API does not support
                                # automated rotation today
    owner: payments-team
    last-rotation-evidence: jira-ticket-tracker
  - name: prod/jwt-signing-key
    class: signing-key
    cadence-days: 365
    automation: vault-transit-engine
    owner: identity-team
    last-rotation-evidence: vault-audit-log
```

Why this satisfies secrets-management.rotation-policy: every credential class
has a documented cadence, automation status, owner, and
evidence trail. The inventory is queryable; periodic
audits compare actual rotation events to this declaration.

## Pattern D: Dual-key window for application-tier rotation

```python
# Application accepts both old and new credentials during
# a dual-key window. Smooth rotation across rolling deploys.
class CredentialValidator:
    def __init__(self):
        self.current_key = secrets.get("api-key/current")
        self.previous_key = secrets.get("api-key/previous")
        # Both are valid; previous expires after window.

    def validate(self, presented_key: str) -> bool:
        return (presented_key == self.current_key
                or presented_key == self.previous_key)
```

Why this satisfies secrets-management.rotation-policy: rotation operates as
a transition: write the new value to current, move the
old to previous, wait for the configured window, then
clear previous. Applications and downstream consumers
have time to converge without service disruption.

## Pattern E: Compromise-triggered rotation runbook

```markdown
# Runbook: Out-of-band credential rotation
# Trigger: suspected credential compromise

## Step 1: Identify the credential
- Confirm the credential identifier from incident detection
- Locate the credential's entry in the rotation inventory

## Step 2: Initiate emergency rotation
- For AWS-rotated secrets: invoke the rotation Lambda
  manually via `aws secretsmanager rotate-secret`
- For Vault-managed secrets: invoke
  `vault write -force database/rotate-role/<role>`
- For manual-rotation secrets: follow the per-credential
  manual procedure listed in the inventory

## Step 3: Revoke old credential immediately
- Skip the dual-key window for compromise-triggered
  rotation
- Revoke at the issuing system (database REVOKE, API
  provider's revocation endpoint)

## Step 4: Audit usage of the compromised credential
- Query audit logs for retrievals of the credential
- Identify what the credential was used for during the
  exposure window
- Coordinate with incident response on user notification
  and forensic preservation

## Step 5: Document
- File post-incident report including timeline
- Update inventory's last-rotation-evidence
- Schedule tabletop exercise if this procedure was
  novel or not recently exercised
```

Why this satisfies secrets-management.rotation-policy: out-of-band rotation
is treated as a first-class procedure with explicit steps,
not improvised during an incident.

## Cross-reference

- Anti-patterns: examples/secrets-management/rotation-policy-anti-pattern.md
- Substrate rule: secrets-management.rotation-policy
- Review checklist: checklist.md
