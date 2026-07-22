<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Template sync and eject

How changes flow from this template into an application built on it, and how
to export an application as a standalone tree with the framework stripped.

This file lives in the template. Every application repo receives it (and the
two tools it describes) through the first sync.

## The one rule

Changes flow one way: template to application. The sync tool never writes to
the template. Author framework and substrate fixes here, in the template,
then pull them into each application. An application never pushes back; if an
application needs a template file to differ, it registers an override
(below), it does not edit the template.

Source of truth, by ownership class:

- The template owns every `framework` and `substrate` path.
- The application owns its own application files, the filled content of
  `scaffold` files, and any path it lists in its override register.

Versions in `VERSION` files and manifest pins are advisory. Sync decides
direction by ownership class and recorded content hashes, never by comparing
version numbers.

The template is a source, never a consumer. Do not run `status`, `pull`, or
`check` from inside the template repo; there is nothing upstream of the
template to pull. The tool enforces this: if the `--template` URL resolves to
the consuming repo's own `origin` remote (which is what happens when you run
it inside the template with the remote default set), it refuses with a clear
message. The one sync command that does belong in the template is
`verify-manifest`.

## File classes

Ownership per path is declared in `sync-manifest.yaml` at the template root.
Three classes, resolved in order (first match wins):

- **substrate** (`governance-commons/**`): replaced as a whole tree whenever
  it differs. Application-side extras under the tree are deleted (backed up
  first). Never file-merged. This matches the frozen-substrate contract in
  `governance-commons/CHARTER.md`.
- **scaffold**: shell files the template delivers once, then the application
  owns and fills (CLAUDE.md, README.md, NORTH-STAR.md, PROJECT-LOG.md,
  project-manifest.yaml, the constitution, dotfiles, and similar). Created
  when missing, never overwritten. A later template-side change to a scaffold
  file is reported, not applied.
- **framework**: everything else the template ships. Overwritten when the
  application copy is untouched since the last sync; three-way merged when
  both sides changed and a base exists; kept and reported as `drift` when
  only the application changed.

Application files the template does not ship are never touched by sync and
are carried by eject. Application files sitting under an enumerated framework
directory (for example a new file under `.specify/templates/`) that the
template does not ship are reported as `orphan`, never deleted.

## Sync: bringing template changes into an application

Run these from the application repo. The first sync uses the template's copy
of the tool; after that the application has its own synced copy at
`tooling/sync/sync.py`.

### Where the template comes from: local or remote

The `--template` value accepts either a local checkout path or a Git URL, and
the tool auto-detects which by scheme (https, http, git@, ssh, or file marks
a URL; anything else is a path). A URL is cloned fresh into a temporary
directory for the run and removed afterward, so no local checkout is
required. A path is used in place with no copying.

Two constants at the top of `tooling/sync/sync.py` set the defaults, so a
bare command with no `--template` uses them:

```python
DEFAULT_TEMPLATE = "https://github.com/yoonation/ai-grounded.git"
DEFAULT_REF = ""
```

Set `DEFAULT_TEMPLATE` to your remote once (or to a local path like
`~/lab/ai-grounded` if you prefer offline-by-default), and `DEFAULT_REF` to a
tag such as `v1.4.0` when you want reproducible release-pinned syncs (empty
means the remote default branch). An explicit `--template` or `--ref` on the
command line always overrides these, so you can keep the remote as the
default and still do a one-off local sync when needed.

The URL clone is intentionally full, not shallow: three-way merges read the
last-synced base blob from template git history, which a shallow clone cannot
guarantee. At this repo size a full clone is a second or two.

### Commands

Remote (uses `DEFAULT_TEMPLATE`, nothing to point at):

```sh
uv run --no-project python tooling/sync/sync.py status
uv run --no-project python tooling/sync/sync.py check
uv run --no-project python tooling/sync/sync.py pull
```

Remote, pinned to a release tag for this run:

```sh
uv run --no-project python tooling/sync/sync.py pull --ref v1.4.0
```

Local checkout, overriding the default for a one-off offline sync:

```sh
uv run --no-project python tooling/sync/sync.py pull --template ~/lab/ai-grounded
```

- **status**: dry run, writes nothing. Always run this first and read the
  report.
- **check**: CI gate. Exits 2 on any drift, pending update, or leftover
  conflict marker; exits 0 when the application matches the template. Safe to
  wire into CI on a schedule.
- **pull**: applies the sync. Refuses a dirty application tree unless
  `--allow-dirty`. Backs up every overwrite and deletion under
  `.template-sync/backup/<timestamp>/`. Rewrites `.template-sync/state.json`
  with the new template ref and per-file hashes; that file is the three-way
  base for the next pull, so it is committed with the synced changes.

Template-side self-check (run from inside the template checkout):

```sh
uv run --no-project python tooling/sync/sync.py verify-manifest --template .
```

