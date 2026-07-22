---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: backup-recovery.strategy-adr
title: "Backup-and-Recovery Strategy Policy"
lifecycle-status: stable
commons-version: "0.8.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M6 close consolidation (2026-06-06) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M6 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-06. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent following the feature-flags-strategy.madr.md precedent; third decision framework authored in Milestone 6; exercises the established MADR pattern for the backup-recovery concern. SPDX header placed as YAML comments inside frontmatter per Section 10 settled decision 15. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft. Substrate-author review required for stable promotion at the M6 close."
authoritative-sources:
  - "https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final"
  - "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final"
  - "https://csrc.nist.gov/pubs/sp/800/209/final"
  - "https://adr.github.io/madr/"
---

# Backup-and-Recovery Strategy Policy

This decision framework provides the substrate's analysis of the
backup-and-recovery strategy decisions a consumer must make. Consumers
reference this framework when authoring their own ADR documenting how their
services keep recoverable copies of data, prove those copies restore, and
meet defined recovery objectives. The substrate-recommended location for
the consumer's ADR is
`/docs/decisions/ADR-XXX-backup-recovery-strategy.md`.

The framework is referenced by substrate rule backup-recovery.strategy-adr, which requires
the consumer to have an explicit, recorded backup-and-recovery strategy.
Consumers satisfy backup-recovery.strategy-adr by authoring an ADR that adapts the
analysis here to their context.

The lower-layer backup-recovery rules enforce the consequences of this
strategy: backup-recovery.backup-retention-set requires declared backup resources to keep a
non-zero retention, backup-recovery.guarded-destructive-operation requires irreversible destruction to be
guarded, backup-recovery.restore-verification requires restores to be proven by a scheduled test,
and backup-recovery.coverage-and-objectives requires coverage to match the protection inventory and
recovery objectives to be defined and met. This framework is the place
where the consumer decides the surface those rules then police.

## Context

Backup-and-recovery strategy is a set of interlocking decisions. The
protection inventory determines what must be recoverable; the topology
determines how copies are made and where they live; retention and
immutability determine how long a copy survives and whether it can be
deleted or altered; the recovery objectives determine how much data loss
and downtime each tier tolerates; the restore-verification cadence
determines how often recoverability is proven; the encryption and
key-custody boundary determines who can read and restore a copy; the
destructive-operation guard convention determines how avoidable loss is
prevented at the source; and change control and ownership determine how the
regime is governed over time. The decisions are coupled: an aggressive
recovery time objective constrains the topology, and a ransomware-exposed
tier constrains the immutability policy.

The substrate cannot make these decisions for the consumer because they
depend on the consumer's data, deployment model, regulatory exposure, and
risk posture. The substrate provides recommended defaults that suit the
common case and documents the trade-offs so the consumer can deviate
deliberately.

## Decision Drivers

- Recoverability: the only property that matters is whether the data comes
  back, proven by restore rather than assumed from a successful backup job.
- Sufficiency: copies must be kept long enough, made often enough, and
  restored fast enough to meet the loss and downtime each tier tolerates.
- Durability against deletion: backups must survive the accidental or
  malicious deletion that motivates them, which mutable, co-located copies
  do not.
- Coverage integrity: everything the protection inventory marks must be in
  the backup set, with no silent gaps.
- Boundary integrity: classification stays in data-classification, keys in
  secrets-management, storage hardening in infrastructure-misconfiguration,
  failover in reliability, and alerting in monitoring-alerting.
- Loss prevention at the source: avoidable destruction is guarded before it
  happens, so the backup is the second line of defense, not the first.

## Considered Options

### Protection inventory and tiers

Option A, implicit (back up everything the same way): simple, but wastes
storage on disposable data and underprotects critical data. Rejected as a
strategy even where it is a starting point.

Option B, classification-driven tiers: the data-classification protection
inventory assigns each store a tier, and the tier sets retention, frequency,
immutability, and recovery objectives.

Substrate-recommended default: Option B, consuming the data-classification
inventory rather than re-deriving it; backup-recovery.coverage-and-objectives reconciles coverage
against it.

### Backup topology

Option A, single co-located copy: a snapshot beside the primary. Convenient
and useless against site loss or ransomware. Rejected for protected tiers.

Option B, multiple copies across locations (the three-copies, two-media,
one-offsite discipline), combining periodic full and frequent incremental
backups, with off-site or cross-region placement sized to the tier.

Substrate-recommended default: Option B, with the number of copies, the
full-and-incremental cadence, and the geographic separation sized to the
tier's recovery objectives and threat model.

### Retention and immutability

Option A, short, mutable retention: cheapest, and defeated by a deletion or
corruption that is discovered after the window or that deletes the backups
too. Rejected for protected tiers.

