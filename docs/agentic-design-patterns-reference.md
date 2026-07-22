<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Agentic System Design Patterns: A Portable Reference

A distilled, project-agnostic reference for designing AI agent and workflow
systems, synthesized from published guidance by the teams that build these
systems in production (Anthropic, Cognition, Manus, Arize, and 2026 academic
work on context engineering). Use this as a checklist and decision framework
when architecting any new LLM-powered system.

Last synthesized: May 2026. Treat as a living document. The field moves fast;
re-validate against current sources before relying on any specific claim.

---

## 0. The Meta-Principles (read these first)

These override everything else. If a specific pattern below conflicts with one
of these, the meta-principle wins.

1. **Start simple. Add complexity only when measurement proves you need it.**
   The most successful production systems use simple, composable patterns, not
   elaborate frameworks. Reach for the simplest pattern that solves the problem.
   (Source: Anthropic, Building Effective Agents.)

2. **Expect to rebuild. It is empirical, not theoretical.**
   Teams building leading agent products report rebuilding their core
   architecture multiple times through trial and error. Do not over-invest in
   a perfect upfront design. Ship the simplest version, measure it, iterate.
   (Source: Manus, "Stochastic Graduate Descent.")

3. **Context engineering is the actual job.**
   When agents fail in production, the problem is rarely the model. It is almost
   always that the context window was mismanaged. Deciding what enters context,
   what is compressed, what is retrieved on demand, and what is dropped is the
   core discipline. (Source: 2026 context engineering consensus.)

4. **Evaluation is not optional, and it is the part everyone skips.**
   The quality of the evaluation harness often matters more than raw model or
   benchmark performance. Build evaluation in from the start, not as an
   afterthought. (Source: Arize field lessons; Anthropic evaluation guidance.)

5. **Keep the system orthogonal to the model.**
   Architect so that model improvements flow in without a rewrite. Bet on
   context engineering and structure, not on the quirks of a specific model
   version. (Source: Manus.)

---

## 1. Workflows vs Agents (the foundational distinction)

Two different things. Choose deliberately.

**Workflows**: LLMs and tools operate through predefined code paths.
Orchestration is programmatic. Execution is predictable. The LLM makes
decisions at defined checkpoints, but the control flow is fixed by you.

**Agents**: The LLM dynamically directs its own process and tool usage. It
plans and operates independently after an initial task is set, using
environmental feedback to assess progress and adapt.

**Decision rule**: Default to workflows. Use a true autonomous agent only when
the task genuinely requires dynamic, unpredictable control flow that you cannot
pre-structure. Most problems that look like they need an agent are better served
by a workflow. Workflows are more predictable, cheaper, easier to debug, and
easier to evaluate.

**Tradeoffs to weigh**: latency, cost, reliability, flexibility. Workflows win
on the first three. Agents win on flexibility for genuinely open-ended tasks.

---

## 2. The Five Workflow Patterns

The canonical building blocks. Compose them; do not reinvent them.

### 2.1 Prompt Chaining
Decompose a task into a fixed sequence of steps, each LLM call feeding the next.
Add programmatic gates between steps to validate before proceeding.
- **Use when**: the task has clear sequential subtasks.
- **Example**: capture raw input -> structure it -> validate -> store.

### 2.2 Routing
Classify the input, then send it to a specialized handler. Avoids overloading a
single prompt with every possible case.
- **Use when**: inputs fall into distinct categories needing different handling.
- **Example**: route a support query to billing vs technical vs account flows.

### 2.3 Parallelization
Run independent subtasks at the same time. Two sub-flavors:
- **Sectioning**: divide one task into independent pieces handled concurrently.
- **Voting**: run the same task multiple times and combine outputs for
  confidence.
- **Use when**: speed matters and subtasks are genuinely independent, or when
  you need confidence through redundancy.

### 2.4 Orchestrator-Workers
An orchestrator dynamically breaks a task into subtasks and delegates each to a
worker. Unlike parallelization, the subtasks are not known in advance.
- **Use when**: task complexity is unpredictable and decomposition must be
  decided at runtime.
- **Example**: a coding agent handling a change that spans an unknown number of
  files.

### 2.5 Evaluator-Optimizer
One LLM generates, a second evaluates against explicit criteria, the generator
refines based on feedback, loop until the output passes.
- **Use when**: you have clear evaluation criteria and iterative refinement
  adds measurable value. Especially valuable for any output a human will send,
  publish, or act on.
