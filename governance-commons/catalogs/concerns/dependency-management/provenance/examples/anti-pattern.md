<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.provenance provenance (anti-patterns)

Substrate-original anti-pattern examples for dependency-management.provenance.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Dependencies from arbitrary git URLs

```json
// DO NOT DO THIS
{
  "dependencies": {
    "useful-lib": "git+https://github.com/random-user/forked-useful-lib#main"
  }
}
```

Why this violates dependency-management.provenance: a git URL with a branch
reference (not a tag or commit hash) resolves
differently over time. The fork's owner can change the
code after the dependency is added. No registry-level
provenance applies. Substrate-recommended pattern: pin
to a specific commit hash AND maintain a fork rationale
in the dependency review record.

## Anti-pattern B: No hash verification

```text
# DO NOT DO THIS - requirements.txt without hashes
fastapi==0.104.1
sqlalchemy==2.0.23
# Versions are pinned but the artifact content is not
# verified.
```

Why this violates dependency-management.provenance: pinning a version without
a hash does not detect artifact substitution at the
registry. The substrate-recommended pattern requires
hash verification (pip --require-hashes, npm integrity,
go.sum).

## Anti-pattern C: Build script downloads from arbitrary URLs

```dockerfile
# DO NOT DO THIS
RUN curl -L https://example.com/some-binary > /usr/local/bin/some-binary && \
    chmod +x /usr/local/bin/some-binary
# No hash, no signature, no provenance.
```

Why this violates dependency-management.provenance: the URL can return
different content over time; no signature verification;
no record of what was installed. Substrate-recommended
pattern: download via a package manager with hash
verification, or `curl -L --output ... && sha256sum -c
expected-hash.txt`.

## Anti-pattern D: Provenance attestations ignored

```yaml
# DO NOT DO THIS
- name: Install
  run: npm install --ignore-scripts
  # npm audit signatures is never run
  # provenance attestations are unverified
```

Why this violates dependency-management.provenance: the upstream provides
provenance (Sigstore-backed) but the project does not
verify. The strongest available signal is unused.
Substrate-recommended pattern: `npm audit signatures`
in CI for packages with provenance attestations.

## Anti-pattern E: No scoping for private packages

```ini
# DO NOT DO THIS - .npmrc
registry=https://registry.npmjs.org/
# No scoped registry config. A name-squatting public
# package can shadow an internal package of the same
# name.
```

Why this violates dependency-management.provenance (dependency confusion):
internal package names without scope configuration are
vulnerable to public packages of the same name being
installed. Substrate-recommended pattern: use a scoped
package name (@example/internal-pkg) AND configure the
scope to resolve only against the internal registry.

## Anti-pattern F: Dependencies under deny-listed licenses

```text
# Production dependency tree includes:
- some-lib: GPL-3.0  (potentially incompatible with
  proprietary distribution)
- other-lib: SSPL-1.0  (typically deny-listed for SaaS)
- third-lib: UNKNOWN  (license not declared)
# License posture per ADR allows only permissive
# licenses (MIT, Apache-2.0, BSD, ISC).
```

Why this violates dependency-management.provenance (license property): the
license posture documented in the consumer's ADR is not
enforced. Substrate-recommended pattern: license check
runs in CI; non-allow-listed licenses fail the build.

## Anti-pattern G: No SBOM generated

```text
# Build produces a container image with hundreds of
# dependencies. No SBOM is generated. No record of what
# was shipped.
```

Why this violates dependency-management.provenance (SBOM property): without
an SBOM, the consumer cannot enumerate what is in the
artifact. Vulnerability response is reactive rather than
proactive. Substrate-recommended pattern: generate SBOM
at build time; sign with cosign; archive with the build.

## Anti-pattern H: Manual provenance review skipped under time pressure

```text
# Team practice: when a deadline is tight, dependency
# additions are merged without the provenance review.
# The review will "happen later" but rarely does.
```

Why this violates dependency-management.provenance (process property): the
provenance review exists in policy but not in practice.
Substrate-recommended pattern: the review is required by
the merge gate; deadlines do not bypass it.

## Cross-reference

- Good patterns: examples/dependency-management/provenance-good.md
- Substrate rule: dependency-management.provenance
- Review checklist: checklist.md