Option B, tier-sized retention with immutability where the threat warrants:
retention long enough to detect and recover from delayed-discovery
corruption, and write-once or object-lock immutability for tiers exposed to
ransomware or insider deletion.

Substrate-recommended default: Option B, with backup-recovery.backup-retention-set enforcing a
non-zero retention floor and the immutability decision recorded per tier
(NIST SP 800-209 informs the write-once and immutability options).

### Recovery objectives (recovery point and recovery time)

Option A, undefined: recovery is best-effort. Rejected; there is then no
standard to measure frequency or restore time against.

Option B, defined per tier: each tier has a recovery point objective (the
tolerable data loss) and a recovery time objective (the tolerable downtime),
with backup frequency set to satisfy the former and topology and tooling set
to satisfy the latter.

Substrate-recommended default: Option B, verified by backup-recovery.coverage-and-objectives (NIST SP
800-34 Rev. 1 informs the recovery-objective framing).

### Restore-verification cadence

Option A, none (trust the backup job): the dominant real-world failure.
Rejected.

Option B, scheduled restore tests proportionate to the tier: higher tiers
restored and integrity-checked more often, into an isolated target, with the
outcome recorded and alerted.

Substrate-recommended default: Option B, enforced by backup-recovery.restore-verification.

### Encryption and key custody

Option A, keys with the backups: convenient, and a single point of
compromise that also defeats recovery if lost. Rejected.

Option B, encryption with keys and restore credentials owned by
secrets-management, referenced by indirection, with custody and rotation
that do not make the backup unrecoverable.

Substrate-recommended default: Option B, deferring key handling to
secrets-management while recording the custody boundary in the ADR.

### Destructive-operation guard convention

Option A, none: destruction runs unconditionally and the backup is the only
safety net. Rejected; it spends recovery effort on avoidable loss.

Option B, a recognized guard convention (snapshot-first, confirmation or
dry-run gate, or safe-delete wrapper) that backup-recovery.guarded-destructive-operation can recognize, so
avoidable destruction is prevented at the source.

Substrate-recommended default: Option B, with the convention recorded so the
L1 binding's guard allow-list reflects it.

### Change control and ownership

Option A, ad hoc: the regime drifts as stores and tiers change. Rejected for
protected data.

Option B, owned and reviewed: a named owner, a review cadence, and a re-
review after any recovery incident or failed restore test.

Substrate-recommended default: Option B, with owner and cadence recorded in
the ADR.

## Decision Outcome

The substrate-recommended strategy for the common case: a classification-
driven protection inventory and tiers; a multi-copy, off-site topology
combining full and incremental backups sized to the tier; tier-sized
retention with immutability where ransomware or insider deletion is a
threat; recovery point and recovery time objectives defined per tier and
met; scheduled restore verification proportionate to the tier; encryption
with keys and credentials owned by secrets-management; a recognized
destructive-operation guard convention; and owned, reviewed change control.
Consumers deviate deliberately and record the deviation and its rationale in
their ADR.

## Substrate Alignment

This framework is the L3 companion to the backup-recovery catalog. It draws
boundaries to sibling concerns rather than absorbing them. The protection
inventory and tiers are owned by data-classification, which this strategy
consumes. The encryption keys and restore credentials are owned by
secrets-management, referenced by indirection. The secure provisioning of
backup storage (public exposure, encryption at rest, least-privilege
access) is owned by infrastructure-misconfiguration. The service-
availability failover path, as distinct from the data-restore path, is owned
by reliability. The alerting on backup-job and restore-test outcomes is
delivered by monitoring-alerting. The strategy records how each boundary is
honored rather than restating the sibling rules.

## Consequences

Positive: a coherent recovery discipline inheritable across stores; backups
proven to restore rather than assumed; copies that survive the deletion that
motivates them; coverage with no silent gaps; avoidable destruction
prevented at the source.

Negative or cost: multi-copy off-site topology, immutability, and scheduled
restore tests are real storage and operational cost; defining objectives per
tier and reconciling coverage impose a discipline tax that pays back at the
first averted unrecoverable-loss incident.

## References

See the authoritative-sources frontmatter: NIST SP 800-34 Rev. 1
(contingency planning, recovery objectives, backup-storage strategy), NIST
SP 800-53 Rev. 5 contingency-planning control family (CP-9 system backup,
CP-10 system recovery and reconstitution), NIST SP 800-209 (storage-
infrastructure security including immutability and write-once protections),
and the MADR format.

## Decision Review Schedule

The consumer's ADR is reviewed at substrate adoption, at the introduction of
a new data store or data tier, at a change of backup tooling, provider, or
topology, after any recovery incident or failed restore test, and on a
substrate-recommended annual cadence.
