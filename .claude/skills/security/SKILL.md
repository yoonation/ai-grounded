---
name: security
description: Security patterns and frameworks. Use when reviewing code for vulnerabilities, designing authentication/authorization, writing IAM policies, handling secrets, or discussing threat models.
---

# Security Patterns

## Frameworks
- OWASP LLM Top 10 — primary reference for AI/ML application security
- MITRE ATLAS — adversarial threat landscape for AI systems
- STRIDE — threat modeling methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- NIST AI RMF — AI risk management framework
- ISO 42001 — AI management system standard

## Input Validation
- Validate at system boundaries — never trust external input
- Use allowlists over denylists where possible
- Parameterize all database queries — never concatenate
- Sanitize output to prevent XSS
- Validate file uploads: type, size, content inspection

## Authentication & Authorization
- Use short-lived tokens over long-lived credentials
- Implement RBAC with least-privilege defaults
- Prefer OIDC federation over stored credentials
- Never store passwords in plaintext — use bcrypt/argon2
- Rate-limit authentication endpoints

## Secrets Management
- Never hardcode secrets in source code
- Use AWS SSM Parameter Store or Secrets Manager
- Rotate credentials on a defined schedule
- Audit secret access with CloudTrail
- .env files are for local dev only — never in production

## Infrastructure Security
- Encrypt at rest (S3, EBS, RDS) and in transit (TLS 1.2+)
- Use VPC with private subnets for backend services
- Security groups: deny all inbound by default, open only what's needed
- Enable CloudTrail, GuardDuty, Config for audit and detection
- Container images: scan for CVEs, run as non-root, use distroless base

## AI/ML Security
- Validate and sanitize all LLM inputs and outputs
- Implement guardrails for prompt injection defense
- Log and monitor model inputs/outputs for abuse detection
- Apply rate limiting to inference endpoints
- Never expose model weights or training data publicly

## Anti-Patterns
- Never disable SSL verification, even in dev
- Never use `eval()`, `exec()`, `os.system()`, `shell=True`
- Never log sensitive data (tokens, passwords, PII)
- Never use `chmod 777` or overly permissive file permissions
- Never trust client-side validation as the only check
