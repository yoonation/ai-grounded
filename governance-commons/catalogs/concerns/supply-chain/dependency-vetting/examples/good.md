<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.dependency-vetting dependency vetting

Substrate-recommended vetting artifact at adoption time.

## Example vetting artifact

`docs/dependency-vetting/pypi-httpx-0.27.0.md`:

```markdown
# Vetting: httpx 0.27.0 (PyPI)

**Adoption date:** 2026-05-23
**Approver:** alice@example.com (engineering-manager-platform)
**Tier classification:** tier-1 critical (on the HTTP-request hot path)

## Identity

- Package name: `httpx`
- Ecosystem: PyPI
- Version pin: `httpx==0.27.0`
- Publisher: encode (Tom Christie + maintainers)
- Publisher URL: https://github.com/encode/httpx
- License: BSD-3-Clause (substrate-acceptable for our distribution)

## Substrate-recognized signals

- SBOM available at upstream releases: yes (via GitHub release assets)
- SLSA provenance attestation: yes (npm-style provenance via
  PyPI Trusted Publishing since 0.26.0)
- Signing posture: Sigstore-signed via PEP 740 attestations
- OpenSSF Best Practices badge: passing
- OpenSSF Scorecard: 8.4/10 (substrate-acceptable tier-1 baseline)
- Most-recent release: 2026-04-12 (recent)
- Maintainer activity: 47 commits in last 90 days; 8 distinct
  contributors in last year (active)

## Architectural fit

**Problem solved:** async HTTP client with HTTP/2 support; the
requests library does not support async natively, and our
substrate-recommended async pattern (asyncio-based) requires
async HTTP.

**Alternatives considered:**
- aiohttp: substrate-acceptable; rejected because httpx's API is
  more similar to requests (smoother migration path for the team)
- requests + sync-to-async wrappers: substrate-rejected because
  the wrapper layer adds operational complexity

**Exit strategy:** if httpx is deprecated, migrate to aiohttp
(estimated 2-3 week effort given current usage surface).

## Audit obligations

- supply-chain.critical-dependency-audit audit cadence: quarterly (tier-1)
- Next audit: 2026-08-23
- Audit owner: platform team
- Deprecation triggers: no commits in 18 months, OpenSSF Scorecard
  regression below 6.0, license change to non-BSD-compatible

## Cross-references

- supply-chain.supply-chain-integrity-strategy ADR: docs/decisions/ADR-007-supply-chain-strategy.md
- supply-chain.vulnerability-disclosure-response runbook section: docs/runbooks/vuln-response.md#http-client
- supply-chain.critical-dependency-audit tier inventory: docs/dependency-inventory.md#tier-1
```

## Key observations

- Every vetting question from the supply-chain.dependency-vetting review checklist
  is addressed with a substantive answer or an explicit "not
  available" with rationale
- Cross-references are concrete paths; broken cross-references
  block merge of the vetting artifact
- The artifact is committed alongside the lockfile change that
  introduces the dependency; CI gates verify both exist
