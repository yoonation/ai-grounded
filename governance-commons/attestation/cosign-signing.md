<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Cosign Signing

Specification for signing attestations using cosign (Sigstore's
signing tool). Cosign provides keyless signing via OIDC identity
binding, with optional traditional key-pair signing for environments
where keyless is unsuitable.

## Why cosign

cosign is the de facto Sigstore tool. It provides:

- **Keyless signing** — no long-lived signing keys to manage or
  rotate; uses ephemeral keys bound to OIDC identity
- **Transparency log** — Rekor records signatures publicly; auditors
  can verify keys weren't compromised retrospectively
- **Standard interface** — works with in-toto statements,
  containers, blobs, OCI artifacts
- **Wide tooling support** — GitHub Actions, GitLab CI, npm, PyPI
  all integrate
- **Strong security guarantees** — backed by the Sigstore CNCF
  project with academic security analysis

## Two signing modes

### Keyless (recommended for CI)

The signer authenticates to Fulcio via OIDC. Fulcio issues a
short-lived (10-minute) certificate bound to the OIDC identity.
The signature is produced with the ephemeral key, then the
certificate and signature are uploaded to Rekor.

Verifiers later check:
- The signature is cryptographically valid
- The certificate was issued by Fulcio (signed by Fulcio root)
- The certificate's subject matches expected OIDC identity
- The Rekor entry timestamp falls within certificate validity

No long-lived keys exist; nothing to rotate or steal.

Best suited for:
- CI builds (GitHub Actions OIDC, GitLab OIDC)
- Personal development with OIDC providers (Google, GitHub)

### Key-pair (recommended for offline/airgapped or organizational
key control)

Traditional ECDSA key pair. The private key is generated locally
(with optional passphrase encryption) and used for signing. The
public key is distributed via key management system.

Verifiers check signature against the trusted public key.

Best suited for:
- Air-gapped environments without OIDC access
- Organizations with mature key management infrastructure
- Cases where regulatory requirements mandate specific key custody

## Installation

cosign is a single Go binary. Common installation paths:

    # via package manager (multiple options)
    brew install cosign
    apt install cosign
    dnf install cosign

    # via mise (recommended for this framework's tooling stack)
    mise use -g cosign@latest

    # via direct download
    # https://github.com/sigstore/cosign/releases

Verify installation:

    cosign version

## Signing an in-toto statement (keyless)

The full workflow for keyless signing of an attestation:

    # 1. Create the in-toto statement (JSON file)
    cat > attestation.json <<'EOF'
    {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [
        {
          "name": "src/feature_foo.py",
          "digest": {"sha256": "abc123..."}
        }
      ],
      "predicateType": "https://example.org/ai-authorship/v1",
      "predicate": {
        "ai_actor": {
          "type": "ai_dev_tool",
          "name": "claude-code",
          "version": "1.0.4",
          "model": "claude-opus-4-7"
        },
        "session_id": "01HXYZW...",
        "principal_human": "<github-handle>"
      }
    }
    EOF

    # 2. Sign and upload to Rekor (keyless)
    cosign attest-blob \
        --predicate attestation.json \
        --type custom \
        --bundle attestation.bundle.json \
        src/feature_foo.py

    # The bundle file contains the signature + certificate + Rekor entry
    # Store this alongside the artifact for downstream verifiers

## Signing an in-toto statement (key-pair)

    # 1. One-time setup: generate key pair
    cosign generate-key-pair
    # Creates cosign.key (private, encrypted with passphrase)
    # and cosign.pub (public)

    # Store cosign.key securely (1Password, Vault, etc.)
    # Distribute cosign.pub to verifiers

    # 2. Sign the attestation
    cosign attest-blob \
        --key cosign.key \
        --predicate attestation.json \
        --type custom \
        --bundle attestation.bundle.json \
        src/feature_foo.py

## Verifying an attestation (keyless)

    # Specify the expected OIDC identity that should have signed
    cosign verify-blob-attestation \
        --bundle attestation.bundle.json \
        --certificate-identity "user@example.com" \
        --certificate-oidc-issuer "https://accounts.google.com" \
        --type custom \
        src/feature_foo.py

For GitHub Actions:

    cosign verify-blob-attestation \
        --bundle attestation.bundle.json \
        --certificate-identity-regexp "https://github\.com/example/.+/\.github/workflows/.+" \
        --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
        --type custom \
        src/feature_foo.py

## Verifying an attestation (key-pair)

    cosign verify-blob-attestation \
        --key cosign.pub \
        --bundle attestation.bundle.json \
        --type custom \
        src/feature_foo.py

