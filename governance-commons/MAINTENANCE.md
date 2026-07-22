<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Maintenance

Governance artifacts decay. Upstream standards evolve, regulations amend,
threat taxonomies update. Without active maintenance, this commons silently
becomes wrong rather than visibly empty - the worst failure mode.

This document defines the discipline that keeps it current.

## Catalog inventory (current state)

For quick reference, the catalogs currently maintained in this commons:

| Catalog | Type | Source | Update mechanism |
|---|---|---|---|
| owasp-llm-top10 | Threat (YAML) | OWASP | Manual quarterly |
| owasp-agentic-asi-2026 | Threat (YAML) | OWASP | Manual quarterly |
| mitre-atlas | Threat (YAML) | MITRE | Manual quarterly |
| stride | Threat (YAML) | Microsoft | Annual (stable methodology) |
| nist-800-53-rev5 | Compliance (OSCAL) | NIST upstream | trestle import |
| nist-csf-v2 | Compliance (OSCAL) | NIST upstream | trestle import |
| nist-800-171-r3 | Compliance (OSCAL) | NIST upstream | trestle import |
| nist-800-218-ssdf | Compliance (OSCAL) | NIST upstream | trestle import |
| nist-ai-rmf | Compliance (OSCAL) | Hand-authored | Manual when NIST AI 100-1 amends |
| eu-ai-act | Compliance (OSCAL) | Hand-authored | Manual when regulation amends |
| iso-42001 | Reference (YAML) | ISO (copyrighted) | Citation updates only |
| soc2-tsc | Reference (YAML) | AICPA (copyrighted) | Citation updates only |

Profiles:

| Profile | Source | Description |
|---|---|---|
| nist-800-53-rev5-moderate-baseline | NIST upstream | Official NIST MODERATE baseline |
| nist-800-53-rev5-privacy-baseline | NIST upstream | Official NIST PRIVACY baseline |
| ai-security-baseline | Hand-authored | Curated 35 800-53 controls for AI security |
| federal-bridge | Hand-authored | Extends NIST MODERATE with 7 AI-relevant additions |

## Maintenance protocol

### Quarterly review (mandatory)

Every quarter, the engineer responsible for the framework reviews each
catalog against its upstream source. The cadence aligns with most
standards' update rhythm.

For each threat catalog file:

1. Check the LAST_REVIEWED field against today
2. Visit the UPSTREAM_SOURCE URL
3. Compare current commons content against upstream
4. If upstream has changed: update commons, update LAST_REVIEWED,
   bump commons VERSION (patch for fixes, minor for additions, major
   for breaking schema changes)
5. If upstream has not changed: update LAST_REVIEWED only

For compliance catalogs, the procedure differs by catalog type (see
"Update protocol per catalog type" below).

### AI-assisted check during audit runs

When /audit-export runs (or /review is invoked), the AI inspects
each catalog's LAST_REVIEWED field (for threats) or last Trestle
import date (for OSCAL catalogs) and surfaces:

- Catalogs older than 6 months: warning in report
- Catalogs older than 12 months: prominent warning, mention in summary
- Catalogs older than 18 months: explicit recommendation to review before
  proceeding with security-critical work

The AI surfaces these. The engineer acts on them. This split (machine
nag, human decide) avoids the trap of automated changes to compliance
mappings, which would themselves be audit findings.

### CI enforcement (automated)

A CI check runs on every push to the framework repo:

- If any catalog LAST_REVIEWED (or Trestle import metadata) is older
  than 12 months without an explicit acknowledgment entry in
  STALE-ACKNOWLEDGMENTS.md, the build fails
- The acknowledgment entry must include: catalog name, current date,
  engineer responsible, reason for deferring update, target review date
- This forces deliberate decisions about staleness rather than silent
  drift

## Required metadata per catalog

### Threat catalogs (YAML)

Every YAML catalog file in catalogs/threats/ must include the
metadata block with catalog_id, catalog_name, last_reviewed,
upstream_source, upstream_version, next_review_due, maintainer,
and review_protocol fields. Catalogs without complete metadata
fail CI validation.

### Compliance catalogs (OSCAL)

OSCAL catalogs use the standard's native metadata structure. The
oscal-version, metadata.last-modified, and metadata.version fields
are required by the OSCAL schema and validated by Trestle on every
operation.

Additionally, this commons tracks:

- The date of last trestle import (recorded in commit history)
- The source URL imported from (recorded in the catalog's links array
  with rel canonical)

For hand-authored OSCAL (AI RMF, EU AI Act), the same fields are
populated manually rather than by import.

### Reference-only catalogs (YAML)

Reference files use a simpler YAML schema since they contain no
control text. Required fields include catalog_id, catalog_name,
copyright_status, redistribution_allowed, upstream_source,
upstream_version, last_reviewed, and maintainer. See existing
files in iso-42001/ and soc2-tsc/ for the format.

## Update protocol per catalog type

### Threat catalogs

Source: OWASP, MITRE, NIST publications.

When upstream updates:
1. Compare new threat IDs against existing entries
2. Add new threats with full metadata
3. Mark removed threats as deprecated true with deprecated_date
4. Update mappings if cross-references change
5. Run CI to validate schema

### Compliance catalogs

Three categories with different update procedures:

Auto-fetched from upstream (NIST catalogs):

Source: NIST publishes machine-readable OSCAL versions at
github.com/usnistgov/oscal-content.

When upstream updates (NIST releases new revisions):
1. Run trestle import per the UPDATE_RUNBOOK.md in
   catalogs/compliance/
