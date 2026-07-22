<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.data-model-single-source-of-truth data-model single source of truth (anti-pattern)

Substrate-original illustration, the original FW-001 instance. A field that
is constant across every persona an operator owns is carried on each persona
row instead of on the one operator. The value is copied per referrer, so a
single change of mind requires one edit per copy and the copies drift.

## SQL: a shared fact duplicated onto every referrer

```sql
-- home_region is the same for every persona an operator owns, yet it is
-- stored on each persona. The fact has no single home.
CREATE TABLE persona (
    persona_id    uuid PRIMARY KEY,
    operator_id   uuid NOT NULL,
    home_region   text NOT NULL,         -- duplicated: same for all the operator's personas
    display_name  text NOT NULL
);
```

Why this is a finding: home_region is one fact about the operator, but it is
written once per persona. Correcting an operator's region means updating
every persona row; an export that already read the old value keeps it; and
two personas can come to disagree about a fact that should be singular. The
data model also never declared whether home_region was per-instance or
shared, so the omission was never put in front of a reviewer. The failure was
a missing question, not a wrong answer.

Remediation: move home_region to the operator, the entity it describes;
reference the operator by key from persona; and record the cardinality
decision in the data model (home_region shared-across persona, home
operator). If a duplicate is genuinely wanted, for example a denormalized
read copy on a hot path, keep it deliberately and record why, naming the read
path it serves and the mechanism that keeps the copy consistent with the
operator. The operator row stays the single point of correction.
