<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.no-credential-files-in-repo credentials in repo (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: .env with real values committed

```bash
# FORBIDDEN: .env file with real credential values, committed
# to the repository. The .gitignore did not exclude .env, or
# someone bypassed .gitignore with git add -f.
DATABASE_PASSWORD=hunter2-actual-password
STRIPE_API_KEY=sk_live_<redacted-example-key>
JWT_SIGNING_SECRET=<redacted-example-jwt-secret>
SENDGRID_API_KEY=SG.real_sendgrid_api_key_here
```

Why this violates authentication.no-credential-files-in-repo:
- Every credential disclosed to every repository reader
- Every CI agent, every backup, every clone has the credentials
- Remediation requires rotating every value and auditing the
  affected services for the entire exposure window

## Anti-pattern B: Private key file committed

```text
# FORBIDDEN: file at deploy/keys/production.pem
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxxx...
[real private key content here]
-----END RSA PRIVATE KEY-----
```

Why this violates authentication.no-credential-files-in-repo:
- Private key in source repository means anyone with read
  access can sign anything authenticated by this key
- The corresponding public key being committed is fine; the
  private key never is

## Anti-pattern C: GCP service account JSON committed

```json
{
  "type": "service_account",
  "project_id": "my-prod-project",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n",
  "client_email": "deployer@my-prod-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

Why this violates authentication.no-credential-files-in-repo:
- Service account private key in repository
- Full GCP API access for the service account's permission scope
- Common anti-pattern: developers download the JSON for local
  testing and commit it "temporarily"

## Anti-pattern D: Database backup committed

```sql
-- FORBIDDEN: file at backups/users.sql committed to repository.
-- The dump contains password hashes, session tokens, OAuth
-- tokens, and any other credential material stored in the
-- users table.
INSERT INTO users (email, password_hash, api_token) VALUES
('alice@example.com', '$argon2id$...', 'tok_aBcDeFg'),
('bob@example.com', '$argon2id$...', 'tok_xYz1234');
```

Why this violates authentication.no-credential-files-in-repo:
- Password hashes are credentials; authentication.password-hashing protects them
  in transit and at rest, but a committed backup bypasses
  those protections
- API tokens are bearer credentials
- Even if hashes are properly slow-hashed, they should not
  travel in version control

## Anti-pattern E: Terraform state with credentials

```text
# FORBIDDEN: terraform.tfstate committed. State file often
# contains sensitive values: database passwords passed via
# variables, generated random_password resources, secrets
# created in cloud secret managers (the state mirrors the
# value).
```

Why this violates authentication.no-credential-files-in-repo:
- Terraform state is sensitive by design
- The recommended pattern is remote state with locking
  (S3+DynamoDB, Terraform Cloud, GCS, etc.)
- Local state files (terraform.tfstate, terraform.tfstate.backup)
  must be excluded from version control

## Anti-pattern F: kubeconfig with embedded credentials

```yaml
# FORBIDDEN: kubeconfig with embedded user token.
apiVersion: v1
kind: Config
clusters:
  - name: production
    cluster:
      server: https://prod-cluster.example.com
users:
  - name: developer
    user:
      token: eyJhbGciOiJSUzI1NiIsImtpZCI6...
```

Why this violates authentication.no-credential-files-in-repo:
- Kubernetes API token grants full access at the token's RBAC scope
- kubeconfig files are personal; they belong in ~/.kube/, not
  in shared repositories

## Anti-pattern G: Bypassing .gitignore with git add -f

```bash
# Even with proper .gitignore configuration, the -f flag
# forces inclusion. This anti-pattern is sometimes used "just
# this once" and ends up in the repository permanently.
git add -f .env
git commit -m "include env for now"
```

Why this violates authentication.no-credential-files-in-repo:
- .gitignore prevents accidental inclusion; -f bypasses
  that protection
- The "just this once" pattern is how credentials reach
  long-term repository history

## What anti-patterns have in common

- Credential-bearing file types committed to source control
- Database dumps, state files, kubeconfig, service account
  JSON, .env, private keys
- Bypasses of the .gitignore protection mechanism

## Cross-reference

- Substrate rule: authentication.no-credential-files-in-repo in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Good examples: examples/authentication/credentials-in-repo-good.md
- Related: authentication.no-hardcoded-credentials (credentials as code literals in source)
