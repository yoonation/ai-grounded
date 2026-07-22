<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.integrity log integrity

## Anti-pattern A: Object storage without object-lock

```hcl
resource "aws_s3_bucket" "audit_logs" {
  bucket = "myorg-audit-logs"
  # object_lock_enabled not set
}
```

Why this violates logging.integrity: without object-lock, an
attacker with bucket-delete permission (a compromised
application admin) can delete the audit record showing the
compromise. The audit trail is structurally vulnerable.

## Anti-pattern B: Hash chain stored alongside logs

```python
class LocalHashChain:
    def __init__(self, chain_file="/var/log/chain.txt"):
        self.chain_file = chain_file

    def append(self, record):
        h = hash(record)
        with open(self.chain_file, 'a') as f:
            f.write(h + '\n')
```

Why this violates logging.integrity: the chain head is stored in
the same location as the logs it protects. An attacker who
modifies a log record can recompute the chain to match.
External publication of the chain head is the substrate-
recommended remedy.

## Anti-pattern C: Application admin has SIEM admin access

```yaml
# IAM group nesting
AppAdminGroup:
  members: [alice, bob, carol]
  group_membership:
    - PlatformAdminGroup
    - SIEMAdminGroup  # ← granted via group inheritance
```

Why this violates logging.integrity: through group nesting, the
application admin role inherits SIEM admin privileges. The
administrative separation the SIEM-based integrity model
depends on is fictional.

## Anti-pattern D: Immutability assumed but not configured

```hcl
# Documentation says: "audit logs are immutable"
# Configuration:
resource "aws_cloudwatch_log_group" "audit" {
  name = "/app/audit"
  retention_in_days = 400
  # no object-lock, no SIEM forwarding, no signing
}
```

Why this violates logging.integrity: documentation asserts
immutability that the configuration does not provide.
CloudWatch Logs alone does not prevent application admins
from deleting log groups; the assertion fails the first
attempted destructive operation.

## Anti-pattern E: Drift on immutability flag unnoticed

```
# 2025-03-15: object-lock enabled per Terraform
# 2025-07-22: cost-cut sprint; engineer disables object-lock via
#             console "temporarily" to delete a stuck record
# 2025-07-23: engineer forgets to re-enable
# 2026-04-01: incident; logs found tampered
```

Why this violates logging.integrity: configuration drift on the
integrity flag goes undetected. The substrate-recommended
quarterly drift detection is the explicit guardrail.

## Anti-pattern F: No verification exercise

```
Q1 2025: documented mechanism: object-lock + IAM separation
Q2 2025: no verification performed
Q3 2025: no verification performed
Q4 2025: no verification performed
Q1 2026: audit asks "show me the verification log" - no answer
```

Why this violates logging.integrity: the mechanism is asserted but
never verified to actually function. Auditors flag absence
of evidence; subsequent incident response cannot rely on
the integrity claim.

## Anti-pattern G: Logs in same retention store as audit log of the audit log

```hcl
# Single bucket, single retention, single access policy
resource "aws_s3_bucket" "everything" {
  bucket = "myorg-logs-and-meta"
}
# Both: application logs AND the audit log of who modified
# the application logs' retention configuration
```

Why this violates logging.integrity: the audit log of integrity-
configuration changes is in the same store as the data it
audits. An attacker with bucket access can delete both the
log and the audit of the deletion.

## Cross-reference

- Good patterns: examples/logging/integrity-good.md
- Substrate rule: logging.integrity
