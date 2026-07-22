<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Attestation Formats

Specifications for provenance and integrity attestations that
consuming frameworks emit. Attestations are signed claims about
artifacts: who built them, when, with what inputs, under what
conditions.

This directory does not contain attestation generators (those live
in consuming frameworks). It contains the format specifications
and integration guidance so that all consumers emit attestations
in compatible forms.

## Why attestation matters

AI-assisted development changes the trust calculus for software
artifacts. Traditional code review assumes humans authored the
code; AI-assisted code requires evidence of which decisions were
AI-influenced, what context the AI had, and what verification
occurred.

Attestation provides this evidence in machine-verifiable form:

- **Auditors** can verify "this code passed your review process"
  without re-running the review
- **Future maintainers** can understand "this function was written
  by AI in session X with these inputs"
- **Compliance frameworks** (EU AI Act Article 12, NIST AI RMF) get
  the record-keeping they require
- **Supply chain consumers** can verify "this dependency was built
  in a controlled environment by the project's official builders"

## The attestation stack

This commons uses a layered approach to attestation:

1. **SLSA** (Supply-chain Levels for Software Artifacts) — defines
   maturity levels of build provenance
2. **in-toto** — provides the underlying statement format SLSA
   provenance uses
3. **Sigstore (cosign, Fulcio, Rekor)** — provides keyless signing
   and transparency log infrastructure

See the individual files for each component:

- [slsa-v1.0-provenance.md](./slsa-v1.0-provenance.md)
- [in-toto-statement.md](./in-toto-statement.md)
- [cosign-signing.md](./cosign-signing.md)

## When to emit attestations

Consuming frameworks should emit attestations at these points:

| Trigger | Attestation type | Frequency |
|---|---|---|
| Successful build in CI | SLSA Provenance | Every build |
| Release tagged | SLSA Provenance + custom release attestation | Every release |
| `/audit-export` runs | Custom audit-record attestation | On demand |
| Specs-to-code generation | Custom spec-to-implementation attestation | Per generation event |
| Compliance evidence collection | Custom compliance attestation | Per audit window |

The pattern: any artifact that downstream consumers need to trust
gets an attestation. The attestation makes the trust verifiable.

## Attestation maturity goals

This commons aligns with SLSA's maturity levels:

- **SLSA Level 1**: Provenance is generated, but unsigned and
  unverified. Minimum viable.
- **SLSA Level 2**: Provenance is signed, builds happen in a
  hosted build platform. Targeted level for the build-time
  framework.
- **SLSA Level 3**: Build platform is hardened, non-falsifiable
  provenance. Future state.
- **SLSA Level 4**: Two-party review, hermetic builds. Out of
  scope for build-time framework.

The runtime governance framework (planned) will target SLSA Level
3 for production agent deployments.

## Custom attestations

Beyond SLSA Provenance, this framework defines custom attestations
for AI-specific concerns:

### AI-authorship attestation

Records that AI-assisted code was generated, what model and version,
what session, and what spec was followed.

    {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [{"name": "path/to/file.py", "digest": {"sha256": "..."}}],
      "predicateType": "https://example.org/ai-authorship/v1",
      "predicate": {
        "ai_actor": {
          "type": "ai_dev_tool",
          "name": "claude-code",
          "version": "1.0.4",
          "model": "claude-opus-4-7"
        },
        "session_id": "01HXYZW...",
        "spec_id": "specs/001-feature-foo/spec.md",
        "spec_hash": "sha256:...",
        "principal_human": "<github-handle>",
        "review_status": "approved",
        "review_session_id": "01HXYZX...",
        "audit_log_digest": "sha256:..."
      }
    }

### Audit-export attestation

Records the contents of an `/audit-export` run for compliance
evidence purposes.

    {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [{"name": "audit-export-2026-05-12.zip", "digest": {"sha256": "..."}}],
      "predicateType": "https://example.org/audit-export/v1",
      "predicate": {
        "time_window": {
          "start": "2026-05-01T00:00:00Z",
          "end": "2026-05-12T00:00:00Z"
        },
        "session_count": 42,
        "event_count": 1337,
        "compliance_tags_included": ["SOC2-CC6", "NIST-AI-RMF-MEASURE-2.7"],
        "audit_log_chain_verified": true,
        "redaction_applied": true
      }
    }

### Spec-to-implementation attestation

Records that a spec was implemented and verified.

    {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [{"name": "src/feature_foo.py", "digest": {"sha256": "..."}}],
      "predicateType": "https://example.org/spec-implementation/v1",
      "predicate": {
        "spec_path": "specs/001-feature-foo/spec.md",
        "spec_hash": "sha256:...",
        "spec_version": "1.2.0",
        "implementation_session": "01HXYZW...",
        "invariants_verified": [
          "all tests pass",
          "type-checker passes",
          "hooks did not block"
        ],
        "review_completed": true
      }
    }

## Verification

Each attestation type has a verification recipe in its respective
file. The general pattern:

1. Verify the signature (cosign verify-blob)
2. Verify the subject digest matches the artifact
3. Verify the predicate's claims (e.g., spec_hash matches the
   referenced spec)
4. Verify any chained attestations (audit_log_digest matches the
   actual audit log)

Verification can be done by:

- CI pipelines before merging or releasing
- Auditors during compliance review
- Future maintainers investigating an artifact's history

## Storage

Attestations are stored in two places:

- **Local**: alongside the artifact, in `attestations/` directory
  or as detached signatures. Pattern: `<artifact>.intoto.jsonl`
  for in-toto statements, `<artifact>.sig` for cosign signatures.
- **Public**: in Sigstore's Rekor transparency log, by default.
  Provides tamper-evident historical record.

For sensitive attestations (e.g., audit-export attestations that
reference internal session IDs), use private Rekor instances or
keep attestations local only.

## Implementation references

Consuming frameworks adapt these specs to their environments. See
the individual files for examples.

For developers building consumers of these specs, start with:

- [slsa-v1.0-provenance.md](./slsa-v1.0-provenance.md) for the
  baseline provenance shape
- [cosign-signing.md](./cosign-signing.md) for signing operations
- Then layer custom attestations as needed

## Anti-patterns

These attestation behaviors create problems:

- **Unsigned attestations** — defeats the purpose; anyone can
  forge claims
- **Self-signed without transparency log** — auditors can't
  verify the signing key wasn't compromised retrospectively
- **Attestations for "build successful" without specifying what
  built** — needs concrete digest of the produced artifact
- **Predicate types with no documentation** — opaque attestation
  is worse than no attestation
- **Reusing predicate types for incompatible meanings** — version
  predicate types when the schema changes
- **Including credentials in attestations** — predicates are
  public; redact like audit envelopes

## References

- SLSA: https://slsa.dev
- in-toto: https://in-toto.io
- Sigstore: https://www.sigstore.dev
- NIST SP 800-218 SSDF: see catalogs/compliance for OSCAL version
