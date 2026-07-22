<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.no-swallowing-default no swallowing default (anti-patterns)

Substrate-original anti-pattern examples for configuration-management.no-swallowing-default. A required value is
read with a swallowing default that lets the workload start misconfigured.

## Python: empty-string fallback on a required host

```python
db_host = os.getenv("DB_HOST", "")   # swallows absence: "" is not a host
engine = create_engine(f"postgresql://{db_host}/app")
```

## TypeScript: nullish-coalescing placeholder on a required value

```typescript
const dbHost = process.env.DB_HOST ?? "";  // masks the missing required value
```

Why this is flagged: the process starts and passes a shallow health check,
then fails at the first query, far from the configuration mistake. The
remediation is a failing read or a startup validation that rejects the empty
value.