Confirms every template file resolves to exactly one class and every
configured glob matches something. Run it after editing `sync-manifest.yaml`.
A URL also works here (it clones and self-checks the remote), but the common
case is validating a local edit before committing it.

### Report line kinds

- `framework-update`: template file changed, application copy untouched;
  overwritten (backed up). The normal case.
- `framework-add`: template ships a new framework file; delivered.
- `framework-delete`: template dropped a framework file and the application
  copy still matches the last-synced base; removed (backed up). Skipped, with
  a `drift` note, if the application had modified it.
- `merge-clean`: both sides changed, different lines; three-way merged
  automatically.
- `merge-conflict`: both changed the same lines; conflict markers written for
  hand resolution. `check` exits 2 until markers are gone.
- `scaffold-create`: a missing shell file delivered.
- `scaffold-template-changed`: the template's shell evolved; the application
  copy is kept. Adopt by hand only if wanted.
- `substrate-replace`: the substrate tree differed; whole-tree replaced.
- `drift`: the application modified a template-owned file the template did not
  change. Kept, not clobbered, reported every run until resolved (revert or
  register an override).
- `override-skip`: a path in the override register; skipped, with a note when
  the template side moved.
- `orphan`: an application file under a framework directory the template does
  not ship; reported, never deleted.
- `migration`: a one-shot migration ran (see below).

### Steady-state pull, step by step

```sh
REPO_ROOT="$HOME/lab/<app>"
cd "$REPO_ROOT"
git status --porcelain
```

The application must be committed and clean first, so the only diff you
review is the sync's own work. When syncing from a remote, the template edit
must already be pushed, because the clone fetches from the remote, not from
your local template checkout. Then (remote default; add `--template
"$HOME/lab/template"` to sync from a local checkout instead):

```sh
cd "$REPO_ROOT"
uv run --no-project python tooling/sync/sync.py status
```

Read the report against what you actually changed in the template. The line
count should roughly match the files you edited. If it is far larger, stop
and investigate before pulling. Then:

```sh
cd "$REPO_ROOT"
uv run --no-project python tooling/sync/sync.py pull
uv run --no-project python tooling/sync/sync.py check
```

`check` should print `summary: clean`, exit 0. If `pull` reported
`merge-conflict`, resolve the markers in those files first; `check` stays at
exit 2 while any remain.

Stage by name, never `-A`, reading the exact paths from the report, and
always include `state.json` in the same commit:

```sh
cd "$REPO_ROOT"
git add <each-updated-path-from-the-report> .template-sync/state.json
git commit -m "chore(sync): pull <short description> from ai-grounded"
```

Committing synced file changes without `state.json` desyncs the recorded
base from the tree and corrupts the next pull's three-way merge.

## Override register: deliberate per-application forks

When an application must own a template-class file permanently (for example a
generated index whose content is specific to that app), record it in the
application's `.template-sync/overrides.yml`:

```yaml
overrides:
  - path: ".capability-index.json"
    reason: "generated from this app's own capabilities; template seeds, app regenerates"
```

Sync then skips that path and only notes when the template side moves. This
is the correct response to a persistent `drift` line whenever the divergence
is intentional. If instead the drift was an accidental edit and the template
version should win, revert the file (`git checkout <path>`) and it syncs
normally again. Keep the register short: every entry is maintenance the
application has chosen to own.

## First sync onto a fresh application

A brand-new application built from the template joins the loop in three
steps:

```sh
REPO_ROOT="$HOME/lab/<new-app>"
cd "$REPO_ROOT"
mkdir -p .template-sync
printf 'overrides: []\n' > .template-sync/overrides.yml
printf '\n.template-sync/backup/\n' >> .gitignore
git add .template-sync/overrides.yml .gitignore
git commit -m "chore(sync): seed template override register"
```

Then the first pull uses `--adopt-template`, which resolves the no-recorded-
base situation by taking the template version of every diverged framework
file (backing up any prior copy). This flag is for the first sync only; every
later pull merges against the recorded base and needs no flag.

For the first pull the application does not yet have its own copy of the
tool, so run it from a template source. From a local checkout:

```sh
cd "$REPO_ROOT"
uv run --no-project python "$HOME/lab/template/tooling/sync/sync.py" pull --template "$HOME/lab/template" --consumer . --adopt-template
uv run --no-project python tooling/sync/sync.py check
git add <paths-from-the-report> .template-sync/state.json
git commit -m "chore(sync): first one-way pull from ai-grounded"
```

Or fetch the tool once from the remote and run it, needing no local
checkout at all (replace the URL with yours):

```sh
cd "$REPO_ROOT"
TEMPLATE_URL="https://github.com/yoonation/ai-grounded.git"
TMP="$(mktemp -d)"
git clone --quiet "$TEMPLATE_URL" "$TMP"
uv run --no-project python "$TMP/tooling/sync/sync.py" pull --template "$TEMPLATE_URL" --consumer . --adopt-template
rm -rf "$TMP"
uv run --no-project python tooling/sync/sync.py check
git add <paths-from-the-report> .template-sync/state.json
git commit -m "chore(sync): first one-way pull from ai-grounded"
```

