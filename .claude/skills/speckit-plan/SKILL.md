---
name: "speckit-plan"
description: "Execute the implementation planning workflow using the plan template to generate design artifacts."
argument-hint: "Optional guidance for the planning phase"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/plan.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before planning)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_plan` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing slash commands from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

1. **Setup**: Run `.specify/scripts/bash/setup-plan.sh --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

5. **Check for extension hooks**: After reporting, check if `.specify/extensions.yml` exists in the project root.
   - If it exists, read it and look for entries under the `hooks.after_plan` key
   - If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
   - Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
   - For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
     - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
     - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
   - When constructing slash commands from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
   - For each executable hook, output the following based on its `optional` flag:
     - **Optional hook** (`optional: true`):
       ```
       ## Extension Hooks

       **Optional Hook**: {extension}
       Command: `/{command}`
       Description: {description}

       Prompt: {prompt}
       To execute: `/{command}`
       ```
     - **Mandatory hook** (`optional: false`):
       ```
       ## Extension Hooks

       **Automatic Hook**: {extension}
       Executing: `/{command}`
       EXECUTE_COMMAND: {command}
       ```
   - If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Instantiate the data-model template** → `data-model.md`:
   - Copy `.specify/templates/data-model-template.md` to `specs/NNN-feature/data-model.md`
     and fill every section, the same instantiate-then-fill pattern that `setup-plan.sh`
     uses for `plan-template.md`. Do not generate the file freehand; the template carries
     the mandatory structure, including the Normalization section, so the forcing function
     is a form you fill rather than an instruction you must remember.
   - Per entity: name, fields, relationships, validation rules from requirements, and state
     transitions if applicable.
   - **Normalization declaration (required)**: fill the template's `## Normalization`
     section. For each entity, state which fields are owned per-instance and which are
     constant across a referencing dimension (one value shared by every persona an operator
     owns, every order a customer places, every instance that shares a parent) and therefore
     live once on the referenced entity, referenced by key, not duplicated per-referrer, per
     the substrate rule `code-organization.data-model-single-source-of-truth`. Replace the
     template's `TODO` with the real declaration; leaving it fails the normalization gate. A
     deliberate duplicate is allowed if the reason is recorded; what is not allowed is
     skipping the decision.

2. **Define interface contracts** (if project has external interfaces) → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

3. **Agent context update**:
   - Update the plan reference between the `<!-- SPECKIT START -->` and `<!-- SPECKIT END -->` markers in `CLAUDE.md` to point to the plan file created in step 1 (the IMPL_PLAN path)

**Output**: data-model.md, /contracts/*, quickstart.md, updated agent context file

## Key rules

- Use absolute paths for filesystem operations; use project-relative paths for references in documentation and agent context files
- ERROR on gate failures or unresolved clarifications
- After any bulk identifier substitution across the plan artifacts (a re-normalization or rename touching several of research.md, data-model.md, contracts/, quickstart.md), verify the rename on disk rather than asserting consistency in prose: run `python3 tooling/rename-integrity/check.py --rename old_name=new_name --repo-root . --text` for each renamed identifier and read the raw counts. The old identifier must show 0 live occurrences and the new identifier must show its propagation footprint. A narrative "consistency sweep" does not satisfy this; the counts on disk do.
- After generating data-model.md, run the normalization gate: `python3 tooling/data-model-normalization/check.py --path specs/NNN-feature/data-model.md --text`. It confirms the required `## Normalization` declaration is present and not a placeholder, per `code-organization.data-model-single-source-of-truth`. The gate checks that the cardinality decision was stated; it does not judge whether the decision is correct, which is staff-engineer's review at C2. Use `--strict` where the dial's andon is blocking.