## Signing in CI (GitHub Actions example)

GitHub Actions workflows can sign keyless using the workflow's
OIDC identity:

    name: Build and Sign

    on:
      push:
        branches: [main]

    permissions:
      contents: read
      id-token: write       # required for OIDC
      attestations: write   # for GH attestations API

    jobs:
      build-and-sign:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - name: Install cosign
            uses: sigstore/cosign-installer@v3

          - name: Build artifact
            run: |
              # ... build steps ...

          - name: Generate attestation
            run: |
              cat > attestation.json <<EOF
              {
                "_type": "https://in-toto.io/Statement/v1",
                ...
              }
              EOF

          - name: Sign attestation
            env:
              COSIGN_EXPERIMENTAL: 1
            run: |
              cosign attest-blob \
                --predicate attestation.json \
                --type custom \
                --bundle attestation.bundle.json \
                ./dist/myartifact

          - name: Upload artifacts
            uses: actions/upload-artifact@v4
            with:
              name: signed-artifacts
              path: |
                ./dist/myartifact
                ./attestation.bundle.json

## Signing locally without OIDC

For local development where OIDC isn't available, key-pair is the
fallback:

    # One-time setup
    cosign generate-key-pair
    # Choose a strong passphrase; store in 1Password

    # Per-signing
    COSIGN_PASSWORD=<from-secrets> cosign attest-blob \
        --key cosign.key \
        --predicate attestation.json \
        --type custom \
        --bundle local-attestation.bundle.json \
        src/feature_foo.py

## Suppressing Rekor upload (private signing)

For attestations that shouldn't be in the public transparency log
(internal compliance, sensitive audit exports):

    cosign attest-blob \
        --predicate attestation.json \
        --type custom \
        --tlog-upload=false \
        --bundle private-attestation.bundle.json \
        artifact

Note: keyless signing requires Rekor for verification of certificate
validity. Suppressing Rekor only makes sense with key-pair signing.

For a private equivalent of Rekor, deploy Rekor in your own
infrastructure (`sigstore/rekor` is open source).

## Common errors and solutions

**"Error: error getting signer"**

The signer identity couldn't be established. For keyless:
- Confirm OIDC provider is reachable
- Confirm OIDC credentials are valid
- For CI: confirm workflow has `id-token: write` permission

**"Error: signature verification failed"**

The signature doesn't match the artifact. Possible causes:
- Artifact was modified after signing
- Wrong bundle file referenced
- Public key doesn't match the private key used for signing

**"Error: certificate has expired"**

For keyless: certificates are valid for 10 minutes. Re-sign.

**"Error: failed to retrieve Rekor entry"**

Rekor service unavailable, or Rekor URL misconfigured. Check:
- https://rekor.sigstore.dev/api/v1/log (status)
- `COSIGN_REKOR_URL` environment variable if using custom Rekor

## Integration with this framework

The audit-export workflow (planned in Commit 3) generates audit
attestations:

    /audit-export → creates audit-export-2026-05-12.zip
                  → generates in-toto statement with audit-export/v1 predicate
                  → signs with cosign (keyless if CI; key-pair if local)
                  → outputs both the zip and the bundle file

The spec-implementation workflow generates spec-to-code
attestations after `/implement` and `/review` complete successfully.

Each consuming framework provides its own automation; this
specification ensures uniform cryptographic operations.

## Key management for production

When the runtime governance framework (planned) emits attestations
for production agents:

- Production agents use long-lived ECDSA keys stored in KMS
  (AWS KMS, GCP KMS, HashiCorp Vault)
- Key rotation policies per organizational standard
- Public keys distributed via internal key directory
- All attestations also published to internal Rekor instance

This is more complex than the keyless build-time pattern but
necessary for production where ephemeral OIDC identities aren't
appropriate.

## Anti-patterns

- **Committing private keys to repos** — never; use KMS or
  password manager
- **Shared signing keys across multiple services** — defeats
  attestation-based attribution
- **Long-lived OIDC tokens** — defeats the keyless model's
  security properties
- **Signing without Rekor** — removes the ability to verify
  certificate non-revocation
- **Skipping verification** — signing without subsequent verification
  is performance theater

## References

- Cosign documentation: https://docs.sigstore.dev/cosign/overview
- Sigstore project: https://www.sigstore.dev
- Fulcio (certificate authority): https://github.com/sigstore/fulcio
- Rekor (transparency log): https://github.com/sigstore/rekor
- GitHub OIDC for Sigstore:
  https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect

## Revision history

    2026-05-12: Initial specification authored.
