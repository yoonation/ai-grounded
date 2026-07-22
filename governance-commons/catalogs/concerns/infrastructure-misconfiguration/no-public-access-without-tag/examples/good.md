<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.no-public-access-without-tag no public access without tag (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.no-public-access-without-tag. Each
shows the substrate's pattern of (a) explicit block-public on
default-deny resources, or (b) public-by-design intent tag with
defense-in-depth on intentionally-public resources.

## Terraform: S3 bucket with public-access-block

```hcl
resource "aws_s3_bucket" "private_data" {
  bucket = "private-data-${var.environment}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "private_data" {
  bucket                  = aws_s3_bucket.private_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Terraform: RDS not publicly accessible

```hcl
resource "aws_db_subnet_group" "payments" {
  name       = "payments-${var.environment}"
  subnet_ids = aws_subnet.data_private[*].id
  tags       = local.common_tags
}

resource "aws_db_instance" "payments" {
  identifier             = "payments-${var.environment}"
  engine                 = "postgres"
  instance_class         = "db.t4g.large"
  allocated_storage      = 100
  db_subnet_group_name   = aws_db_subnet_group.payments.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  storage_encrypted      = true
  tags                   = local.common_tags
}
```

## Terraform: Public-by-design CDN origin bucket with intent tag and OAC

```hcl
resource "aws_s3_bucket" "marketing_cdn_origin" {
  bucket = "marketing-cdn-origin-${var.environment}"
  tags = merge(local.common_tags, {
    "governance-commons.intent"               = "public-by-design"
    "governance-commons.intent-justification" = "CloudFront origin for static marketing assets; access restricted via OAC"
  })
}

resource "aws_s3_bucket_public_access_block" "marketing_cdn_origin" {
  bucket                  = aws_s3_bucket.marketing_cdn_origin.id
  block_public_acls       = true
  block_public_policy     = false  # CloudFront OAC requires bucket policy
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_cloudfront_origin_access_control" "marketing" {
  name                              = "marketing-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
```

The bucket carries the intent tag declaring public exposure as
deliberate; the bucket policy still restricts access to the
CloudFront OAC service principal only, so "public" here means
"reachable via CloudFront" rather than "directly anonymous."

## GCP: GCS bucket with uniform bucket-level access

```hcl
resource "google_storage_bucket" "private_data" {
  name                        = "private-data-${var.environment}"
  location                    = "US-WEST1"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning {
    enabled = true
  }
  labels = local.common_labels
}

resource "google_storage_bucket_iam_binding" "private_data_readers" {
  bucket = google_storage_bucket.private_data.name
  role   = "roles/storage.objectViewer"
  # Specific principals; never allUsers or allAuthenticatedUsers
  members = [
    "serviceAccount:${google_service_account.app.email}",
  ]
}
```

## Kubernetes: internal LoadBalancer Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: payments
  annotations:
    # AWS internal NLB
    service.beta.kubernetes.io/aws-load-balancer-internal: "true"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internal"
    # GCP internal load balancer
    networking.gke.io/load-balancer-type: "Internal"
    # Azure internal load balancer
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  type: LoadBalancer
  selector:
    app: payments-api
  ports:
    - port: 443
      targetPort: 8080
      protocol: TCP
```

## What the L1 binding catches in PR review

- `aws_s3_bucket` without an accompanying
  `aws_s3_bucket_public_access_block` resource setting all four
  flags to true.
- `aws_db_instance` with `publicly_accessible = true` or omitted
  (the substrate requires explicit false even though
  provider-default is false).
- `aws_lambda_function_url` with `authorization_type = "NONE"`
  without the public-by-design tag.
- `aws_eks_cluster` with `endpoint_public_access = true` and
  `public_access_cidrs = ["0.0.0.0/0"]` (overlaps with
  infrastructure-misconfiguration.no-unrestricted-ingress detection).
- `google_storage_bucket` without `uniform_bucket_level_access`
  or `public_access_prevention`, or with IAM bindings to
  `allUsers` / `allAuthenticatedUsers`.
- `azurerm_storage_account` with
  `allow_blob_public_access = true` or
  `public_network_access_enabled = true` without the intent tag.
- Kubernetes `Service` of type `LoadBalancer` without the
  internal-load-balancer annotation appropriate to the cloud
  provider, and without the public-by-design tag.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
