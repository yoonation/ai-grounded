<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# OSCAL Model

This commons adopts the Open Security Controls Assessment Language
(OSCAL) as the canonical format for compliance content. This document
explains what OSCAL is, which parts of it we adopt, which parts we
defer, and why.

## What OSCAL is

OSCAL is a NIST-led standard that expresses security and privacy
controls in machine-readable formats (JSON, XML, YAML). It exists
because compliance content traditionally lived in PDFs and Word
documents - formats designed for humans to read once and machines to
ignore. OSCAL turns that content into structured data that can be
diffed, version-controlled, automatically validated, and cross-referenced.

The standard has several models, each addressing a different stage of
the compliance lifecycle:

- **Catalog** - A collection of controls (e.g., NIST 800-53 Rev 5
 catalog has hundreds of controls organized into families)
- **Profile** - A tailored subset of a catalog, with selected controls
 and parameter values applied (e.g., FedRAMP Moderate baseline is a
 profile of 800-53)
- **Component Definition** - Description of how a specific product or
 service implements controls (e.g., "this AWS service satisfies these
 controls in these ways")
- **System Security Plan (SSP)** - How a system implements its
 selected controls (organization-level deliverable)
- **Assessment Plan (AP)** - What an auditor plans to verify and how
- **Assessment Results (AR)** - What the auditor actually found
- **Plan of Action and Milestones (POAM)** - How identified gaps will
 be fixed and by when
- **Control Mapping** - Cross-references between controls in
 different catalogs (e.g., 800-53 AC-2 equivalent-to ISO 27001 A.5.15)

## What this commons adopts

Three OSCAL models, scoped to what makes sense for a project-level
framework:

### Catalog model - YES, adopted

This commons stores OSCAL catalogs for compliance frameworks we care
about. Each catalog is the structured representation of a framework's
controls.

Sources for our catalogs:
- **Auto-fetched from upstream** when NIST publishes OSCAL: 800-53,
 CSF v2, 800-171, 800-218 (SSDF)
- **Hand-authored from public-domain text** when no OSCAL exists yet:
 AI RMF, EU AI Act
- **Not stored** for copyrighted frameworks: ISO 42001, SOC 2 TSC
 (reference-only pointers to authoritative sources)

### Profile model - YES, adopted

Profiles are how we curate the controls relevant to specific work.
Rather than always referencing the entire 800-53 catalog (hundreds of
controls), we define profiles that select only the controls relevant
to a use case.

Initial profiles in this commons:
- `ai-security-baseline` - Controls most relevant to AI security
 architecture work, drawn from 800-53, AI RMF, and EU AI Act
- `federal-bridge` - Controls relevant to FedRAMP-adjacent target
 roles, drawn primarily from 800-53 with selected baselines

### Control Mapping model - YES, adopted (OSCAL v1.2.0+)

When OSCAL 1.2.0 introduced the Control Mapping model, it became
possible to express relationships between controls across frameworks
in machine-readable form. We use this for:

- 800-53 controls equivalent-to or subset-of ISO 27001 controls
- AI RMF subcategories intersecting-with EU AI Act articles
- 800-53 controls mapped to threats in our threat catalogs

Cross-framework reasoning that previously required spreadsheets now
lives as structured OSCAL data.

## What this commons does NOT adopt

Five OSCAL models are deliberately out of scope. They are organization-
level or operational artifacts that don't belong in a project-level
governance commons.

### System Security Plan (SSP) - NOT adopted

An SSP describes how a specific organization's system implements its
selected controls. It's a deliverable produced *by users of this
commons* for their projects, not by the commons itself.

A consuming project might generate an SSP using Trestle, referencing
profiles from this commons. The SSP lives in the project, not the
commons.

### Assessment Plan (AP), Assessment Results (AR), POAM - NOT adopted

These are the audit lifecycle artifacts. They describe what auditors
plan to check, what they actually found, and what gaps will be fixed.
All organization-level.

If a consuming project needs these (e.g., for a real FedRAMP ATO),
they generate them in their own Trestle workspace using this commons
as a catalog and profile source.

### Component Definition - DEFERRED, evaluate at runtime framework start

Component Definitions describe how specific products implement
controls. They become valuable when:

- A project is building a component intended for reuse across systems
- The runtime governance framework starts (then we'd describe how
 agentic systems implement controls)

For build-time governance, components are mostly the systems being
built, not described abstractly. We defer this to the runtime
framework's scope.

## Tooling: Trestle

Trestle (`compliance-trestle`) is the canonical open-source tool for
managing OSCAL content. Originally developed by IBM, now maintained
by the OSCAL Compass community. It provides:

- Workspace management (`trestle init`)
- Import of OSCAL from URLs or files (`trestle import`)
- Validation against OSCAL schemas (`trestle validate`)
- Splitting and merging large OSCAL files (`trestle split` /
 `trestle merge`)
- A task framework for extensible operations (`trestle task`)

Trestle stores OSCAL artifacts in a structured workspace that follows
the model directory convention:

  workspace/
  ├── catalogs/
  ├── profiles/
  ├── component-definitions/
  ├── system-security-plans/
  ├── assessment-plans/
  ├── assessment-results/
  ├── plan-of-action-and-milestones/
  └── .trestle/

In this commons, we use only `catalogs/` and `profiles/` per the
scoping decisions above. The other directories exist after
`trestle init` but remain empty by design.

## Why OSCAL over alternatives

Two alternatives were considered:

**Custom YAML schema we define**: Rejected. Reinvents what NIST has
already standardized. Creates a translation step between our format
and OSCAL when interacting with upstream tools and downstream
consumers. No advantages over OSCAL beyond familiarity.

**SCAP (Security Content Automation Protocol)**: Rejected as primary
format. SCAP excels at operational hardening content (Ansible
playbooks, configuration baselines) but is heavier-weight than OSCAL
for catalog representation. SCAP and ComplianceAsCode are noted in
the ROADMAP as relevant for runtime hardening - different concern.

**ISO 27001 OSCAL representation**: Considered. ISO publishes
controls but doesn't publish OSCAL versions. AWS published OSCAL
versions of Canadian ITSG-33 (which is based on 800-53), but ISO
27001 itself has copyright restrictions on redistribution. We treat
ISO as reference-only.

## Versioning

OSCAL itself is versioned. Trestle 4.0.x is built on OSCAL 1.2.x.

When OSCAL releases a new version with schema changes, Trestle
releases a corresponding version. The commons VERSION (separate from
both) tracks our adoption progress.

When Trestle bumps OSCAL versions:
1. Test compatibility of our catalogs against new schema
2. Re-import upstream NIST OSCAL releases
3. Validate via `trestle validate`
4. Bump commons VERSION
5. Document the OSCAL version change in MAINTENANCE.md review log

## Maintenance discipline

The promise of OSCAL is automation - but only if we maintain the
discipline. See MAINTENANCE.md for the full protocol. Key points:

- NIST catalogs auto-fetched from upstream on a schedule
- Re-import is a deterministic operation (Trestle handles UUIDs,
 schema, and structure)
- Validation runs on every change via `trestle validate`
- Profile selections reviewed quarterly to ensure they still capture
 the controls relevant to current work

## Practical implications

What this means for someone using this commons:

- **Reading control text**: Open the OSCAL JSON file in your editor or
 use `trestle describe` for a structured view
- **Adding a new framework**: If it has an upstream OSCAL release, run
 `trestle import` with the URL. If not, hand-author following the
 OSCAL Catalog schema.
- **Cross-referencing controls**: Use the Control Mapping model
 artifacts under `mappings/`, not flat lookup tables
- **Defining a tailored set of controls**: Create a Profile, don't
 duplicate the catalog
- **Generating a project's compliance documentation**: Use Trestle's
 SSP generation against our profiles (operation happens in the
 consuming project, not this commons)

## References

- OSCAL official site: https://pages.nist.gov/OSCAL/
- OSCAL specification: https://pages.nist.gov/OSCAL/reference/latest/
- Trestle: https://github.com/oscal-compass/compliance-trestle
- NIST OSCAL content: https://github.com/usnistgov/oscal-content
- OSCAL Compass community: https://github.com/oscal-compass
- NIST CSWP 53 "Charting the Course for NIST OSCAL" (Dec 2025)
