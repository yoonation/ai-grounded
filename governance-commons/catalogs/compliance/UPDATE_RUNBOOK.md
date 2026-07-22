<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Compliance Catalog Update Runbook

Commands for updating compliance catalogs from upstream sources.
Trestle handles fetching, schema validation, and workspace structure.
No custom scripts needed.

All URLs verified working as of 2026-05-12.

## When to run

- Quarterly review (per MAINTENANCE.md) - verify upstream hasn't
  changed since last fetch
- Notification of upstream release - NIST publishes new revisions
  occasionally
- Audit prep - confirm catalogs are current before any compliance
  conversation
- Project onboarding - first time setting up the framework on a
  new machine

## Prerequisites

Working in a clone of this repository with Trestle installed
(`mise use -g pipx:compliance-trestle@latest`). All commands run from
inside the trestle workspace:

    cd governance-commons/catalogs/compliance/trestle-workspace/

If the workspace doesn't exist yet, see compliance/README.md for
initial setup.

## URL pre-flight check

Before running imports, verify the URLs still resolve. NIST occasionally
moves files or renames them. Run this check first:

    for url in \
      "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json" \
      "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json" \
      "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_PRIVACY-baseline_profile.json" \
      "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-171/rev3/json/NIST_SP800-171_rev3_catalog.json" \
      "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-218/ver1/json/NIST_SP800-218_ver1_catalog.json" \
      "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/CSF/v2.0/json/NIST_CSF_v2.0_catalog.json"
    do
      echo "Checking: $url"
      curl -sI "$url" | head -1
      echo
    done

Expected output: HTTP/2 200 for each. If any return 404, browse to
https://github.com/usnistgov/oscal-content/tree/main/nist.gov to find
the correct path, then update this runbook before proceeding.

## NIST SP 800-53 Rev 5

The largest and most universally-referenced compliance catalog. Maps
to the security and privacy controls used by FedRAMP and many other
frameworks.

    trestle import \
      -f https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json \
      -o nist-800-53-rev5

## NIST 800-53 Rev 5 Baselines

NIST publishes official baseline profiles that select subsets of the
catalog for different impact levels. We import the two most relevant
to our work:

MODERATE baseline - Standard for most federal systems; basis for
FedRAMP Moderate authorization:

    trestle import \
      -f https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json \
      -o nist-800-53-rev5-moderate-baseline

PRIVACY baseline - Privacy-specific controls; relevant for systems
processing PII, including AI systems handling user data:

    trestle import \
      -f https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_PRIVACY-baseline_profile.json \
      -o nist-800-53-rev5-privacy-baseline

LOW and HIGH baselines are also available at the same path with
LOW and HIGH substituted. Add them via trestle import if your
work requires them.

## NIST SP 800-171 Rev 3

Controls for protecting Controlled Unclassified Information (CUI) in
non-federal systems. Relevant for defense contractors and federal
adjacent work.

    trestle import \
      -f https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-171/rev3/json/NIST_SP800-171_rev3_catalog.json \
      -o nist-800-171-r3

Note: filename uses NIST_SP800-171 (no dash between SP and 800),
unlike 800-53 which uses NIST_SP-800-53 (with dash). NIST's
filenames are inconsistent; this is the actual upstream format.

## NIST SP 800-218 ver1 (SSDF)

Secure Software Development Framework. Directly relevant to AI
development practices and supply chain security.

    trestle import \
      -f https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-218/ver1/json/NIST_SP800-218_ver1_catalog.json \
      -o nist-800-218-ssdf

Note: path uses ver1, not v1.1. The upstream OSCAL uses ver1
as the directory name even though the publication may be referred
to as 1.1 in NIST documentation.

## NIST CSF v2.0

Cybersecurity Framework v2.0. Higher-level framework that maps to
800-53 controls. Useful for governance conversations and executive
reporting.

    trestle import \
      -f https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/CSF/v2.0/json/NIST_CSF_v2.0_catalog.json \
      -o nist-csf-v2

## Validation after import

After all imports complete:

    trestle validate -a

If validation passes, all catalogs are correctly structured and ready
to use. If it fails, Trestle reports the schema violation - likely
indicates an upstream file changed format and we need to update the
commons VERSION accordingly.

## Verifying what got imported

    # Show all imported catalogs
    ls -la catalogs/

    # Show file sizes (sanity check)
    du -sh catalogs/*

    # Show all imported profiles (the baselines arrive here)
    ls -la profiles/

    # Describe a specific catalog
    trestle describe -f catalogs/nist-800-53-rev5/catalog.json | head -30

## Updating the LAST_REVIEWED metadata

After successful import:

1. Open governance-commons/MAINTENANCE.md
2. Add an entry to the review log noting the date, what was updated,
   and the upstream version
3. Bump governance-commons/VERSION (patch for refresh, minor for
   meaningful upstream changes, major for breaking schema changes)
4. Commit with conventional commit message:
   chore(commons): refresh NIST OSCAL content from upstream YYYY-MM-DD

## Catalogs not imported (and why)

Some compliance frameworks are intentionally not auto-fetched:

- NIST AI RMF: NIST has not yet published this in OSCAL format.
  Hand-authored OSCAL catalog at trestle-workspace/catalogs/nist-ai-rmf/
  (created in Batch 1C-ii-c).
- EU AI Act: Not published in OSCAL by EU authorities.
  Hand-authored OSCAL catalog at trestle-workspace/catalogs/eu-ai-act/.
- ISO 42001 / ISO 27001: Copyrighted standards; redistribution
  prohibited. Reference-only at compliance/iso-42001/.
- SOC 2 TSC: AICPA copyrighted. Reference-only at
  compliance/soc2-tsc/.
- NIST 800-53 LOW/HIGH baselines: Available at the same upstream
  path; import on demand when work requires them.

## Future automation (deferred)

For now this runbook is run manually. When the framework reaches the
point of needing scheduled updates (e.g., when shared across a team),
candidate automation paths:

- GitHub Actions workflow running these imports weekly with a PR
  if drift is detected
- A trestle task plugin that wraps the import commands
- OSCAL Compass C2P integration when that project matures

These are documented in the FUTURE.md roadmap with trigger conditions.
Until those triggers fire, manual quarterly runs are the discipline.

## Troubleshooting

Trestle says "directory is not in a valid trestle root directory":
You're not inside the trestle-workspace directory. Run
cd governance-commons/catalogs/compliance/trestle-workspace/ first.

Import succeeds but validation fails:
Check the OSCAL version Trestle expects vs the upstream file. NIST
sometimes publishes content using a newer OSCAL schema than the
installed Trestle supports. Upgrade Trestle:
mise use -g pipx:compliance-trestle@latest

Connection errors:
Verify network access to raw.githubusercontent.com. The import
command needs to be able to download from GitHub.

404 errors despite pre-flight check passing:
NIST may have published a new file between the pre-flight check and
the import. Re-run the pre-flight check to confirm.
