<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.no-public-access-without-tag no public access without tag (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.no-public-access-without-tag. Each
shows a common way the rule is violated.

## Anti-pattern 1: S3 bucket without public-access-block

```hcl
# Bad: no PublicAccessBlock; relies on AWS account-default
resource "aws_s3_bucket" "data" {
  bucket = "company-data-prod"
}
```

**Why it matters:** AWS account-default block-public-access has
been on by default for new accounts since 2023, but the IaC
does not declare the intent and the substrate's static analysis
cannot determine the account-level setting. A consumer
inheriting an older account (where account-default may be off)
or transferring the IaC to a new account inherits the silent
exposure. The substrate requires explicit declaration.

## Anti-pattern 2: RDS marked publicly accessible

```hcl
# Bad: database with public endpoint
resource "aws_db_instance" "main" {
  identifier          = "main"
  engine              = "postgres"
  instance_class      = "db.t4g.large"
  allocated_storage   = 100
  publicly_accessible = true  # internet-reachable
}
```

**Why it matters:** A publicly-accessible RDS instance is
reachable from the internet on the database port. Even with
security groups restricting access, the endpoint is enumerable
and the substrate's bias is that database resources have no
internet exposure. Database access from the application tier
within the same VPC; ad-hoc DBA access via VPN or identity-aware
proxy.

## Anti-pattern 3: Lambda function URL with NONE auth

```hcl
# Bad: anonymously-invocable Lambda function URL
resource "aws_lambda_function" "webhook" {
  function_name = "webhook"
  filename      = "webhook.zip"
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  role          = aws_iam_role.lambda.arn
}

resource "aws_lambda_function_url" "webhook" {
  function_name      = aws_lambda_function.webhook.function_name
  authorization_type = "NONE"  # anonymous
  # No public-by-design tag
}
```

**Why it matters:** A Lambda URL with `NONE` authorization is
anonymously invokable from the entire internet. The function's
own authentication logic becomes the only barrier; mistakes in
that logic become exposures. The substrate accepts anonymous
Lambda URLs only when the intent tag declares it deliberate
*and* infrastructure-misconfiguration.network-segmentation reviews the defense-in-depth posture (WAF,
rate limiting).

## Anti-pattern 4: GCS bucket with legacy ACL granting allUsers

```hcl
# Bad: legacy ACL with allUsers principal
resource "google_storage_bucket" "data" {
  name     = "company-data-prod"
  location = "US-WEST1"
  # uniform_bucket_level_access not declared (defaults to false)
}

resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"  # anonymous internet
}
```

**Why it matters:** `allUsers` is GCP's anonymous-principal
identifier; the IAM binding grants read access to the entire
internet. The substrate's bias: `uniform_bucket_level_access =
true` plus `public_access_prevention = "enforced"` to make this
configuration impossible.

## Anti-pattern 5: Azure storage with public blob access

```hcl
# Bad: storage account permits public blob containers
resource "azurerm_storage_account" "data" {
  name                          = "companydataprod"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  account_tier                  = "Standard"
  account_replication_type      = "LRS"
  allow_blob_public_access      = true   # bad
  public_network_access_enabled = true   # bad
  # No public-by-design tag
}
```

**Why it matters:** Both attributes default to `false` in newer
provider versions but explicit `true` declares the intent to
expose. The substrate flags both as L1 violations when the
intent tag is absent.

## Anti-pattern 6: Kubernetes Service of type LoadBalancer without internal annotation

```yaml
# Bad: LoadBalancer with no internal-LB annotation
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: payments
  # No internal-LB annotation for any cloud provider
  # No public-by-design tag
spec:
  type: LoadBalancer
  selector:
    app: payments-api
  ports:
    - port: 443
      targetPort: 8080
```

**Why it matters:** A `LoadBalancer` service without
provider-specific internal-LB annotation provisions a public
load balancer with a public IP, exposing the service to the
internet. The substrate requires either the internal-LB
annotation (private) or the public-by-design tag (deliberate
exposure with defense-in-depth).

## Anti-pattern 7: ECR repository with public policy

```hcl
# Bad: ECR repository with anonymous-pull policy
resource "aws_ecr_repository" "public_image" {
  name = "company/public-image"
  # Not an aws_ecrpublic_repository (ECR Public is the
  # substrate-preferred public-image resource); this is a
  # standard private ECR repo with a public policy attached.
}

resource "aws_ecr_repository_policy" "public_read" {
  repository = aws_ecr_repository.public_image.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicRead"
      Effect    = "Allow"
      Principal = "*"  # anonymous
      Action    = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
    }]
  })
}
```

**Why it matters:** Anonymous pull from a private ECR repository
defeats the purpose of having a private repository. The
substrate-preferred pattern for public images is ECR Public
(`aws_ecrpublic_repository`); the resource type itself
declares intent.

## How each anti-pattern is detected

- Anti-pattern 1: Checkov CKV_AWS_53/54/55/56; Trivy
  s3-bucket-public-access-block; terrascan AC_AWS_*.
- Anti-pattern 2: Checkov CKV_AWS_17; Trivy aws-rds-no-public-db-access.
- Anti-pattern 3: Checkov CKV_AWS_258 (Lambda Function URL auth).
- Anti-pattern 4: Checkov CKV_GCP_28, CKV_GCP_29; Trivy
  google-storage-no-public-access.
- Anti-pattern 5: Checkov CKV_AZURE_*; Trivy
  azure-storage-no-public-access.
- Anti-pattern 6: Checkov CKV_K8S_* for Service exposure;
  kube-linter check for cluster-external services.
- Anti-pattern 7: Checkov CKV_AWS_32 (ECR repository policy).

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`no-public-access-without-tag-good.md` example.
