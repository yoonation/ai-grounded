<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.least-privilege-iac-iam least-privilege IaC IAM (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.least-privilege-iac-iam. Each
shows a common way the rule is violated.

## Anti-pattern 1: Star action on star resource

```hcl
# Bad: classic "give it everything" policy
data "aws_iam_policy_document" "app" {
  statement {
    effect    = "Allow"
    actions   = ["*"]
    resources = ["*"]
  }
}
```

**Why it matters:** This is functionally equivalent to attaching
`AdministratorAccess`. The blast radius is the entire account.
Often introduced as a "stop the spurious denials" debug hack
that never gets reverted; the L2 review's first question
catches it.

## Anti-pattern 2: Service-wide wildcard on star resource

```hcl
# Bad: s3:* on every bucket in the account
data "aws_iam_policy_document" "app" {
  statement {
    effect    = "Allow"
    actions   = ["s3:*"]
    resources = ["*"]
  }
}
```

**Why it matters:** Even when the application only reads from
one bucket, this policy grants Create, Delete, PutObjectAcl, and
every other S3 action against every bucket in the account.
Substrate-required: bounded actions on bounded resources.

## Anti-pattern 3: iam:PassRole on star resource

```hcl
# Bad: PassRole to anything
data "aws_iam_policy_document" "ci" {
  statement {
    effect    = "Allow"
    actions   = ["iam:PassRole"]
    resources = ["*"]
  }
}
```

**Why it matters:** Privilege escalation via PassRole is a
well-documented AWS attack pattern: an attacker who controls a
service that accepts an IAM role can pass any role in the
account, including roles with administrator permissions. The
substrate requires `Resource` to name specific role ARNs and a
`iam:PassedToService` condition.

## Anti-pattern 4: Trust policy with wildcard principal

```hcl
# Bad: anyone can assume
data "aws_iam_policy_document" "anyone_can_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}
```

**Why it matters:** A wildcard principal in a trust policy
permits any AWS account in the world to assume the role; this
is the "lost role" pattern that surfaces in cloud-account-
takeover incident reports. Substrate-required: specific account
or identity, plus `ExternalId` and `SourceAccount` conditions
for cross-account trust.

## Anti-pattern 5: AdministratorAccess on daily-use principal

```hcl
# Bad: developer role with AdministratorAccess
resource "aws_iam_role" "developer" {
  name = "developer"
  assume_role_policy = data.aws_iam_policy_document.dev_assume.json
}

resource "aws_iam_role_policy_attachment" "developer_admin" {
  role       = aws_iam_role.developer.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
```

**Why it matters:** Daily-use principals with administrator
permissions have outsized blast radius. The substrate accepts
administrator-equivalent attachments only on break-glass
principals (explicitly named in the consumer's roster) with
step-up authentication (PIM, AWS IAM Identity Center
permission-set with MFA-step-up).

## Anti-pattern 6: Resource-based policy with anonymous principal

```hcl
# Bad: S3 bucket policy with Principal *
resource "aws_s3_bucket_policy" "exposed" {
  bucket = aws_s3_bucket.data.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicRead"
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject"]
      Resource  = "${aws_s3_bucket.data.arn}/*"
    }]
  })
}
```

**Why it matters:** A `Principal: *` in a bucket policy grants
anonymous read; overlaps with infrastructure-misconfiguration.no-public-access-without-tag detection but appears
in infrastructure-misconfiguration.least-privilege-iac-iam's resource-policy review surface. Substrate-
required: a binding condition (`aws:SourceAccount`,
`aws:SourceArn`, `aws:PrincipalOrgID`) when wildcard principal
is used.

## Anti-pattern 7: Kubernetes ClusterRole with wildcard verbs and resources

```yaml
# Bad: cluster-wide everything
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: dev-cluster-admin
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
```

**Why it matters:** This is `cluster-admin` under another name.
Even when bound to "developer" subjects, it grants ability to
create privileged pods, modify cluster networking, and read
secrets across all namespaces. Substrate-required: namespace-
scoped Role with specific resources and verbs.

## How each anti-pattern is reviewed

These patterns are surfaced by:
- IAM-policy-content analysis in Checkov, terrascan, and KICS
  (resource-graph aware scanners).
- `iam-policy-analyzer` (formerly Parliament).
- AWS Access Analyzer for unused-access findings.
- The L2 reviewer's manual judgment per the infrastructure-misconfiguration.least-privilege-iac-iam
  checklist's eight review questions.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired `least-privilege-iac-iam-good.md`
example.
