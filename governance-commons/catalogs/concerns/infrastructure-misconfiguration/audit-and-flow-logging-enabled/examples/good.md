<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.audit-and-flow-logging-enabled audit and flow logging enabled (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.audit-and-flow-logging-enabled. Each
shows the substrate's pattern of declaring audit and flow logging
at the IaC source on cloud resources that support it.

## Terraform: CloudTrail multi-region trail with log file validation

```hcl
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "cloudtrail-logs-${data.aws_caller_identity.current.account_id}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {
  bucket                  = aws_s3_bucket.cloudtrail_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.logs.arn
    }
  }
}

resource "aws_cloudtrail" "account" {
  name                          = "account-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  is_organization_trail         = false
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.logs.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::*/*"]  # all S3 objects
    }
  }

  tags = local.common_tags
}
```

## Terraform: VPC Flow Logs to CloudWatch

```hcl
resource "aws_flow_log" "vpc" {
  vpc_id          = aws_vpc.main.id
  log_destination = aws_cloudwatch_log_group.vpc_flow.arn
  iam_role_arn    = aws_iam_role.vpc_flow.arn
  traffic_type    = "ALL"

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/aws/vpc/flow/${aws_vpc.main.id}"
  retention_in_days = 90  # cross-references logging.retention-policy retention
  kms_key_id        = aws_kms_key.logs.arn
  tags              = local.common_tags
}
```

## Terraform: ALB access logs and RDS audit logs

```hcl
resource "aws_lb" "app" {
  name               = "app-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  access_logs {
    bucket  = aws_s3_bucket.lb_access_logs.bucket
    prefix  = "app-alb"
    enabled = true
  }

  tags = local.common_tags
}

resource "aws_db_instance" "payments" {
  identifier        = "payments"
  engine            = "postgres"
  instance_class    = "db.t4g.large"
  allocated_storage = 100

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  performance_insights_enabled = true
  monitoring_interval          = 60

  tags = local.common_tags
}
```

## Terraform: EKS audit logging enabled

```hcl
resource "aws_eks_cluster" "main" {
  name     = "production"
  role_arn = aws_iam_role.eks.arn

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler",
  ]

  vpc_config {
    subnet_ids              = aws_subnet.private[*].id
    endpoint_public_access  = false
    endpoint_private_access = true
  }
}
```

## Azure: Activity Log diagnostic setting

```hcl
resource "azurerm_log_analytics_workspace" "audit" {
  name                = "audit-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 90
  tags                = local.common_tags
}

resource "azurerm_monitor_diagnostic_setting" "subscription_activity" {
  name                       = "subscription-activity-log"
  target_resource_id         = data.azurerm_subscription.current.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.audit.id

  enabled_log { category = "Administrative" }
  enabled_log { category = "Security" }
  enabled_log { category = "ServiceHealth" }
  enabled_log { category = "Alert" }
  enabled_log { category = "Recommendation" }
  enabled_log { category = "Policy" }
  enabled_log { category = "Autoscale" }
  enabled_log { category = "ResourceHealth" }
}
```

## GCP: Cloud Audit Logs at project level

```hcl
resource "google_project_iam_audit_config" "all_services" {
  project = var.project_id
  service = "allServices"

  audit_log_config { log_type = "ADMIN_READ" }
  audit_log_config { log_type = "DATA_READ" }
  audit_log_config { log_type = "DATA_WRITE" }
}

resource "google_compute_subnetwork" "private" {
  name          = "private-subnet"
  ip_cidr_range = "10.0.1.0/24"
  network       = google_compute_network.main.id
  region        = "us-west1"

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}
```

## What the L1 binding catches in PR review

- AWS accounts whose IaC does not include an `aws_cloudtrail`
  with `is_multi_region_trail = true` and
  `include_global_service_events = true`.
- `aws_vpc` resources without an accompanying `aws_flow_log`.
- `aws_lb` (ALB / NLB) without `access_logs { enabled = true }`.
- `aws_db_instance` whose `enabled_cloudwatch_logs_exports` is
  empty or absent.
- `aws_eks_cluster` whose `enabled_cluster_log_types` excludes
  `"audit"`.
- Azure resources lacking
  `azurerm_monitor_diagnostic_setting`.
- GCP projects without `google_project_iam_audit_config` for
  `ADMIN_READ`, `DATA_READ`, `DATA_WRITE`.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging and cross-reference the logging concern's
logging.retention-policy retention rule.
