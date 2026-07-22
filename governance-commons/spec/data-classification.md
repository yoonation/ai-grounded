<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Data Classification

Defines the data sensitivity taxonomy used by consuming frameworks to
make access decisions. AI tools, hooks, and policies reference these
levels to determine what AI can read, what requires human approval,
and what must never appear in audit logs.

## Levels

Five levels, ordered from least to most sensitive.

### Level 0: Public

Information intended for unrestricted distribution.

**Examples**:
- Open-source code in public repos
- Public API documentation
- Marketing content
- Published threat models

**AI access**: Unrestricted read and reasoning. Safe to include in
prompts to external LLM providers.

**Audit treatment**: Full path may appear in audit log.

### Level 1: Internal

Information intended for organizational use, not externally
distributed but not restricted within the organization.

**Examples**:
- Internal documentation
- Non-customer-facing code
- Engineering wikis
- Build logs without secrets

**AI access**: Read allowed. Reasoning allowed. Inclusion in prompts
to external LLM providers governed by organizational policy (most
organizations allow this; some require enterprise-tier LLM agreements).

**Audit treatment**: Full path may appear in audit log.

### Level 2: Confidential

Information restricted to specific teams or roles within an
organization. Disclosure outside that scope is a controlled event.

**Examples**:
- Customer data analytics (without PII)
- Pre-release product specifications
- Pricing strategy documents
- Internal financial reports

**AI access**: Read requires explicit human approval per session.
Reasoning allowed once approved. Inclusion in prompts to external
LLM providers typically requires enterprise-tier agreement with
zero-retention guarantees.

**Audit treatment**: Path hash in audit log; full path requires
elevated audit access.

### Level 3: Restricted

Information requiring formal access controls. Unauthorized disclosure
has material consequences (contractual, regulatory, financial).

**Examples**:
- PII subject to GDPR/CCPA
- PHI subject to HIPAA
- Cardholder data subject to PCI DSS
- Financial records subject to SOX
- Customer credentials (API keys, OAuth tokens belonging to customers)

**AI access**: Read BLOCKED by default. Requires:
- Explicit human approval per file, per session
- Documented business justification
- Audit log entry recording the access decision
- Use of enterprise-tier LLM agreement with zero-retention and
 no-training guarantees
- Compliance team awareness for production data

**Audit treatment**: Path always hashed in audit log. Access events
emit compliance tags (e.g., GDPR-Art-32, HIPAA-164.312). Audit
retention extended to regulatory minimums.

### Level 4: Regulated

Information subject to legal restrictions on access, location, or
processing that go beyond standard compliance.

**Examples**:
- Classified government data (CUI, Secret, etc.)
- Data subject to export controls (ITAR, EAR)
- Data subject to data residency requirements (financial regulators,
 EU data sovereignty)
- Customer secrets stored by us in custody (private keys, signing keys)

**AI access**: BLOCKED. No AI access path. Disclosure to external LLM
providers prohibited regardless of agreement tier. If AI assistance
is needed for code that processes regulated data, AI works against
synthetic test data only; humans handle the regulated data path.

**Audit treatment**: AI tools should never touch this data; the
audit event is the *attempt*, which itself is a policy violation
requiring incident response.

## Classification of paths

Consuming frameworks map filesystem paths to classification levels
via configuration. Default mappings:

| Path pattern | Classification |
|---|---|
| `LICENSE`, `README.md`, public docs | Public |
| Source code in repo | Internal (unless explicitly higher) |
| `.env*`, `secrets/`, `credentials/`, `*.pem`, `*.key` | Restricted |
| Customer data fixtures (`fixtures/customers/`, `data/customers/`) | Restricted |
| Production database dumps | Restricted or Regulated per content |
| `classified/`, `regulated/`, paths matching `cui-*` | Regulated |

Per-project overrides go in the consuming framework's configuration
(for example a `data-classification.yaml` in the consumer's config
directory). Defaults are
permissive (Internal) for unspecified paths; promotion to higher
levels requires explicit declaration.

## Audit log integration

Every access event records the classification level in the audit
log:

  "subject": {
   "type": "file",
   "path_hash": "sha256:...",
   "classification": "restricted"
  }

Reviewers querying the audit log can filter by classification:
"show me every AI access to Restricted or higher in the last 30 days."

## Hook integration

Consuming frameworks implement a PreToolUse hook that checks
classification before allowing read access:

- Public, Internal: allowed unconditionally
- Confidential: prompt for human approval (or check session-level
 approval token)
- Restricted: block unless explicit approval flag set
- Regulated: block always

The hook reads classification from the consuming framework's
classification config; this commons defines the levels and their
semantics, not the implementation.

## Policy integration

Cedar policies in `policies/` reference classification levels:

  permit (
   principal,
   action == Action::"Read",
   resource
  )
  when {
   resource.classification == "public" ||
   resource.classification == "internal"
  };

Higher levels require explicit permit rules with additional
conditions (approval token, business justification, etc.).

## Cross-framework consistency

These five levels are the standard across this commons and any
consuming framework. Consumers should NOT define their own levels
or rename these. Project-specific extensions go *inside* a level
(e.g., "Restricted - PCI" vs "Restricted - HIPAA"), never as a new
top-level.

## References

- NIST SP 800-60 Volume I: Guide for Mapping Types of Information
 and Information Systems to Security Categories (informs the
 taxonomy)
- ISO/IEC 27001 Annex A.5.12 (Classification of Information)
- TLP (Traffic Light Protocol) - broader concept but our levels are
 more granular than TLP's four colors
- GDPR Article 32 (informs Restricted level for PII)
- HIPAA 45 CFR 164.312 (informs Restricted level for PHI)
- PCI DSS v4.0 (informs Restricted level for cardholder data)

## Anti-patterns

These classification behaviors create governance problems:

- **Treating all source code as Internal** - some code may be
 Public (open source) or Confidential (pre-release product code).
 Default classification ≠ blanket classification.
- **Letting AI tools determine classification** - classification is
 a human decision; AI may help by suggesting based on path patterns
 but the consuming framework must require explicit confirmation
 for elevations.
- **Mixing classifications in one file** - if a file has both
 Internal and Restricted content, the whole file is Restricted.
 Don't store mixed-classification data in one file.
- **Classification creep** - overclassifying creates friction that
 encourages workarounds; underclassifying creates breach risk.
 Both extremes are failures.
