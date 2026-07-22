<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.sensitive-files-gitignored sensitive files gitignored (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.sensitive-files-gitignored.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Missing .env exclusion

```gitignore
# .gitignore - INCOMPLETE
node_modules/
build/
dist/
# .env is missing
```

Why this violates secrets-management.sensitive-files-gitignored: a contributor running
`git add .` from the project root will stage `.env`. The
.gitignore is the principal preventive control; omitting
the most common credential-bearing file pattern defeats
the rule.

## Anti-pattern B: Committing .env directly

```bash
# DO NOT DO THIS - shell history showing committing .env
$ git add .env
$ git commit -m "add production env file"
$ git push
```

Why this violates secrets-management.sensitive-files-gitignored: the .env file contains
real production credentials. Committing rewrites history
to include them; remediation requires (1) immediate
rotation of every secret, (2) history rewrite or repo
recreation, and (3) treating the period since commit as
the leak window for incident response.

## Anti-pattern C: Excluding the wrong pattern (typo)

```gitignore
# DO NOT DO THIS - typo creates false sense of protection
.evn
.env.prod
*.key.bak
```

Why this violates secrets-management.sensitive-files-gitignored: `.evn` is a typo;
`.env` is not excluded. `.env.prod` is excluded but `.env`
itself is not. `*.key.bak` is excluded but `*.key` is
not. Each typo creates a false sense of protection.

## Anti-pattern D: Including private keys in test fixtures

```
test/fixtures/
├── test-cert.pem        # Test certificate, intentionally committed
├── test-private-key.pem # Real-looking private key, intentionally committed
└── test-credentials.json # Test credentials, intentionally committed
```

Why this violates secrets-management.sensitive-files-gitignored (in spirit): even if the
keys are "test only", a casual observer cannot tell them
from real material. Tooling will flag them as findings.
The substrate-recommended pattern is to:
- Use clearly mock values (all zeros, "DUMMY_KEY_FOR_TESTING")
- Generate test keys at test setup time, not commit them
- Annotate test fixtures clearly with comments

If real-looking test material must be committed, the
consumer's gitleaks `.gitleaksignore` or detect-secrets
baseline records the exemption explicitly.

## Anti-pattern E: Negation pattern incorrectly placed

```gitignore
# DO NOT DO THIS - negation order is wrong
!.env.example
.env
*.tfvars
!*.tfvars.example
```

Why this violates secrets-management.sensitive-files-gitignored: in git's negation
semantics, `!pattern` must appear AFTER the rule that
would otherwise exclude the file. Here `!.env.example`
appears BEFORE `.env`; but `.env.example` was not yet
excluded, so the negation is meaningless. The substrate-
recommended pattern is `pattern` first, then `!negation`.

## Anti-pattern F: Excluding directory but not contents

```gitignore
# DO NOT DO THIS - the directory is excluded but a contributor
# could still git add specific files inside it.
secrets/
```

Why this violates secrets-management.sensitive-files-gitignored (partial): `secrets/`
prevents `git add secrets/`, but `git add secrets/file.key`
may add a specific file. Substrate-recommended addition:
`secrets/*` plus `!secrets/.gitkeep` to keep the directory
present while excluding all contents.

## Anti-pattern G: Relying on .gitignore alone (no scanning)

```gitignore
# DO NOT DO THIS - the .gitignore is correct but there is
# no backup verification.
.env
*.pem
# (no pre-commit hook, no CI scan)
```

Why this violates secrets-management.sensitive-files-gitignored (in spirit): a
contributor with `git add --force` or an unusual commit
flow bypasses .gitignore. Without a pre-commit hook
(gitleaks, detect-secrets) and a CI guard, there is no
catch for the bypass case.

## Cross-reference

- Good patterns: examples/secrets-management/sensitive-files-gitignored-good.md
- Substrate rule: secrets-management.sensitive-files-gitignored
- Static analysis binding: binding.yaml