- **This is the pattern most teams skip and most need.**

---

## 3. The Read / Write / Action Separation

The most useful architectural lens for deciding where to parallelize and where
to keep things single-threaded. The single-vs-multi-agent debate resolves here.

**READ tasks** (research, analysis, information gathering):
- Easy to parallelize. Suit multiple concurrent sub-agents well.
- Independent reads do not conflict, so fan them out.
- This is where the large measured gains from multi-agent approaches come from.

**WRITE tasks** (code generation, content creation, file editing):
- Create coordination problems when parallelized. Favor a single agent with a
  single coherent context.
- Multiple agents writing different parts produce conflicting decisions and
  fragile context sharing.
- Keep these single-threaded.

**ACTION tasks** (anything with external side effects: submit, send, post,
commit, pay, delete):
- Gate with human approval or hard programmatic guardrails.
- The cost of an error here is high and often irreversible.

**Architectural rule**: For mixed tasks, separate the read and write phases
explicitly. Parallelize the reads. Single-thread the writes. Gate the actions.
Do not let a single flow blur the three.

---

## 4. Context Engineering (five quality criteria)

For every context window you assemble, evaluate against these five. Treat
context as the system's operating system.

1. **Relevance**: Does every token relate to the current task? Drop the rest.
2. **Sufficiency**: Is everything needed to succeed actually present?
3. **Isolation**: Are unrelated concerns kept out? (e.g., separate system rules
   from user data from task data, so each can be reasoned about and updated
   independently.)
4. **Economy**: Is the context as small as it can be while remaining sufficient?
   Every extra token costs money, latency, and signal dilution.
5. **Provenance**: Can you trace where each piece of context came from? This
   matters for trust, debugging, and preventing fabrication.

**Compression techniques** when context grows: summarization, trimming,
clearing stale history, hierarchical compression (keep summaries, drop detail).

**Memory tiers** for long-running systems: hot cache (active), warm session
(recent), cold archive (historical, retrieved on demand).

**Failure modes to watch**: context poisoning (bad data persists and
compounds), distraction (irrelevant content pulls focus), confusion (too much
at once), clash (contradictory context).

---

## 5. Evaluation Discipline

The part that separates hobby projects from production systems.

**Start immediately, with small samples.** Do not wait for a big dataset. Ten
to twenty hand-labeled examples is enough to begin.

**Three complementary layers:**
- **Golden dataset**: hand-curated inputs with known-good outputs. Run against
  it whenever you change logic, to catch regressions and drift.
- **LLM-as-judge**: a separate LLM scores outputs against a rubric. Scales well
  when the rubric is explicit. Use for continuous, high-volume evaluation.
- **Human evaluation**: catches what automation misses. Use periodically and
  for high-stakes outputs.

**Metrics beyond accuracy** (for any agentic system):
- Task success rate: did it accomplish the goal?
- Tool success rate: were tools used correctly?
- Latency: how long did it take?
- Cost: tokens or dollars per task.
- Drift: is output quality or scoring distribution changing over time?

**Prompt learning loop**: improve performance without changing the model by
iterating system prompts through an action -> evaluation -> improvement cycle.
Often more cost-effective than swapping models.

---

## 6. Observability

You cannot improve what you cannot see. For anything you will run repeatedly:

- **Decision-path visibility**: not just output logs, but why a given tool or
  branch was chosen. When failures propagate downstream, you need to inspect
  the decision, not just the result.
- **Per-step metrics**: cost, latency, success/failure at each stage.
- **Drift tracking**: score distributions and quality metrics over time.
- **Replayability**: ability to reconstruct what happened on a given run.

Minimum viable observability is a metrics table plus a periodic summary. It does
not need to be elaborate to be essential.

---

## 7. Scaffolding vs Harness (the two-phase structure)

A clean way to organize any agentic system.

**Scaffolding** (assembled before the first prompt):
- System prompts
- Tool schemas and definitions
- Sub-agent registry
- Static configuration and policy

**Harness** (orchestrates at runtime):
- Tool dispatch
- Context management (assembly, compression, dropping)
- Safety enforcement and guardrails
- Long-conversation management within finite context limits

