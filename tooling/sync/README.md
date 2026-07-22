<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# tooling/sync

One-way template-to-consumer synchronization. The template is read-only
input; the consumer is the only tree written. Ownership per path comes from
`sync-manifest.yaml` at the template root; consumer-side deliberate forks of
template-owned files live in the consumer's `.template-sync/overrides.yml`.

## Commands

Run from the consumer repo (first ever run uses the template's copy of this
tool, after which the consumer has its own synced copy):

    uv run --no-project python tooling/sync/sync.py status --template ~/lab/ai-grounded
    uv run --no-project python tooling/sync/sync.py check  --template ~/lab/ai-grounded
    uv run --no-project python tooling/sync/sync.py pull   --template ~/lab/ai-grounded

Template-side self-check:

    uv run --no-project python tooling/sync/sync.py verify-manifest --template .

`status` is a dry run. `check` exits 2 on any drift or leftover conflict
markers (CI-friendly). `pull` applies, refuses a dirty consumer tree unless
`--allow-dirty`, backs up every overwrite and deletion under
`.template-sync/backup/<timestamp>/`, and records the synced template
commit plus per-file hashes in `.template-sync/state.json` (commit that
file; it is the three-way base for the next sync).

`--adopt-template` resolves no-base conflicts (typically only the first
sync) by taking the template version, prior copy backed up.

## File classes

- substrate (`governance-commons/**`): replaced as a whole tree, consumer
  extras under it deleted, never file-merged.
- scaffold: delivered once, consumer-owned forever after; template-side
  shell changes are reported, never applied.
- framework: everything else the template ships; overwritten when the
  consumer copy is untouched, three-way merged when both sides changed and
  a base exists, drift-reported (kept) when only the consumer changed.

Consumer files the template does not ship are never touched. Consumer files
matching a `framework-explicit` glob without a template counterpart are
reported as orphans, never deleted.

## Overrides register

`.template-sync/overrides.yml` in the consumer:

    overrides:
      - path: ".claude/skills/myapp-*/**"
        reason: "application skills, consumer-owned"

Registered paths are skipped by sync with a note when the template side has
moved. An unregistered consumer edit to a framework file is kept but
reported as drift every run until registered or reverted.

## Tests

    python3 tooling/sync/test_sync.py
