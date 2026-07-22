<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.signature-verification signature verification absent or defeated

Substrate-rejected patterns.

## Anti-pattern A: signed artifact consumed without verification

```yaml
- name: Pull and deploy
  run: |
    # Image is signed upstream but consumer does not verify
    docker pull "registry.example.com/upstream-tool:v2.1.0"
    ./deploy.sh
```

The upstream signature exists but is not consulted. A registry
account compromise can substitute an unsigned or differently-
signed image; the consumer cannot tell the difference.

## Anti-pattern B: verification with no signer-identity policy

```yaml
- name: Verify (substrate-rejected)
  run: |
    # Verifies *some* signature exists but does not pin signer
    cosign verify "registry.example.com/api:${VERSION}"
```

Any valid signature passes, including a signature from an
attacker who obtained any OIDC-issued identity certificate from
any supported issuer.

## Anti-pattern C: npm signature warnings suppressed

```yaml
- name: Install
  run: |
    # Substrate-rejected: --no-audit suppresses signature checks
    npm install --no-audit
```

Or:

```bash
npm audit signatures || true
```

The signature check runs but its failure does not block the
build.

## Anti-pattern D: long-lived signing key with no rotation

```yaml
# Substrate-rejected: signing private key in CI secret store,
# no rotation discipline, no expiry policy
- name: Sign release
  env:
    GPG_SIGNING_KEY: ${{ secrets.GPG_KEY_DO_NOT_TOUCH }}  # First created 2019
  run: |
    echo "${GPG_SIGNING_KEY}" | gpg --import
    gpg --armor --detach-sign release-binary
```

The `DO_NOT_TOUCH` naming pattern indicates substrate-rejected
key management: keys that cannot be rotated cannot recover from
compromise.

## Why these patterns fail

Signature verification's value is in the consumer's policy
enforcement: a signature exists is not sufficient; the signature
must come from a specific signer the consumer has accepted.
Anti-patterns above either skip verification or enforce no
identity policy.
