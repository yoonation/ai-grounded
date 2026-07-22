<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.audit-and-flow-logging-enabled audit and flow logging enabled (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.audit-and-flow-logging-enabled. Each
shows a common way the rule is violated.

## Anti-pattern 1: Account without CloudTrail in IaC

```hcl
# Bad: account-level IaC has no CloudTrail resource
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# No aws_cloudtrail anywhere; account relies on the 90-day
# CloudTrail Event history visible in the AWS console.
```

**Why it matters:** AWS retains 90 days of management events in
the CloudTrail Event history visible in the console, but
without a configured trail, no long-term storage exists, log
file integrity is not validated, and data events (S3 object
access, Lambda function execution) are not captured. The
substrate requires an explicit, multi-region, log-file-validated
trail.

## Anti-pattern 2: VPC without flow logs

```hcl
# Bad: VPC declared without aws_flow_log
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = local.common_tags
}

resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = "us-west-2${["a","b","c"][count.index]}"
}
# No aws_flow_log resource targeting the VPC
```

**Why it matters:** VPC Flow Logs are the only source of truth
for network-layer activity in AWS. Absent flow logs, no
network-side forensics is possible after an incident; lateral
movement, exfiltration, and connection patterns are invisible.
The substrate requires flow logs on every VPC.

## Anti-pattern 3: Load balancer without access logs

```hcl
# Bad: ALB without access_logs block
resource "aws_lb" "app" {
  name               = "app"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  # No access_logs block
}
```

**Why it matters:** Load balancer access logs are the
application-edge audit trail; absent them, no record exists of
what requests reached the application. The substrate requires
access logs on every public-facing load balancer.

## Anti-pattern 4: RDS without audit log exports

```hcl
# Bad: RDS without cloudwatch_logs_exports
resource "aws_db_instance" "main" {
  identifier        = "main"
  engine            = "postgres"
  instance_class    = "db.t4g.large"
  allocated_storage = 100
  # enabled_cloudwatch_logs_exports absent
  # performance_insights_enabled absent
}
```

**Why it matters:** Without cloudwatch_logs_exports, RDS audit
events stay inside the database; they do not reach the
substrate's logging surface (logging.retention-policy retention does not
apply because no logs are emitted). The substrate requires
`postgresql`, `upgrade`, or engine-equivalent log types exported
for production databases.

## Anti-pattern 5: EKS cluster without audit log type

```hcl
# Bad: EKS without audit log type
resource "aws_eks_cluster" "main" {
  name     = "production"
  role_arn = aws_iam_role.eks.arn

  enabled_cluster_log_types = ["api"]  # audit missing

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}
```

**Why it matters:** EKS audit logs are the only record of every
kubectl verb and every controller action. Absent audit logs,
no record exists of who created, modified, or deleted Kubernetes
resources. The substrate requires `"audit"` in
`enabled_cluster_log_types` at minimum (substrate-recommended
set: `api`, `audit`, `authenticator`).

## Anti-pattern 6: Azure subscription without diagnostic settings

```hcl
# Bad: subscription with no Activity Log diagnostic setting
resource "azurerm_resource_group" "main" {
  name     = "company-prod"
  location = "westus2"
  tags     = local.common_tags
}

# No azurerm_monitor_diagnostic_setting targeting the subscription
```

**Why it matters:** Azure Activity Log retains events for 90
days by default, but without a diagnostic setting routing the
log to Log Analytics or Storage, no long-term retention,
integration with downstream tools, or alerting is possible. The
substrate requires the diagnostic setting at subscription scope.

## Anti-pattern 7: GCP project with only default audit logs

```hcl
# Bad: project relying on default ADMIN_READ audit logs only;
# DATA_READ and DATA_WRITE not enabled
provider "google" {
  project = var.project_id
}

# No google_project_iam_audit_config explicitly enabling
# DATA_READ and DATA_WRITE
```

**Why it matters:** GCP enables ADMIN_READ by default but
DATA_READ and DATA_WRITE require explicit configuration. Absent
these, data-access events (object reads from GCS, table reads
from BigQuery) are not logged; the substrate's bias is full
data-access audit at production tier.

## How each anti-pattern is detected

- Anti-pattern 1: Checkov CKV_AWS_67, CKV_AWS_36; Trivy
  cloudtrail-enabled-all-regions.
- Anti-pattern 2: Checkov CKV_AWS_9; Trivy vpc-flow-logs-enabled.
- Anti-pattern 3: Checkov CKV_AWS_91, CKV_AWS_150; Trivy
  alb-access-logs-enabled.
- Anti-pattern 4: Checkov CKV_AWS_157, CKV_AWS_118.
- Anti-pattern 5: Checkov CKV_AWS_38.
- Anti-pattern 6: Checkov CKV_AZURE_37, CKV_AZURE_38.
- Anti-pattern 7: Checkov CKV_GCP_71, CKV_GCP_73.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`audit-and-flow-logging-enabled-good.md` example.