2. Run trestle validate -a to verify schema compliance
3. Review the diff against the previous version
4. Update review log and add review entry below
5. Bump commons VERSION (patch for refresh, minor for meaningful
   upstream changes, major for breaking schema changes)
6. Run any threat-catalog cross-reference updates if control IDs
   changed

Hand-authored OSCAL (AI RMF, EU AI Act):

Source: public-domain text from authoritative publications. Stored as
OSCAL JSON in the trestle workspace, but authored by us rather than
imported.

When upstream amends (regulation changes, framework updates):
1. Identify changed sections in upstream publication
2. Edit the OSCAL JSON directly, or use Trestle's split/edit/merge
   workflow for larger changes
3. Copy verbatim text from authoritative source - never paraphrase
4. Run trestle validate -a after edits
5. Update last-modified field, add review log entry, bump VERSION

Reference-only (ISO 42001, SOC 2 TSC):

Source: copyrighted standards we cannot redistribute. We store
citations and mapping references only.

When upstream amends:
1. Update the citation URL and version metadata in reference.yaml
2. Update cross-references to threats and other frameworks if the
   amendment changes mappings
3. Update LAST_REVIEWED only (no text to verify)

### Policy primitives

Source: this commons (we maintain these, no upstream).

When updating:
1. Add new policies as new files; don't modify existing ones in ways
   that break semantics for current consumers
2. If a policy semantics changes, create v2 filename and deprecate v1
3. Document policy intent in policy file comments
4. Test policy logic against synthetic actor/action/resource cases

### Playbooks

Source: this commons (we maintain these, no upstream).

When updating:
1. Add new playbooks as new files
2. Update existing playbooks when incident patterns reveal gaps
3. Include date and incident reference (anonymized if needed) in
   playbook revision history

### Library context

Source: official library documentation, release notes.

When library updates:
1. Check upstream changelog
2. Update API signatures, deprecations, breaking changes
3. Verify version metadata reflects current stable release
4. Test guidance against current library version

## Common gotchas (lessons recorded)

These are things that have bitten us during framework development.
Future-you will appreciate them being documented.

### OSCAL UUID format strictness

OSCAL validates UUIDs against a strict regex requiring proper UUID
version 4 or version 5 format. Two requirements that look like UUIDs
but fail:

- Third group must start with 4 or 5 (version digit)
- Fourth group must start with 8, 9, A, B, a, or b (variant digit)

Placeholder UUIDs like 00000000-0000-0000-0000-000000000001 will fail
validation. Generate real UUIDs:

    python3 -c "import uuid; print(uuid.uuid4())"

Or:

    uuidgen | tr '[:upper:]' '[:lower:]'

### trestle validate requires a flag in v4

The bare trestle validate command errors in Trestle v4 plus. Use:

    trestle validate -a        # validate everything
    trestle validate -f FILE   # validate one file
    trestle validate -t TYPE   # validate one model type

### Trestle workspace dependency

All Trestle commands require running from inside an initialized
workspace. If you get "directory is not in a valid trestle root
directory," cd into trestle-workspace/ first.

### Back-matter resource warnings are informational

Trestle warns when back-matter resources aren't referenced from the
model body. The warning message says "Resources have N uuids and N
are not referenced by model."

This is informational, not an error. If your back-matter contains
documentation for human readers (rationale, source citations), the
warning is expected and acceptable.

### NIST's 800-218 has dangling references

NIST's published OSCAL for 800-218 includes 200 back-matter resources
but only references 177 of them. The warning surfaces this. Not our
issue to fix.

## Anti-patterns

These maintenance behaviors cause more harm than the gaps they try to
close:

- AI-generated catalog content without verification against upstream.
  Plausible-but-wrong compliance mappings are worse than missing ones.
- Updating LAST_REVIEWED without actual review. The field becomes
  meaningless and creates false audit evidence.
- Removing deprecated entries instead of marking them deprecated.
  Consumers may still reference deprecated IDs; removing them creates
  broken references with no migration guidance.
- Paraphrasing regulatory text. Auditors check verbatim; paraphrases
  can change legal meaning. Quote upstream exactly.
- Bypassing Trestle for OSCAL edits. Direct JSON edits can violate
  schema invariants. Use Trestle's editing workflow or run
  trestle validate -a after any direct edit.
- Reproducing copyrighted ISO or AICPA content in public commits.
  Reference-only files exist precisely to prevent this.

## Accountability

The engineer maintaining this commons is named in each catalog's
maintainer field (YAML threat catalogs) or in the OSCAL
metadata.parties array (compliance catalogs). When the maintainer
changes, all maintainer references must be updated. There is no
team-owned maintenance - accountability is individual to avoid
diffusion of responsibility.

If no maintainer is available, mark the catalog as unmaintained true
and the AI will surface this prominently. Better to admit the gap
than pretend to maintenance that isn't happening.

## Review log

Major reviews and updates are logged here. Most recent at the top.

    2026-05-12: Initial population of governance-commons compliance catalogs.
                Imported NIST 800-53 Rev 5, 800-53 Rev 5 MODERATE baseline,
                800-53 Rev 5 PRIVACY baseline, 800-171 Rev 3, 800-218 ver1
                (SSDF), CSF v2.0 from upstream via trestle import.
                Hand-authored NIST AI RMF v1.0 and EU AI Act Title III
                (Articles 6-27) OSCAL catalogs. Created reference-only files
                for ISO 42001 and SOC 2 TSC. All compliance content
                validates against OSCAL 1.2.1 schema (Trestle 4.0.2).
                Commons VERSION: 0.1.0.
