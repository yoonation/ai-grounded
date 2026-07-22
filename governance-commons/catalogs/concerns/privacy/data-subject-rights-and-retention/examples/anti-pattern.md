<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.data-subject-rights-and-retention DSR and retention architecture ADR (anti-pattern)

Substrate-original illustration.

```markdown
# (no rights-and-retention architecture exists)

Erasure is a manual DELETE on the primary database when a request comes in. No
store inventory. No defined portability format. No retention schedule. Backups
keep everything forever.
```

## Why this violates the rule

There is no recorded architecture: erasure is a manual delete on the primary
store, there is no inventory of the other stores, no portability format, and no
retention schedule, while backups keep everything indefinitely. The rights are not
operable end to end and retention is unenforced. Recording the store inventory,
the erasure propagation, the portability format, the request flow, and the
retention schedule in an ADR is the fix.
