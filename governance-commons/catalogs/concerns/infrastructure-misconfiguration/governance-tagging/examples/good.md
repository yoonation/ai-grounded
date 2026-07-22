<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.governance-tagging governance tagging (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.governance-tagging. Each
shows the substrate's pattern of provider-default tag composition,
closed-vocabulary values, data-sensitivity tagging on data-bearing
resources, and organization-level enforcement.

## Terraform: provider default_tags carrying substrate floor

```hcl
locals {
  common_tags = {
    owner            = "team-payments@example.com"
    environment      = "production"
    cost-center      = "CC-PAYMENTS-001"
    service          = "payments"
    "data-sensitivity" = "confidential"  # default; overridden per resource
    managed-by       = "terraform"
  }
}

provider "aws" {
  region = "us-west-2"
  default_tags {
    tags = local.common_tags
  }
}

provider "google" {
  project = var.project_id
  region  = "us-west1"
  default_labels = {
    owner            = "team-payments"
    environment      = "production"
    cost-center      = "cc-payments-001"
    service          = "payments"
    managed-by       = "terraform"
    # GCP labels: lowercase, no email-format, no special chars
  }
}
```

## Terraform: per-resource data-sensitivity override

```hcl
# Public marketing assets: override data-sensitivity to public
resource "aws_s3_bucket" "marketing_assets" {
  bucket = "marketing-assets-${var.environment}"
  tags = {
    "data-sensitivity"                       = "public"
    "governance-commons.intent"              = "public-by-design"
    "governance-commons.intent-justification" = "Marketing static assets; CloudFront origin"
  }
}

# Payments transaction log: restricted classification
resource "aws_s3_bucket" "payments_audit" {
  bucket = "payments-audit-${var.environment}"
  tags = {
    "data-sensitivity" = "restricted"
  }
  # inherits owner, environment, cost-center, service from
  # provider default_tags
}
```

## AWS Organization tag policy (declared in IaC)

```hcl
resource "aws_organizations_policy" "required_tags" {
  name        = "required-tags"
  description = "Substrate-required tag floor on every billable resource"
  type        = "TAG_POLICY"
  content = jsonencode({
    tags = {
      owner = {
        tag_key = { "@@assign" = "owner" }
        enforced_for = { "@@assign" = ["ec2:*", "s3:*", "rds:*", "dynamodb:*"] }
      }
      environment = {
        tag_key   = { "@@assign" = "environment" }
        tag_value = {
          "@@assign" = ["production", "staging", "development", "ephemeral"]
        }
        enforced_for = { "@@assign" = ["ec2:*", "s3:*", "rds:*", "dynamodb:*"] }
      }
      cost-center = {
        tag_key = { "@@assign" = "cost-center" }
        enforced_for = { "@@assign" = ["ec2:*", "s3:*", "rds:*", "dynamodb:*"] }
      }
    }
  })
}

resource "aws_organizations_policy_attachment" "required_tags_root" {
  policy_id = aws_organizations_policy.required_tags.id
  target_id = data.aws_organizations_organization.current.roots[0].id
}
```

## Azure Policy: required-tag rule at subscription scope

```hcl
resource "azurerm_policy_definition" "require_owner_tag" {
  name         = "require-owner-tag"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "Require owner tag"

  policy_rule = jsonencode({
    if = {
      field = "tags['owner']"
      exists = "false"
    }
    then = {
      effect = "deny"
    }
  })
}

resource "azurerm_subscription_policy_assignment" "require_owner_tag" {
  name                 = "require-owner-tag"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = azurerm_policy_definition.require_owner_tag.id
}
```

## GCP Organization Policy: required resource labels

```hcl
resource "google_org_policy_policy" "required_labels" {
  parent = "organizations/${var.org_id}"
  name   = "organizations/${var.org_id}/policies/gcp.resourceLocations"
  # GCP Organization Policy syntax; the substrate's recommended
  # approach is to combine Org Policy with a Terraform module
  # that enforces label presence at the resource declaration
  # layer.
  spec {
    rules {
      values {
        allowed_values = [
          "in:us-locations",  # example: location constraint as
                              # adjacent governance control
        ]
      }
    }
  }
}
```

## Consumer-mapping document (README excerpt)

```markdown
## Tag schema mapping

Our team uses a slightly different schema; this file documents
the mapping to the governance-commons substrate's required
information.

| Substrate key       | Our key                  | Vocabulary                                  |
|---------------------|--------------------------|---------------------------------------------|
| owner               | TeamOwner                | team-<slug>@example.com format              |
| environment         | Env                      | prod, stage, dev, ephem                     |
| cost-center         | CostCenter               | CC-XXX-NNN format                           |
| data-sensitivity    | DataClass                | public, internal, confidential, restricted  |

Mapping verified at substrate adoption 2026-MM-DD; reviewed
quarterly.
```

## What the L2 review verifies

- provider default_tags (or equivalent) declares the substrate's
  required keys.
- Tag values are from the substrate's closed vocabulary (or the
  documented consumer-equivalent vocabulary).
- Data-bearing resources carry the data-sensitivity tag.
- Tag schema is consistent across modules and providers.
- Organization-level tag enforcement is declared in IaC.
- Where the consumer's schema differs from substrate
  recommendation, the mapping is documented.
