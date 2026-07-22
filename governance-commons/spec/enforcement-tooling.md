<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Enforcement tooling guidance

This document is referenced from every L1 static-analysis binding
via the `engine-guidance-ref` field. It centralizes substrate policy
on which static-analysis engine consumers should use, where rule
content comes from, and how consumers invoke the engine. Keeping
this policy in one place avoids duplicating it across every binding
file.

## Substrate-recommended engine: OpenGrep

The substrate recommends OpenGrep (https://github.com/opengrep/opengrep)
for enforcing L1 mechanical rules. OpenGrep is a static analysis
engine that pattern-matches source code against rules expressed in
the semgrep-pattern-v1 YAML format.

### Why OpenGrep

OpenGrep was forked from Semgrep Community Edition in January 2025
by a consortium of 10+ application security vendors (Aikido Security,
Endor Labs, Jit, Orca Security, and others). The fork was a response
to Semgrep Inc.'s December 13, 2024 license update, which moved
several features (cross-function taint analysis, inter-procedural
scanning, fingerprinting, tracking ignores, Windows support) from
the free Community Edition into the commercial AppSec Platform.

OpenGrep restores those features under LGPL-2.1 and commits to
keeping them open. The substrate's reasons for preferring OpenGrep:

- **License alignment.** OpenGrep is LGPL-2.1 throughout. The
  substrate is Apache-2.0. Both are OSI-approved open source. There
  is no commercial gating on OpenGrep capabilities.

- **Governance.** OpenGrep is managed by a multi-vendor consortium
  with a stated roadmap toward foundation oversight (OWASP, Linux
  Foundation, or similar). Single-vendor capture is structurally
  prevented.

- **Capability.** OpenGrep includes the features Semgrep moved
  behind paywall (cross-function taint analysis in particular)
  which materially affect detection quality for real security
  bugs.

- **Compatibility.** OpenGrep accepts the same rule format as
  Semgrep Community Edition. Substrate L1 bindings work on both
  engines without modification.

### Compatible alternative: Semgrep Community Edition

Consumers who prefer Semgrep Community Edition (https://semgrep.dev)
can use it instead of OpenGrep. The substrate names the SAST
capability gate rather than shipping engine-specific patterns; the
gate resolves to either engine, which runs the same community rule
set unmodified.

Semgrep CE remains LGPL-2.1 at the engine level. Consumers using
Semgrep CE accept that several features (listed above) are not
available without a commercial Semgrep AppSec Platform subscription.

The substrate does not endorse Semgrep AppSec Platform (the
commercial product). Consumers choosing it do so independently of
substrate guidance.

## Rule source: semgrep/semgrep-rules

The canonical rule source the substrate points consumers at is
https://github.com/semgrep/semgrep-rules. The substrate names the
SAST gate and selects OpenGrep as the engine; the consumer supplies
the rule content from this source at scan time. The substrate does
not ship rule content or per-rule bindings into this repository.

### About the opengrep-rules fork

OpenGrep forked semgrep-rules in December 2024 at the
opengrep/opengrep-rules repository. That fork was archived on
November 28, 2025 and is now read-only. The OpenGrep team chose
not to maintain a long-term separate rule library, reflecting the
project's positioning as "engine that runs Semgrep-format rules
from any source."

In practical terms: the substrate continues to reference
semgrep/semgrep-rules because it remains the largest, most actively
maintained source of community rules in the semgrep-pattern-v1
format. Both OpenGrep and Semgrep CE consume these rules without
modification.

### Rule license

Rules in semgrep/semgrep-rules are licensed under the Semgrep Rules
License v.1.0. This license permits use in internal, non-competing,
non-SaaS contexts and explicitly limits certain commercial usage.

The substrate does NOT redistribute rule content. It names the
SAST gate; consumers obtain rule content from the source at scan
time under the source's license terms.

The substrate's own content (catalogs, profiles, bindings, decision
frameworks, examples, schemas) is licensed Apache-2.0 and is not
constrained by the Semgrep Rules License.

### Supplementary rule sources

Consumers may add rules from other sources to their scan
configuration, including:

- https://github.com/AikidoSec/opengrep-rules (MIT licensed; Aikido
  Security's contributed rules)
- Custom in-house rules authored by the consumer
- Other vendor-published rule packs

The substrate binding format's `rule-sources` field is a list to
accommodate multi-source configurations.

## Consumer invocation patterns

### OpenGrep (substrate-recommended)

OpenGrep's canonical invocation is `opengrep scan -f <rules-path>
<code-path>`. The `-f` flag accepts a path to a rule file or a
directory of rule files. Multiple `-f` flags are allowed.

One-time setup for substrate consumers:

```
git clone https://github.com/semgrep/semgrep-rules.git ~/.opengrep-rules
```

Per-binding scan invocation. The example below uses authentication.password-hashing's
rules; consumers translate `referenced-rules` entries into `-f`
arguments using the `source-path-in-semgrep-rules` field from each
rule entry:

```
opengrep scan \
  -f ~/.opengrep-rules/python/lang/security/audit/md5-used-as-password.yaml \
  -f ~/.opengrep-rules/python/lang/security/audit/sha1-used-as-password.yaml \
  -f ~/.opengrep-rules/java/lang/security/audit/crypto/weak-hash.yaml \
  path/to/your/code/
```

Useful flags:

- `--error` exits with status 1 if any finding is reported (CI gate)
- `--sarif-output=results.sarif` produces SARIF 2.1.0 output
- `--exclude-rules=<id>` skips specific rules
- `--include` / `--exclude` filter scanned files

Detailed CLI reference: https://github.com/opengrep/opengrep

### Semgrep Community Edition (alternative)

Semgrep CE accepts `--config=r/<registry-id>` arguments which fetch
rules from semgrep.dev at scan time. The example below uses the same
authentication.password-hashing rules referenced via the registry:

```
semgrep scan \
  --config=r/python.lang.security.audit.md5-used-as-password \
  --config=r/python.lang.security.audit.sha1-used-as-password \
  --config=r/java.lang.security.audit.crypto.weak-hash \
  path/to/your/code/
```

Useful flags:

- `--error` exits with status 1 if any finding is reported
- `--sarif-output=results.sarif` produces SARIF 2.1.0 output
- `--exclude=<pattern>` skips files

Detailed CLI reference: https://semgrep.dev/docs

### Choosing between the two

For consumers starting fresh: pick OpenGrep. The substrate's
preference is clear; the LGPL-2.1 license keeps long-term licensing
risk low; the feature set is broader at the OSS tier.

For consumers with established Semgrep CE workflows: continue using
Semgrep CE. The substrate's bindings work on either engine; there's
no urgency to migrate unless the consumer wants the features
OpenGrep restores (cross-function taint analysis in particular).

The substrate does not require consumers to use OpenGrep. It
recommends.

## CI integration

Both engines integrate with standard CI platforms:

- GitHub Actions: official OpenGrep action; semgrep/semgrep-action
- GitLab CI: SAST template; custom job definitions
- Jenkins, CircleCI, etc.: invoke the CLI directly

Substrate-recommended CI pattern: run on every pull request,
configure `--error` to fail the build on any L1 finding, emit
SARIF output and surface findings in the platform's code-review UI.

## What this document does NOT cover

- Specific CI pipeline configurations (consumer choice)
- Rule authoring (substrate references rules; doesn't author them)
- Engine performance tuning (engine-specific concern)
- Integration with consumer's specific issue tracker or vulnerability
  management system

## Maintenance

This document is reviewed when:

- A material change occurs in OpenGrep, Semgrep CE, or their
  governance/licensing
- A new rule source emerges that the substrate should reference
- The substrate adds a new binding type that complements
  static-analysis (CodeQL, OPA Rego, etc.)

Next review: when the OpenGrep consortium transitions to foundation
governance (estimated 2026-2027 per the project's announced roadmap).
