<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Best Practices Reference

Collected from official Anthropic documentation, production repos, and
practitioner experience. This file is for YOU — Claude does not read this
unless you explicitly reference it.

This document is Claude-Code-operational (session hygiene, cost, CLAUDE.md
authoring). For architecture-level design guidance (workflows vs agents,
read/write/action separation, evaluation discipline), see the companion
`docs/agentic-design-patterns-reference.md`.

---

## Core Principle

**Define success criteria before building.**

The prompt engineering docs reinforce this: have a clear definition of
success, ways to test against it, and a first draft before optimizing.
Our /plan command and SPEC.md template enforce this workflow.

---

## Claude Code Session Practices

### Context Management (biggest cost lever)
- `/clear` between unrelated tasks — stale context wastes tokens on every
  subsequent message
- `/compact` before starting complex work in a long session — or
  `/compact Focus on [topic]` to preserve specific context
- Manual `/compact` at ~50% context — don't wait for auto-compact at 95%
- One logical task per session: one bug, one feature, one refactor
- `/rename` sessions before clearing so you can `/resume` later

### Model Selection (second biggest cost lever)
- Start every session with Sonnet (default)
- Switch to Opus only for: complex architecture, multi-file refactors,
  deep security review, debugging hard problems
- Use Haiku for: quick lookups, formatting, renaming, repetitive tasks
- `/model` switches mid-session — no restart needed

### Prompting for Efficiency
- Be specific: file paths, line numbers, expected vs actual behavior
- Direct Claude to files: "look at src/auth/validate.ts line 42" not
  "fix the auth bug"
- Pipe data: `cat error.log | claude` instead of "read the error log"
- Use `@` to reference files instead of describing where code lives
- Paste images/screenshots for UI work — visual context saves tokens

### Session Hygiene
- Don't mix topics in one session — 39% performance degradation
  (TheDecipherist research)
- Use subagents for investigation — they explore in separate context
  without polluting your main session
- If you've corrected Claude twice on the same issue, `/clear` and
  start fresh with a better prompt
- Leave breadcrumbs in CLAUDE.local.md for resuming across sessions

---

## CLAUDE.md Authoring Rules

Source: Official docs, HumanLayer blog, shanraisshan best practices

- Under 200 lines. Under 100 is better. 60 lines ideal.
- For each line ask: "Would removing this cause Claude to make mistakes?"
  If not, cut it.
- ~150-200 instruction budget before compliance drops. System prompt
  uses ~50, leaving ~100-150 for your rules.
- Don't duplicate what Claude can infer from your code
- Don't include standard language conventions Claude already knows
- Don't put documentation — link to it instead
- Use IMPORTANT or YOU MUST for critical rules (increases adherence)
- Treat it like code: review when things go wrong, prune regularly
- Check into git so team inherits the same context
- If Claude ignores your rules, the file is probably too long

### When Claude Ignores CLAUDE.md
Claude Code injects CLAUDE.md with a system reminder that says:
"this context may or may not be relevant to your tasks."
The more irrelevant content in the file, the more likely Claude
ignores ALL of it. Keep it focused.

---

## Skill Authoring Rules

Source: Official docs, ChrisWiles showcase

- The `description` field is the trigger — Claude uses semantic matching
  on it to decide when to load the skill
- Include trigger keywords in the description: file types, actions,
  concepts that should activate this skill
- Standard sections: When to Use, Core Patterns, Anti-Patterns
- Keep skills focused — one domain per skill
- Skills load on demand, not every session — put domain knowledge here,
  not in CLAUDE.md

---

## Hook Design Rules

Source: Official docs, TheDecipherist, shanraisshan

- CLAUDE.md is advisory (~80%). Hooks are deterministic (100%).
- If something MUST happen every time → hook, not CLAUDE.md
- Exit code 0 = allow. Exit code 2 + JSON stderr = block.
- timeout: 5 for simple checks, 10 for file operations
- PostToolUse hooks for formatting — auto-format after every edit
- PreToolUse hooks for security — block before damage happens
- Stop hooks for quality gates — verify before Claude declares done
- Don't put in CLAUDE.md what a linter/formatter/hook can enforce
  deterministically. "LLMs are comparably expensive and slow compared
  to traditional linters" (HumanLayer)

---

## Subagent Design Rules

Source: Official docs, gstack, ChrisWiles

- Give subagents minimal tool access (least privilege)
- Reviewers get Read, Grep, Glob, Bash — never Edit or Write
- Use Opus for deep analysis (security review)
- Use Sonnet for routine checks (code quality)
- Use Haiku for simple lookups
- Name agents by role, not domain: "security-reviewer" not
  "security-skill-agent"
- Keep descriptions specific — Claude auto-invokes based on matching

---

## Hallucination Reduction

Source: platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations

- Allow Claude to say "I don't know" — explicitly give permission to
  admit uncertainty in CLAUDE.md
