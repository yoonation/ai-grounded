<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.no-hardcoded-credentials credentials hardcoded (good patterns)

Substrate-original good-pattern examples for authentication.no-hardcoded-credentials.

## Pattern A: Environment variables (Python)

```python
import os

# Credentials read at process startup from environment.
# The deployment platform supplies the values from its
# secrets management.
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
STRIPE_API_KEY = os.environ["STRIPE_API_KEY"]
JWT_SIGNING_SECRET = os.environ["JWT_SIGNING_SECRET"]

# Optional credentials with defensible defaults (None).
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
```

Why this satisfies authentication.no-hardcoded-credentials:
- Source code references the variable name, not the value
- Value lives outside source: in deployment-provided
  environment, never in the repository
- Missing credentials fail fast at startup (KeyError) rather
  than silently using empty strings

## Pattern B: AWS Secrets Manager (Python / boto3)

```python
import boto3
import json
from functools import lru_cache

# Application authenticates to AWS via IAM role (no stored
# AWS credentials in the application; the cloud provides
# identity via instance profile, ECS task role, etc).
secrets_client = boto3.client("secretsmanager")

@lru_cache(maxsize=None)
def get_secret(name):
    response = secrets_client.get_secret_value(SecretId=name)
    return json.loads(response["SecretString"])

# At use site:
db_secret = get_secret("prod/database/credentials")
db_password = db_secret["password"]
```

Why this satisfies authentication.no-hardcoded-credentials:
- No credentials in source code
- Zero-bootstrap-credential: the application's identity to
  AWS is provided by the cloud, not by stored credentials
- Secrets are centrally rotatable without redeployment

## Pattern C: HashiCorp Vault (Python)

```python
import hvac

# Vault client authenticates via Kubernetes service account
# token, AWS IAM, or other workload identity. No stored Vault
# credentials in source.
vault = hvac.Client(url="https://vault.example.com")
vault.auth.kubernetes.login(
    role="myapp",
    jwt=open("/var/run/secrets/kubernetes.io/serviceaccount/token").read(),
)

# Read secret from Vault at runtime.
secret = vault.secrets.kv.v2.read_secret_version(path="myapp/prod")
db_password = secret["data"]["data"]["db_password"]
```

Why this satisfies authentication.no-hardcoded-credentials:
- No credentials in source
- Workload identity provides Vault authentication
- Vault's audit log records every secret access for security
  monitoring

## Pattern D: .env file with .gitignore (Node.js)

```javascript
// In source: load .env at startup. The .env file itself is
// listed in .gitignore (see authentication.no-credential-files-in-repo) so it never reaches
// the repository.
require("dotenv").config();

const dbPassword = process.env.DATABASE_PASSWORD;
const apiKey = process.env.STRIPE_API_KEY;

if (!dbPassword || !apiKey) {
  throw new Error("Required environment variables missing");
}
```

```bash
# .gitignore
.env
.env.local
.env.*.local
!.env.example
```

```bash
# .env.example (committed; safe because values are placeholders)
DATABASE_PASSWORD=changeme
STRIPE_API_KEY=sk_test_placeholder
```

Why this satisfies authentication.no-hardcoded-credentials:
- Real .env never committed (see authentication.no-credential-files-in-repo)
- .env.example documents required variables without exposing
  real values
- Fail-fast pattern catches missing variables at startup

## Pattern E: Spring Boot externalized configuration (Java)

```java
@Component
public class DatabaseConfig {
    // Property is supplied at runtime from application.yaml,
    // environment, command-line, or Spring Cloud Config Server.
    // Source contains the property name, not the value.
    @Value("${database.password}")
    private String databasePassword;

    // ...
}
```

```yaml
# application.yaml (committed)
database:
  password: ${DATABASE_PASSWORD}  # resolved from env at runtime
```

Why this satisfies authentication.no-hardcoded-credentials:
- @Value reference is the property name
- Property resolution defers to environment or external config
- Spring's profile and config-server mechanisms allow
  centralized rotation

## What good patterns have in common

- Source code names credentials but does not contain their values
- Value lives in: environment variables, secrets management
  service, encrypted configuration, or hardware secure module
- Fail-fast on missing values rather than silently defaulting
  to empty strings (which would create authentication failures
  that are hard to diagnose)

## Cross-reference

- Substrate rule: authentication.no-hardcoded-credentials in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Anti-patterns: examples/authentication/credentials-hardcoded-anti-pattern.md
- Related rule: authentication.no-credential-files-in-repo covers credential-bearing files in source repositories
