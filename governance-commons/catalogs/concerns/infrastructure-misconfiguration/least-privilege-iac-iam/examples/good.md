<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.least-privilege-iac-iam least-privilege IaC IAM (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.least-privilege-iac-iam. Each
shows the substrate's pattern of declaring cloud-IAM grants
scoped tightly to specific actions, specific resources, and
specific conditions.

## Terraform: AWS application role with bounded S3 and KMS

```hcl
data "aws_iam_policy_document" "payments_app" {
  statement {
    sid    = "ReadPaymentsDataBucket"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.payments_data.arn,
      "${aws_s3_bucket.payments_data.arn}/*",
    ]
  }

  statement {
    sid    = "WritePaymentsAuditPrefix"
    effect = "Allow"
    actions = ["s3:PutObject"]
    resources = [
      "${aws_s3_bucket.payments_data.arn}/audit/*",
    ]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }
  }

  statement {
    sid    = "UseKMSForPaymentsBucketOnly"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey",
    ]
    resources = [aws_kms_key.data_at_rest.arn]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["s3.us-west-2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "payments_app" {
  name               = "payments-app"
  assume_role_policy = data.aws_iam_policy_document.payments_app_assume.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy" "payments_app" {
  name   = "payments-app"
  role   = aws_iam_role.payments_app.id
  policy = data.aws_iam_policy_document.payments_app.json
}
```

## Terraform: PassRole scoped to specific service and role

```hcl
data "aws_iam_policy_document" "ci_deploy" {
  statement {
    sid     = "PassExecutionRolesToLambdaOnly"
    effect  = "Allow"
    actions = ["iam:PassRole"]
    resources = [
      aws_iam_role.lambda_execution.arn,  # specific role
    ]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["lambda.amazonaws.com"]
    }
  }
}
```

## Terraform: Cross-account trust with ExternalId

```hcl
data "aws_iam_policy_document" "partner_data_export_assume" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::444455556666:root"]  # specific account
    }
    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values   = [var.partner_external_id]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = ["444455556666"]
    }
  }
}
```

## Kubernetes: RBAC scoped to namespace and resource names

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payments-config-reader
  namespace: payments
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["payments-runtime-config"]  # specific resource name
    verbs: ["get", "watch", "list"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["payments-db-credentials"]  # specific resource name
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-config-reader
  namespace: payments
subjects:
  - kind: ServiceAccount
    name: payments-api  # specific workload identity
    namespace: payments
roleRef:
  kind: Role
  name: payments-config-reader
  apiGroup: rbac.authorization.k8s.io
```

## GCP: ABAC condition on resource tag

```hcl
resource "google_project_iam_binding" "team_payments_storage_reader" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  members = ["group:team-payments@example.com"]

  condition {
    title       = "team-payments-resources-only"
    description = "Access restricted to resources tagged owner=team-payments"
    expression  = "resource.matchTag('${var.project_id}/owner', 'team-payments')"
  }
}
```

## What the L2 review verifies

- Wildcard actions are bounded by specific Resource ARNs.
- Wildcard Resources are bounded by narrow Actions (typically
  read-only listing) or by ABAC conditions on tags.
- `iam:PassRole` grants name specific role ARNs and a
  `PassedToService` condition.
- Cross-account trust policies carry `ExternalId` and
  `SourceAccount` conditions.
- Administrator-equivalent managed policies attach only to
  break-glass principals with step-up authentication.
- ABAC conditions resolve against tags governed by infrastructure-misconfiguration.governance-tagging.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