- Use direct quotes for factual grounding — for tasks with long documents,
  ask Claude to extract word-for-word quotes before performing analysis
- Chain-of-thought verification — ask Claude to explain reasoning
  step-by-step before giving a final answer
- External knowledge restriction — instruct Claude to only use
  information from provided documents, not general knowledge
- Best-of-N verification — run same prompt multiple times, compare
  outputs for inconsistencies
- Verify with citations — have Claude cite sources, then verify each
  claim by finding supporting quote. Retract if no quote found.

---

## Prompt Engineering Principles

Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering

- Be clear and specific — ambiguity wastes tokens and produces wrong output
- Use positive and negative examples — show what you want AND what you don't
- Encourage step-by-step reasoning — "think through this step by step"
- Use XML tags for structure — `<instructions>`, `<context>`, `<example>`
- Specify desired output format — "respond in JSON", "use bullet points"
- Put instructions before content — Claude prioritizes what comes first
- For complex tasks, use prompt chaining — break into sequential steps
- Role prompting works: "You are a senior security engineer reviewing..."
  (this is what our agent definitions do)

---

## Cost Reference

Source: code.claude.com/docs/en/costs, practitioner reports

### Typical Costs
- Average: ~$6/developer/day
- 90th percentile: <$12/day
- Monthly (Sonnet-primary): ~$100-200/developer
- Pro subscription: $20/month (included usage, rate limited)
- Max subscription: $100-200/month (higher limits)

### Where Tokens Go (biggest to smallest)
1. Re-reading file contents on every turn (40-60% of read tokens are
   redundant reads — use .claudeignore)
2. Stale context from previous tasks (use /clear)
3. CLAUDE.md and skills loaded every session (keep lean)
4. Command output filling context (git log, test suites, build logs)
5. Using Opus for tasks Sonnet handles fine

### Cost Savings Stack (compound effect)
- .claudeignore: eliminates redundant file reads
- Lean CLAUDE.md (<200 lines): reduces per-turn base cost
- On-demand skills: loads only when relevant
- Subagents: isolate exploration from main context
- Model routing (Sonnet default): 5x cheaper than Opus
- /clear between tasks: prevents context bloat
- Specific prompts: reduces search/exploration tokens
- Combined savings: 30-70% reduction reported by practitioners

---

## Security Practices for AI-Assisted Development

Source: Backslash Security research, TheDecipherist, FlorianBruniaux

- Claude Code reads .env files without explicit permission if not
  restricted — use hooks to block access
- CLAUDE.md rules about secrets are advisory. Hooks are enforcement.
- Never paste credentials into Claude's context window
- Audit MCP server configurations for data exposure risks
- Scope AI tool permissions to project directories only
- Review Claude's git commits before pushing — it may include
  debug code, commented-out secrets, or overly permissive configs
- Run `npx ecc-agentshield scan` periodically to audit your
  Claude Code configuration for vulnerabilities

---

## Platform API Practices (Direct Claude API Use)

These apply when building applications that call the Claude API directly,
not when using Claude Code CLI as a development tool.

### Prompt Caching (90% cost reduction on cached reads)
- Place static content (system prompts, tool definitions) at the beginning
- Mark cacheable sections with cache_control
- Use automatic caching for multi-turn conversations
- 5-minute default TTL, refreshed on each use
- Minimum cacheable length: 1024-4096 tokens depending on model
- Cache reads: 10% of base input token price
- Cache writes: 125% of base input token price (one-time)

### Guardrails
- Reduce hallucinations: allow "I don't know", direct quotes, CoT verification
- Mitigate jailbreaks: input validation, output filtering, system prompt hardening
- Reduce prompt leak: never expose system prompts, use layered defenses
- Increase consistency: structured outputs, temperature control, examples

### Batch Processing
- 50% cost reduction for non-time-sensitive workloads
- Send large batches of queries asynchronously
- Results available within 24 hours

Full documentation links in FUTURE.md under "Claude API Documentation"

---

## Links

### Official Documentation
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code .claude directory: https://code.claude.com/docs/en/claude-directory
- Claude API features overview: https://platform.claude.com/docs/en/build-with-claude/overview
- Prompt engineering: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
- Prompt engineering tutorial: https://github.com/anthropics/prompt-eng-interactive-tutorial
- Guardrails: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
- Test & evaluate: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests

### Practitioner Guides
- Tweag Agentic Coding Handbook: https://tweag.github.io/agentic-coding-handbook
- 12 Proven Token Saving Techniques: https://aslamdoctor.com/12-proven-techniques-to-save-tokens-in-claude-code/
- Claude Code Cost Optimization: https://systemprompt.io/guides/claude-code-cost-optimisation
- Reduce Token Usage 30-50%: https://docs.bswen.com/blog/2026-03-10-reduce-claude-code-token-usage/
- Steve Kinney Cost Management: https://stevekinney.com/courses/ai-development/cost-management
- Claude Code Pricing Optimization: https://claudefa.st/blog/guide/development/usage-optimization
