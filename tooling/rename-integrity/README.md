# rename-integrity - bulk-rename token check (IMP-13)

After a bulk identifier substitution, counts the old and new tokens on disk so a rename is verified by raw counts rather than a prose sweep that carries no information about what actually broke.

A re-normalization, a refactor rename, or a sed pass across several files is the
operation most likely to leave an old identifier live or mangle a new one, and the
step that follows it has historically been a narrative "consistency sweep" that checks
referential agreement and says nothing about token integrity. That is the
green-but-not-exercised class: a botched substitution passes the sweep clean. The
closure auditor already guards closures with disk-truth (it recomputes a sha256 from
disk instead of trusting a summary); this tool carries the same shape to the rename
seam. It does not assert consistency in prose. It counts the actual tokens and shows
the raw result the operator reads.

For each declared rename `old=new` it reports:

- the OLD identifier's live occurrences, expected 0 after a clean substitution, with
  `path:line` locations so the operator sees exactly what remains, and
- the NEW identifier's occurrences, the propagation footprint, as a count and the
  files it landed in.

Matching is whole-token (word boundaries), so renaming `profile_block` does not match
inside `profile_blockchain`. It scans UTF-8 text files under the given paths (default:
the repo root), skipping vendor and build directories, and does not restrict by
extension, because a rename legitimately appears in code, schemas, migrations, and
docs, and all of them must be verified.

Advisory and exits 0 by default, so a fresh-session orientation or a rework step can
consume it. `--strict` exits 1 when any OLD identifier is still live, so a rework can
be wired to fail rather than self-report clean. Any count is independently
re-verifiable with ripgrep (`rg -c '\bold_name\b'`); the two agree on what a token is
because both anchor on word boundaries.

The scanning core is pure and stdlib-only, so the tool is fully unit-tested without
ripgrep or any external tool installed.

```
python3 tooling/rename-integrity/check.py --rename old_name=new_name --repo-root . --text
python3 tooling/rename-integrity/check.py --rename a=b --rename c=d --scope src --scope docs --strict
```

Tests (invoke directly): `python3 tooling/rename-integrity/test_check.py`
