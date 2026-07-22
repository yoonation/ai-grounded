<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Tooling

Substrate-native utilities that operate on substrate content and emit
consumer-agnostic outputs. Per Charter Article VII Section 7.1, substrate
tooling does not depend on specific consumer architectures, and per
discipline rule 11 the substrate is description, not implementation. Some
are implemented substrate self-maintenance tools (catalog and rule
validation, toolchain audit, enforcement-floor generation); others are
skeletons (a documented contract, a procedure, and at most a thin
read-only reference script). None is a consumer-runtime product; a
consumer runs the work in their own environment.

Utilities (each with its own README inside its subdirectory):

| Utility | Purpose | Status |
|---|---|---|
| `assemble/` | Validates catalogs and rules against schemas and assembles the published catalog form | Maintained (wired into `make gc-validate` / `gc-assemble`) |
| `toolchain/` | Audits the tool registry and capability selection | Maintained (wired into `make gc-toolchain-audit`) |
| `floor-generator/` | Generates the consumer enforcement floor (pre-commit, CI, L2 review manifest) from the resolved toolchain | Maintained (wired into `make gc-generate-floor`) |
| `profile-resolver/` | Resolves profile-of-a-profile inheritance to a flat effective profile (selected controls with effective severity) | Skeleton + read-only reference script |
| `mapping-coverage-reporter/` | Reports cross-taxonomy mapping coverage and gaps between source taxonomies and substrate concerns | Skeleton + read-only reference script |
| `tailoring-agent/` | AI-assisted tailoring workflow (consumer-side, future) | Skeleton (README-only, future) |

The reference scripts are read-only analyses of the substrate's own
published content (bindings, profiles, mappings). They are bash 3.2
compatible, take no network access, and are illustrative of the documented
procedure rather than maintained substrate runtime. Each tool's README
states what is reference, what is documented contract, and what is the
extension point.

Cross-references:

- `../CHARTER.md` Article VII (consumer-agnostic tooling obligation),
  Article III (AI proposes, humans approve)
- `../schemas/` (schemas the validators use)
- `../profiles/` (profiles the resolver operates on)
- `../mappings/` (mappings the coverage reporter operates on)
- `../toolchain/` (the registry and selection the toolchain audit operates on)
