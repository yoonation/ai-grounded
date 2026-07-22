<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.data-classification-policy data-classification policy (good pattern)

Substrate-original illustration.

```markdown
# ADR 0042: Data-Classification Policy

## 1. Scheme and vocabulary
Four classes: public, internal, confidential, restricted. Same vocabulary as
the infrastructure data-sensitivity tags.

## 2. Determination rule
Classify by what a field can contain. Personal data and free-text notes are
confidential; payment and health fields are restricted. Aggregates and
derivations take the most restrictive input class.

## 3. Per-class handling matrix
| class | encryption | access | retention | logging |
| internal | in transit | role-based | 1y | allowed |
| confidential | rest + transit | need-to-know + audit | 2y | masked only |
| restricted | rest + transit, managed key | minimized + audit | 3y | never |

## 4. Propagation rules
Class inherits to copies, exports, messages, caches (most-restrictive-wins).
Restricted data is never cached in a shared or edge tier.

## 5. Tag-and-label binding
The policy vocabulary is the source of truth for both the code
classification labels and the infrastructure-misconfiguration.governance-tagging data-sensitivity tags.

## 6. Ownership and review
Owned by the service lead; reviewed annually and on any new data type or
regulatory change.
```

## Why this satisfies the rule

The ADR is short but covers all six sub-decisions, each with its drivers, and
binds the scheme vocabulary to both the code labels and the infrastructure
tags so the two layers agree. A new contributor can classify and handle data
consistently, and a data or regulatory change updates this document rather
than rediscovering the decisions after an exposure.
