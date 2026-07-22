<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.integrity log integrity (good patterns)

## Pattern A: AWS CloudWatch Logs to S3 with object-lock

```hcl
resource "aws_s3_bucket" "audit_logs" {
  bucket = "myorg-audit-logs"
  object_lock_enabled = true
}

resource "aws_s3_bucket_object_lock_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    default_retention {
      mode = "COMPLIANCE"  # ← prevents deletion until expiry
      days = 400           # 13 months
    }
  }
}

resource "aws_cloudwatch_log_subscription_filter" "audit_to_s3" {
  name            = "audit-archival"
  log_group_name  = aws_cloudwatch_log_group.audit.name
  filter_pattern  = ""
  destination_arn = aws_lambda_function.export_to_s3.arn
}
```

Why this satisfies logging.integrity: audit logs are exported to S3
with object-lock in COMPLIANCE mode; the lock prevents
deletion or modification even by the AWS root account until
the retention expires. Tampering is structurally impossible
during the retention window.

## Pattern B: GCP Cloud Logging bucket with retention lock

```hcl
resource "google_logging_project_bucket_config" "audit" {
  project        = var.project_id
  location       = "us"
  retention_days = 400
  locked         = true  # ← retention cannot be reduced
  bucket_id      = "audit-bucket"
}
```

Why this satisfies logging.integrity: GCP's locked retention prevents
the retention period from being reduced. Combined with the
project IAM separation, this provides the substrate's
append-only integrity guarantee.

## Pattern C: Hash chain with external publication

```python
import hashlib
import requests

class HashChainAppender:
    def __init__(self, attestation_url):
        self.prev_hash = "0" * 64
        self.attestation_url = attestation_url

    def append(self, record_bytes):
        h = hashlib.sha256(self.prev_hash.encode() + record_bytes).hexdigest()
        record_with_hash = {
            "record": record_bytes.decode(),
            "chain_hash": h,
            "prev_hash": self.prev_hash,
        }
        emit_record(record_with_hash)
        self.prev_hash = h
        return h

    def publish_head(self):
        """Run periodically; publish head to external attestation."""
        requests.post(self.attestation_url, json={"head": self.prev_hash})
```

Why this satisfies logging.integrity: each record's hash incorporates
the previous record's hash; tampering with any past record
invalidates every subsequent hash. Periodic publication of
the chain head to an external service prevents an attacker
with full log-store access from re-computing a tampered
chain undetected.

## Pattern D: SIEM with administrative isolation

```yaml
# IAM separation: SecurityTeam role can read SIEM; AppAdmin cannot
SecurityTeam:
  policies:
    - effect: Allow
      action: ['logs:Get*', 'logs:Describe*', 'logs:FilterLogEvents']
      resource: 'arn:aws:logs:*:siem-account:*'

AppAdminTeam:
  policies:
    - effect: Allow
      action: ['logs:*']
      resource: 'arn:aws:logs:*:app-account:*'
    - effect: Deny
      action: ['logs:*']
      resource: 'arn:aws:logs:*:siem-account:*'
```

Why this satisfies logging.integrity: SIEM is in a separate AWS
account (siem-account) administered by a different team than
the application admins. AppAdmin role has explicit Deny on
SIEM resources. Application admins compromised by attacker
cannot reach the SIEM.

## Pattern E: Signed records via Fluent Bit signing output

```yaml
[OUTPUT]
    Name              http
    Match             audit.*
    Host              audit-collector.internal
    Port              443
    URI               /v1/logs
    Format            json
    tls               on
    tls.verify        on
    # Signing plugin (substrate-acceptable pattern)
    Signing_Algorithm ed25519
    Signing_Key       ${ED25519_PRIVATE_KEY_PATH}
```

Why this satisfies logging.integrity: Fluent Bit signs each batch
of records with Ed25519 before shipping. The collector
verifies the signature at ingestion. Modifying a record
post-shipping invalidates the signature.

## Pattern F: Quarterly verification exercise

```bash
#!/usr/bin/env bash
# Substrate-recommended quarterly integrity verification
set -eu

# Attempt to delete a record from the audit stream;
# expected to fail.
aws s3 rm s3://myorg-audit-logs/2026/04/test-record.json \
  2>&1 | tee /tmp/delete-attempt.log

if grep -q "AccessDenied\|InvalidObjectState" /tmp/delete-attempt.log; then
  echo "PASS: deletion blocked as expected"
else
  echo "FAIL: deletion was not blocked"
  exit 1
fi
```

Why this satisfies logging.integrity: a documented exercise verifies
the protection is configured and functional, not just
documented.

## Cross-reference

- Anti-patterns: examples/logging/integrity-anti-pattern.md
- Substrate rule: logging.integrity
- Review checklist: checklist.md
