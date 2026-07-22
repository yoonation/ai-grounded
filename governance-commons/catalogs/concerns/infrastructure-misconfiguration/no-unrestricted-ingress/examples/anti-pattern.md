<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.no-unrestricted-ingress no unrestricted ingress (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.no-unrestricted-ingress. Each
shows a common way the rule is violated and the resulting
exposure pattern.

## Anti-pattern 1: SSH open to the internet

```hcl
# Bad: SSH from anywhere
resource "aws_security_group" "app" {
  name        = "app"
  description = "Application instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Why it matters:** Internet-exposed SSH is the most common
cloud-account compromise vector across published incident
reports. Attackers run continuous scans (Shodan, Censys);
credential-stuffing and zero-day SSH exploits arrive
opportunistically. The substrate's bias: SSH access via
identity-aware proxy (AWS SSM Session Manager, GCP IAP, Azure
Bastion) or bastion CIDR allow-list.

## Anti-pattern 2: Database port open to the internet

```hcl
# Bad: PostgreSQL accessible from the internet
resource "aws_security_group" "rds" {
  name   = "rds"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Why it matters:** Database services are not designed to harden
against arbitrary internet access. Even with strong passwords,
the exposure enables credential-spraying, version-fingerprinting
for known CVEs, and amplification attacks. The substrate's bias:
database access from application security group only; ad-hoc
DBA access via VPN or identity-aware proxy.

## Anti-pattern 3: Kubernetes API endpoint public without authorized networks

```hcl
# Bad: EKS cluster with public endpoint and no IP restriction
resource "aws_eks_cluster" "main" {
  name     = "production"
  role_arn = aws_iam_role.eks.arn

  vpc_config {
    subnet_ids              = aws_subnet.private[*].id
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]  # full internet
  }
}
```

**Why it matters:** A public Kubernetes API endpoint reachable
from any source is exposed to the entire internet's Kubernetes
attack tooling (kubeletmein, kube-hunter, peirates). Even with
strong IAM-based authentication, the API surface itself is
substantial (every kubectl verb is a potential exploitation
vector). The substrate's bias: private endpoint or public
endpoint with authorized networks restricted to bastion / VPN
CIDRs.

## Anti-pattern 4: IPv6 dual-stack ingress missed

```hcl
# Bad: IPv4 restricted but IPv6 wide open
resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks       = ["10.0.0.0/8"]  # internal only
    ipv6_cidr_blocks  = ["::/0"]        # IPv6 unrestricted
  }
}
```

**Why it matters:** A dual-stack network attaches IPv6 addresses
automatically; an IPv6 ingress without restriction renders the
IPv4 restriction moot. Static analyzers consistently catch the
pattern but the human eye often misses it. The substrate's bias:
symmetric restriction.

## Anti-pattern 5: Azure NSG with Internet service tag

```hcl
# Bad: Azure NSG permitting Internet to RDP
resource "azurerm_network_security_rule" "rdp_from_internet" {
  name                        = "allow-rdp"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "3389"
  source_address_prefix       = "Internet"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.app.name
}
```

**Why it matters:** Azure's `Internet` service tag is equivalent
to `0.0.0.0/0`; the substrate flags both. RDP is in the
sensitive-port list (3389); exposure is comparable to SSH.
The substrate's bias: Azure Bastion or restricted CIDR.

## Anti-pattern 6: GCP firewall with wildcard source

```hcl
# Bad: GCP firewall allowing all sources to a sensitive port
resource "google_compute_firewall" "ssh_open" {
  name    = "allow-ssh"
  network = google_compute_network.main.name
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}
```

**Why it matters:** GCP's firewall ruleset is the analog of AWS
security groups; the same anti-pattern applies. The substrate's
bias: scoped `source_ranges` (Google IAP CIDR for SSH-via-IAP)
or `source_service_accounts` for identity-based scoping.

## How each anti-pattern is detected

- Anti-patterns 1, 2, 4: Checkov CKV_AWS_24 (SSH), CKV_AWS_25
  (port range), CKV_AWS_260 (PostgreSQL); Trivy
  aws-vpc-no-public-ingress-sgr family; Semgrep
  terraform.aws.security.aws-security-group-* family.
- Anti-pattern 3: Checkov CKV_AWS_*, Trivy
  aws-eks-no-public-cluster-access.
- Anti-pattern 5: Checkov CKV_AZURE_10, Trivy
  azure-network-no-public-ingress.
- Anti-pattern 6: Checkov CKV_GCP_2, Trivy
  google-compute-no-public-ingress.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`no-unrestricted-ingress-good.md` example.
