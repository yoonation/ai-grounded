<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.update-cadence update cadence (good patterns)

Substrate-original good-pattern examples for dependency-management.update-cadence.

## Pattern A: Renovate with lockfile maintenance

```json
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "lockFileMaintenance": {
    "enabled": true,
    "schedule": ["before 5am on monday"],
    "automerge": false
  },
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true,
      "platformAutomerge": true
    },
    {
      "matchUpdateTypes": ["minor"],
      "automerge": false,
      "schedule": ["before 5am on monday"]
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["dependencies", "major-update"]
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  }
}
```

Why this satisfies dependency-management.update-cadence: cadence is mechanized;
patch updates auto-merge after CI; minor updates batched
weekly; major updates flagged for human review;
vulnerability alerts pull through immediately.

## Pattern B: Dependabot configuration with grouped updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    groups:
      production-dependencies:
        dependency-type: "production"
        update-types: ["patch", "minor"]
      development-dependencies:
        dependency-type: "development"
        update-types: ["patch", "minor"]

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

Why this satisfies dependency-management.update-cadence: cadence is documented in
the config; grouping reduces PR noise; per-ecosystem
schedules acknowledge different change rates (npm
weekly, GitHub Actions monthly).

## Pattern C: Documented dependency inventory

```yaml
# /docs/dependency-inventory.yaml
last-reviewed: 2026-05-01
next-review: 2026-08-01

ecosystems:
  - name: npm
    direct-count: 23
    transitive-count: ~412
    automation: renovate
    cadence: weekly
    owner: platform-team

  - name: pip
    direct-count: 18
    transitive-count: ~85
    automation: dependabot
    cadence: weekly
    owner: data-team

critical-dependencies:
  - name: express
    rationale: HTTP server framework, high attack
                surface
    upgrade-policy: minor and patch within 7 days of
                     release after CI passes
  - name: pg
    rationale: database driver, security-sensitive
    upgrade-policy: patch within 24h; minor within
                     7 days
```

Why this satisfies dependency-management.update-cadence: the inventory makes
cadence explicit per dependency; critical dependencies
have tighter SLAs; ownership is named; review is
scheduled.

## Pattern D: Automated PR triage workflow

```yaml
# .github/workflows/dependency-triage.yml
name: Dependency PR Triage
on:
  pull_request:
    types: [opened]
    paths:
      - "package-lock.json"
      - "requirements.txt"
      - "go.sum"

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - name: Check if security-only
        run: |
          if echo "${{ github.event.pull_request.title }}" \
             | grep -iE "security|vulnerab|cve"; then
            gh pr edit ${{ github.event.pull_request.number }} \
              --add-label "security,priority-high"
          fi

      - name: Notify on stale dependency PRs
        run: |
          STALE=$(gh pr list --label dependencies \
                  --json number,createdAt \
                  --jq '[.[] | select(
                    ((now - (.createdAt | fromdateiso8601)) / 86400) > 14
                  )] | length')
          if [ "$STALE" -gt 5 ]; then
            echo "::warning::$STALE dependency PRs aged >14 days"
          fi
```

Why this satisfies dependency-management.update-cadence: cadence is observable;
security-flagged PRs are escalated; PR backlog drift
is surfaced as a CI warning.

## Pattern E: Quarterly self-assessment artifact

```markdown
# /security/dep-cadence-reviews/2026-Q2-review.md

Date: 2026-04-15
Reviewer: myoung
Period: 2026-Q1 (Jan 1 to Mar 31)

## Metrics
- Dependency PRs opened: 142
- Auto-merged after CI: 98 (69%)
- Merged after human review: 38 (27%)
- Rejected with rationale: 6 (4%)
- Median PR age at merge: 2 days
- Maximum PR age at merge: 14 days

## SLA compliance
- Patch updates within 7 days: 96% (target: 95%)
- High-severity advisories within 7 days: 100%
  (target: 100%)
- Major version updates evaluated within 30 days: 88%
  (target: 90%; one major upgrade blocked on
  breaking-change migration plan)

## Findings
1. One dependency (legacy-module) had no PR activity
   for 9 months. Investigation: upstream is archived.
   Action: migration to alternative-module tracked in
   JIRA-2345.
2. Major version backlog of 4 PRs. Action: dedicated
   sprint scheduled 2026-Q2.

Next review: 2026-07-15.
```

Why this satisfies dependency-management.update-cadence (review evidence):
cadence is measured against targets; abandoned
dependencies are identified; remediation is tracked.

## Cross-reference

- Anti-patterns: examples/dependency-management/update-cadence-anti-pattern.md
- Substrate rule: dependency-management.update-cadence
- Review checklist: checklist.md
