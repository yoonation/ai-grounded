<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.no-secrets-in-source no secrets in source (good patterns)

Substrate-original good-pattern examples for secrets-management.no-secrets-in-source.

## Pattern A: Reading from a secrets manager client at startup (Python)

```python
import boto3
from functools import lru_cache

@lru_cache(maxsize=None)
def get_secret(name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=name)
    return response["SecretString"]

DATABASE_URL = get_secret("prod/db/url")
```

Why this satisfies secrets-management.no-secrets-in-source: no secret string literal
appears in source. The secret value lives in AWS Secrets
Manager; the code references it by name. The build artifact
contains no secret material.

## Pattern B: Environment variable as opaque pointer to platform (Node.js)

```javascript
// SecretId points at the platform; the value is not in source.
const secretClient = new SecretManagerServiceClient();
const secretId = process.env.STRIPE_API_KEY_SECRET_ID;
const [accessResponse] = await secretClient.accessSecretVersion({
  name: secretId,
});
const stripeKey = accessResponse.payload.data.toString();
```

Why this satisfies secrets-management.no-secrets-in-source: the environment variable
holds a pointer (a GCP Secret Manager resource name like
`projects/123/secrets/stripe-key/versions/latest`), not the
secret value itself. The secret value retrieval happens at
runtime through the platform's authenticated API.

## Pattern C: Encrypted at rest, committed file (Go)

```go
// secrets.enc is committed; decryption requires KMS access
// that the workload's IAM role is granted at runtime.
decrypted, err := kms.Decrypt(ctx, &kms.DecryptInput{
    KeyId:          aws.String(kmsKeyArn),
    CiphertextBlob: ciphertext,
})
if err != nil {
    return fmt.Errorf("secret decrypt: %w", err)
}
apiKey := string(decrypted.Plaintext)
```

Why this satisfies secrets-management.no-secrets-in-source: secrets committed in
encrypted form depend on a separately-controlled KMS key
for decryption. An attacker with the source repository
cannot recover the plaintext. The substrate's secrets-management.encryption-at-rest
review additionally checks the key separation property.

## Pattern D: Example file pattern (.env.example committed)

```bash
# .env.example - committed to repository. Values are placeholders.
# Developers copy to .env and fill from the platform.
DATABASE_URL=postgres://user:[REPLACE_VIA_VAULT]@host/db
STRIPE_SECRET_KEY=[REPLACE_VIA_VAULT]
JWT_SIGNING_KEY=[REPLACE_VIA_VAULT]
```

Why this satisfies secrets-management.no-secrets-in-source: the file documents what
secrets the application expects without committing values.
The .env file (containing real values) is gitignored per
secrets-management.sensitive-files-gitignored.

## Pattern E: Build-time secret injection via platform (Dockerfile)

```dockerfile
# Dockerfile uses BuildKit secret mount; secret is never
# baked into image layers.
RUN --mount=type=secret,id=npm_token,target=/root/.npmrc \
    npm install --omit=dev
```

Why this satisfies secrets-management.no-secrets-in-source: the secret is mounted
from the build environment at build time and is not written
to any image layer. The secret value never enters the
committed source or the build output.

## Cross-reference

- Anti-patterns: examples/secrets-management/no-secrets-in-source-anti-pattern.md
- Substrate rule: secrets-management.no-secrets-in-source
- Static analysis binding: binding.yaml
