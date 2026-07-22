<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.network-segmentation network segmentation (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.network-segmentation.

## Anti-pattern 1: Flat single-subnet topology

```hcl
# Bad: one subnet hosting everything
resource "aws_subnet" "everything" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.0.0/16"  # entire VPC in one subnet
  availability_zone = "us-west-2a"
}

resource "aws_route_table" "everything" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}
# Application instances, databases, and load balancers all in
# the same subnet with internet path
```

**Why it matters:** Database and application resources share
the public-internet egress / ingress surface. A compromised
application can exfiltrate database content to any internet
destination; a compromised database can reach attacker-
controlled C2. The substrate's bias is tiered subnet topology
with the data tier having no internet path.

## Anti-pattern 2: Application in public subnet

```hcl
# Bad: application instance with public IP
resource "aws_instance" "app" {
  ami                         = data.aws_ami.app.id
  instance_type               = "m5.large"
  subnet_id                   = aws_subnet.public[0].id
  associate_public_ip_address = true  # directly internet-reachable
  security_groups             = [aws_security_group.app.id]
}
```

**Why it matters:** Application instances should be in private
subnets behind a load balancer. Direct public-IP exposure
multiplies the attack surface (every running service binds to
a public-facing interface).

## Anti-pattern 3: Database in subnet with internet egress

```hcl
# Bad: RDS in app-tier subnet that has NAT egress
resource "aws_db_instance" "main" {
  identifier              = "main"
  engine                  = "postgres"
  instance_class          = "db.t4g.large"
  allocated_storage       = 100
  db_subnet_group_name    = aws_db_subnet_group.app_tier.name  # NAT-routed
  publicly_accessible     = false  # not publicly accessible, but in NAT-routed subnet
}
```

**Why it matters:** A compromised RDS instance with egress
to the internet (via NAT) can exfiltrate data without
detection. The substrate's bias: data-tier subnets have no
default route to internet; managed-service calls (KMS for
encryption operations, Secrets Manager for credential rotation)
are routed via VPC endpoints.

## Anti-pattern 4: Single permissive security group attached to everything

```hcl
# Bad: one "everything" security group
resource "aws_security_group" "everything" {
  name   = "everything"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true  # all members of the SG can reach all members
  }
}

resource "aws_instance" "app"      { vpc_security_group_ids = [aws_security_group.everything.id] }
resource "aws_db_instance" "db"    { vpc_security_group_ids = [aws_security_group.everything.id] }
resource "aws_elasticache_cluster" "cache" { security_group_ids = [aws_security_group.everything.id] }
```

**Why it matters:** A flat SG attached to unrelated workloads
permits cross-workload east-west traffic on all ports. A
compromised application reaches the database, cache, and every
other workload sharing the SG. Substrate-required: workload-
specific SGs with ingress allows referencing peer SGs by ID.

## Anti-pattern 5: Kubernetes namespace without NetworkPolicy

```yaml
# Bad: no NetworkPolicy in production namespace
apiVersion: v1
kind: Namespace
metadata:
  name: payments
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: payments
spec:
  # ... no NetworkPolicy elsewhere in this namespace
```

**Why it matters:** Without an explicit NetworkPolicy,
Kubernetes namespaces permit pod-to-pod traffic from any
namespace by default. A compromised pod in any namespace can
reach the payments namespace's pods. Substrate-required:
default-deny NetworkPolicy plus explicit allow.

## Anti-pattern 6: Public-by-design surface without WAF or rate limiting

```hcl
# Bad: public ALB with no WAF, no rate limiting
resource "aws_lb" "marketing" {
  name               = "marketing-public"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    "governance-commons.intent" = "public-by-design"
  }
  # No aws_wafv2_web_acl_association
  # No CloudFront in front
}
```

**Why it matters:** The intent tag declares public exposure as
deliberate, but the L2 review requires defense-in-depth: a
WAF, rate limiting, or DDoS protection. The intent tag is not
permission to skip the defenses; it is the trigger for the L2
review to verify the defenses are in place.

## Anti-pattern 7: Cross-VPC peering without documented purpose or condition

```hcl
# Bad: peering to another account's VPC with no documentation
resource "aws_vpc_peering_connection" "to_unknown" {
  peer_owner_id = "444455556666"  # who is this account?
  peer_vpc_id   = "vpc-aaaa1111"
  vpc_id        = aws_vpc.main.id
  auto_accept   = false
}
# No record of why this peering exists, what traffic patterns
# it enables, who reviewed the cross-account exposure.
```

**Why it matters:** Cross-VPC peering, transit gateway
attachments, and cross-cloud connectivity create paths that
bypass the VPC's egress controls. The substrate requires every
such path to be documented in the consumer's connectivity
inventory with a business reason, a traffic pattern, and a
review record.

## How each anti-pattern is reviewed

The L2 review surfaces these patterns via reachability-analysis
tooling (AWS VPC Reachability Analyzer, Azure Connection
Monitor, GCP Connectivity Tests) and inspection of the
infrastructure-misconfiguration.network-segmentation review-checklist questions 1 through 6. Tag-based
patterns are detected by tag-aware scanners.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired `network-segmentation-good.md`
example.
