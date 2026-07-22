<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.runtime-retrieval runtime retrieval (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.runtime-retrieval.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Environment variable as the platform (Python)

```python
# DO NOT DO THIS - the deployment system is acting as the
# secrets platform.
DATABASE_URL = os.environ["DATABASE_URL"]
STRIPE_KEY = os.environ["STRIPE_KEY"]
```

Why this violates secrets-management.runtime-retrieval: the deployment system
(Kubernetes Secret manifest, Helm values, Terraform
variables) is functioning as the secrets store. There is
no platform retrieval, no audit trail, no per-secret
access policy, and rotation requires redeploy. The
substrate-recommended pattern is to use the environment
variable as a POINTER to the platform (e.g., the secret's
ARN or resource name), not as the value carrier.

## Anti-pattern B: Read at startup, never refresh (Java)

```java
// DO NOT DO THIS
public class AppConfig {
    private static final String API_KEY;
    static {
        // Read once at class initialization; never refresh
        API_KEY = SecretsClient.read("api-key");
    }
}
```

Why this violates secrets-management.runtime-retrieval: even though retrieval
is from the platform, the read-once-and-cache-forever
pattern defeats rotation. When the platform rotates the
secret, the application continues using the old value
until restart. Substrate-recommended pattern: re-read on
a TTL or on authentication failure.

## Anti-pattern C: Static credential to retrieve secrets (Node.js)

```javascript
// DO NOT DO THIS - chicken-and-egg with static credential
const vaultClient = new VaultClient({
  endpoint: process.env.VAULT_ADDR,
  token: "s.X1y2Z3a4B5c6D7e8F9g0H1i2",  // static token in source
});

const apiKey = await vaultClient.read("secret/api-key");
```

Why this violates secrets-management.runtime-retrieval (and secrets-management.no-secrets-in-source): the
Vault token used to authenticate to the platform is itself
a static credential in source. The chicken-and-egg problem
is solved by workload identity: Kubernetes service account,
AWS IRSA, GCP workload identity, Azure managed identity.

## Anti-pattern D: Credential passed through many function arguments

```python
# DO NOT DO THIS - the credential propagates far from its retrieval point
def main():
    creds = get_creds()
    do_work(creds)

def do_work(creds):
    helper_a(creds)
    helper_b(creds)
    # ... credential threaded through many call sites
```

Why this violates secrets-management.runtime-retrieval (in spirit): the
credential's scope is much broader than its use. A
refactor to log function arguments anywhere in the chain
risks disclosure. Substrate-recommended pattern: retrieve
close to the use site, or pass an opaque accessor that
performs retrieval on demand.

## Anti-pattern E: Fallback to default on platform failure

```python
# DO NOT DO THIS - silent degradation
def get_api_key() -> str:
    try:
        return secrets_client.get("api-key")
    except Exception:
        # Fall back to a default value
        return "fallback-key"  # which is treated by the API as invalid
```

Why this violates secrets-management.runtime-retrieval: silent fallback hides
the platform failure. The application "succeeds" at
retrieval but the API call subsequently fails. Errors
appear in an unrelated place. Substrate-recommended
pattern: fail-closed (let the retrieval failure propagate)
or use a cached value with explicit degraded-state
signaling to monitoring.

## Anti-pattern F: Secret retrieved via shell command in init script

```bash
# DO NOT DO THIS - retrieval via shell script with no
# audit, no caching, no error handling
export DATABASE_URL=$(aws secretsmanager get-secret-value \
                     --secret-id prod/db/url \
                     --query SecretString --output text)
exec ./app
```

Why this violates secrets-management.runtime-retrieval: the secret is retrieved
once at process start, placed in the environment, and the
process runs forever with the value in memory. Rotation
requires container or process restart. No structured
audit of in-application use. Substrate-recommended
pattern: in-process platform client with caching.

## Anti-pattern G: Secret carried in custom HTTP header to downstream

```python
# DO NOT DO THIS - propagating the credential downstream
@app.get("/data")
async def get_data(request):
    api_key = request.headers["X-API-Key"]  # caller's key
    # Propagate the caller's API key to downstream service
    resp = httpx.get("https://internal-api/data",
                     headers={"X-API-Key": api_key})
    return resp.json()
```

Why this violates secrets-management.runtime-retrieval (in spirit): the
caller's credential is propagated to the downstream
service. The downstream service has the caller's
credential and can misuse it. Substrate-recommended
pattern: the calling service authenticates to the
downstream service with its OWN service-account
credential.

## Anti-pattern H: Secret stored in long-lived in-memory plain string

```javascript
// DO NOT DO THIS - global plain string, no wrapper
let API_KEY = null;

async function init() {
  API_KEY = await secretsClient.get("api-key");
  // API_KEY is a plain JavaScript string accessible to
  // every module via the closure.
}

// Anything that introspects globals (debug endpoints,
// stack traces, error reporters) can capture the value.
```

Why this violates secrets-management.runtime-retrieval (in spirit): the plain-
string storage makes the value visible to every code
path. Stack traces from any error include the closure
scope; debug endpoints serialize globals. Substrate-
recommended pattern: a typed SecretString wrapper as
shown in the secrets-management.no-secrets-in-logs good-patterns examples.

## Cross-reference

- Good patterns: examples/secrets-management/runtime-retrieval-good.md
- Substrate rule: secrets-management.runtime-retrieval
- Review checklist: checklist.md
