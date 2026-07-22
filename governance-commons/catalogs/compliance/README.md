<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Compliance Catalogs

OSCAL-formatted compliance content managed by Trestle.

## Structure

    compliance/
    ├── README.md                    This file
    ├── UPDATE_RUNBOOK.md           Commands for updating catalogs
    ├── trestle-workspace/          Trestle workspace
    │   ├── catalogs/               OSCAL catalogs
    │   │   ├── nist-800-53-rev5/   Imported from NIST upstream
    │   │   ├── nist-csf-v2/        Imported from NIST upstream
    │   │   ├── nist-800-171-r3/    Imported from NIST upstream
    │   │   ├── nist-800-218-ssdf/  Imported from NIST upstream
    │   │   ├── nist-ai-rmf/        Hand-authored (no upstream OSCAL)
    │   │   └── eu-ai-act/          Hand-authored (no upstream OSCAL)
    │   ├── profiles/               OSCAL profiles
    │   │   ├── nist-800-53-rev5-moderate-baseline/  Imported NIST baseline
    │   │   ├── nist-800-53-rev5-privacy-baseline/   Imported NIST baseline
    │   │   ├── ai-security-baseline/                Our hand-authored
    │   │   └── federal-bridge/                      Our hand-authored
    │   ├── mapping-collections/    Cross-framework control mappings (OSCAL 1.2.0)
    │   ├── component-definitions/  Empty by design (see oscal-model.md)
    │   ├── system-security-plans/  Empty by design
    │   ├── assessment-plans/       Empty by design
    │   ├── assessment-results/     Empty by design
    │   ├── plan-of-action-and-milestones/  Empty by design
    │   ├── dist/                   Trestle build output (assemble target)
    │   └── .trestle/               Trestle metadata
    ├── iso-42001/                  Reference-only (copyrighted)
    │   └── reference.yaml
    ├── pci-dss/                    Reference-only (copyrighted)
    │   └── reference.yaml
    └── soc2-tsc/                   Reference-only (copyrighted)
        └── reference.yaml

## What's here

### Auto-fetched from NIST (always current)

Imported from github.com/usnistgov/oscal-content via trestle import.
These are the authoritative OSCAL representations published by NIST.

- NIST SP 800-53 Rev 5: comprehensive security and privacy controls
- NIST CSF v2.0: cybersecurity framework
- NIST SP 800-171 Rev 3: controls for protecting CUI
- NIST SP 800-218 ver1: Secure Software Development Framework (SSDF)

Plus two official NIST baseline profiles:

- NIST 800-53 Rev 5 MODERATE baseline: basis for FedRAMP Moderate
- NIST 800-53 Rev 5 PRIVACY baseline: privacy-specific controls

Update procedure: see UPDATE_RUNBOOK.md

### Hand-authored OSCAL (public-domain text, no upstream OSCAL)

Frameworks whose text is freely usable but not yet published in OSCAL
format. We author the OSCAL representation ourselves from authoritative
sources.

- NIST AI RMF: AI Risk Management Framework v1.0 (NIST AI 100-1, January 2023)
  - 4 functions, 19 categories, 72 subcategories
  - Full coverage of GOVERN, MAP, MEASURE, MANAGE
- EU AI Act: Regulation (EU) 2024/1689
  - Title III articles (high-risk AI systems): Articles 6-27
  - Coverage includes risk management, data governance, technical
    documentation, record-keeping, transparency, human oversight,
    cybersecurity, provider obligations, deployer obligations,
    fundamental rights impact assessment

Update procedure: when upstream amends, edit the OSCAL JSON directly
and copy verbatim text from authoritative sources. See MAINTENANCE.md.

### Hand-authored OSCAL profiles

- ai-security-baseline: 35 controls drawn from 800-53 most relevant
  to AI security architecture work
- federal-bridge: Extends the official NIST MODERATE baseline with 7
  AI-specific controls. Honest framing: this is "NIST MODERATE plus
  AI additions" for learning and practice, not equivalent to FedRAMP
  Moderate.

### Reference-only (copyrighted)

Frameworks where redistribution of control text would violate
copyright. We store pointers to authoritative sources, not the text
itself. Practitioners with licensed access can populate locally.

- ISO/IEC 42001: AI management system standard (ISO copyright)
- SOC 2 Trust Services Criteria: AICPA copyrighted
- PCI DSS v4.0.1: Payment Card Industry Data Security Standard (PCI SSC
  copyright; the standard is free to download but redistribution is
  restricted, so only structure and citations are stored here)

Files in these directories contain URLs, structural references, and
mapping references to other frameworks, but no verbatim control text.

## Mapping collections

Cross-framework relationships expressed in OSCAL 1.2.0 Control Mapping
format. Stored in trestle-workspace/mapping-collections/. Trestle v4
provides this as a native top-level model.

Mapping collections planned (built as work surfaces needs):

- 800-53-to-iso-27001: equivalences and overlaps with ISO 27001
- ai-rmf-to-eu-ai-act: relationships between AI RMF subcategories
  and EU AI Act articles
- threats-to-controls: mapping our YAML threat catalogs to OSCAL
  controls that mitigate them
- nist-csf-to-800-53: CSF outcomes mapped to specific 800-53 controls
- ai-rmf-to-800-53: AI RMF subcategories mapped to relevant 800-53
  controls

These are populated as we identify and validate the cross-references.
Empty at framework v0.1.0; built up over time.

## Initial setup

The Trestle workspace must exist before any catalog content can be
imported. One-time setup per machine clone:

    cd governance-commons/catalogs/compliance/
    mkdir -p trestle-workspace
    cd trestle-workspace
    trestle init

After init, Trestle creates the standard OSCAL directory structure.

Then run the import commands from UPDATE_RUNBOOK.md to populate the
NIST catalogs from upstream.

## Validation

Trestle validates catalogs against the OSCAL schema on import and
edit. To run validation manually:

    cd governance-commons/catalogs/compliance/trestle-workspace/
    trestle validate -a

CI integrations should run this before any merge that touches OSCAL
content.

## Conventions

### Catalog directory naming inside trestle-workspace/

Trestle uses the catalog directory name as the catalog's identifier.
Use kebab-case names matching the upstream source:

- nist-800-53-rev5/
- nist-csf-v2/
- nist-800-171-r3/
- nist-800-218-ssdf/
- nist-ai-rmf/
- eu-ai-act/

### File naming for reference-only

Reference-only directories use a flat reference.yaml containing
metadata, citations, and mappings - no embedded control text.

## Trestle commands worth knowing

Most commonly used inside the workspace:

- trestle import -f URL-or-path -o NAME: fetch a catalog
- trestle validate -a: validate everything in the workspace
- trestle describe -f MODEL: inspect a model's contents
- trestle task --list: see available conversion tasks
- trestle split: break large OSCAL files into smaller editable pieces
- trestle merge: recombine split files for export
- trestle assemble: produce dist/ output ready for external use

The split / merge pattern is the Trestle-canonical way to edit large
OSCAL files in git-friendly chunks. Useful when reviewing PR diffs of
catalog changes.

## References

- OSCAL model overview: ../../spec/oscal-model.md
- Maintenance protocol: ../../MAINTENANCE.md
- Trestle documentation: https://oscal-compass.github.io/compliance-trestle/
- NIST OSCAL content: https://github.com/usnistgov/oscal-content
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- EU AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
