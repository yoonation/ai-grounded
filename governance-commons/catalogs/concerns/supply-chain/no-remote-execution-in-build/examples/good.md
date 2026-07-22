<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.no-remote-execution-in-build no remote execution in build

Substrate-accepted alternatives to remote-execution patterns.

## Pattern A: pre-built and digest-pinned container base

```dockerfile
# Substrate-accepted: pre-built tool image, digest-pinned
FROM ghcr.io/sigstore/cosign/cosign:v2.4.1@sha256:9c8d5f3e... AS tools

FROM cgr.dev/chainguard/static:latest@sha256:f4f47c...
COPY --from=tools /ko-app/cosign /usr/local/bin/cosign
```

The tool's installation is built into the consumer's substrate-
trusted base image; the runtime Dockerfile never fetches code
from the network.

## Pattern B: checksum-verified binary download

```bash
#!/bin/bash
# install-tool.sh - substrate-accepted

set -euo pipefail

TOOL_VERSION="2.4.1"
TOOL_SHA256="d3a1f2b8c4e5..."  # substrate-required pinned hash
TOOL_URL="https://github.com/org/tool/releases/download/v${TOOL_VERSION}/tool-linux-amd64"

# Substrate-accepted: download then verify before execute
curl -fsSL "${TOOL_URL}" -o tool
echo "${TOOL_SHA256}  tool" | sha256sum --check
chmod +x tool
./tool --version
```

## Pattern C: ecosystem package manager with lockfile

```dockerfile
# Substrate-accepted: ecosystem-native installation with pinned versions
FROM python:3.12-slim@sha256:abc...

WORKDIR /app
COPY requirements.txt .
# pip install with hash verification from requirements.txt
RUN pip install --require-hashes --no-deps -r requirements.txt
```

The `requirements.txt` lockfile contains `--hash=sha256:...` for
each dependency; pip refuses to install if the hash does not
match.

## Pattern D: CI-native action with provenance

```yaml
# Substrate-accepted: action with SHA pin and SLSA provenance
- name: Setup Cosign
  uses: sigstore/cosign-installer@4959ce089c160ce0b7e1ec3a72e22e22b9fed5e2  # v3.5.0
```

The action is itself digest-pinned per supply-chain.digest-pinned-artifacts; the action's
publisher operates a SLSA-compliant build pipeline.

## Pattern E: substrate-rejected installer wrapped in checksum

```bash
#!/bin/bash
# install-rustup.sh - substrate-accepted alternative

set -euo pipefail

# Substrate-accepted: download rustup-init separately, verify
# checksum, then run; not "curl | sh"
RUSTUP_INIT_SHA256="a3339fb004c3d0bb9862ba0bce001861fe5cbde9c10d16591eb3f39ee6cd3e7f"
curl -fsSL https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init -o rustup-init
echo "${RUSTUP_INIT_SHA256}  rustup-init" | sha256sum --check
chmod +x rustup-init
./rustup-init -y --default-toolchain stable
```

## Key observations

- Every legitimate need (install a tool, fetch a dependency, run
  an installer) has a substrate-accepted alternative
- The substrate accepts that upstream installer documentation
  often shows curl-pipe-shell; the consumer's responsibility is
  to translate to the substrate-accepted form
- Checksums are pinned in source; if upstream rotates a binary,
  the build fails noisily until the consumer reviews and updates
