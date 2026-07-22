<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.signed-commit-and-protected-branch source-authority discipline absent

Substrate-rejected patterns.

## Anti-pattern A: unprotected main branch

```yaml
branches:
  main:
    # No protection rules configured
```

Anyone with push access can push directly to main, bypass review,
push unsigned commits, force-push to overwrite history. The
release pipeline consumes whatever is at HEAD without verification.

## Anti-pattern B: protection without signature requirement

```yaml
branches:
  main:
    required_pull_request_reviews:
      required_approving_review_count: 1
    required_signatures: false  # Substrate-rejected
```

Reviews are required, but commits are unsigned. The reviewer
sees the diff but cannot verify which signing identity committed
to those bytes; commits from compromised accounts are
indistinguishable.

## Anti-pattern C: enforce_admins disabled with no bypass log

```yaml
branches:
  main:
    required_pull_request_reviews:
      required_approving_review_count: 1
    enforce_admins: false  # Bypass enabled
    # No bypass log; no audit cadence
```

Administrators can bypass the protection silently. Substrate-
acceptable alternative: enforce_admins true (no bypass) or
bypass invocations logged and reviewed quarterly per supply-chain.attestation-and-sbom-retention.

## Anti-pattern D: personal access token used as automation principal

```yaml
# CI configuration uses a long-lived PAT
env:
  GITHUB_TOKEN: ${{ secrets.PAT_FROM_ALICE }}  # Personal token
```

The PAT is tied to alice's personal account. If alice leaves,
the PAT continues to function until rotated. PATs are substrate-
rejected for automation; substrate-preferred is OIDC-bound
short-lived credentials.

## Why these patterns fail

The protection-and-signing combination anchors the consumer's
source authority. Anti-patterns A and B remove one anchor each;
C creates an undocumented bypass path; D substitutes a long-
lived credential where short-lived is substrate-required.
