<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.sensitive-files-gitignored sensitive files gitignored (good patterns)

Substrate-original good-pattern examples for secrets-management.sensitive-files-gitignored.

## Pattern A: Comprehensive .gitignore with environment files

```gitignore
# Environment files (never committed)
.env
.env.local
.env.*.local
.env.production
.env.staging
.env.development

# Allow example/template files
!.env.example
!.env.template
!.env.sample
```

Why this satisfies secrets-management.sensitive-files-gitignored: production environment
files are excluded by pattern. The negation pattern allows
the documented `.env.example` to be committed as a template
without enabling real values to slip in.

## Pattern B: Cryptographic material excluded

```gitignore
# Private keys and certificates
*.pem
*.key
*.priv
*.pfx
*.p12
*.jks
*.keystore

# SSH keys (in any directory)
id_rsa
id_rsa.pub
id_ecdsa
id_ed25519
id_dsa
```

Why this satisfies secrets-management.sensitive-files-gitignored: cryptographic material
is excluded by file extension and known filename. The
patterns cover the common formats; consumers may extend
for ecosystem-specific naming.

## Pattern C: Cloud and tool credentials excluded

```gitignore
# Cloud provider credentials
.aws/credentials
gcp-service-account*.json
service-account-*.json
azure-credentials.json

# Terraform sensitive state and variable files
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
*.tfvars
!*.tfvars.example
!*.tfvars.sample

# Database dumps
*.sql.gz
*.dump
backup-*.tar*
```

Why this satisfies secrets-management.sensitive-files-gitignored: cloud provider
credentials and infrastructure-as-code sensitive files are
excluded. The Terraform tfvars pattern allows example
files (with placeholder values) while excluding real ones.

## Pattern D: Pre-commit hook configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Why this satisfies secrets-management.sensitive-files-gitignored (complementary): the
.gitignore is preventive, but pre-commit hooks back it up.
Hooks catch attempted commits of sensitive files even when
a contributor's local .gitignore is mis-configured.

## Pattern E: CI guard for sensitive-file patterns

```yaml
# .github/workflows/security.yml
- name: Sensitive file pattern guard
  run: |
    if git diff --name-only origin/main...HEAD | \
       grep -E '\.(pem|key|pfx|p12|jks)$|^\.env$|^id_rsa$|^credentials\.json$'; then
      echo "Sensitive file pattern detected in PR"
      exit 1
    fi
```

Why this satisfies secrets-management.sensitive-files-gitignored: CI guard backstops the
.gitignore and pre-commit hook. Even if a contributor
bypasses pre-commit (with --no-verify), the CI gate catches
the pattern.

## Cross-reference

- Anti-patterns: examples/secrets-management/sensitive-files-gitignored-anti-pattern.md
- Substrate rule: secrets-management.sensitive-files-gitignored
- Static analysis binding: binding.yaml
