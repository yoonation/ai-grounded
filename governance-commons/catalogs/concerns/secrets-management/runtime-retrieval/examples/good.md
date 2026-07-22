<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.runtime-retrieval runtime retrieval (good patterns)

Substrate-original good-pattern examples for secrets-management.runtime-retrieval.

## Pattern A: AWS Secrets Manager with workload identity (Python)

```python
import boto3
from functools import lru_cache
from datetime import datetime, timedelta

class SecretCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = timedelta(seconds=ttl_seconds)
        self._cache = {}  # name -> (value, expiry)

    def get(self, secret_name: str) -> str:
        now = datetime.utcnow()
        if secret_name in self._cache:
            value, expiry = self._cache[secret_name]
            if now < expiry:
                return value
        # Cache miss or expired
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        value = response["SecretString"]
        self._cache[secret_name] = (value, now + self.ttl)
        return value

# Module-level singleton
secrets = SecretCache(ttl_seconds=300)

def get_db_password() -> str:
    return secrets.get("prod/db/password")
```

Why this satisfies secrets-management.runtime-retrieval: secret is retrieved at
runtime from a dedicated platform (not from environment
variables alone); workload identity (the EC2 instance role,
ECS task role, or Lambda execution role) authenticates to
the platform; caching with TTL allows rotation to propagate
without restart; the platform's audit log records each
retrieval.

## Pattern B: HashiCorp Vault with Kubernetes auth (Go)

```go
package secrets

import (
    "context"
    vault "github.com/hashicorp/vault/api"
    "github.com/hashicorp/vault/api/auth/kubernetes"
)

func NewVaultClient(ctx context.Context, role string) (*vault.Client, error) {
    config := vault.DefaultConfig()
    client, err := vault.NewClient(config)
    if err != nil {
        return nil, err
    }
    // Workload identity: Kubernetes service account token
    k8sAuth, err := kubernetes.NewKubernetesAuth(role)
    if err != nil {
        return nil, err
    }
    authInfo, err := client.Auth().Login(ctx, k8sAuth)
    if err != nil {
        return nil, err
    }
    // Background refresh via LifetimeWatcher
    watcher, _ := client.NewLifetimeWatcher(&vault.LifetimeWatcherInput{
        Secret: authInfo,
    })
    go watcher.Start()
    return client, nil
}
```

Why this satisfies secrets-management.runtime-retrieval: the workload's
Kubernetes service account token authenticates to Vault;
LifetimeWatcher renews the lease automatically; no static
credential is shipped to the workload.

## Pattern C: GCP Secret Manager via SDK (Node.js)

```javascript
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');

class SecretAccessor {
  constructor() {
    this.client = new SecretManagerServiceClient();
    this.cache = new Map();  // name -> {value, expiry}
    this.ttlMs = 5 * 60 * 1000;
  }

  async get(name) {
    const cached = this.cache.get(name);
    if (cached && cached.expiry > Date.now()) {
      return cached.value;
    }
    const [version] = await this.client.accessSecretVersion({
      name: `${name}/versions/latest`,
    });
    const value = version.payload.data.toString();
    this.cache.set(name, {value, expiry: Date.now() + this.ttlMs});
    return value;
  }
}

const secrets = new SecretAccessor();
module.exports = secrets;
```

Why this satisfies secrets-management.runtime-retrieval: GCP workload identity
federation (in GKE, Cloud Run, or GCE with attached
service account) authenticates the SDK call; the secret
name references a versioned platform resource; caching
allows refresh on TTL.

## Pattern D: External-secrets operator with Kubernetes (manifest)

```yaml
# ExternalSecret resource reconciled by external-secrets
# operator. Application reads from a normal Kubernetes
# Secret object; operator keeps it in sync with AWS
# Secrets Manager.
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-db-credentials
spec:
  refreshInterval: 5m
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  target:
    name: app-db-credentials
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: prod/app/db
        property: password
```

Why this satisfies secrets-management.runtime-retrieval: the operator pattern
delegates retrieval to a controller; the application
reads from a Kubernetes Secret object; the platform's
audit log records retrievals by the operator's service
account; refresh interval ensures rotation propagation.

## Pattern E: Per-session dynamic database credential (Vault)

```python
# Vault database secrets engine issues per-session
# credentials. Each application instance gets its own
# credential with a TTL.
class DatabaseConnector:
    def __init__(self, vault_client, role: str):
        self.vault_client = vault_client
        self.role = role
        self._lease = None

    def get_credential(self):
        if self._lease and self._lease.is_valid():
            return self._lease.credential
        # Request a new dynamic credential
        response = self.vault_client.secrets.database.generate_credentials(
            name=self.role,
        )
        self._lease = Lease(
            credential=DBCredential(
                username=response["data"]["username"],
                password=response["data"]["password"],
            ),
            lease_id=response["lease_id"],
            ttl=response["lease_duration"],
        )
        return self._lease.credential
```

Why this satisfies secrets-management.runtime-retrieval: dynamic secrets engine
issues per-session credentials; the database is configured
to accept the dynamically-created users with role-scoped
permissions; on lease expiry the credential is revoked.
This pattern strengthens both L2-001 (runtime retrieval)
and L2-003 (least-privilege access).

## Cross-reference

- Anti-patterns: examples/secrets-management/runtime-retrieval-anti-pattern.md
- Substrate rule: secrets-management.runtime-retrieval
- Review checklist: checklist.md
