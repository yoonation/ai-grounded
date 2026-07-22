<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.build-environment-isolation build environment isolation defeated

Substrate-rejected patterns.

## Anti-pattern A: persistent self-hosted runner

```yaml
jobs:
  release-build:
    runs-on: self-hosted  # substrate-rejected without isolation guarantees
    steps:
      - name: Build
        run: |
          # Build artifacts accumulate in the runner filesystem
          ./build.sh
          ./sign.sh
```

The self-hosted runner persists between jobs. Files, cached
dependencies, and shell history accumulate. An attacker who
gains access to one job can persist state that affects future
jobs.

## Anti-pattern B: SLSA Build Level below ADR target

`supply-chain.supply-chain-integrity-strategy ADR` documents Build L3 target; operational
pipeline runs:

```yaml
- name: Build
  run: docker build -t api:${VERSION} .
# No provenance generation; no slsa-github-generator
```

ADR-and-operation drift. Substrate-recommended supply-chain.supply-chain-integrity-strategy
review checklist catches this; supply-chain.build-environment-isolation audit flags it.

## Anti-pattern C: open-network production build

```yaml
- name: Build
  run: |
    # Build stage with full network access; pip can fetch arbitrary URLs
    pip install --no-cache-dir -r requirements.txt
    npm install --no-audit
    curl https://example.com/binary -o /usr/local/bin/tool && chmod +x /usr/local/bin/tool
    ./build.sh
```

The build stage has unrestricted network access. Network policy
defeats hermeticity. Substrate-recommended is pre-fetching
dependencies in a separate stage with network access, then
running the actual build stage hermetically.

## Anti-pattern D: no reproducibility verification

`docs/reproducibility-verification/` directory empty.

The consumer has no evidence that the build environment is
substantively reproducible. When a deployed artifact differs
from a re-built artifact at incident-response time, the
substrate cannot tell whether the difference is benign drift
(time-stamp variation) or attack (substituted bytes).

## Anti-pattern E: build-time secrets in environment variables

```yaml
- name: Build
  env:
    SIGNING_KEY: ${{ secrets.SIGNING_KEY }}
    DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
  run: |
    echo "Building with key length: ${#SIGNING_KEY}"
    # Substrate-rejected: secret leaked to build log
    ./build.sh
```

The secret length is printed to the build log, leaking metadata
about the secret. Even without explicit leakage, build-time
secrets in environment variables are visible to any code the
build runs.

## Why these patterns fail

Build-environment isolation is the structural anchor beneath the
L1 mechanical rules: digest pinning and signature verification
establish trust in the artifact, but the artifact's bytes were
produced by the build environment. A compromised or leaky build
environment poisons every artifact produced by it.
