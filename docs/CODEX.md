# Codex Local Delivery

AI Grounded supports local Codex without replacing the existing Claude Code
delivery. The governance substrate, feature artifacts, dispatcher, event log,
and Git pre-commit gates are shared.

## First-time setup

1. Install Codex CLI **0.146.1 or later** before starting the adapter. This is
   the verified capability baseline for the project-local permission profile,
   hooks, child-agent configuration, and GPT-5.6 role map:

   ```bash
   npm install -g @openai/codex@latest
   codex --version  # must report 0.146.1 or newer
   ```

2. Install or upgrade Spec-Kit, then install Codex beside Claude:

   ```bash
   specify integration install codex
   specify integration list
   ```

   The template retains its current default integration. Use
   `specify integration use codex` only if a project wants Codex as its default.

3. Run `./scripts/bootstrap.sh` to refresh the preset and activate the Git
   hooks. In Codex, trust the project configuration and review the local hooks
   with `/hooks` before enabling them.

4. Start Codex from the repository root. It loads `AGENTS.md`, `.codex/`, and
   `.agents/skills`. Invoke the workflow with `$speckit-specify`,
   `$speckit-plan`, `$speckit-tasks`, and `$speckit-implement`; use the
   `$speckit-workflow-*` skills at the four framework checkpoints.

## Agents and isolation

The 12 names in `.codex/agents/` match the existing framework roles. The
project caps concurrent child agents at four
(`agents.max_concurrent_threads_per_session`). Their
canonical instructions remain in `.claude/agents/`, preventing prompt drift
between delivery layers. Review roles default to `read-only`, while the parent
session remains responsible for artifact persistence and event-log writes.

On native Windows, read-only children require Codex's `elevated` sandbox. The
first run may show a UAC prompt; approve it to set up the sandbox users and
firewall rules. If an organization blocks that setup, use WSL2 or record the
prominent advisory-isolation warning required by the checkpoint skill before
continuing with a less restrictive child configuration.

Do not launch a governance review wave with a permissive runtime override such
as a full-access session. If Codex reports that a parent override superseded a
child sandbox, continue only with the resulting isolation warning recorded in
the dispatch artifact.

## Protections

The generated `ai-grounded` permission profile grants workspace editing while
denying the reviewed sensitive-path registry: `.env*`, credential/certificate/
key directories, cloud and package-manager credentials, `secrets.json`, and
key/certificate file types. Do not hand-edit `.codex/config.toml`; regenerate
it from that registry.

The PreToolUse hook fails closed for malformed or oversized input, blocks
sensitive paths and destructive commands, and permits shell use only for a
small read-only inspection allowlist. It blocks direct edits on `main` and
blocks unclassified shell mutations on every branch; use Codex's edit tool for
normal feature edits. Post-edit linting is report-only. These are defense in
depth: the tracked Git gates remain the final cross-tool enforcement layer.

## Verification

```bash
python tooling/codex/generate_agents.py --check
python tooling/codex/generate_config.py --repo-root . --check
python tooling/codex/capabilities.py --repo-root .
python tooling/skill-drift/render.py --repo-root . --check
python tooling/skill-drift/check.py --repo-root . --strict --text
```

Codex hooks require local trust and are defense in depth. The Git pre-commit
dispatcher does not depend on Codex and must remain enabled for every clone.
