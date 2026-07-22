<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.retention-policy retention policy (good patterns)

## Pattern A: Documented retention policy with bands

```markdown
# /docs/security/log-retention-policy.md

## Retention bands

| Stream class    | Hot tier  | Warm tier | Cold tier | Disposition |
|-----------------|-----------|-----------|-----------|-------------|
| Operational     | 7 days    | 23 days   | none      | delete      |
| Application     | 14 days   | 76 days   | none      | delete      |
| Audit (auth)    | 30 days   | 11 months | 12 months | archive     |
| Audit (admin)   | 30 days   | 11 months | 6 years   | archive     |
| Payment-PCI     | 90 days   | 12 months | 6 years   | archive     |

## Drivers

- Audit (auth, admin) at 13 months satisfies PCI DSS 10.5.1
  (12 months minimum) plus a buffer for late-arriving audit
  needs.
- Admin audit at 7 years total satisfies SOX-driven retention
  for financial-system administrative actions.
- Payment-PCI at 7 years total satisfies PCI DSS audit-trail
  retention plus the consumer's contractual data-retention
  obligations.

## Review cadence

Substrate-recommended quarterly review; retention amendments
follow Charter Article IX procedures.
```

Why this satisfies logging.retention-policy: a written policy with per-band
retention, documented drivers, and a review cadence.

## Pattern B: AWS CloudWatch Logs retention via Terraform

```hcl
resource "aws_cloudwatch_log_group" "operational" {
  name              = "/app/operational"
  retention_in_days = 30
  tags = {
    band     = "operational"
    policy_ref = "log-retention-policy:v1.2"
  }
}

resource "aws_cloudwatch_log_group" "application" {
  name              = "/app/application"
  retention_in_days = 90
  tags = {
    band     = "application"
    policy_ref = "log-retention-policy:v1.2"
  }
}

resource "aws_cloudwatch_log_group" "audit" {
  name              = "/app/audit"
  retention_in_days = 400  # 13 months
  tags = {
    band     = "audit"
    policy_ref = "log-retention-policy:v1.2"
  }
}
```

Why this satisfies logging.retention-policy: per-stream retention is
configured by IaC and tagged with the policy reference. Drift
detection is straightforward (Terraform plan output reveals
unauthorized changes).

## Pattern C: Elastic ILM policy for tiered retention

```json
{
  "policy": {
    "phases": {
      "hot": { "min_age": "0ms", "actions": {
        "rollover": { "max_age": "7d", "max_size": "50gb" }
      }},
      "warm": { "min_age": "7d", "actions": {
        "shrink": { "number_of_shards": 1 },
        "forcemerge": { "max_num_segments": 1 }
      }},
      "cold": { "min_age": "30d", "actions": {
        "freeze": {}
      }},
      "delete": { "min_age": "90d", "actions": {
        "delete": {}
      }}
    }
  }
}
```

Why this satisfies logging.retention-policy: Elastic ILM expresses the
retention bands as policy phases. The application stream
moves through hot, warm, cold, and delete based on age.

## Pattern D: Quarterly drift detection job

```bash
#!/usr/bin/env bash
# Substrate-recommended quarterly retention check
set -eu

POLICY_FILE=/docs/security/log-retention-policy.yaml
DRIFT_REPORT=/tmp/retention-drift.txt
: > "${DRIFT_REPORT}"

while IFS=$'\t' read -r stream_name expected_days; do
  actual_days=$(aws logs describe-log-groups \
    --log-group-name-prefix "${stream_name}" \
    --query "logGroups[0].retentionInDays" --output text)
  if [ "${actual_days}" != "${expected_days}" ]; then
    echo "DRIFT: ${stream_name} expected=${expected_days} actual=${actual_days}" \
      >> "${DRIFT_REPORT}"
  fi
done < <(python3 extract-streams-from-policy.py "${POLICY_FILE}")

if [ -s "${DRIFT_REPORT}" ]; then
  echo "Retention drift detected, see ${DRIFT_REPORT}"
  exit 1
fi
```

Why this satisfies logging.retention-policy: the drift check compares
configured retention to documented policy; findings produce
remediation.

## Cross-reference

- Anti-patterns: examples/logging/retention-policy-anti-pattern.md
- Substrate rule: logging.retention-policy
- Review checklist: checklist.md
