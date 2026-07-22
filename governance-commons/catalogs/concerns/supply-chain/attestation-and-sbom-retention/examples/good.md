<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.attestation-and-sbom-retention attestation and SBOM retention

Substrate-recommended retention discipline with audit trail.

## Pattern A: OCI registry referrers-attached retention

After release, the consumer's registry stores:

```
registry.example.com/api:v2.4.1
registry.example.com/api@sha256:abc123...
  ├─ application/vnd.dev.cosign.simplesigning.v1+json   (signature)
  ├─ application/vnd.in-toto+json [predicate: slsaprovenance1]   (SLSA provenance)
  ├─ application/vnd.cyclonedx+json [predicate: cyclonedx]   (SBOM attestation)
  └─ application/vnd.in-toto+json [predicate: vuln]   (vuln-scan attestation)
```

Retrieved via:

```bash
cosign tree "registry.example.com/api@sha256:abc123..."
```

## Pattern B: Dependency-Track retention surface

Consumer operates a Dependency-Track instance for SBOM-aware
retention:

```bash
# Query: which deployed releases use cryptography 41.x?
curl -H "X-Api-Key: ${DT_API_KEY}" \
  "${DT_URL}/api/v1/component?name=cryptography&version=41" \
  | jq '.[] | {project: .project.name, version: .project.version}'
```

During incident response (e.g., advisory on cryptography
41.0.0), this query returns all production releases that
contained the affected version. Retrieval completes within seconds.

## Pattern C: Retention policy file

`docs/supply-chain/retention-policy.md`:

```markdown
# Attestation and SBOM Retention Policy

**Profile:** production-grade-baseline
**Retention window:** 3 years

## Storage surfaces

| Artifact Type | Primary Store | Replication |
|---------------|---------------|-------------|
| SLSA provenance | OCI referrers + Rekor public log | None (Rekor is the immutable log) |
| Signature | OCI referrers + Rekor | None |
| CycloneDX SBOM | OCI referrers + Dependency-Track | S3 bucket (versioned, lifecycle policy 3 years) |
| Vuln-scan attestation | OCI referrers | S3 bucket |

## Access controls

- **Write:** github-actions release workflow service account
  (OIDC-bound) and security-team service account; authorization.least-privilege-role-design
  least-privilege enforced
- **Read:** all engineers via Dependency-Track UI; security team
  via OCI registry direct access; CI gates via service-account
  read-only credentials

## Audit trail

- Dependency-Track audit log: retained 3 years, integrity per
  logging.integrity (S3 object versioning + lifecycle policy)
- OCI registry audit log: AWS CloudTrail (encrypted, retention
  matches consumer's profile)

## Most recent retrieval test

2026-05-01: randomly-selected 5 releases from past 90 days;
all attestations retrievable in under 60 seconds.
```

## Pattern D: Audit trail entry

```json
{
  "timestamp": "2026-05-23T14:23:17Z",
  "subject": "alice@example.com (oidc: token.actions.githubusercontent.com)",
  "action": "retrieve",
  "target": "registry.example.com/api@sha256:abc123...",
  "artifact-type": "slsaprovenance1",
  "result": "success",
  "retrieval-time-ms": 423
}
```

## Key observations

- Multiple retention surfaces (OCI, Dependency-Track, S3) reduce
  single-point-of-failure risk
- Access controls enforce write-only-from-CI and read-via-
  service-account patterns
- Audit trail records retrieval events for incident-response
  forensics
