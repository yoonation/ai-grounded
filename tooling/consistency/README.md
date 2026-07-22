# consistency - declared-vs-actual gate (IMP-1)

A task checkbox is a declaration; the file system is the actual. When a task is
marked done (`[x]`) but the file path it names is absent from disk, `tasks.md` and
the repository disagree. That gap shipped real defects in the feature 003 run (Step
17: work recorded against a wrong or relocated path), and it is the
verify-the-artifact-not-the-declaration class the framework's disk discipline
exists to catch.

This fitness function reads a `tasks.md`, finds the tasks marked done, extracts the
file paths in their descriptions, and flags any done task whose named artifact does
not exist on disk.

Scope (narrow for precision): done-side only ("claimed done, named artifact
missing"), which is high precision. The reverse ("artifact present, task still
open") is intentionally not flagged because a named path commonly exists for
reasons unrelated to the task being done, so flagging it would be noisy.
Spec-internal enumerated-set consistency (the "six versus seven" class) is
prose-fragile and is deferred to a checklist item rather than a deterministic
parser here.

Advisory: reports a verdict (`done_checked`, `missing`, `passes`) and always exits
0. It is meant to be consumed by a fresh-session orientation or a resume doctor
(IMP-10); honoring the verdict is the operator's call. The task-line grammar is
stock spec-kit's, the same the `task-granularity` gate parses, so the two agree on
what a task line is. Placeholder `TXXX` lines and template `[placeholder]` paths
are skipped.

```
python3 tooling/consistency/check.py specs/001-feature/tasks.md --repo-root . --text
```

Tests (invoke directly): `python3 tooling/consistency/test_check.py`
