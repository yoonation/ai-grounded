<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.fail-static-default fail-static default (anti-patterns)

Substrate-original anti-pattern examples for feature-flags.fail-static-default. A flag is evaluated
with no default, or with a default that opens the new or more-permissive path,
so a provider outage changes behavior in the unsafe direction.

## Python: no default, so a provider error decides behavior

```python
# if the provider raises or returns null, behavior is undefined or crashes
use_new_pricing = flags.get_boolean("checkout.new-pricing-engine")
if use_new_pricing:
    price = new_pricing_engine(cart)
```

## TypeScript: a permission gate that defaults open

```typescript
// an unknown or errored flag opens a privileged capability
const canBulkExport = await flags.getBooleanValue("admin.bulk-export", true);
if (canBulkExport) {
  await runBulkExport(request); // reachable during a provider outage
}
```

Why this is flagged: when the provider is unreachable or the flag is unknown,
the first call has no defined fallback and the second fails open to a
privileged path. The remediation is to supply an explicit default whose value
is the safe branch for that specific flag.
