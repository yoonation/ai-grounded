<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.no-credential-files-in-repo credentials in repo (good patterns)

Substrate-original good-pattern examples for authentication.no-credential-files-in-repo.

## Pattern A: .gitignore excludes credential files

```bash
# .gitignore (committed)

# Environment files with real values
.env
.env.local
.env.*.local
.env.production

# Allow example files
!.env.example
!.env.template

# Private key files
*.pem
*.key
*.pfx
*.p12
id_rsa
id_rsa.pub
id_ecdsa
id_ed25519

# Cloud credential files
aws-credentials
.aws/credentials
gcp-service-account*.json
gcp-key*.json

# Generic credential files
credentials.json
credentials.yaml
credentials.yml
secrets.json
secrets.yaml
secrets.yml

# Application-specific
config/secrets.yml
config/master.key
.netrc
.npmrc
.pypirc
```

Why this satisfies authentication.no-credential-files-in-repo:
- Standard credential file patterns excluded
- `.env.example` allowed via `!` prefix for documentation purposes
- File patterns cover common credential storage conventions
  across languages and ecosystems

## Pattern B: .env.example documents required variables

```bash
# .env.example (committed; safe because values are placeholders)
# Copy to .env and fill in real values. .env is gitignored.

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
DATABASE_PASSWORD=changeme

# External services
STRIPE_API_KEY=sk_test_replace_with_real_key
SENDGRID_API_KEY=SG.replace_with_real_key

# Application
JWT_SIGNING_SECRET=generate_with_openssl_rand_-base64_32
SESSION_SECRET=generate_with_openssl_rand_-base64_32
```

Why this satisfies authentication.no-credential-files-in-repo:
- Documents the contract (what variables the app needs)
  without exposing real values
- Placeholder values are explicit non-credentials
- New developers know what to fill in without reading
  application code

## Pattern C: Encrypted credential file with SOPS

```yaml
# secrets.enc.yaml (committed; safe because encrypted at rest)
database:
    password: ENC[AES256_GCM,data:hXxL...,iv:...,tag:...,type:str]
api:
    stripe_key: ENC[AES256_GCM,data:Y2Pk...,iv:...,tag:...,type:str]
sops:
    kms:
        - arn: arn:aws:kms:us-east-1:123456789012:key/abc-def
    age:
        - recipient: age1...
    lastmodified: '2026-05-18T12:00:00Z'
    version: 3.7.3
```

```bash
# Decrypt at runtime
sops -d secrets.enc.yaml > /tmp/secrets.yaml
# (or use SOPS integrations for Kubernetes, Terraform, etc.)
```

Why this satisfies authentication.no-credential-files-in-repo:
- File is committed but its content is encrypted
- Decryption keys are managed by KMS or age, not in the
  repository
- SOPS metadata identifies the decryption mechanism

## Pattern D: Pre-commit hook prevents accidental commits

```yaml
# .pre-commit-config.yaml (committed)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

Why this satisfies authentication.no-credential-files-in-repo:
- Mechanical prevention at commit time
- Catches credentials before they reach the repository
- detect-secrets baseline tracks known and accepted findings

## Pattern E: CI gate scans pull requests

```yaml
# .github/workflows/secret-scan.yml (committed)
name: Secret scan
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history for diff scanning
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Why this satisfies authentication.no-credential-files-in-repo:
- Catches credentials in PR diff before merge
- Defense in depth alongside pre-commit hooks (developers can
  skip pre-commit; CI gate they cannot)

## What good patterns have in common

- .gitignore excludes credential file patterns by default
- Example files (.env.example) document the contract without
  exposing values
- Encrypted credentials in repository are safe because
  decryption keys are managed separately
- Mechanical prevention via pre-commit hooks and CI gates

## Cross-reference

- Substrate rule: authentication.no-credential-files-in-repo in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Anti-patterns: examples/authentication/credentials-in-repo-anti-pattern.md
- Related: authentication.no-hardcoded-credentials (credentials as code literals in source)
