<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.fail-static-default fail-static default (good patterns)

Substrate-original good-pattern examples for feature-flags.fail-static-default. Every flag evaluation
supplies an explicit default that resolves to the safe path when the provider
is unreachable, the flag is unknown, or evaluation errors.

## Python: explicit fail-static default at the call site

```python
# the default is the off/safe path; if the provider is down the call is safe
use_new_pricing = flags.get_boolean("checkout.new-pricing-engine", default=False)
if use_new_pricing:
    price = new_pricing_engine(cart)
else:
    price = legacy_pricing(cart)
```

## TypeScript: a permission gate that defaults closed

```typescript
// an unknown or errored flag must not open the gated capability
const canBulkExport = await flags.getBooleanValue("admin.bulk-export", false);
if (canBulkExport) {
  await runBulkExport(request);
} else {
  return forbidden("bulk export not enabled");
}
```

Each evaluation names a default, and the default is the conservative branch:
provider failure degrades to the known-safe behavior, never to the new or
more-permissive path.
