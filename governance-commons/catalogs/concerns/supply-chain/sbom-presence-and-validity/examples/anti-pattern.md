<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.sbom-presence-and-validity SBOM missing or invalid

Substrate-rejected release patterns.

## Anti-pattern A: release with no SBOM

```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push
        run: |
          docker build -t "api:${GITHUB_REF_NAME}" .
          docker push "api:${GITHUB_REF_NAME}"
      # Substrate-rejected: no SBOM generation step
```

When log4shell-class advisories drop, the consumer cannot answer
"are we affected?" without manually rebuilding each release.

## Anti-pattern B: SBOM generated but not validated

```yaml
- name: Generate SBOM
  run: syft "api:${VERSION}" -o cyclonedx-json=sbom.cdx.json
  continue-on-error: true  # Substrate-rejected: errors suppressed

- name: Upload
  run: gh release upload "${VERSION}" sbom.cdx.json
  # Substrate-rejected: no format validation; malformed SBOM uploaded
```

Malformed SBOMs are unusable for downstream tooling; the rule
requires validation before publication.

## Anti-pattern C: SBOM never attached to artifact

```yaml
- name: Generate SBOM
  run: syft . -o cyclonedx-json=sbom.cdx.json

- name: Build
  run: docker build -t "api:${VERSION}" .
  # Substrate-rejected: SBOM and artifact built but never associated
```

The SBOM exists somewhere in the CI workspace but is not attached
to the artifact or stored in the retention surface. After the CI
run completes, the SBOM is lost.

## Anti-pattern D: SBOM for the wrong artifact

```yaml
# Substrate-rejected: SBOM generated from source repo, not from
# the built artifact; the SBOM does not reflect the artifact's
# actual contents
- name: Generate SBOM from source
  run: syft dir:. -o cyclonedx-json=sbom.cdx.json
  # then build a separate container image
- name: Build
  run: docker build -t api .
```

The source-tree SBOM does not enumerate the runtime dependencies
of the built container (base-image layers, runtime packages).
Substrate-recommended: SBOM is generated from the built artifact.

## Why these patterns fail

SBOMs anchor the consumer's incident-response capability. Each
anti-pattern above breaks one of three properties the L1 rule
requires: presence (the SBOM exists), validity (the SBOM is
well-formed), and association (the SBOM corresponds to the
specific artifact deployed).
