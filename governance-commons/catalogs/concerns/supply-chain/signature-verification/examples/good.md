<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.signature-verification signature verification

Substrate-recommended signature verification with OIDC-bound
signer-identity policy.

## Pattern A: cosign verification with explicit signer identity

```yaml
- name: Verify image signature
  run: |
    cosign verify \
      --certificate-identity-regexp '^https://github\.com/myorg/myrepo/\.github/workflows/release\.yaml@refs/tags/v[0-9]+\.[0-9]+\.[0-9]+$' \
      --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
      "registry.example.com/api:${VERSION}@${DIGEST}"
```

The identity pattern pins the expected signer (the consumer's
release workflow); the OIDC issuer pins the trust anchor.

## Pattern B: Allowed-signers policy file consumed by verification

The substrate-recommended policy file at
`policy/allowed-signers.yaml`:

```yaml
# SPDX-License-Identifier: <consumer-internal>
# Reviewed: 2026-05-23, owner: security-team@example.com
production:
  - issuer: "https://token.actions.githubusercontent.com"
    identity-pattern: "^https://github\\.com/myorg/api/\\.github/workflows/release\\.yaml@refs/tags/v[0-9]+\\.[0-9]+\\.[0-9]+$"
    description: "Production releases via myorg/api release workflow"
staging:
  - issuer: "https://token.actions.githubusercontent.com"
    identity-pattern: "^https://github\\.com/myorg/api/\\.github/workflows/staging\\.yaml@refs/heads/main$"
    description: "Staging builds via myorg/api staging workflow"
```

The CI gate parses the policy and invokes cosign per environment.
The policy file is itself version-controlled and reviewed under
authorization.least-privilege-role-design.

## Pattern C: npm package signature verification

```yaml
- name: Verify npm package signatures
  run: |
    # Reject if any package fails signature verification
    npm audit signatures
    if [ "$?" -ne 0 ]; then
      echo "Signature verification failed"
      exit 1
    fi
```

## Pattern D: Verifying a signed git tag at release time

```bash
#!/bin/bash
# release.sh - substrate-recommended pre-release verification

set -euo pipefail

RELEASE_TAG="$1"

# Verify tag signature before building from this tag
git fetch --tags
if ! git verify-tag "${RELEASE_TAG}" 2>&1; then
  echo "Tag ${RELEASE_TAG} signature verification failed; aborting release"
  exit 1
fi

# Verify commit signature on the tagged commit
COMMIT=$(git rev-list -n 1 "${RELEASE_TAG}")
if ! git verify-commit "${COMMIT}" 2>&1; then
  echo "Commit ${COMMIT} signature verification failed; aborting release"
  exit 1
fi

echo "Signature verification passed; proceeding with build"
./build.sh "${RELEASE_TAG}"
```

## Key observations

- OIDC issuer pinning is substrate-required; wildcard issuer
  acceptance defeats the trust anchor
- The allowed-signers policy is per-environment (production
  signers distinct from staging signers); stricter profiles
  require explicit per-environment lists
- Signature verification and provenance verification compose;
  both gates run in production deployment pipelines
