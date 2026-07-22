<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.vulnerable-dependencies vulnerable dependencies (good patterns)

Substrate-original good-pattern examples for dependency-management.vulnerable-dependencies.

## Pattern A: osv-scanner in CI with SARIF upload

```yaml
# .github/workflows/security.yml
- name: Run osv-scanner
  run: |
    osv-scanner --lockfile=package-lock.json \
                --lockfile=requirements.txt \
                --format=sarif \
                --output=osv-results.sarif \
                ./

- name: Upload SARIF to GitHub
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: osv-results.sarif
    category: osv-scanner

- name: Fail on findings at high or critical
  run: |
    HIGH_COUNT=$(jq '[.runs[].results[] | select(.level == "error")] | length' osv-results.sarif)
    if [ "$HIGH_COUNT" -gt 0 ]; then
      echo "Build blocked: $HIGH_COUNT high or critical findings"
      exit 1
    fi
```

Why this satisfies dependency-management.vulnerable-dependencies: osv-scanner runs against
all ecosystem lockfiles; SARIF output integrates with
GitHub's security tab; the build blocks at the substrate-
recommended threshold (high or above).

## Pattern B: pip-audit with strict mode

```yaml
# .github/workflows/python-security.yml
- name: Run pip-audit
  run: |
    pip-audit --requirement requirements.txt \
              --format sarif \
              --output pip-audit.sarif \
              --strict \
              --ignore-vuln GHSA-EXAMPLE-1234  # documented exemption
```

Why this satisfies dependency-management.vulnerable-dependencies: `--strict` treats audit
findings as errors; the build blocks when CVEs are
present. The single ignored advisory references the
project's exemption file with rationale.

## Pattern C: Dependabot for continuous monitoring

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
    groups:
      patch-updates:
        update-types:
          - "patch"

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Why this satisfies dependency-management.vulnerable-dependencies (continuous monitoring):
Dependabot watches the advisory feed continuously;
critical CVEs result in automatic PRs; patch-updates
grouped to reduce noise.

## Pattern D: Documented exemption with deadline

```yaml
# .security/exemptions/dependency-management.vulnerable-dependencies-exemptions.yaml
exemptions:
  - advisory: "GHSA-EXAMPLE-1234"
    dependency: "old-library"
    affected-version-range: "<2.5.0"
    reason: |
      The vulnerable code path is not reached by our
      application. Confirmed via Semgrep reachability
      scan 2026-05-15. The library has no upstream fix;
      we are migrating off this library.
    remediation-plan: |
      Migration to alternative-library tracked in
      JIRA-1234. Expected complete by 2026-06-15.
    deadline: "2026-06-15"
    approved-by: "myoung"
    approved-date: "2026-05-16"
```

Why this satisfies dependency-management.vulnerable-dependencies (exemption discipline):
exemptions are time-bounded; rationale is concrete; the
remediation path is named; the approval is auditable.

## Pattern E: govulncheck with reachability analysis (Go)

```yaml
# Go vulnerability check with reachability
- name: govulncheck
  run: |
    go install golang.org/x/vuln/cmd/govulncheck@latest
    govulncheck -mode=binary -format=sarif ./... > vuln.sarif

- name: Fail on reachable findings only
  run: |
    REACHABLE=$(jq '[.runs[].results[] | select(.kind == "fail")] | length' vuln.sarif)
    if [ "$REACHABLE" -gt 0 ]; then
      echo "Build blocked: $REACHABLE reachable vulnerabilities"
      exit 1
    fi
```

Why this satisfies dependency-management.vulnerable-dependencies (with reachability):
govulncheck reports vulnerabilities AND whether the
application's call graph reaches the vulnerable
function. Substrate-acceptable to block only on reachable
findings, with non-reachable findings as warnings.

## Cross-reference

- Anti-patterns: examples/dependency-management/vulnerable-dependencies-anti-pattern.md
- Substrate rule: dependency-management.vulnerable-dependencies
- Static analysis binding: binding.yaml
