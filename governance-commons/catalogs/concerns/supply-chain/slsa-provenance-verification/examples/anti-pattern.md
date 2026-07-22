<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.slsa-provenance-verification SLSA provenance verification absent

Substrate-rejected deployment patterns.

## Anti-pattern A: deployment with no verification step

```yaml
name: Deploy

on:
  push:
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # Substrate-rejected: no verification of the artifact's origin
      - name: Pull image
        run: docker pull "registry.example.com/api:${GITHUB_REF_NAME}"

      - name: Deploy
        run: ./deploy.sh "${GITHUB_REF_NAME}"
```

The pipeline pulls and deploys without verifying that the image
was built by the consumer's expected source and build platform.
A compromised registry account can substitute a malicious image
under the expected tag.

## Anti-pattern B: verification with warning-only failure

```yaml
- name: Verify SLSA provenance (warning only)
  continue-on-error: true  # Substrate-rejected
  run: |
    slsa-verifier verify-artifact \
      --provenance-path attestation.intoto.jsonl \
      --source-uri "github.com/${{ github.repository }}" \
      artifact

- name: Deploy
  # Deployment proceeds regardless of verification result
  run: ./deploy.sh
```

`continue-on-error: true` defeats the verification gate. Failures
surface in logs but do not block deployment.

## Anti-pattern C: verification without source-URI pinning

```yaml
- name: Verify provenance (substrate-rejected; missing source-URI)
  run: |
    # Verifier confirms the attestation is signed by *some* signer
    # but does not require the attestation to declare the expected
    # source repository
    slsa-verifier verify-artifact \
      --provenance-path attestation.intoto.jsonl \
      artifact
```

Without `--source-uri`, the verifier accepts any attested build,
including builds from a different repository under the same
trust chain. An attacker who produces an attested build from a
different repository can pass verification.

## Anti-pattern D: wildcard OIDC issuer acceptance

```yaml
- name: Verify with wildcard signer
  run: |
    cosign verify-attestation \
      --certificate-identity-regexp '.*' \
      --certificate-oidc-issuer-regexp '.*' \
      "registry.example.com/api:${VERSION}"
```

Wildcard acceptance defeats the trust anchor. Any OIDC-bound
signer from any issuer passes verification.

## Why these patterns fail

The substrate-relevant threat: provenance verification anchors
the consumer's trust to a specific build platform and source
repository. Each anti-pattern above removes one anchor; the
combination of removed anchors is the substrate-recognized
fail-open posture that defeats the rule's value.
