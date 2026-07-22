<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.retention-policy retention policy

## Anti-pattern A: No retention configuration

```hcl
resource "aws_cloudwatch_log_group" "application" {
  name = "/app/application"
  # retention_in_days not set
}
```

Why this violates logging.retention-policy: CloudWatch defaults to
indefinite retention when retention_in_days is unset. Cost
accumulates unboundedly; disclosure surface grows with every
retained day. The implicit "never expire" is rarely the
deliberate choice.

## Anti-pattern B: Single retention for all streams

```hcl
locals {
  log_retention = 7  # ← applies to everything
}

resource "aws_cloudwatch_log_group" "operational"  {
  name = "/app/operational"
  retention_in_days = local.log_retention
}
resource "aws_cloudwatch_log_group" "audit" {
  name = "/app/audit"
  retention_in_days = local.log_retention  # ← compliance gap
}
```

Why this violates logging.retention-policy: 7-day retention is far below
PCI DSS 10.5.1 (12 months minimum for audit logs). The audit
stream's retention is wrong for its compliance band. An audit
will surface this finding.

## Anti-pattern C: Retention determined by aggregator default

```javascript
// Datadog API client; no retention argument
const dd = require('datadog-api-client');
dd.LogsApi.submitLog(logEntry);
```

Why this violates logging.retention-policy: the consumer relies on the
aggregator's default retention. If the default changes (the
SaaS vendor changes pricing tier), the consumer's compliance
posture changes silently. The substrate-recommended posture
is explicit retention configuration.

## Anti-pattern D: Retention drift accepted

```
# 2025-03-15: Retention policy authored at 90 days
# 2025-08-20: Aggregator default changed to 30 days during cost cut
# 2025-12-01: Policy still says 90 days; aggregator still at 30
# 2026-04-01: Audit finds 6 months of missing logs
```

Why this violates logging.retention-policy: the policy and configuration
drifted; no periodic verification caught the drift. The
substrate-recommended quarterly check is the explicit
guardrail.

## Anti-pattern E: Multi-year retention without compliance driver

```hcl
resource "aws_cloudwatch_log_group" "debug" {
  name              = "/app/debug"
  retention_in_days = 3650  # ← 10 years for debug logs
}
```

Why this violates logging.retention-policy: debug-level logs retained for
10 years multiply cost and disclosure surface without
operational or compliance benefit. The retention should
match the band's intrinsic value (debug logs: operational
window of days).

## Anti-pattern F: Production retention applied to non-production

```hcl
locals {
  retention_in_days = 400  # ← compliance-driven for production
}

resource "aws_cloudwatch_log_group" "dev_app" {
  name = "/dev/application"
  retention_in_days = local.retention_in_days  # ← unnecessary in dev
}
```

Why this violates logging.retention-policy: dev and staging environments
inherit production retention without justification. The cost
penalty is paid for an environment whose logs have no
compliance significance.

## Cross-reference

- Good patterns: examples/logging/retention-policy-good.md
- Substrate rule: logging.retention-policy
