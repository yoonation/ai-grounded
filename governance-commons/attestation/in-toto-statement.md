<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# in-toto Statement Format

Specification for in-toto statements that underlie all attestations
in this framework. SLSA Provenance is one specific kind of in-toto
statement; this commons defines several more (AI-authorship,
audit-export, spec-implementation).

## Why in-toto

in-toto provides a uniform structural envelope for any signed claim
about an artifact. By standardizing the envelope, this commons gets:

- Uniform signing operations (one cosign command works for all
  statement types)
- Uniform verification operations (one cosign-verify works for all)
- Uniform storage in transparency logs
- Predicate-specific semantics layered on top of common shape

## Statement structure

Every in-toto statement v1 has this shape:

    {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [
        {
          "name": "<artifact-identifier>",
          "digest": {"sha256": "<hex>"}
        }
      ],
      "predicateType": "<URI>",
      "predicate": {
        // Arbitrary structured data specific to the predicate type
      }
    }

### `_type`

Always exactly `https://in-toto.io/Statement/v1`. This identifies
the envelope schema. Statements not bearing this type are not
in-toto v1 statements.

### `subject`

Array of artifacts this statement is about. Each subject:

- `name`: How to identify the artifact. Can be a path, package
  name, container image reference, etc.
- `digest`: Cryptographic digest. SHA-256 standard. Multiple
  digest algorithms allowed simultaneously.

