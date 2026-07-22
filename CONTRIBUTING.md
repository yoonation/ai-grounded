<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Contributing

AI Grounded is open source under Apache-2.0, and issues, discussions, and
pull requests are all welcome.

Ways to contribute:

- **File an issue** for a bug, a gap, or a concrete improvement.
- **Open a discussion** to talk through a design idea before building it.
- **Send a pull request** for a fix or an addition (see the flow below).

The framework is intentionally bounded. The constitution limits scope to
prevent uncontrolled growth, and `FUTURE.md` records additions that were
considered and rejected, so a change that re-opens a settled decision will
be pointed there. For anything larger than a bug fix or a docs change, open
an issue first so we can agree on the shape before you invest the work.

## Development setup

```bash
mise install            # install the pinned runtimes (see .mise.toml)
./scripts/bootstrap.sh  # install the spec-kit preset and arm the pre-commit hook
```

The pre-commit hook runs the same checks as CI: a secret scan, schema and
manifest validation, quality/lint checks, and the loop-closure verifier. Run
the Python test suites directly with `python3 tooling/<tool>/test_<tool>.py`
(stdlib `unittest`, no extra dependencies).

## Pull request flow

1. Fork the repository and create a branch (`feature/`, `fix/`, or `chore/`
   prefix).
2. Make focused changes; keep diffs small and follow the conventions in
   `.claude/rules/`.
3. Use [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `chore:`, ...).
4. Run the test suites and let the pre-commit gate chain pass.
5. **Sign off your commits** to certify the Developer Certificate of Origin
   (see below): `git commit -s`.
6. Open the pull request against `main`. The PR template's checklist covers
   tests and sign-off.

A maintainer reviews for fit with the framework's bounded scope, then merges
or explains why not. Significant changes are expected to carry an ADR under
`docs/decisions/` following the constitution's Article II (Context, Decision,
Consequences, Alternatives Considered).

## Sign-off (DCO)

This project uses the [Developer Certificate of Origin](https://developercertificate.org/)
(DCO 1.1) instead of a contributor license agreement. By adding a
`Signed-off-by` line to every commit you certify that you wrote the change,
or otherwise have the right to submit it under the project's Apache-2.0
license. Add it automatically with:

```bash
git commit -s -m "fix: ..."
```

The line must match the name and email on the commit, for example:
`Signed-off-by: Jane Doe <jane@example.com>`. The full DCO text is in the
`DCO` file at the repository root.

## If you are forking

The template's structure is intentionally bounded. The constitution
explicitly limits scope to prevent uncontrolled growth, and `FUTURE.md`
tracks rejected additions to prevent re-litigation.

When you fork, you are welcome to:

- Add agents not present in the twelve-agent roster (and document them
  in a `CONTRIBUTING-fork.md` so others know what diverges)
- Replace the constitution with your own values
- Substitute different threat catalogs, compliance catalogs, or policy
  frameworks for the included ones
- Add CI workflows, additional hooks, or integrations not present here

When you fork, do not:

- Strip the attribution acknowledgments in `README.md` or the `NOTICE` file
- Misrepresent the template as your original work
- Remove the constitution Article VI loop-closure requirement without
  understanding what you are giving up

The template is provided as-is. See `LICENSE` for the legal terms.

## Modifying preset templates

The framework's customizations to spec-kit (the 7-article constitution
template, the governance-aware spec template, and the Write→Edit
cosmetic fix for `/speckit-specify` and `/speckit-clarify`) live in
the vendored spec-kit preset at `presets/spec-driven-governance/`.
This is the canonical source for those files.

If you need to modify any of them (in your fork, or via a pull request
upstream), follow this workflow:

1. Edit files inside `presets/spec-driven-governance/`. The two
   directories are:
   - `templates/` for artifact template overrides (currently
     `constitution-template.md` and `spec-template.md`)
   - `commands/` for command template overrides (currently
     `speckit.specify.md` and `speckit.clarify.md`)
2. Re-run bootstrap to propagate the change:

   ```bash
   BOOTSTRAP_FORCE=1 ./scripts/bootstrap.sh    # template repo
   ./scripts/bootstrap.sh                       # any derived project
   ```

   Bootstrap blindly removes the existing preset registration and
   re-adds it from the vendored source. This is idempotent in effect:
   subsequent edits propagate to spec-kit's runtime state on the next
   bootstrap.

3. Verify the change is live:

   - For templates: `specify preset resolve <template-name>` should
     resolve to the file under `.specify/presets/spec-driven-governance/templates/`
   - For commands: `grep` for the new wording in the rendered SKILL.md
     files (e.g., `.claude/skills/speckit-specify/SKILL.md`); the
     `--ai-skills` propagation handles this automatically at
     `specify preset add` time

4. Commit the change in `presets/spec-driven-governance/`. The
   rendered SKILL.md files under `.claude/skills/` will also have
   been modified by the propagation; commit those alongside the
   preset source so fresh clones have the working state without
   needing bootstrap to run first.

Do NOT edit files inside `.specify/presets/spec-driven-governance/`
directly. That directory is spec-kit-managed runtime state regenerated
from the vendored source on every `specify preset add`. It is in
`.gitignore` for the same reason: the canonical state lives in
`presets/`, the runtime extraction is incidental.

If you're patching a spec-kit command file (like `speckit.specify.md`)
to address a similar cosmetic issue or to add behavior, the workflow
above applies. Add a brief header comment to the patched file noting
which upstream source you derived it from and what you modified, the
same way the existing patched files do.

## Questions

Open a GitHub issue or start a discussion. For anything security-sensitive,
follow the private reporting process in `SECURITY.md`.