Designing these as distinct concerns keeps the system model-agnostic and makes
the runtime behavior inspectable.

---

## 8. Compound AI Systems

State-of-the-art results increasingly come from systems that compose multiple
models, retrievers, and tools, not from a single monolithic LLM call.

**Implications:**
- Make the system model-agnostic by construction. Bind each workflow step to a
  configurable model so you can route cheap steps to cheap models and hard
  steps to capable ones.
- Apply learned or rule-based model routing at the workflow level (cost vs
  capability per cognitive task).
- The system is an ensemble of workflows and tools, each independently
  swappable.

---

## 9. Tool Design

The interface between the system and its tools is as critical as a
human-computer interface.

- **Describe tools precisely.** Clear, distinct descriptions. Ambiguity causes
  wrong tool selection.
- **Provide selection heuristics.** Give explicit guidance on when to use which
  tool.
- **Typed inputs and outputs.** Use structured schemas, not free-form text, for
  anything downstream code must parse.
- **Make tools deterministic where possible.** Reserve LLM reasoning for
  judgment; use plain code for anything deterministic (parsing, dedup, I/O,
  math).

---

## 10. Human-in-the-Loop (HITL)

- Pause for human feedback at checkpoints, at blockers, and before any
  high-stakes or irreversible action.
- Distinguish "human reviews the output" (cheap, approve/reject) from "human
  does the work" (expensive). Push toward the former; reserve the latter for
  the irreducible substance only the human can provide.
- Never blur review into rubber-stamping. The review must have a real gate
  (a rubric, a confidence threshold) or it adds no value.

---

## 11. Structured Outputs

- For any data another system or downstream step consumes, generate structured
  output (JSON mode, tool calls, typed entities), not prose that must be parsed
  with regex or trust.
- Reserve markdown and prose for human-facing presentation only.
- Validate structured output against a schema before using it. Handle
  validation failure explicitly.

---

## 12. Anti-Patterns (do not do these)

- **Calling everything "multi-agent."** Most systems are workflows. Overclaiming
  invites the fragility of true multi-agent coordination without the benefit.
- **Parallelizing write tasks.** Causes conflicting decisions and broken context
  sharing.
- **Skipping the eval harness** because the demo looked good. Demos pass; reality
  introduces tool misuse, context drift, and ambiguous input.
- **Keyword-stuffing the context window.** More context is not better context.
  Economy and relevance beat volume.
- **Free-form text as the data contract** between steps. Brittle. Use structured
  outputs.
- **Designing the perfect architecture upfront.** Ship simple, measure, iterate.
  Over-design is a form of procrastination.
- **Building complex abstractions before simple patterns are proven
  insufficient.**

---

## 13. A Decision Framework (apply to any new system)

Ask, in order:

1. **Can this be solved without an LLM at all?** If deterministic code works,
   use it. Reserve the LLM for genuine judgment.
2. **Is this a workflow or a true agent?** Default to workflow.
3. **Which of the five patterns fit?** Compose the simplest set that works.
4. **What are the read, write, and action phases?** Separate them. Parallelize
   reads, single-thread writes, gate actions.
5. **For each context window: relevance, sufficiency, isolation, economy,
   provenance?**
6. **What is the golden dataset and the evaluation rubric?** Define before
   building the feature, not after.
7. **What metrics will I track to know it is working and not drifting?**
8. **Where are the human gates?**
9. **What is the simplest version I can ship and measure this week?**

If you cannot answer 6 and 7, you are not ready to build the feature yet.

---

## Source Lineage

- Anthropic, "Building Effective Agents" (workflow/agent taxonomy, five
  patterns, tool design, evaluation guidance).
- Anthropic, "How We Built Our Multi-Agent Research System" (parallel reads,
  measured multi-agent gains, token cost tradeoff).
- Cognition, "Don't Build Multi-Agents" (single-agent reliability, context
  sharing fragility for writes).
- Manus, "Context Engineering for AI Agents" (expect-to-rebuild, model
  orthogonality, Stochastic Graduate Descent).
- Arize, field lessons on production agents (evaluation harness primacy,
  metrics beyond accuracy).
- 2026 context engineering literature (five context quality criteria,
  scaffolding/harness, compound systems).

Re-verify all specifics against primary sources before relying on them. This
document is a synthesis, not a citation of record.
