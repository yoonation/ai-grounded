<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.iac-sources-version-pinned IaC sources version-pinned (good patterns)

Substrate-original good-pattern examples for infrastructure-misconfiguration.iac-sources-version-pinned. Each
shows the substrate's pattern of pinning IaC external sources
(providers, modules, container images, Helm charts) to specific
versions or immutable references.

## Terraform: required_providers with version constraints

```hcl
terraform {
  required_version = "~> 1.12"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.95"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.36"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
```

The `.terraform.lock.hcl` file is checked into the repository
(cross-references dependency-management.pinned-versions's lockfile-checked-in rule).

## Terraform: registry module pinned by version

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"  # pinned

  name = "main"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
  public_subnets  = ["10.0.20.0/24", "10.0.21.0/24", "10.0.22.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  enable_flow_log        = true
  flow_log_destination_type = "cloud-watch-logs"

  tags = local.common_tags
}
```

## Terraform: git-sourced module pinned by commit SHA

```hcl
module "internal_eks" {
  # Pinned by commit SHA; immutable reference
  source = "git::https://github.com/company/terraform-aws-eks-internal.git?ref=4d8a2e1c6f3b9a8e2d1f7c5b3a9e8d2f1c4b5a6e"

  cluster_name    = "production"
  cluster_version = "1.31"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  tags = local.common_tags
}
```

A tag reference (e.g. `?ref=v2.4.1`) is acceptable when the
upstream repository uses signed tags or branch-protection rules
preventing tag re-pointing.

## Kubernetes: container image with digest pinning

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: payments
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payments-api
  template:
    metadata:
      labels:
        app: payments-api
    spec:
      containers:
        - name: api
          # Digest-pinned image; immutable reference
          image: 111122223333.dkr.ecr.us-west-2.amazonaws.com/payments-api@sha256:a3b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
          ports:
            - containerPort: 8080
```

## Helm: chart version pinned in helm_release

```hcl
resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = "7.7.10"  # pinned
  namespace        = "argocd"
  create_namespace = true

  values = [file("${path.module}/argocd-values.yaml")]
}
```

## Helm: Chart.yaml dependencies with exact versions

```yaml
apiVersion: v2
name: payments
description: Payments service chart
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: "16.4.6"  # exact
    repository: "oci://registry-1.docker.io/bitnamicharts"

  - name: redis
    version: "20.7.0"
    repository: "oci://registry-1.docker.io/bitnamicharts"
```

## What the L1 binding catches in PR review

- `required_providers` blocks with a provider entry lacking
  `version` or using `>=` without an upper bound.
- `module` blocks whose `source` references the public registry
  without a `version` attribute.
- `module` blocks whose `source` is a git URL with `?ref=main`,
  `?ref=master`, or `?ref=develop` (mutable branch refs).
- Kubernetes container images with `image: name:latest`, no tag
  at all, or a tag that the substrate's binding recognizes as
  mutable on the registry.
- Helm `helm_release` resources without `version`.
- Helm `Chart.yaml` dependencies with `>=` or `*` version
  expressions.

All examples carry the substrate-recommended tag schema per
infrastructure-misconfiguration.governance-tagging and cross-reference the dependency-management
concern's dependency-management.pinned-versions pinning rule for the application-package
companion surface.
