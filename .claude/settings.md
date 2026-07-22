# Hook Documentation

Human-readable reference for the hooks configured in settings.json.
Review this when a hook blocks an action you expected to succeed.

Hooks receive the tool event as JSON on stdin. Script hooks are anchored
with "$CLAUDE_PROJECT_DIR" so they resolve regardless of the session's
working directory. Hook configuration is captured at session start; after
changing settings.json or a hook script, start a new Claude Code session.

## PreToolUse Hooks

### 1. Main Branch Protection
- **Matcher**: Edit, Write
- **Behavior**: Blocks file modifications when on the `main` branch
- **Resolution**: Create a feature branch (`git checkout -b feature/your-change`)

### 2. Dangerous Command Blocker
- **Script**: `.claude/hooks/block-dangerous-commands.sh`
- **Matcher**: Bash
- **Blocked patterns, destructive**: `rm -rf`, `rm -r /`, `chmod 777`,
  `> /dev/sd`, `mkfs`, `dd if=`
- **Blocked patterns, secrets paths in command text**: `.env` and `.env.*`,
  `secrets.json`, `.pem`, `.key`, `.p12`, `credentials/` (case-insensitive,
  boundary-guarded; deliberately tighter than hook 3's set because command
  text is prose-adjacent, so a bare `credentials` substring would
  false-positive)
- **Behavior**: Reads `tool_input.command` from the stdin JSON and exits 2 on
  a match, which blocks execution and returns the message to Claude
- **Division of labor with gitleaks**: this hook is pre-execution and matches
  secrets paths so file contents never enter the model context; the
  commit-time 10-gitleaks gate is fail-closed and matches secret values in
  staged bytes. Complementary layers, no overlap in responsibility.
- **Resolution**: If the command is intentional, run it manually outside
  Claude Code

### 3. Secrets File Blocker
- **Script**: `.claude/hooks/block-secret-file-access.sh`
- **Matcher**: Read, Edit, Write
- **Blocked patterns**: `.env`, `.env.*`, `credentials`, `secrets.json`,
  `*.pem`, `*.key`, `*.p12` (case-insensitive; mirrors the credentials
  section of `.claudeignore`)
- **Behavior**: Reads `tool_input.file_path` from the stdin JSON and exits 2
  on a secrets path, which blocks the tool call so file contents never enter
  the model context
- **Scope note**: Covers the Read, Edit, and Write tools. Shell reads through
  the Bash tool (for example `cat .env`) are covered by hook 2's secrets-path
  patterns; obfuscated paths (variables, encodings) remain out of reach of
  any path matcher, which is what the commit-time gitleaks value scan is for.
- **Resolution**: Handle secrets files manually. Never paste secrets into
  Claude's context

## PostToolUse Hooks

### 4. Lint on Edit
- **Script**: `.claude/hooks/lint-on-edit.sh`
- **Matcher**: Edit, Write
- **Behavior**: Formats and lints the edited file by type. Code files
  (Python, TypeScript/JavaScript) run only for languages declared in
  `project-manifest.yaml` `stack.languages`; Terraform and prose/config
  files (json, md, yaml, css, html) run when their tool is available.
  Formatters fix in place; lint findings are surfaced on stderr.
- **When it appears to do nothing**: with `stack.languages: []` every code
  file is skipped, with a one-line stderr notice saying so. Declare the
  project's languages in the manifest to activate it.
- **Blocking**: report-only by default (always exits 0). Set
  `LINT_ON_EDIT_STRICT=1` to exit 2 on unresolved lint errors.

## Permissions
- Currently empty. Add project-specific allow/deny rules as needed.
- Example: `"allow": ["Bash(terraform plan *)"]` to skip prompting for plan commands.

## Environment Variables
- Currently empty. Use for non-sensitive project config only.
- Example: `"env": {"AWS_REGION": "us-west-2"}`
- NEVER put credentials, API keys, or tokens here.

## Cost Management

### Model Selection
`/model` switches the MAIN session's model only; sub-agent routing is fixed
per agent by the `model:` field in `.claude/agents/*.md` frontmatter (the
authoritative source) and does not follow `/model`.

Current lineup (verified pricing and tier guidance live in
`governance-commons/lib-context/ai-model-pricing.yaml`):
- **Fable 5**: frontier tier at 2x Opus; long-horizon autonomous work only.
  No standing agent assignment; its classifier reroutes flagged security
  queries to Opus 4.8 anyway.
- **Opus 4.8**: judgment-dense and security-sensitive work. All security
  agents stay on the opus tier per the pricing file's security caveat.
- **Sonnet (5)**: session default and scaffolded-review tier. New tokenizer
  emits roughly 30 percent more tokens for the same text; recount before
  budgeting.
- **Haiku 4.5**: mechanical, high-volume, low-judgment tasks.

Rule: start every session with Sonnet. Switch to Opus for deep analysis;
consider Fable 5 only for long-horizon implementation runs where fewer
failed loops justify 2x Opus rates.

### Context Management Commands
- `/cost` - Check current token usage
- `/clear` - Reset context between unrelated tasks (biggest cost saver)
- `/compact` - Compress conversation, preserving key context
- `/compact Focus on [topic]` - Custom compaction preserving specific context
- `/model` - Switch models mid-session

### Cost Patterns
- Average: ~$6/developer/day, <$12 for 90% of users
- Biggest waste: stale context from previous tasks (use /clear)
- Second biggest: reading files Claude doesn't need (.claudeignore)
- Third biggest: using Opus for simple tasks (use model routing)

### Session Discipline
- One logical task per session (one bug, one feature, one refactor)
- `/clear` when switching tasks
- `/compact` before starting a complex task in a long session
- Use subagents for investigation to keep main context clean
- Be specific in prompts: file paths, line numbers, expected behavior
