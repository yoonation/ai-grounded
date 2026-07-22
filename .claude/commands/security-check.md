---
name: security-check
description: Quick security audit of the current project.
disable-model-invocation: true
---

Perform a security audit of this project:

1. Check .gitignore for missing entries (.env, *.tfstate, *.pem, *.key)
2. Search for hardcoded credentials: `grep -rn 'password\|api_key\|secret\|token' --include='*.py' --include='*.tf' --include='*.yaml' --include='*.json' src/ infra/`
3. Check Terraform for overly permissive IAM policies: `grep -rn '"*"' --include='*.tf' infra/`
4. Check for dangerous function usage: `grep -rn 'eval\|exec\|os.system\|shell=True' --include='*.py' src/`
5. Verify no .env files are tracked: `git ls-files | grep -i env`
6. Report findings with severity and remediation.