A statement may have multiple subjects when one claim applies to
multiple artifacts (e.g., "these 5 files were all generated in
this session"). Each subject is verifiable independently.

### `predicateType`

URI identifying what kind of claim the predicate makes. This is
the discriminator that tells verifiers how to interpret the
predicate.

Standard predicateTypes:

- `https://slsa.dev/provenance/v1` — SLSA build provenance
- `https://spdx.dev/Document` — SPDX SBOM
- `https://cyclonedx.org/bom/v1.5` — CycloneDX SBOM
- `https://in-toto.io/attestation/vulns/v0.1` — vulnerability scan

Custom predicateTypes for this framework (URIs you control):

- `https://example.org/ai-authorship/v1` — AI-generated code claim
- `https://example.org/audit-export/v1` — audit log export claim
- `https://example.org/spec-implementation/v1` — spec-to-code claim
- `https://example.org/compliance-evidence/v1` — compliance evidence

Replace `example.org` with the actual domain or namespace you
control. The URI doesn't need to resolve to anything; it just
needs to be a unique identifier.

### `predicate`

The structured data of the claim. Schema is determined by the
predicateType. Verifiers use predicateType to know how to parse
this field.

## Custom predicates for this framework

### `ai-authorship/v1`

Claim: an AI-assisted authoring session generated or modified this
artifact.

    {
      "ai_actor": {
        "type": "<actor-type>",   // ai_dev_tool | ai_sub_agent | production_agent
        "name": "<tool-name>",     // e.g., claude-code, cursor
        "version": "<tool-version>",
        "model": "<model-string>"  // e.g., claude-opus-4-7
      },
      "session_id": "<ulid>",
      "spec_id": "<path-or-id>",   // optional; the spec being implemented
      "spec_hash": "<digest>",     // optional; hash of the spec at generation time
      "principal_human": "<id>",   // human ultimately responsible
      "review_status": "<status>", // pending | approved | rejected
      "review_session_id": "<ulid>", // optional; the review session
      "audit_log_digest": "<digest>" // hash of relevant audit log section
    }

**Required fields**: `ai_actor`, `session_id`, `principal_human`

**Optional fields**: everything else

### `audit-export/v1`

Claim: an audit log export was performed with the listed contents.

    {
      "time_window": {
        "start": "<RFC3339>",
        "end": "<RFC3339>"
      },
      "session_count": <integer>,
      "event_count": <integer>,
      "compliance_tags_included": [<list of tag strings>],
      "audit_log_chain_verified": <boolean>,
      "redaction_applied": <boolean>,
      "exporter": {
        "type": "<actor-type>",
        "id": "<actor-id>"
      },
      "redaction_policy_id": "<policy-id>",
      "export_format": "<format>"   // jsonl | csv | pdf
    }

**Required fields**: `time_window`, `session_count`, `event_count`,
`audit_log_chain_verified`, `exporter`

### `spec-implementation/v1`

Claim: a spec was implemented and verified.

    {
      "spec_path": "<path>",
      "spec_hash": "<digest>",
      "spec_version": "<version>",
      "implementation_session": "<ulid>",
      "invariants_verified": [<list of strings>],
      "invariant_evidence": {
        "tests_passed": <boolean>,
        "type_check_passed": <boolean>,
        "hooks_no_blocks": <boolean>,
        "review_approved": <boolean>
      },
      "review_completed": <boolean>,
      "principal_human": "<id>"
    }

**Required fields**: `spec_path`, `spec_hash`, `implementation_session`,
`invariants_verified`

### `compliance-evidence/v1`

Claim: a body of evidence supports a specific compliance assertion.

    {
      "compliance_framework": "<framework-id>",   // SOC2 | NIST-800-53 | EU-AI-ACT
      "control_id": "<control-id>",
      "control_version": "<version>",
      "evidence_artifacts": [
        {
          "name": "<artifact>",
          "digest": "<digest>",
          "type": "<artifact-type>"   // audit-log | code-review | test-results | etc
        }
      ],
      "assertion_period": {
        "start": "<RFC3339>",
        "end": "<RFC3339>"
      },
      "assertion": "<text>",
      "evaluator": {
        "type": "<actor-type>",
        "id": "<id>"
      }
    }

## Signing statements

in-toto statements are signed as DSSE (Dead Simple Signing Envelope)
payloads. The result:

    {
      "payloadType": "application/vnd.in-toto+json",
      "payload": "<base64-encoded statement>",
      "signatures": [
        {
          "keyid": "<key identifier>",
          "sig": "<base64 signature>"
        }
      ]
    }

Use cosign for the actual signing operation. See cosign-signing.md
for the workflow.

## Storage and retrieval

### Local storage

Statements stored alongside artifacts:

    src/
    ├── feature_foo.py
    └── feature_foo.py.intoto.jsonl   # contains DSSE-wrapped statement(s)

For multiple statements about one artifact, append to the .jsonl
file (one statement per line).

### Transparency log storage

cosign signs and uploads to Rekor (Sigstore transparency log) by
default. Provides:

- Tamper-evident historical record
- Public discoverability of attestations
- Independent verification path

For sensitive attestations, suppress Rekor upload with
`cosign sign --no-tlog-upload` or use private Rekor instance.

## Verification flow

1. Retrieve the DSSE envelope
2. Verify signature with cosign-verify-attestation
3. Decode the payload to get the in-toto statement
4. Verify the subject digest matches the artifact you have
5. Parse predicateType to determine semantic
6. Verify predicate-specific claims (e.g., spec_hash matches actual
   spec content)
7. Chain to other attestations if predicate references them

A complete verification may involve verifying multiple chained
attestations (e.g., AI-authorship references audit_log_digest;
verifier may want to verify the audit log itself is intact).

## Versioning predicate types

When a predicate's schema changes incompatibly, bump the version
in the URI:

- `https://example.org/ai-authorship/v1`
- `https://example.org/ai-authorship/v2`

Verifiers branch on the version. Old attestations remain verifiable
under their original schema.

Compatible additions (new optional fields) don't require version
bumps; verifiers tolerate unknown fields.

## Anti-patterns

- **Custom envelope formats** — defeats the in-toto interoperability
  benefit
- **Predicates with no documentation** — opaque attestation is
  worse than no attestation
- **Unversioned predicateTypes** — schema evolution becomes
  impossible
- **Inlining the artifact content** — predicates are public; only
  reference by digest, never include content
- **Multiple semantic claims in one predicate** — keep predicates
  focused on one kind of claim

## References

- in-toto Statement v1:
  https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- in-toto Attestations:
  https://github.com/in-toto/attestation
- DSSE specification:
  https://github.com/secure-systems-lab/dsse
- Predicate examples:
  https://github.com/in-toto/attestation/tree/main/spec/predicates

## Revision history

    2026-05-12: Initial specification authored.
