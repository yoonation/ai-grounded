# Spec-Driven Governance Preset

This is the vendored spec-kit preset that ships the governance-aware
templates, the 7-article constitution, and the framework's command
overrides. It exists so that the framework's customizations survive
`specify init --here --force` without manual intervention: after any
upgrade, re-running `./scripts/bootstrap.sh` re-installs this preset
and re-renders everything it owns.

## What this preset contains

| Layer 2 artifact | Purpose |
|---|---|
| `templates/constitution-template.md` | The 7-article constitution (v1.2.0, byte-parity with `.specify/memory/constitution.md`) |
| `templates/spec-template.md` | The governance-aware spec template with prioritized user stories, threat-modeling, evaluations, backward-compat, operational-handoff sections |
| `commands/speckit.specify.md` | Stock `/speckit-specify` command with the Write→Edit cosmetic fix at the spec-write step |
| `commands/speckit.clarify.md` | Stock `/speckit-clarify` command with the Write→Edit cosmetic fix at the spec-write step |
| `commands/speckit.plan.md` | Stock `/speckit-plan` command with rename-integrity verification and the data-model normalization gate |
| `commands/speckit.implement.md` | Stock `/speckit-implement` command with capability index regeneration, the discovery-agent reuse survey, the duplication gate, and construct-time constitution injection |

The tasks and checklist templates are intentionally NOT in this
preset; they fall through to spec-kit's Layer 4 core defaults so
upstream improvements flow in automatically.

The framework-additive deferrals template (no stock counterpart)
lives at `.specify/templates/`, its single home; it is committed, so
`git checkout` restores it if an upgrade removes it. The north-star
ships as the root `NORTH-STAR.md` placeholder itself, filled in place
by consumer projects; there is no separate template copy anywhere.
The preset carries copies of neither.

Known limitation, constitution seeding: nothing routes
`constitution-template` through the preset resolution stack
(`resolve_template()` serves only the spec, plan, and tasks
templates). On the clone path, new projects seed the constitution by
copying the committed `.specify/memory/constitution.md`; this preset
copy is the portability channel for non-clone spec-kit consumers and
is kept at byte-parity with the instance.

## Why this preset exists

Before this preset, spec-kit upgrades (`specify init --here --force`)
risked clobbering the framework's template customizations because
spec-kit treats `.specify/templates/` and `.specify/memory/` as
spec-kit-managed scope. The preset moves the customizations to
`.specify/presets/spec-driven-governance/`, which is outside
spec-kit's refresh scope and is honored by the 4-layer template
resolution stack at Layer 2 (above core, below project overrides
and extensions).

It also carries the framework's command-content overrides. Rendered
`.claude/skills/speckit-*` files are derived output of this preset;
edit the command files here and re-propagate, never the rendered
skills. Vendoring command content here means it survives every
future spec-kit upgrade, including the Write→Edit cosmetic fix in
specify/clarify (the Write tool refuses to overwrite an existing
spec file, producing a cosmetic error before falling back to Edit).

## Compatibility

This preset is portable to any spec-kit-compatible AI tool (Cursor,
Codex, Continue, Cline, etc.). It is designed for highest leverage
with the governance-loop-closure framework's twelve Claude Code
sub-agents and pre-commit hooks, which complete Article VI loop
closure, but those agents are **not required**. Without them, the
templates and Write→Edit fix still apply and provide value on their
own.

## Installation

Installation is automated by the template repo's `scripts/bootstrap.sh`,
which runs `specify preset add --dev` against this directory if the
preset is not already registered. Manual install:

    specify preset add spec-driven-governance \
      --dev <path-to-this-directory> \
      --priority 50

Re-running the same command is idempotent and refreshes the
registered version against the current source files.

### Wiring Governance Commons reference agents

The substrate publishes consumer-agnostic reference agent templates at
`governance-commons/reference/agents/` (code-review, implementation-planning,
threat-modeling). The substrate deliberately does not assume a consumer
layout, so the templates say only "copy into your consumer's agent-template
location." For a spec-kit consumer, that location is
`.specify/templates/agents/`: copy each reference agent out of
`governance-commons/reference/agents/` into `.specify/templates/agents/`
and adapt the prose framing to your tooling. The substrate's contract is on
the slot list, the structured `consultation-events` output, and the
constitution-slicing discipline (see
`governance-commons/spec/consumer-scaffold.md` Section 3); the prose framing
is yours to edit in your copy.

## How to modify

Edits to this preset's content (templates, commands, manifest) follow
this workflow:

1. Edit files inside `presets/spec-driven-governance/` in the template
   repo (this directory).
2. Re-run the install command above to refresh the registered version.
3. Verify resolution with `specify preset resolve <target>` for each
   modified artifact.
4. Commit the changes to the template repo.

Do **not** edit files inside `.specify/presets/spec-driven-governance/`
directly. That directory is spec-kit-managed and gets overwritten on
each `specify preset add` refresh.

## Versioning

This preset's `version:` field tracks the preset itself, independent
of:

- The constitution version (currently 1.2.0, lives inside
  `templates/constitution-template.md` at byte-parity with
  `.specify/memory/constitution.md`).
- The spec-kit version (compatibility floor declared in
  `speckit_version:`).
- The template repo's release tags.

Bump the preset version on changes to the manifest schema or to
artifact targets. Content edits inside individual templates do not
require a preset version bump.
