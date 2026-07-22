<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.digest-pinned-artifacts digest-pinned artifacts

Substrate-recommended digest-pinning patterns across substrate-
recognized artifact-consumption surfaces.

## Pattern A: Dockerfile with digest-pinned base

```dockerfile
# Substrate-accepted: tag-with-digest form, digest binds the build
FROM cgr.dev/chainguard/static:latest@sha256:f4f47c12dee01b40e770e36df8a85f1d4a6f02e3f3fe5cdf07e3b5e3c5c8d2a1

COPY app /app/
ENTRYPOINT ["/app/server"]
```

The version label (`latest`) remains for human readability; the
digest (`@sha256:...`) binds the deployment to the specific bytes.

## Pattern B: Kubernetes manifest with digest-pinned image

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: production
spec:
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api-service:v2.4.1@sha256:9bf8c5e2a3...
          ports:
            - containerPort: 8080
```

## Pattern C: GitHub Actions with SHA-pinned action references

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      - name: Setup Node
        uses: actions/setup-node@8f152de45cc393bb48ce5d89d36b731f54556e65  # v4.0.0
        with:
          node-version: '20'
```

The trailing comment preserves the human-readable version label;
the SHA binds the action.

## Pattern D: terraform with lock-file integrity hash

```hcl
# versions.tf
terraform {
  required_version = "= 1.7.4"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.31.0"
    }
  }
}
```

The `.terraform.lock.hcl` file (substrate-required to be
committed) records the provider's `h1:` and `zh:` hashes that
terraform uses as digest-equivalents at apply time.

## Pattern E: Automated digest refresh via dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot opens pull requests that update both the version label
and the SHA-256 digest together. The substrate's review process
(supply-chain.dependency-vetting vetting for major version bumps; lighter touch for
patch updates) handles the merge.

## Key observations

- Digest binding does not replace the version label; both are
  retained for human readability and substrate-acceptable upgrade
  operability
- Dependabot or Renovate automates the digest refresh; manual
  digest maintenance is substrate-acknowledged-difficult
- Production manifests are digest-pinned; development overlays
  may use mutable tags during active iteration
