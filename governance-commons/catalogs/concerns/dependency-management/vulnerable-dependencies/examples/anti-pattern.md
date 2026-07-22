<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.vulnerable-dependencies vulnerable dependencies (anti-patterns)

Substrate-original anti-pattern examples for dependency-management.vulnerable-dependencies.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: No vulnerability scanning in CI

```yaml
# DO NOT DO THIS
# .github/workflows/ci.yml has no security scan step
- name: Build and test
  run: |
    npm ci
    npm test
```

Why this violates dependency-management.vulnerable-dependencies: no scanner is consulted;
known-vulnerable dependencies pass through to production
silently. The substrate's L1-002 rule requires
mechanical enforcement at build time.

## Anti-pattern B: Scanner runs but findings are ignored

```yaml
# DO NOT DO THIS
- name: Run npm audit
  run: npm audit  # exits non-zero but...
  continue-on-error: true  # ...we continue anyway
```

Why this violates dependency-management.vulnerable-dependencies: `continue-on-error: true`
makes the scan informational rather than enforcing. The
build proceeds with known vulnerabilities. Substrate-
recommended pattern: fail the build on findings at the
configured threshold; exemptions are documented, not
silently allowed.

## Anti-pattern C: Permanent exemptions without deadlines

```yaml
# DO NOT DO THIS
exemptions:
  - advisory: "CVE-2023-12345"
    reason: "We don't think this affects us"
    deadline: never  # permanent exemption
```

Why this violates dependency-management.vulnerable-dependencies (exemption discipline):
exemptions without deadlines accumulate indefinitely.
The "we don't think this affects us" reasoning is
unverifiable. Substrate-recommended pattern: time-
bounded exemptions with reachability evidence.

## Anti-pattern D: Threshold too permissive

```yaml
# DO NOT DO THIS - block only on critical, ignore high
- name: Run osv-scanner
  run: |
    osv-scanner --format=sarif --output=results.sarif ./
    CRITICAL=$(jq '[.runs[].results[] | select(.level == "error")
                    | select(.properties.severity == "critical")] | length' results.sarif)
    if [ "$CRITICAL" -gt 0 ]; then
      exit 1
    fi
    # Many high-severity findings accumulate without action
```

Why this violates dependency-management.vulnerable-dependencies: the substrate-recommended
threshold for production-grade-baseline is high or above,
not critical only. Limiting to critical produces
backlogs of high-severity findings that compound risk.

## Anti-pattern E: Manual scanning instead of CI

```text
# Team practice: someone runs `npm audit` locally
# "every couple of weeks" and files tickets for findings.
# Tickets backlog; some are addressed, some are not.
```

Why this violates dependency-management.vulnerable-dependencies (process property): manual
scanning is unreliable. Findings published between
manual scans go undetected. Substrate-recommended
pattern: automated CI scanning on every PR plus
scheduled scans on production branches.

## Anti-pattern F: Suppressing findings via package overrides without evidence

```json
// DO NOT DO THIS
// package.json - override pulls a non-vulnerable version
{
  "overrides": {
    "vulnerable-lib": "0.0.1-fake-override"
  }
}
```

Why this violates dependency-management.vulnerable-dependencies (in spirit): overrides
are legitimate for forcing transitive dependency
versions to fixed patches; they become abusive when they
force a non-existent or unrelated version to "silence"
the scanner. Substrate-recommended pattern: overrides
that genuinely upgrade to a fixed version, with the
override documented.

## Anti-pattern G: SLA exists but is never enforced

```text
# Policy says: high-severity advisories must be
# addressed within 7 days.
# Reality: tracked in JIRA; tickets age 60+ days; no
# escalation; no consequence; the policy is decorative.
```

Why this violates dependency-management.vulnerable-dependencies (operational property): a
policy without enforcement provides no protection.
Substrate-recommended pattern: SLA breach triggers
automated escalation (Slack notification, leadership
alert) and pause of unrelated deploys.

## Anti-pattern H: Scanning only in production branch CI

```yaml
# DO NOT DO THIS
on:
  push:
    branches: [main]   # scan only after merge
# PRs are not scanned; vulnerable dependencies merge
# unobserved and only fail the main-branch build later.
```

Why this violates dependency-management.vulnerable-dependencies: shifting detection to
post-merge means vulnerable dependencies enter main
before being caught. Substrate-recommended pattern:
scan on every PR and on the main branch.

## Cross-reference

- Good patterns: examples/dependency-management/vulnerable-dependencies-good.md
- Substrate rule: dependency-management.vulnerable-dependencies
- Static analysis binding: binding.yaml
