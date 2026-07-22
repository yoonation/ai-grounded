# quality - commit-time quality gate (IMP-9)

The edit-time hook (`.claude/hooks/lint-on-edit.sh`) formats and lints files Claude
edits, but it deliberately skips project-wide type-checking ("slow per-edit, left
to commit-time / CI") and only fires on Claude Code Edit/Write. Nothing closes
those gaps at the commit boundary: type errors, and any change made in another
editor, go unchecked. This gate closes them.

For the languages the project declares in `project-manifest.yaml` `stack.languages`,
it runs the project-wide type-checker and lints the staged files:

| language | type-check (project) | lint (staged files) |
|---|---|---|
| typescript | `tsc --noEmit` | `eslint` |
| javascript | (none) | `eslint` |
| python | `mypy` | `ruff check` |

It is gated by `stack.languages` exactly as `lint-on-edit.sh` is, so it never runs
a toolchain the project does not use, and availability-gated: a tool that is not
installed is skipped with a note, never an error. JS/TS tools resolve through the
project runner (`pnpm exec`, else `npx`).

Posture matches `.githooks/pre-commit.d/30-sast`: report-only by default, exits 0;
`QUALITY_STRICT=1` makes findings block; `SKIP_QUALITY=1` bypasses. Deliberately
not fail-closed like `10-gitleaks` (a lint finding is advisory; a leaked secret is
not). The toolchain map (constitution Section 2.7) is extended by adding to
`TOOLCHAINS` in `check.py`.

The planner core is pure and stdlib-only, so it is fully unit-tested without any
linter installed; the manifest read is a regex, the same approach `lint-on-edit.sh`
uses.

```
python3 tooling/quality/check.py path/to/file.ts path/to/file.py --repo-root . --text
```

The gate wrapper is `.githooks/pre-commit.d/40-quality`, run automatically by the
pre-commit dispatcher. Tests (invoke directly): `python3 tooling/quality/test_check.py`

## Whole-repo lint span (IMP-14)

The per-commit gate lints staged files only, by construction: it is handed the staged
diff so the commit stays fast. The cost is that lint debt in files no commit happens to
touch is never seen, so "lint clean" is true about the diff and false about the codebase
(feature 004 found 182 pre-existing lint errors that every commit gate had passed clean).
The fix is not to block every commit on the whole tree, which would punish a feature for
inherited debt; it is to make the divergence visible at a feature or phase boundary.

`--whole-repo` runs the lint scope over the whole declared-language tree and over the
staged set separately, and reports whether the repository carries lint failures the
staged delta does not:

```
python3 tooling/quality/check.py [STAGED_FILE ...] --repo-root . --whole-repo --text
```

It is visibility only and always exits 0, so it never blocks a commit. The per-commit
`40-quality` gate is unchanged and stays staged and fast. Wire the span at the
post-implementation (C3) self-check, where `speckit-workflow-post-impl` lists it among
the on-demand verifiers.
