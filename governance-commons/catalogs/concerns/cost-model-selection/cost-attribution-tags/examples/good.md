<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-attribution-tags cost attribution tags (good patterns)

Substrate-original good-pattern examples for cost-model-selection.cost-attribution-tags. These
illustrate the substrate-recommended pattern of declaring the
cost-attribution tag floor (cost-center, environment, service,
owner) on every billable IaC-declared resource through stack-level
composition.

## Terraform: stack-level common tags composed into resources

```hcl
locals {
  common_tags = {
    cost-center = "CC-PAYMENTS-001"
    environment = "production"
    service     = "payments-api"
    owner       = "team-payments@example.com"
  }
}

resource "aws_instance" "payments_app" {
  ami           = data.aws_ami.app.id
  instance_type = "m5.large"

  tags = merge(local.common_tags, {
    role = "app-server"
  })
}

resource "aws_s3_bucket" "payments_audit" {
  bucket = "payments-audit-${var.environment}"

  tags = merge(local.common_tags, {
    role        = "audit-log-store"
    data-class  = "audit"
    retention   = "7-years"
  })
}

resource "aws_db_instance" "payments_db" {
  identifier        = "payments-${var.environment}"
  engine            = "postgres"
  instance_class    = "db.m5.large"
  allocated_storage = 200

  tags = merge(local.common_tags, {
    role = "primary-database"
  })
}
```

Why this is good: the substrate-required tag floor lives in a
single local block; every resource composes it via merge with
resource-specific extensions. tflint with the substrate's required-
tags ruleset passes on every resource. Reviewers verify the locals
block holds the floor and that every billable resource calls
merge(local.common_tags, ...).

## Kubernetes: workload labels via Kustomize commonLabels

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

commonLabels:
  cost-center: CC-PAYMENTS-001
  environment: production
  service: payments-api
  owner: team-payments

resources:
  - deployment.yaml
  - service.yaml
  - pvc.yaml
```

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
    spec:
      containers:
        - name: app
          image: payments-api:1.42.0
```

Why this is good: kustomize commonLabels applies the substrate-
required tag floor to every resource the kustomization renders.
The Deployment manifest itself does not need to repeat the labels;
the rendered manifest carries them. kube-linter passes on every
rendered resource. Reviewers verify the kustomization's
commonLabels holds the floor.

## CloudFormation: stack-level tags inherited by every resource

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Payments API stack

Parameters:
  Environment:
    Type: String

Resources:
  PaymentsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub payments-audit-${Environment}
      Tags:
        - Key: cost-center
          Value: CC-PAYMENTS-001
        - Key: environment
          Value: !Ref Environment
        - Key: service
          Value: payments-api
        - Key: owner
          Value: team-payments@example.com
        - Key: role
          Value: audit-log-store

  PaymentsLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub payments-processor-${Environment}
      Runtime: python3.12
      MemorySize: 512
      Tags:
        - Key: cost-center
          Value: CC-PAYMENTS-001
        - Key: environment
          Value: !Ref Environment
        - Key: service
          Value: payments-api
        - Key: owner
          Value: team-payments@example.com
        - Key: role
          Value: event-processor
```

Why this is good: every resource carries the full substrate-required
tag set explicitly. The substrate's recommended CloudFormation
pattern uses CDK's Tags.of(stack).add() at the stack root to apply
the floor once; the example above shows the raw-CFN equivalent
where the tags are duplicated per resource. cfn-lint with the
substrate's cost-tag ruleset passes on every resource.

## Pulumi: stack tag defaults applied via stack configuration

```python
import pulumi
import pulumi_aws as aws

config = pulumi.Config()

common_tags = {
    "cost-center": "CC-PAYMENTS-001",
    "environment": pulumi.get_stack(),
    "service": "payments-api",
    "owner": "team-payments@example.com",
}

bucket = aws.s3.Bucket(
    "payments-audit",
    tags={**common_tags, "role": "audit-log-store"},
)

function = aws.lambda_.Function(
    "payments-processor",
    runtime="python3.12",
    memory_size=512,
    role=lambda_role.arn,
    tags={**common_tags, "role": "event-processor"},
)
```

Why this is good: the common tag dict is defined once and spread
into each resource. The substrate's recommended Pulumi pattern
uses pulumi.ResourceOptions(tags=...) at the stack level via a
provider default; the example above uses the explicit per-resource
spread pattern. checkov with the substrate's cost-tag ruleset
passes on every resource.

## What the L1 binding catches in PR review

When a developer adds a new aws_instance resource and forgets the
tags block, the Semgrep registry rule fires at PR time:

```
PR diff:
+ resource "aws_instance" "new_app" {
+   ami           = data.aws_ami.app.id
+   instance_type = "m5.large"
+ }

CI output:
ERROR: terraform.aws.security.aws-resource-without-tags
  Resource aws_instance "new_app" omits the tags block.
  cost-model-selection.cost-attribution-tags requires the substrate-required tag floor:
  cost-center, environment, service, owner.
  Suggested fix: add tags = merge(local.common_tags, { role = "..." })
```

The developer applies the suggested fix and the PR passes.
