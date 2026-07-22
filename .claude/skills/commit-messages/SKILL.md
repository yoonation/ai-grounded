---
name: commit-messages
description: Conventional commit message format. Use when committing code, creating PRs, or generating changelogs.
---

# Conventional Commits

## Format

    <type>(<scope>): <short description>

    [optional body]

    [optional footer]

## Types
- `feat` — new feature or capability
- `fix` — bug fix
- `docs` — documentation only
- `chore` — maintenance, dependencies, tooling
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or updating tests
- `ci` — CI/CD configuration changes
- `security` — security-related changes (patches, hardening)

## Rules
- Subject line: imperative mood, lowercase, no period, under 72 chars
- Body: explain what and why, not how
- Footer: reference issue numbers (Closes #123)
- Breaking changes: add BREAKING CHANGE: in footer or ! after type

## Examples
- feat(auth): add OAuth2 OIDC provider support
- fix(api): handle null response from payment gateway
- security(iam): restrict S3 bucket policy to specific ARNs
- chore(deps): upgrade terraform provider to 5.x
- docs(readme): add architecture diagram
