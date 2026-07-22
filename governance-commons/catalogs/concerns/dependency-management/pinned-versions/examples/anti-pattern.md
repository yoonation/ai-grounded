<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.pinned-versions pinned versions (anti-patterns)

Substrate-original anti-pattern examples for dependency-management.pinned-versions.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Lockfile in .gitignore

```gitignore
# DO NOT DO THIS
node_modules/
package-lock.json   # lockfile excluded from version control
yarn.lock           # also excluded
```

Why this violates dependency-management.pinned-versions: the lockfile is THE
mechanism that pins versions. Excluding it from version
control means every install resolves differently;
reproducibility is gone. This is a surprisingly common
anti-pattern, often from misreading older Node.js
guidance.

## Anti-pattern B: CI uses non-strict install command

```yaml
# DO NOT DO THIS
- name: Install
  run: npm install   # may modify package-lock.json
```

Why this violates dependency-management.pinned-versions: `npm install` (without
`ci`) can modify the lockfile. If a new transitive
dependency is published between commit and CI, the
install resolves to it and rewrites the lockfile on disk.
The build is no longer reproducible from the committed
lockfile.

## Anti-pattern C: Wide version ranges in manifest with no lockfile

```python
# DO NOT DO THIS - requirements.txt with no lockfile
fastapi>=0.100
sqlalchemy>=2.0
pandas
# No requirements.lock; no pip-tools; install resolves
# differently across time and machines.
```

Why this violates dependency-management.pinned-versions: wide ranges without a
lockfile produce unreproducible installs. Two
deployments hours apart can have different transitive
graphs. Substrate-recommended pattern: pip-compile to
produce a hashed requirements.txt or use uv/Poetry/Pipenv.

## Anti-pattern D: Lockfile out of sync with manifest, ignored in CI

```yaml
# package-lock.json says express@4.18.2
# package.json says "express": "^5.0.0"
# CI:
- name: Install
  run: npm install --no-save  # silently accepts drift
```

Why this violates dependency-management.pinned-versions: the lockfile and manifest
have diverged. The install command does not surface the
drift. The two artifacts that should agree do not.

## Anti-pattern E: Floating tags in container build

```dockerfile
# DO NOT DO THIS
FROM node:latest
RUN apt-get update && apt-get install -y python3
COPY package.json /app/
WORKDIR /app
RUN npm install
```

Why this violates dependency-management.pinned-versions (extension to container
layer): `node:latest` is a floating tag; `apt-get
update && apt-get install` resolves to whatever is
current. The build is not reproducible. Substrate-
recommended pattern: pinned base image with digest
(`node:22.5.0@sha256:...`), pinned apt package
versions.

## Anti-pattern F: Vendored dependencies committed without manifest record

```text
# vendor/ directory contains 200 files copied from
# upstream projects. No manifest records which version
# was vendored. No update procedure.
```

Why this violates dependency-management.pinned-versions (in spirit): vendoring can
satisfy the rule's intent (capture exact versions) but
only with manifest discipline. Vendored content without
a manifest is unmanageable. Substrate-recommended: if
vendoring, commit a vendor.json or equivalent recording
upstream source and version.

## Anti-pattern G: Lockfile checked in but routinely deleted and regenerated

```text
# Team practice: "we always regenerate the lockfile
# before merging to main to pick up latest patches."
```

Why this violates dependency-management.pinned-versions (in spirit): regenerating
the lockfile at every merge defeats the lockfile's
purpose. The lockfile records what was tested;
regenerating it before merge means the tested state is
not the merged state. Substrate-recommended pattern:
update the lockfile in a dedicated update PR, run the
test suite, then merge.

## Anti-pattern H: Different lockfile generators across team

```text
# Contributor A uses npm; their PRs update
# package-lock.json.
# Contributor B uses yarn; their PRs update yarn.lock.
# Contributor C uses pnpm; their PRs update
# pnpm-lock.yaml.
# Repository has all three lockfiles, all stale.
```

Why this violates dependency-management.pinned-versions: multiple lockfile
generators produce drift. The "true" install resolution
depends on which generator the operator uses.
Substrate-recommended pattern: one ecosystem package
manager per project, documented in the README.

## Cross-reference

- Good patterns: examples/dependency-management/pinned-versions-good.md
- Substrate rule: dependency-management.pinned-versions
- Static analysis binding: binding.yaml
