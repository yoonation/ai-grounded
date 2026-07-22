<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.attestation-and-sbom-retention retention discipline absent

Substrate-rejected patterns.

## Anti-pattern A: no retention surface

The consumer generates SBOMs and attestations at release time but
does not retain them after CI completes. The CI workspace is the
only location; after 90 days, GitHub Actions garbage-collects the
artifacts and they are gone.

When an advisory drops three months later, the consumer cannot
query "which deployed releases contain the affected component"
without rebuilding each release.

## Anti-pattern B: retention exists but no append-only property

```yaml
# S3 bucket without versioning, without object lock
Bucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: supply-chain-attestations
    # VersioningConfiguration omitted
    # ObjectLockConfiguration omitted
```

An attacker who gains write access can overwrite or delete
historical attestations to conceal a prior compromise. Substrate-
recommended: object versioning enabled with retention policy
matching the consumer's profile, or object lock in compliance
mode.

## Anti-pattern C: retention without audit trail

The consumer retains attestations but does not log access:

```yaml
# S3 bucket logging disabled
Bucket:
  Properties:
    LoggingConfiguration: {}  # No access logs
```

The retention surface exists but the consumer cannot answer "who
accessed which attestations when" during incident response.

## Anti-pattern D: retrieval test never performed

The retention surface holds three years of artifacts, but no
substrate-recommended retrieval test has been run. When the first
real incident requires retrieval, latent infrastructure issues
(IAM misconfiguration, expired credentials, missing client
tooling) surface under pressure.

## Anti-pattern E: deployed-vs-retained digest mismatch

A retention audit reveals:

- Deployed api v2.3.1 digest: `sha256:abc...`
- Retained SLSA provenance for v2.3.1 attests digest: `sha256:def...`

The retained attestation does not match the deployed artifact.
Either the wrong artifact was deployed, the wrong attestation was
retained, or an attacker substituted one of them. Substrate-
recommends incident response.

## Why these patterns fail

Retention's value is realized at incident-response time. Each
anti-pattern degrades the response capability: absence (A)
prevents response; mutability (B) defeats forensic integrity;
no audit (C) prevents forensic reasoning; untested retrieval (D)
surfaces infrastructure failures under pressure; deployed-vs-
retained mismatch (E) is a substrate-recognized incident
indicator.
