<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.build-environment-isolation build environment isolation and reproducibility

Substrate-recommended hermetic build configuration with
reproducibility verification.

## Pattern A: GitHub Actions hosted-runner build with SLSA L3 generator

```yaml
name: Release Build

on:
  push:
    tags: ['v*']

permissions:
  id-token: write   # Required for OIDC signing
  contents: write   # Required for release attachment
  attestations: write

jobs:
  build:
    runs-on: ubuntu-latest  # Substrate-default: ephemeral hosted runner
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - id: build
        name: Build container with reproducibility flags
        run: |
          # SOURCE_DATE_EPOCH for build reproducibility
          export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
          docker buildx build \
            --provenance=mode=max \
            --sbom=true \
            --label "org.opencontainers.image.created=${SOURCE_DATE_EPOCH}" \
            --output type=image,name=registry.example.com/api,push=true \
            .
          echo "digest=$(docker buildx imagetools inspect registry.example.com/api --format '{{json .Manifest.Digest}}')" >> "$GITHUB_OUTPUT"

  provenance:
    needs: [build]
    permissions:
      id-token: write
      packages: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v2.0.0
    with:
      image: registry.example.com/api
      digest: ${{ needs.build.outputs.digest }}
      registry-username: ${{ github.actor }}
    secrets:
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

## Pattern B: Hermetic build with bazel

```python
# WORKSPACE.bazel - pin all dependencies with digest hashes
http_archive(
    name = "rules_python",
    sha256 = "778f9c8ec8b5e5a3c5e8cf6f4d2f6dc3a7e9c5e8c5e8c5e8c5e8c5e8c5e8c5e8",
    urls = ["https://github.com/bazelbuild/rules_python/releases/download/0.31.0/rules_python-0.31.0.tar.gz"],
)
```

```bash
# Hermetic build invocation
bazel build //:release --config=ci --execution_log_binary_file=execlog.bin
```

The bazel `--config=ci` profile configures sandbox isolation,
network restriction, and execution logging. The execution log
binary is retained per supply-chain.attestation-and-sbom-retention.

## Pattern C: Reproducibility verification record

`docs/reproducibility-verification/2026-05-01-v2.4.0.md`:

```markdown
# Reproducibility Verification: api v2.4.0

**Verification date:** 2026-05-01
**Auditor:** platform-team
**Method:** diffoscope byte-level comparison

## Procedure

1. Built api v2.4.0 in GitHub Actions on hosted runner (build A)
2. Re-built api v2.4.0 in GitHub Actions on hosted runner (build B,
   12 hours later)
3. Compared the two resulting container images with diffoscope

## Result

**Byte-identical:** the final image layers are identical between
build A and build B.

```
diffoscope --max-report-size=1000000 \
  oci-archive:build-a.tar oci-archive:build-b.tar
# (exit 0; no differences)
```

**Verdict:** reproducible. Next verification scheduled
2026-11-01.
```

## Key observations

- Hosted runners are ephemeral by default; substrate-recommended
  for production builds
- SLSA Build L3 via slsa-github-generator is substrate-recommended
  for stricter profiles
- Reproducibility verification is performed semi-annually for
  production-grade-baseline and retained per supply-chain.attestation-and-sbom-retention
