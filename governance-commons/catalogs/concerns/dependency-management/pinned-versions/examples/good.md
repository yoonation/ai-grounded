<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.pinned-versions pinned versions (good patterns)

Substrate-original good-pattern examples for dependency-management.pinned-versions.

## Pattern A: npm with package-lock.json

```json
// package.json (manifest)
{
  "name": "my-app",
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.0"
  }
}
```

```json
// package-lock.json (lockfile) - committed to repo
{
  "lockfileVersion": 3,
  "packages": {
    "node_modules/express": {
      "version": "4.18.2",
      "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
      "integrity": "sha512-..."
    }
  }
}
```

```yaml
# .github/workflows/ci.yml
- name: Install dependencies
  run: npm ci  # uses lockfile strictly; fails on drift
```

Why this satisfies dependency-management.pinned-versions: lockfile is committed;
CI uses `npm ci` (strict mode) which fails when the
lockfile and manifest disagree; every package has a
resolved version and integrity hash.

## Pattern B: Python with uv lockfile

```toml
# pyproject.toml (manifest)
[project]
name = "my-app"
dependencies = [
    "fastapi>=0.104",
    "sqlalchemy>=2.0",
]
```

```toml
# uv.lock (lockfile) - committed to repo
[[package]]
name = "fastapi"
version = "0.104.1"
source = { registry = "https://pypi.org/simple" }
sdist = { hash = "sha256:..." }
wheels = [
    { hash = "sha256:..." },
]
```

```yaml
# CI
- name: Install
  run: uv sync --frozen  # fails on lockfile drift
```

Why this satisfies dependency-management.pinned-versions: uv.lock committed; CI
uses `--frozen` which fails on drift; every package has
hashes; resolution is reproducible.

## Pattern C: Go with go.sum verification

```go
// go.mod (manifest)
module example.com/my-app

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/jackc/pgx/v5 v5.5.0
)
```

```text
# go.sum (lockfile) - committed to repo
github.com/gin-gonic/gin v1.9.1 h1:4idEAncQnU5cB7BeOkPtxjfCSye0AAm1R0RVIqJ+Jmg=
github.com/gin-gonic/gin v1.9.1/go.mod h1:hPrL7YrpYKXt5YId3A/Tnip5kqbEAP+KLuI3SUcPTeU=
```

```yaml
# CI
- name: Verify dependencies
  run: go mod verify
- name: Build
  run: go build ./...
```

Why this satisfies dependency-management.pinned-versions: go.mod and go.sum both
committed; `go mod verify` confirms hashes match; the
build is reproducible from go.sum alone.

## Pattern D: Rust with Cargo.lock and --locked

```toml
# Cargo.toml (manifest)
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
```

```text
# Cargo.lock - committed for binary crates
[[package]]
name = "tokio"
version = "1.35.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "841d45b238a16291a4e1584e61820b8ae57d696cc5015c459c229ccc6990cc1c"
```

```yaml
# CI
- name: Build with locked dependencies
  run: cargo build --locked --release
```

Why this satisfies dependency-management.pinned-versions: Cargo.lock committed;
`--locked` flag fails if Cargo.lock would change; every
crate has a checksum from crates.io.

## Pattern E: Pre-commit hook for lockfile drift

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: lockfile-sync
        name: Lockfile in sync with manifest
        entry: bash -c 'npm ci --dry-run && pip-compile --quiet --dry-run requirements.in'
        language: system
        files: ^(package\.json|package-lock\.json|requirements\.in|requirements\.txt)$
        pass_filenames: false
```

Why this satisfies dependency-management.pinned-versions (defense in depth):
catches lockfile drift at commit time, before it reaches
CI. Contributors get fast feedback rather than waiting
for CI failure.

## Cross-reference

- Anti-patterns: examples/dependency-management/pinned-versions-anti-pattern.md
- Substrate rule: dependency-management.pinned-versions
- Static analysis binding: binding.yaml
