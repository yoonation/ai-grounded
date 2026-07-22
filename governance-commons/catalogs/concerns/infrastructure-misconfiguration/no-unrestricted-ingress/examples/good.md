<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.no-unrestricted-ingress no unrestricted ingress (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.no-unrestricted-ingress. Each
shows substrate-recommended patterns for restricting ingress on
sensitive ports, using identity-aware proxies, bastion CIDRs, or
internal-only network constructs in place of internet-wide
allowance.

## Terraform: SSH access via Systems Manager Session Manager (no SSH port exposed)

```hcl
# Application instance with no SSH port in security group;
# access via SSM Session Manager only.

resource "aws_security_group" "app" {
  name        = "app-${var.environment}"
  description = "Application instances; no inbound SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTPS from ALB"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "HTTPS to internet via NAT"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_iam_role" "app_instance" {
  name = "app-instance-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.app_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
```

## Terraform: Database access from application security group only

```hcl
resource "aws_security_group" "rds" {
  name        = "rds-payments-${var.environment}"
  description = "RDS PostgreSQL; from app SG only"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from application tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = local.common_tags
}
```

## Terraform: Restricted bastion CIDR for legacy SSH

```hcl
# When SSM Session Manager is not yet adopted, restrict SSH to
# bastion CIDR only.

variable "bastion_cidrs" {
  type    = list(string)
  default = ["10.200.0.0/24"]  # bastion VPC range
}

resource "aws_security_group" "legacy_ssh" {
  name        = "legacy-ssh-${var.environment}"
  description = "Legacy SSH from bastion CIDRs only"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH from bastion CIDRs"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.bastion_cidrs
  }

  tags = local.common_tags
}
```

## Kubernetes: Default-deny NetworkPolicy + explicit allow

```yaml
# Default-deny in payments namespace; nothing reaches pods
# without explicit allow.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: payments
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-ingress-gateway
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: payments-api
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: istio-system
          podSelector:
            matchLabels:
              app: istio-ingressgateway
      ports:
        - port: 8080
          protocol: TCP
```

## GCP: Firewall rule scoped by service account, no 0.0.0.0/0

```hcl
resource "google_compute_firewall" "app_ssh_iap_only" {
  name    = "app-ssh-iap-only"
  network = google_compute_network.main.name

  # Identity-Aware Proxy CIDR range for SSH (Google-published)
  source_ranges = ["35.235.240.0/20"]

  target_service_accounts = [google_service_account.app.email]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}
```

## What the L1 binding catches in PR review

- Any `cidr_blocks` containing `"0.0.0.0/0"` paired with a port
  in the substrate's sensitive-port list (SSH 22, RDP 3389,
  database ports, Kubernetes API 6443, etcd 2379-2380, etc.).
- Any `ipv6_cidr_blocks` containing `"::/0"` to a sensitive port.
- Azure NSGs with `source_address_prefix` of `"*"`, `"Internet"`,
  or `"0.0.0.0/0"` to a sensitive port.
- GCP firewall rules with `source_ranges` containing
  `"0.0.0.0/0"` to a sensitive port.
- Kubernetes NetworkPolicy with empty `from` selector permitting
  network-wide ingress (interpretation depends on the CNI but
  the substrate flags the pattern).

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging.
