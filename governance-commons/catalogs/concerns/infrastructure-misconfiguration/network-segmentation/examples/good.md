<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.network-segmentation network segmentation (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.network-segmentation. Each
shows the substrate's pattern of tiered subnet topology, scoped
east-west traffic, private endpoint routing, and defense-in-depth
for public-by-design surfaces.

## Terraform: Three-tier subnet topology

```hcl
# Public tier: load balancers, NAT, bastion only
resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false  # explicit even though false-default
  tags = merge(local.common_tags, { tier = "public" })
}

# Application tier: workloads, no direct internet
resource "aws_subnet" "app_private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags              = merge(local.common_tags, { tier = "app-private" })
}

# Data tier: databases, caches; no internet path at all
resource "aws_subnet" "data_private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 20}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags              = merge(local.common_tags, { tier = "data-private" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table" "app_private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[0].id
  }
}

resource "aws_route_table" "data_private" {
  vpc_id = aws_vpc.main.id
  # No default route; data tier reaches managed services via
  # VPC endpoints only.
}
```

## Terraform: VPC endpoints for managed services

```hcl
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-west-2.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = concat(
    aws_route_table.app_private[*].id,
    aws_route_table.data_private[*].id,
  )

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = "*"
      Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.payments_data.arn,
        "${aws_s3_bucket.payments_data.arn}/*",
      ]
      Condition = {
        StringEquals = {
          "aws:PrincipalAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

resource "aws_vpc_endpoint" "kms" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.us-west-2.kms"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.app_private[*].id
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
}
```

## Kubernetes: default-deny NetworkPolicy plus scoped allow

```yaml
# Default deny across namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: payments
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# Allow payments-api ingress from istio-ingressgateway only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-api-ingress
  namespace: payments
spec:
  podSelector:
    matchLabels: { app: payments-api }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels: { name: istio-system }
          podSelector:
            matchLabels: { app: istio-ingressgateway }
      ports:
        - port: 8080
          protocol: TCP
---
# Allow payments-api egress to payments-db only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-api-egress
  namespace: payments
spec:
  podSelector:
    matchLabels: { app: payments-api }
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector:
            matchLabels: { app: payments-db }
      ports:
        - port: 5432
          protocol: TCP
```

## Terraform: WAF and rate-limiting for public-by-design ALB

```hcl
resource "aws_wafv2_web_acl" "marketing" {
  name  = "marketing-waf"
  scope = "REGIONAL"

  default_action { allow {} }

  rule {
    name     = "rate-limit"
    priority = 1
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    action { block {} }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "marketing-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws-managed-common"
    priority = 2
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-managed-common"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "marketing-waf"
    sampled_requests_enabled   = true
  }
}
```

## What the L2 review verifies

- Subnet tiering: data resources in data-tier subnets without
  internet path; app workloads in app-tier private subnets.
- Egress filtering: NAT for app tier; no egress route for data
  tier (managed-service access via VPC endpoints only).
- Private endpoints for S3, KMS, STS, and other managed services
  the workload calls.
- Kubernetes default-deny NetworkPolicy plus explicit allow.
- Public-by-design surfaces have WAF, rate limiting, and the
  intent tag (cross-references infrastructure-misconfiguration.no-public-access-without-tag).

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
