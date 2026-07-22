<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.slsa-provenance-verification SLSA provenance verification

Substrate-recommended CI verification gate consuming SLSA
provenance attestation before deployment.

## Pattern A: GitHub Actions verification gate with slsa-verifier

```yaml
name: Verify and Deploy

on:
  workflow_run:
    workflows: ["Build"]
    types: [completed]

jobs:
  verify-and-deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - name: Install slsa-verifier
        uses: slsa-framework/slsa-verifier/actions/installer@5c0c52aa8c0aaa5a3fbf7faf5a2c39e29e6c6e9e  # v2.5.1

      - name: Download artifact and attestation
        run: |
          gh release download "${TAG}" \
            --pattern 'api-server-*' \
            --pattern 'multiple.intoto.jsonl'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Verify SLSA provenance
        run: |
          slsa-verifier verify-artifact \
            --provenance-path multiple.intoto.jsonl \
            --source-uri "github.com/${{ github.repository }}" \
            --source-tag "${TAG}" \
            api-server-linux-amd64

      - name: Record verification result
        run: |
          cat > verification-record.json <<JSON
          {
            "artifact-digest": "$(sha256sum api-server-linux-amd64 | cut -d' ' -f1)",
            "verifier-tool": "slsa-verifier",
            "verifier-version": "$(slsa-verifier version)",
            "source-uri": "github.com/${{ github.repository }}",
            "source-tag": "${TAG}",
            "verification-result": "pass",
            "verification-timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
          }
          JSON
          # Retain per supply-chain.attestation-and-sbom-retention
          aws s3 cp verification-record.json \
            "s3://supply-chain-attestations/${TAG}/verification.json"

      - name: Deploy
        run: ./deploy.sh "${TAG}"
```

## Pattern B: cosign verification for OCI attestations

```yaml
- name: Verify SLSA provenance on container image
  run: |
    cosign verify-attestation \
      --certificate-identity-regexp '^https://github\.com/myorg/myrepo/\.github/workflows/build\.yaml@refs/tags/v[0-9]+\.[0-9]+\.[0-9]+$' \
      --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
      --type slsaprovenance1 \
      "registry.example.com/api:${VERSION}@${DIGEST}"
```

## Pattern C: Profile-keyed policy file

The substrate-recommended policy file at
`policy/supply-chain/attestation-policy.yaml`:

```yaml
profile: production-grade-baseline
required-predicate-types:
  - "https://slsa.dev/provenance/v1"
minimum-slsa-build-level: 2
verify-signing-identity: true
allowed-signers:
  - issuer: "https://token.actions.githubusercontent.com"
    pattern: "^https://github\\.com/myorg/.+@refs/tags/v[0-9]+\\.[0-9]+\\.[0-9]+$"
transparency-log: "https://rekor.sigstore.dev"
```

The CI gate consumes the policy file to drive the verification
invocation; the policy file is itself reviewed under supply-chain.supply-chain-integrity-strategy
ADR change discipline.

## Key observations

- Verification failure blocks deployment; no fallthrough on
  verifier errors
- The verification record is retained per supply-chain.attestation-and-sbom-retention with
  substrate-required fields
- Source-URI pinning is substrate-required: the attestation must
  declare a build originating from the consumer's expected source
  repository
