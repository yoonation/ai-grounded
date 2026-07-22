<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.signed-commit-and-protected-branch signed commits and protected branches

Substrate-recommended source-authority discipline.

## Pattern A: GitHub branch protection configuration

GitHub repository settings (as YAML for clarity):

```yaml
# Equivalent to the GitHub branch-protection rules UI
branches:
  main:
    required_pull_request_reviews:
      required_approving_review_count: 2  # stricter profile
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
    required_signatures: true  # signed-commit enforcement
    required_status_checks:
      strict: true
      contexts:
        - "ci / lint"
        - "ci / test"
        - "ci / supply-chain.no-remote-execution-in-build-no-remote-execution"
        - "ci / sbom-generation"
        - "ci / slsa-provenance-verification"
    enforce_admins: true  # administrator-bypass disabled
    restrictions:
      users: []
      teams:
        - "release-bots"  # only the release-bot team may push
```

## Pattern B: gitsign-based commit signing

Developer machine configuration (substrate-recommended for
keyless signing):

```bash
# .git/config (per-repo) or ~/.gitconfig (global)
[user]
    name = Alice Engineer
    email = alice@example.com
    signingkey = alice@example.com  # OIDC identity

[gpg]
    format = x509
    x509.program = gitsign

[gpg "x509"]
    program = gitsign

[commit]
    gpgsign = true

[tag]
    gpgsign = true
```

The developer's commits are signed with a short-lived OIDC-bound
certificate issued by Fulcio against the developer's
authenticated identity (GitHub, Google, or enterprise IdP).

## Pattern C: CI verification of signed commits on release

```yaml
# .github/workflows/release.yaml
jobs:
  verify-release-tag:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout with tag
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
        with:
          ref: ${{ github.ref }}
          fetch-depth: 0
          fetch-tags: true

      - name: Verify tag signature
        run: |
          git verify-tag "${GITHUB_REF_NAME}"

      - name: Verify commit signatures on release-branch path
        run: |
          # Verify the last 50 commits on main
          for commit in $(git log --format=%H -50 origin/main); do
            git verify-commit "${commit}" || {
              echo "Unsigned commit: ${commit}"
              exit 1
            }
          done
```

## Pattern D: Bypass log

`docs/bypass-log.md`:

```markdown
# Branch-Protection Bypass Log

| Date | Branch | Bypasser | Reason | Approval |
|------|--------|----------|--------|----------|
| 2026-04-12 | main | alice@example.com | Emergency revert of broken commit; manager approval pre-event in Slack #incidents | Bob (VP Eng) |
```

Bypass invocations are recorded with rationale and approver.

## Key observations

- Branch protection enforces pull-request review, signed-commit
  requirement, status checks, and push restrictions
- Signing via gitsign eliminates long-lived key management
- Bypass discipline preserves audit trail for the substrate-
  acknowledged-rare cases where bypass is operationally required