After this first pull the application has `tooling/sync/sync.py` of its own,
and every later pull is just `sync.py pull` with the remote default.

## Migrations: changes a file copy cannot express

For a structured rewrite inside an application-owned file, or a rename with a
content transform, add an executable step at
`tooling/sync/migrations/NNN-name.py` in the template. Each defines
`apply(consumer_root, template_root)`, must be idempotent, and runs once per
application during `pull`, recorded in that application's `state.json`. The
ordinal is immutable once shipped. None are required for ordinary file
changes; use them only when a plain overwrite or merge cannot produce the
right result.

## Eject: exporting an application as a standalone tree

Eject produces a copy of an application with the governance framework
stripped out: application code plus the filled scaffold, minus the excludes,
with all `framework` and `substrate` paths removed. It never mutates the
application; it writes a fresh tree to an output directory, so it can be
re-run after any change. This is a build artifact, not a one-way door: the
governed repo remains the home, and a newer standalone cut can be produced at
any time.

Run from the application repo:

```sh
uv run --no-project python tooling/eject/eject.py --template ~/lab/ai-grounded --consumer . --out dist/standalone
```

`--out` defaults to `dist/standalone` under the application (kept out of
version control by `.gitignore`). `--consumer` defaults to the current
directory.

### What ships and what is stripped

Ships: application files (anything the template does not own) plus the
application's filled scaffold files, minus the `eject.exclude` globs in
`sync-manifest.yaml` (scaffold files that only make sense inside a governed
repo, such as CLAUDE.md and `.claude/`).

Stripped: everything classified `framework` or `substrate`, plus the
excludes.

### Verification (all three run automatically)

1. **Reference scan**: no exported file may mention a framework path
   (governance-commons, `.specify/`, `presets/`, `tooling/`, `.githooks`,
   `.claude/`), except files listed under `eject.allow-references` in the
   manifest (comment or prose references that are legitimately part of the
   application, such as a pricing note that cites a substrate catalog path).
2. **Marker scan**: no exported file may carry a template-managed marker.
3. **Proof gate**: printed by default, executed with `--run-proof`. Runs
   `pnpm install --frozen-lockfile`, `pnpm run build`, `pnpm run typecheck`,
   and `pnpm run test:unit` inside the exported tree. The eject is not done
   until the standalone tree passes its own suite.

Findings on scans 1 or 2 exit 2 and leave the export in place for
inspection. If a scan flags a file that legitimately belongs in the
standalone app, add it to `eject.exclude` (drop it) or
`eject.allow-references` (keep it, allow the mention) in `sync-manifest.yaml`,
here in the template, then re-run.

```sh
uv run --no-project python tooling/eject/eject.py --template ~/lab/ai-grounded --consumer . --out dist/standalone --run-proof
```

## Gotchas learned in practice

- **Deleting a tracked directory before a sync**: use `git rm -r <dir>`, not
  `rm -rf <dir>`. A plain `rm` leaves the deletions unstaged, the tree reads
  dirty, and `pull` refuses. This bites when removing a stale vendored copy
  before the first sync.
- **gitleaks and `state.json`**: the sync state file stores a sha256
  fingerprint per synced file. Entries whose file paths contain a detector
  keyword (secret, api, credential, pii) put that keyword and a high-entropy
  hex value on the same line and false-positive the generic-api-key rule. The
  scaffold `.gitleaks.toml` allowlists `.template-sync/state.json` by exact
  path; keep that entry. It cannot use an inline `gitleaks:allow` comment
  because the file is machine-written JSON, rewritten on every pull.
- **Named staging only**: stage every synced path by name and include
  `state.json`. Never `git add -A` a sync commit; it sweeps in unrelated
  working-tree changes and breaks the scoped-commit discipline.
- **`docs/GATES.md` staleness**: regenerate it in the template
  (`tooling/gates/describe.py > docs/GATES.md`), commit there, then pull. It
  is a framework file; regenerating it in an application creates drift on the
  next sync.
- **`.template-sync/` is partly tracked, not ignored wholesale**: commit
  `state.json` (the three-way merge base) and `overrides.yml` (the fork
  register); ignore only `.template-sync/backup/`. Ignoring the whole
  directory silently drops the merge base, and the next fresh clone then
  degrades every framework file to adopt-or-conflict instead of a clean
  incremental merge. The scaffold `.gitignore` ships this contract (ignore
  `backup/`, re-include `state.json` and `overrides.yml`) so every app
  inherits it.
- **Running sync inside the template**: refused by design (see The one rule).
  If you tried it and a `.template-sync/` folder appeared, it was never
  committed; delete it with `rm -rf .template-sync` and run from an
  application repo instead.
- **Template gates not running**: if the template repo itself never blocks on
  its own gates, check `git config core.hooksPath`; it should be `.githooks`.
  A template with gates installed but not wired will pass content that an
  application then rejects.
