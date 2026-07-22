---
description: Security rules enforced on all code changes
globs: ["**/*.py", "**/*.tf", "**/*.sh", "**/*.yaml", "**/*.json", "**/*.js", "**/*.ts"]
---

# Security Rules

These rules supplement the hooks in settings.json.
Hooks enforce critical blocks deterministically.
These rules guide Claude's behavior for everything else.

## Credentials
- NEVER hardcode credentials, API keys, tokens, or passwords
- Use environment variables or secrets manager references
- If you see a credential in code, flag it immediately — do not proceed

## IAM and Access Control
- Every IAM policy must follow least-privilege
- Never use Action: "*" or Resource: "*" without explicit justification
- Prefer managed policies over inline policies
- Document why elevated permissions are needed in code comments

## Data Protection
- Encrypt at rest and in transit by default
- Never log sensitive data: tokens, passwords, PII, PHI
- Sanitize error messages — never expose stack traces to users
- Use parameterized queries for all database operations

## Dependencies
- Pin dependency versions — no floating ranges in production
- Check for known CVEs before adding new dependencies
- Prefer well-maintained libraries with active security response

## Container Security
- Never run containers as root
- Use distroless or minimal base images
- Scan images for vulnerabilities before pushing
- Never mount sensitive host paths into containers
