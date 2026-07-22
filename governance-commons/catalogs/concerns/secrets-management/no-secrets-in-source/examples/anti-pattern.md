<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.no-secrets-in-source no secrets in source (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.no-secrets-in-source.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Hardcoded AWS access key (Python)

```python
# DO NOT DO THIS
import boto3

s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
)
```

Why this violates secrets-management.no-secrets-in-source: AWS credentials appear as
string literals. The credential is committed to history;
gitleaks and Semgrep will both flag it. Remediation requires
rotating the credentials, not just deleting the line.

## Anti-pattern B: Stripe API key in config (Node.js)

```javascript
// DO NOT DO THIS
const config = {
  stripeSecretKey: "sk_live_<redacted-example-key>",
  stripePublishableKey: "pk_live_<redacted-example-key>",
};
```

Why this violates secrets-management.no-secrets-in-source: Stripe live keys are
unambiguous secret material. The "config object" pattern
does not exempt the value from being a secret. The Stripe
key format is well-known to scanners.

## Anti-pattern C: Database URL with embedded credentials (Go)

```go
// DO NOT DO THIS
const dbURL = "postgres://app_user:hunter2@db.prod.example.com:5432/app_db"

func main() {
    db, _ := sql.Open("postgres", dbURL)
    // ...
}
```

Why this violates secrets-management.no-secrets-in-source: the connection string
contains the database password. URL-encoded credentials are
still credentials. Use environment-variable-as-pointer or
secrets-manager retrieval.

## Anti-pattern D: Django SECRET_KEY hardcoded

```python
# DO NOT DO THIS
# settings.py
SECRET_KEY = "django-insecure-1@5h(j8gx0!4q@4dw3rs_5tm9p&v8x9z@!q^&"
DEBUG = False
```

Why this violates secrets-management.no-secrets-in-source: Django's SECRET_KEY signs
session cookies and CSRF tokens. Disclosure enables session
forgery. Semgrep's
`python.django.security.audit.secret-key-loaded-from-env`
rule catches this. Even with "insecure-" prefix, production
deployments commit similar real keys.

## Anti-pattern E: PEM private key in repo

```python
# DO NOT DO THIS - private key as Python string
SIGNING_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
[example key body redacted - not a real key]
...many lines of base64...
-----END RSA PRIVATE KEY-----
"""
```

Why this violates secrets-management.no-secrets-in-source: PEM-encoded private keys
in source are detected by the generic private-key Semgrep
rule and by every dedicated secret scanner. Wrapping in a
language string does not hide the format.

## Anti-pattern F: "Encrypted" with hardcoded key (Java)

```java
// DO NOT DO THIS
public class Config {
    // "Encryption" with a hardcoded key offers no protection
    // when both ciphertext and key live in source.
    private static final byte[] KEY = "0123456789ABCDEF".getBytes();
    private static final String ENCRYPTED_API_KEY =
        "aXgrV2lYRWZuU1BkN09yWg==";  // base64 of XOR with KEY
}
```

Why this violates secrets-management.no-secrets-in-source: the key and the encrypted
material live in the same artifact. Anyone with the source
can recover the plaintext. The substrate's secrets-management.no-secrets-in-source
rule prohibits committing secret material regardless of
intermediate transformations that an attacker with source
access can reverse.

## Anti-pattern G: GitHub PAT in CI script

```yaml
# DO NOT DO THIS - workflow yaml
- name: Deploy
  run: |
    curl -H "Authorization: token ghp_<redacted-example-token>" \
      https://api.github.com/repos/org/repo/deployments
```

Why this violates secrets-management.no-secrets-in-source: a GitHub personal access
token in a CI workflow file is committed to the repository.
GitHub's secret scanning detects this format and revokes
the token. Use the workflow's `secrets.GITHUB_TOKEN` or a
manually-stored repository secret.

## Cross-reference

- Good patterns: examples/secrets-management/no-secrets-in-source-good.md
- Substrate rule: secrets-management.no-secrets-in-source
- Static analysis binding: binding.yaml
