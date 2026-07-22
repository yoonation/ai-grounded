<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.sbom-presence-and-validity SBOM presence and validity

Substrate-recommended SBOM generation, validation, and storage.

## Pattern A: Release pipeline with SBOM generation and validation

```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Build container image
        run: docker buildx build -t "api:${GITHUB_REF_NAME}" .

      - name: Generate SBOM with syft
        run: |
          syft "api:${GITHUB_REF_NAME}" \
            -o cyclonedx-json=sbom.cdx.json
          # Substrate-recommended: also generate SPDX for downstream consumers
          syft "api:${GITHUB_REF_NAME}" \
            -o spdx-json=sbom.spdx.json

      - name: Validate SBOM format
        run: |
          cyclonedx-cli validate \
            --input-file sbom.cdx.json \
            --input-format json \
            --input-version v1_6
          pyspdxtools --infile sbom.spdx.json

      - name: Attach SBOM as OCI attestation
        run: |
          cosign attest \
            --predicate sbom.cdx.json \
            --type cyclonedx \
            "registry.example.com/api:${GITHUB_REF_NAME}@${DIGEST}"

      - name: Publish to Dependency-Track
        run: |
          curl -X POST -H "X-Api-Key: ${{ secrets.DT_API_KEY }}" \
            -F "autoCreate=true" \
            -F "projectName=api" \
            -F "projectVersion=${GITHUB_REF_NAME}" \
            -F "bom=@sbom.cdx.json" \
            "${{ vars.DT_URL }}/api/v1/bom"
```

## Pattern B: Ecosystem-native SBOM generation (Python)

```yaml
- name: Generate Python SBOM
  run: |
    cyclonedx-py environment \
      --output-format json \
      --output-file sbom.cdx.json
    cyclonedx-cli validate --input-file sbom.cdx.json --input-format json --input-version v1_6
```

## Pattern C: Multi-stage Dockerfile with SBOM in final image

```dockerfile
FROM cgr.dev/chainguard/static:latest@sha256:f4f47c12dee01b40e770e36df8a85f1d4a6f02e3f3fe5cdf07e3b5e3c5c8d2a1

COPY app /app/
COPY sbom.cdx.json /sbom/sbom.cdx.json

LABEL io.cyclonedx.bom.format=CycloneDX
LABEL io.cyclonedx.bom.specVersion=1.6
ENTRYPOINT ["/app/server"]
```

The SBOM is shipped with the artifact; consumers can extract it
via `docker run --rm api:tag cat /sbom/sbom.cdx.json` or via the
OCI referrers attestation.

## Key observations

- SBOM generation, validation, and attachment are pipeline gates;
  any failure blocks the release
- Both CycloneDX and SPDX are substrate-accepted; the consumer's
  profile selects primary format
- SBOM storage is via OCI referrers (substrate-default for
  container artifacts) and Dependency-Track for query capability
