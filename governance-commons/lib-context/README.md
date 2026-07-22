<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Library Context

Version-pinned API guidance for libraries that AI coding tools
frequently hallucinate APIs for. Each file is a structured YAML
document describing the current API surface, common hallucination
patterns to watch for, and concrete examples.

## Why this exists

LLMs are trained on a snapshot of public code. Libraries evolve
faster than model training cycles. Result: AI tools confidently
generate code using:

- APIs that no longer exist (deprecated/removed)
- APIs from prior major versions (e.g., Pydantic v1 patterns in
  Pydantic v2 codebases)
- APIs from popular forks confused with the canonical library
- Fabricated APIs that "look right" but don't exist

This directory provides current-API ground truth that AI tools
consume as context. When the AI sees the lib-context file for
LangChain, it has authoritative information about the current
API and shouldn't hallucinate.

## How consuming frameworks use these

Three integration patterns:

### Pattern 1: Inject into system prompt

When the AI tool is invoked for work touching a specific library,
the framework prepends the relevant lib-context as system context:

    System prompt includes:
    - General governance principles
    - lib-context/langchain.yaml (because the task involves LangChain)
    - Project-specific spec

### Pattern 2: On-demand reference

The AI tool can fetch lib-context entries on demand when
encountering ambiguity:

    /lib-context langchain
    /lib-context pydantic v2

### Pattern 3: PreToolUse hook validation

When the AI is about to write code that imports a tracked library,
a hook injects the lib-context as additional reasoning material
before the write proceeds.

The consuming framework chooses the pattern that fits its
architecture. This commons just provides the content.

## File format

Each lib-context file is YAML with this structure:

    library:
      name: <library-name>
      ecosystem: <python | javascript | rust | etc>
      current_version: <version>
      last_reviewed: <YYYY-MM-DD>
      review_cadence: <monthly | quarterly>

    deprecations:
      - api: <old-api>
        deprecated_in: <version>
        removed_in: <version-or-null>
        replacement: <new-api>
        migration: <text>

    current_api:
      - name: <api-name>
        signature: <signature>
        description: <text>
        example: <code>
        notes: <text>

    common_hallucinations:
      - pattern: <what-AI-might-write>
        problem: <why-it's-wrong>
        correct: <what-should-be-written>

    references:
      - <url>
      - <url>

Files are written in YAML for easy human and AI parsing. They
should not have raw code blocks containing markdown backticks
that could break parsing.

## Maintenance

These files have a high maintenance burden. Libraries change
frequently. Stale lib-context is worse than no lib-context (gives
AI false confidence).

Per [../MAINTENANCE.md](../MAINTENANCE.md), lib-context files
have monthly or quarterly review cadence based on the library's
release velocity:

| Library | Cadence | Reasoning |
|---|---|---|
| langchain | Monthly | High release velocity, breaking changes common |
| langgraph | Monthly | New project, still evolving |
| pydantic | Quarterly | Stable major version, slower changes |
| fastapi | Quarterly | Mature, stable API |
| terraform-aws | Quarterly | AWS provider evolves with AWS services |
| cedar | Quarterly | Stable language; new policy patterns emerge |

When the maintenance owner detects a library has shipped a
significant API change since last review, they:

1. Update the affected `current_api` entries
2. Add deprecations for removed APIs
3. Update `current_version` and `last_reviewed`
4. Note the change in commit message

## Index

| File | Library | Why it's tracked |
|---|---|---|
| [langchain.yaml](./langchain.yaml) | LangChain | Hallucination-prone; v0.1 vs v0.3 differences |
| [langgraph.yaml](./langgraph.yaml) | LangGraph | Primary enterprise agent framework; rapid evolution |
| [pydantic.yaml](./pydantic.yaml) | Pydantic | v1 vs v2 migration still incomplete; mixed code common |
| [fastapi.yaml](./fastapi.yaml) | FastAPI | Common in AI service stacks; lifespan/dependency patterns hallucinated |
| [terraform-aws.yaml](./terraform-aws.yaml) | terraform-provider-aws | Many resource arguments evolved; AI uses outdated args |
| [cedar.yaml](./cedar.yaml) | Cedar | Used for policies/ in this commons; syntax reference |

## Adding new libraries

When adding a new lib-context file:

1. Use the template from any existing file as a starting point
2. Reference upstream's official docs as primary source
3. Cover the most-used API surface (not every method; the 80/20)
4. Include at least 3-5 common hallucination patterns
5. Add to the index table above
6. Add to the maintenance cadence table

Files should be ~200-500 lines. Longer files become harder to
maintain. If a library has more API surface than fits, scope to
the parts AI tools touch most often.

## Anti-patterns

These maintenance behaviors cause more harm than help:

- **Letting files go stale without removal** — outdated lib-context
  is misleading. Either update it or remove it.
- **Documenting every API** — focus on the parts AI hallucinates.
  Documenting everything dilutes the signal.
- **No version field** — without `current_version`, verifiers can't
  detect whether the lib-context is in sync with the library
  version being used
- **Vendoring library docs verbatim** — these files supplement
  official docs; they don't replace them. Link to official.
- **Including code that requires runtime context** — examples
  should be self-contained. Snippets that require initialization
  not shown become confusing.

## License note

These lib-context files contain summaries and short illustrative
examples; they don't redistribute library documentation. Each file
links to the upstream's authoritative documentation as the primary
source.
