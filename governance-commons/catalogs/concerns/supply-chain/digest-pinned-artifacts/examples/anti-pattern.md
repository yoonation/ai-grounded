<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.digest-pinned-artifacts digest pinning bypassed

Substrate-rejected patterns. Detection by the supply-chain.digest-pinned-artifacts
binding flags each.

## Anti-pattern A: tag-only Dockerfile FROM

```dockerfile
# Substrate-rejected: tag is mutable; upstream re-push substitutes
# the bytes underneath the consumer
FROM ubuntu:24.04

COPY app /app/
ENTRYPOINT ["/app/server"]
```

The image referenced as `ubuntu:24.04` today may be different
bytes than the image referenced as `ubuntu:24.04` tomorrow. The
deployment manifest does not bind to specific bytes.

## Anti-pattern B: `:latest` tag in production

```yaml
# Substrate-rejected: :latest in production is the substrate-
# recognized highest-risk tag drift pattern
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api-service:latest
```

## Anti-pattern C: GitHub Actions tag reference

```yaml
# Substrate-rejected: tag-pinning of actions; tag is mutable
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
```

The `v4` tag may be re-pointed by the action maintainer. supply-chain.digest-pinned-artifacts
requires the full 40-character commit SHA.

## Anti-pattern D: terraform without lock file

```hcl
# Substrate-rejected: .terraform.lock.hcl not committed
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

`~> 5.0` is a permissive constraint allowing any 5.x version; without
the lock file, the provider's hash is not bound either.

## Anti-pattern E: branch-pinned terraform module

```hcl
# Substrate-rejected: branch ref is mutable
module "vpc" {
  source = "git::https://github.com/org/terraform-vpc.git?ref=main"
}
```

The `main` branch ref changes as the upstream module evolves.
supply-chain.digest-pinned-artifacts requires `?ref=<commit-sha>`.

## Why these patterns fail

The substrate-relevant threat model: an upstream account compromise
or tag re-push substitutes different bytes under the same tag.
The consumer's tested staging artifact and deployed production
artifact diverge silently. supply-chain.slsa-provenance-verification SLSA provenance
verification catches the byte substitution at deployment, but only
if the artifact reference binds to specific bytes; mutable-tag
references defeat that anchor.
