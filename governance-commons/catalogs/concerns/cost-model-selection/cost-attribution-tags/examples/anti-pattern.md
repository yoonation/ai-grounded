<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-attribution-tags cost attribution tags (anti-patterns)

Substrate-original anti-pattern examples for cost-model-selection.cost-attribution-tags. Each
shows a common way the rule is violated and explains why the
violation matters.

## Anti-pattern 1: No tags at all on billable resources

```hcl
resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "m5.large"
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket-${var.environment}"
}

resource "aws_db_instance" "main" {
  identifier        = "main-db"
  engine            = "postgres"
  instance_class    = "db.m5.large"
  allocated_storage = 200
}
```

Why this fails: no tags on any of the billable resources. The
cost-model-selection.cost-emission-pipeline pipeline cannot attribute the spend; the cost rolls
into the consumer's undifferentiated cost pool and resists
attribution retroactively. tflint with the required-tags ruleset
fails on every resource; the substrate's Semgrep registry rule
fails as well.

The remediation cost compounds: the operator who comes back six
months later to attribute the spend faces an inventory crawl
(identify which IaC source produced each running resource) and
either a re-run of the IaC plan with tags added (operationally
disruptive for production resources) or a manual API-level
re-tag (incomplete because the IaC source-of-truth diverges from
runtime state).

## Anti-pattern 2: Tags block present but partially populated

```hcl
locals {
  partial_tags = {
    cost-center = "CC-PAYMENTS-001"
    # missing: environment, service, owner
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "m5.large"

  tags = local.partial_tags
}
```

Why this fails: the cost-model-selection.cost-attribution-tags floor requires four tags (cost-
center, environment, service, owner). Three of the four are
missing here. The cost-center alone enables a single-dimension
chargeback but does not support service-level cost analysis,
environment-segmented analysis, or owner-routed alerting (COST-
L2-002 cannot route alerts without an owner). tflint with the
substrate's required-tag-keys configured to all four tags fails
on this resource.

This anti-pattern is more insidious than complete absence
because reviewers may approve the PR thinking "tags are present."
The substrate's discipline is that the L1 rule's mechanical core
includes the full floor; partial coverage is a finding.

## Anti-pattern 3: Tag values templated from variables that resolve empty

```hcl
locals {
  common_tags = {
    cost-center = var.cost_center  # default is ""
    environment = var.environment  # default is ""
    service     = var.service       # default is ""
    owner       = var.owner         # default is ""
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "m5.large"

  tags = local.common_tags
}
```

Why this fails: the tags block is present at IaC source time
(tflint's required-tag-keys check passes because the keys are
declared), but the values resolve to empty strings at apply time
when the variables are not supplied. The provisioned resource
carries tag keys with empty values, which is effectively the same
as no tags from the pipeline's perspective: the allocation rules
cannot match against the empty value.

The substrate's Semgrep generic.iac.cost.empty-tag-value rule
catches this pattern. Reviewers also catch it by inspecting the
variable defaults: any required tag variable with an empty
default is a finding.

## Anti-pattern 4: Tags applied to some but not all resource types

```hcl
locals {
  common_tags = {
    cost-center = "CC-PAYMENTS-001"
    environment = "production"
    service     = "payments-api"
    owner       = "team-payments@example.com"
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "m5.large"
  tags          = local.common_tags
}

# But the EBS volume attached to the instance has no tags:
resource "aws_ebs_volume" "app_data" {
  availability_zone = "us-east-1a"
  size              = 100
  # no tags
}

# And the load balancer has no tags:
resource "aws_lb" "app" {
  name               = "app-lb"
  load_balancer_type = "application"
  subnets            = var.subnets
  # no tags
}
```

Why this fails: the EC2 instance is tagged but the supporting
resources (EBS volume, ALB) are not. EBS volumes attached to EC2
instances do not always inherit instance tags (provider behavior
varies); ALBs bill separately and need their own tags. The
service-level cost view in the pipeline shows only the instance
spend, undercounting the actual service cost by a meaningful
fraction.

Reviewers verify by listing every billable resource type the
stack creates and confirming each has the tag block. The
substrate's Semgrep rules cover the common types but consumer-
specific resource compositions may need consumer-side ruleset
extension.

## Anti-pattern 5: Tag values that don't match the cost-model-selection.cost-emission-pipeline pipeline expectations

```hcl
locals {
  common_tags = {
    cost-center = "Payments Team"  # human-readable but not the pipeline's value
    environment = "prod"           # pipeline expects "production"
    service     = "Payments API"   # pipeline expects "payments-api"
    owner       = "Jane Smith"     # pipeline expects an email or team identifier
  }
}
```

Why this fails: tags are present (the L1 rule passes mechanically)
but the values do not match the pipeline's allocation rule
vocabulary. The pipeline either misattributes the spend (if the
allocation rules have a fuzzy-match fallback) or defaults the
spend into a generic bucket (if the rules require exact match).
Either way, the L1 rule's intent is not realized.

This anti-pattern is an L2 review concern technically (value
correctness is L2 per the catalog's layer-boundary-disclosure)
but originates at the L1 declaration. Reviewers verify by sampling
tag values against the consumer's vocabulary documentation.

## Anti-pattern 6: Provider-side enforcement absent

```hcl
# IaC tagging is correct on day one, but the consumer's AWS
# account does not enforce tag presence at provisioning time.
```

Why this fails: when a developer or operator creates a resource
outside IaC (console-created EC2 instances; SDK-driven
provisioning in operational scripts; emergency workarounds during
incident response), the resource is provisioned without tags
and the IaC linter never sees it. Without provider-side
enforcement (Service Control Policies, Azure Policy, GCP Org
Policy), the consumer's account accumulates untagged resources
over time.

This anti-pattern is documented in the cost-model-selection.cost-attribution-tags layer-
boundary-disclosure: provider-side enforcement is substrate-
recommended as a belt-and-braces complement. The L2 review
surfaces the absence as a finding.

## What the consequences look like in operation

A multi-team consumer with consistent cost-model-selection.cost-attribution-tags violations
sees the consequences at month-end:

- The chargeback ledger shows large "Other" buckets the
  finance team cannot attribute to any team
- Cost anomaly alerts (cost-model-selection.cost-anomaly-alerting) fire account-wide because
  per-service granularity does not exist
- The cost-model ADR (cost-model-selection.cost-model-selection-policy) cannot reason at service
  granularity because the pipeline does not produce service-
  level data
- The remediation effort to backfill is substantial: each
  resource type, each provider, each environment, each missed
  IaC pattern is a separate cleanup task

The substrate's discipline is to enforce L1 at PR time so the
backfill never starts accumulating.
