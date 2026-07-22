<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.governance-tagging governance tagging (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.governance-tagging.

## Anti-pattern 1: No default_tags; per-resource tagging only

```hcl
# Bad: provider without default_tags
provider "aws" {
  region = "us-west-2"
  # No default_tags block
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "m5.large"
  tags = {
    owner = "team-payments"
    # other tags inconsistent across resources because each
    # resource block declares its own
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "data"
  tags = {
    Owner = "team-payments"  # capitalization drift
  }
}
```

**Why it matters:** Per-resource tag declarations drift over
time as different substrate-authors copy from different
templates. The same logical concept ends up under multiple keys
(`owner`, `Owner`, `ownedBy`, `team`); downstream operations
(cost attribution, on-call routing) fragment. Substrate-
required: provider default_tags carrying the floor.

## Anti-pattern 2: Tag value outside the closed vocabulary

```hcl
# Bad: environment value not in substrate-accepted vocabulary
resource "aws_db_instance" "main" {
  identifier        = "main"
  engine            = "postgres"
  instance_class    = "db.t4g.large"
  allocated_storage = 100
  tags = {
    owner       = "team-payments"
    environment = "prod"           # bad: not "production"
    cost-center = "payments"       # bad: not in CC-XXX-NNN format
  }
}
```

**Why it matters:** "prod" and "production" do not match in
queries; the cost-attribution pipeline sees them as distinct
environments. Substrate-required vocabulary is closed; consumer
variations require documented mapping.

## Anti-pattern 3: Data-bearing resource without data-sensitivity tag

```hcl
# Bad: data-bearing resource missing data-sensitivity
resource "aws_s3_bucket" "customer_records" {
  bucket = "customer-records"
  tags = {
    owner       = "team-payments"
    environment = "production"
    cost-center = "CC-PAYMENTS-001"
    # data-sensitivity absent
  }
}
```

**Why it matters:** Without data-sensitivity, data-class-aware
controls (CMK-tier encryption, retention policy, access-control
ABAC conditions) cannot be applied correctly. The resource is
indistinguishable from a public-classification resource for
downstream tooling.

## Anti-pattern 4: Tag schema drift across modules

```hcl
# Module A
resource "aws_instance" "app" {
  tags = {
    Owner       = "team-payments"
    Environment = "Production"
  }
}

# Module B (different style)
resource "aws_instance" "worker" {
  tags = {
    owner       = "team-payments@example.com"
    environment = "prod"
  }
}

# Module C (yet another style)
resource "aws_instance" "scheduler" {
  tags = {
    ownedBy     = "team-payments"
    deploymentTier = "production"
  }
}
```

**Why it matters:** Three modules; three different schemas. The
cost-attribution pipeline, on-call routing, and access-control
ABAC conditions all behave differently across the modules.
Substrate-required: one schema across the whole IaC repository.

## Anti-pattern 5: No organization-level enforcement

```hcl
# Bad: no AWS Organization tag policy, no Azure Policy, no GCP
# Org Policy enforcing tag presence. Tag enforcement is only
# at provider default_tags level, which catches IaC-declared
# resources but not resources created via console, CLI, or
# Lambda automation outside IaC.
```

**Why it matters:** provider default_tags applies only to
Terraform-managed resources; resources created in the console,
via CLI, or by Lambda functions invoked outside IaC have no
tag enforcement. Substrate-recommended: organization-level
enforcement at the cloud-provider tier so the floor applies to
every resource regardless of provisioning method.

## Anti-pattern 6: Consumer schema not documented

```hcl
# Bad: consumer uses custom keys but no mapping doc exists
resource "aws_instance" "app" {
  tags = {
    Team   = "PAY"      # what is PAY?
    Env    = "P"        # what is P?
    BU     = "FINANCE"  # what is BU?
  }
}
# No README, no tagging-policy.md, no mapping documented
```

**Why it matters:** A new substrate-author joining the team
cannot determine what these tags mean. The substrate accepts
consumer-specific schemas only when the mapping to substrate-
required information is documented.

## Anti-pattern 7: governance-commons.intent tag misused

```hcl
# Bad: intent tag used as a generic escape hatch
resource "aws_s3_bucket" "data" {
  bucket = "company-data-prod"
  tags = {
    "governance-commons.intent" = "skip-checks"  # invalid value
  }
}
```

**Why it matters:** The substrate's intent-tag vocabulary is
fixed: `public-by-design`, `ephemeral`, `test-fixture`,
`ci-fixture`. "skip-checks" is not a valid value and would not
be honored by the substrate's recommended scanner-suppression
configuration. Substrate-required: values from the substrate's
intent vocabulary, accompanied by a justification tag.

## How each anti-pattern is reviewed

The L2 review surfaces these via inspection of the IaC's tag
declarations and live-state tag retrieval. Schema drift
(Anti-pattern 4) is detected by enumerating every tag key used
in the repository and flagging the synonyms.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired `governance-tagging-good.md`
example.
