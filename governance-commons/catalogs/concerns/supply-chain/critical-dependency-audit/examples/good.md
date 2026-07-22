<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.critical-dependency-audit critical dependency audit

Substrate-recommended tiered inventory with cadence.

## Pattern A: Dependency inventory file

`docs/dependency-inventory.md`:

```markdown
# Production Dependency Inventory

**Last reviewed:** 2026-05-23

## Tier-1 (Critical) - Quarterly Audit

| Dependency | Version | Ecosystem | Vetting Artifact | Last Audit |
|------------|---------|-----------|------------------|------------|
| cryptography | 42.0.5 | PyPI | [vet](dependency-vetting/pypi-cryptography-42.0.5.md) | 2026-04-15 |
| httpx | 0.27.0 | PyPI | [vet](dependency-vetting/pypi-httpx-0.27.0.md) | 2026-05-23 |
| sqlalchemy | 2.0.29 | PyPI | [vet](dependency-vetting/pypi-sqlalchemy-2.0.29.md) | 2026-04-15 |
| express | 4.19.2 | npm | [vet](dependency-vetting/npm-express-4.19.2.md) | 2026-03-30 |
| ubuntu | 24.04 | OCI | [vet](dependency-vetting/oci-ubuntu-24.04.md) | 2026-04-01 |

## Tier-2 (Important) - Semi-Annual Audit

| Dependency | Version | Ecosystem | Vetting Artifact | Last Audit |
|------------|---------|-----------|------------------|------------|
| prometheus-client | 0.20.0 | PyPI | [vet](dependency-vetting/pypi-prometheus-client-0.20.0.md) | 2026-01-10 |
| structlog | 24.1.0 | PyPI | [vet](dependency-vetting/pypi-structlog-24.1.0.md) | 2026-02-20 |

## Tier-3 (Commodity) - Annual Audit

| Dependency | Version | Ecosystem | Vetting Artifact | Last Audit |
|------------|---------|-----------|------------------|------------|
| python-dateutil | 2.9.0 | PyPI | [vet](dependency-vetting/pypi-python-dateutil-2.9.0.md) | 2025-08-15 |
| colorlog | 6.8.2 | PyPI | [vet](dependency-vetting/pypi-colorlog-6.8.2.md) | 2025-09-22 |
```

## Pattern B: Audit record example

`docs/dependency-audits/2026-04-15-cryptography.md`:

```markdown
# Audit: cryptography 42.0.5 (PyPI) - Q2 2026

**Audit date:** 2026-04-15
**Tier:** tier-1 critical
**Auditor:** security-team
**Previous audit:** 2026-01-15
**Next audit due:** 2026-07-15

## Signal drift

- Maintainer activity: 52 commits in last 90 days (was 48 last
  audit; stable)
- OpenSSF Scorecard: 9.2/10 (was 9.1; minor improvement)
- Release recency: most recent release 2026-04-09 (within window)
- Signing posture: Sigstore-signed via PEP 740 (unchanged)
- SBOM availability: yes (unchanged)
- Provenance attestation: yes (unchanged)

**Verdict:** no substantive drift; continue at tier-1.

## Advisory history

- CVE-2026-30474: pyca/cryptography vulnerability in RSA OAEP
  decryption (CVSS 5.3). Patched in 42.0.5; consumer running
  42.0.5; not affected.

**Verdict:** no open advisories affecting consumer.

## Deprecation triggers evaluated

- Maintainer abandonment: no
- Upstream sunset: no
- Persistent unpatched advisory: no
- License change: no (Apache-2.0/BSD)
- Ecosystem migration: no

**Verdict:** no triggers fired.

## Continued-adoption decision

Continue at tier-1. Next audit 2026-07-15.
```

## Key observations

- The inventory enumerates every production dependency at a tier
- Each tier has a substrate-recommended cadence; the audit
  records demonstrate the cadence is being met
- Audit records cite specific signal values to make drift visible
