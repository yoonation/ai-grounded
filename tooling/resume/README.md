# resume - session-recovery orientation (IMP-10)

A fresh session, a crash recovery, or a context-clear should orient from disk, not
from memory of the prior conversation. Context is disposable; the on-disk artifacts
are the truth. This tool computes that orientation deterministically, so the resume
prompt is a disk read rather than a hand-written summary that can itself drift.

For the active feature it reports:

- **git**: HEAD (short sha + subject) and whether the tree is clean or has named
  in-flight (uncommitted) files. An uncommitted, half-written increment is the one
  genuinely dangerous resume state, so it is surfaced first.
- **consistency**: the declared-vs-actual check (`tooling/consistency/check.py`) run
  on the feature's `tasks.md`, so a task marked done whose artifact is absent from
  disk is caught at orientation. This composes the consistency CLI rather than
  duplicating it.
- **events**: the tail of `events.jsonl` - last event, count of pending P1/P2 items,
  and any closure-rejections not later verified - so a checkpoint left mid-flight
  and its open closures are visible. The event log already is the progress record;
  no separate marker file is introduced.

The irreducibly-human call stays human: whether uncommitted in-flight work is safe
to commit versus discard-and-redo is the operator's judgment. The tool surfaces
that state and never decides it.

Advisory: always exits 0. Active-feature resolution mirrors
`.specify/scripts/bash/common.sh` (`SPECIFY_FEATURE`/`--feature`, then the git
branch if it names a `specs/<branch>` directory, then the highest-numbered
`specs/*`). In a template repo with no feature it reports no active feature, the
same way the staleness gate does; it does its real work in consumer repos.

```
python3 tooling/resume/doctor.py --repo-root . --text
```

Tests (invoke directly): `python3 tooling/resume/test_doctor.py`
