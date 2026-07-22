<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.iac-sources-version-pinned IaC sources version-pinned (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.iac-sources-version-pinned. Each
shows a common way the rule is violated.

## Anti-pattern 1: required_providers without version

```hcl
# Bad: provider without version constraint
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      # version absent; resolves to whatever is latest at init time
    }
  }
}
```

**Why it matters:** Without a version constraint, `terraform
init` resolves to the latest provider release at the moment of
init. Two consequences: (1) the same IaC produces different
plans on different days, breaking determinism; (2) breaking
changes in the provider can break the IaC silently between two
`terraform init` runs. The substrate requires explicit version
constraint.

## Anti-pattern 2: Module sourced from git main branch

```hcl
# Bad: module pulled from mutable branch
module "eks" {
  source = "git::https://github.com/company/terraform-aws-eks.git"
  # No ?ref= query parameter; defaults to HEAD of default branch

  # ... module inputs ...
}

# Bad: explicit branch ref
module "vpc" {
  source = "git::https://github.com/company/terraform-aws-vpc.git?ref=main"
}
```

**Why it matters:** A `main` branch ref pulls whatever HEAD is
at `terraform init` time. The module's content can change
between two inits without any change to the consumer's IaC.
The substrate requires `?ref=<tag>` (for upstreams with
signed/protected tags) or `?ref=<commit-SHA>` (for guaranteed
immutability).

## Anti-pattern 3: Container image with :latest tag

```yaml
# Bad: image:latest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  template:
    spec:
      containers:
        - name: api
          image: company/api:latest  # mutable
```

**Why it matters:** A `:latest` tag points to whatever the
publisher last pushed; the same Deployment manifest produces
different running images on different days. Worse, Kubernetes'
default imagePullPolicy for `:latest` is `Always`, so every
pod restart pulls a potentially-different image. Substrate-
required: digest pin (`image@sha256:...`) or a signed-and-
verified immutable tag.

## Anti-pattern 4: Container image with no tag

```yaml
# Bad: no tag at all (Kubernetes treats as :latest)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  template:
    spec:
      containers:
        - name: api
          image: company/api  # equivalent to :latest
```

**Why it matters:** Identical failure mode to anti-pattern 3;
Kubernetes resolves missing tags to `:latest`. The substrate
treats both as violations.

## Anti-pattern 5: Helm release without version

```hcl
# Bad: helm_release without version
resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  # version absent; resolves to latest chart at apply time
  namespace  = "ingress-nginx"
}
```

**Why it matters:** Without `version`, Helm resolves to the
latest chart version at apply time; chart upgrades can include
breaking changes in CRDs or in default values that the consumer
did not vet. The substrate requires explicit `version`.

## Anti-pattern 6: Chart dependency with wildcard version

```yaml
# Bad: Chart.yaml dependency with wildcard
apiVersion: v2
name: payments
version: 1.0.0
dependencies:
  - name: postgresql
    version: "*"  # any version
    repository: "oci://registry-1.docker.io/bitnamicharts"
```

**Why it matters:** A wildcard version constraint resolves to
whatever is latest at `helm dependency update` time; chart
behavior can change between two updates. The substrate-
preferred pattern is exact version pinning or a tilde range
with a defined upper bound.

## Anti-pattern 7: Provider version with lower-bound only

```hcl
# Bad: >= constraint with no upper bound
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"  # any 5.x or higher
    }
  }
}
```

**Why it matters:** A lower-bound-only constraint accepts any
future major version, including breaking ones (the AWS provider
v4 → v5 transition broke many resource attribute shapes; an
analogous v5 → v6 transition would silently break). The
substrate requires an upper bound (`~> 5.95` or `= 5.95.0`).

## How each anti-pattern is detected

- Anti-patterns 1, 7: tflint `terraform_required_providers`,
  Checkov CKV_TF_*, Trivy iac module-version policies.
- Anti-pattern 2: tflint `terraform_module_pinned_source`,
  Checkov CKV_TF_1.
- Anti-patterns 3, 4: Checkov CKV_K8S_14, CKV_K8S_43;
  kube-linter `latest-tag`; Trivy
  yaml.kubernetes.security.container-image-latest-tag.
- Anti-pattern 5: substrate-original Semgrep rule
  `terraform.security.helm-release-no-version`.
- Anti-pattern 6: substrate-original rule for Chart.yaml
  wildcard version patterns.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`iac-sources-version-pinned-good.md` example.
