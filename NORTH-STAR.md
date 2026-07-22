<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->
<!--
Your project's north-star: the longest-horizon context, loaded first on every agent run
by tooling/compose/compose_context.py, ahead of the manifest slice and open log items.
Hold only durable intent here. Change it only at phase boundaries, never per feature
(per-feature churn recreates the handoff problem inside the north-star). Keep it to about
a page.

Pointers, not copies: project-manifest.yaml is the source of truth for the active
profile; .specify/memory/constitution.md for governance. Don't duplicate them here.

current-objective is checked by the staleness gate (tooling/staleness/check.py): it must
resolve to an active feature under specs/ or an open PROJECT-LOG item, or the gate flags
the north-star as drifted. Update it when you start a new phase. This file ships as a
placeholder in the template repo, so the gate correctly reports no active feature until
a consumer project fills it; it does its real work in consumer repos.

This root file is the single copy: there is no separate north-star template. Fill it in
place when you adopt the framework.
-->
---
purpose: "<one or two sentences: what this project is for and who it serves>"
definition-of-good: "<what 'done well' means here: the bar a feature must clear, in your terms>"
active-profile: "see project-manifest.yaml -> substrate.profile (authoritative)"
constitution: ".specify/memory/constitution.md"
current-objective: "<the current phase's objective; must resolve to an active feature under specs/ or an open PROJECT-LOG item>"
---

# North star

## Why this exists

<A short paragraph on the durable purpose. Not this quarter's tasks, the reason the
project exists at all.>

## What good looks like

<Concrete, verifiable description of quality for this project. Prefer "the gate refused
X" over "the code is clean." Name the conditions an outside reviewer could check.>

## The horizons

- **North star (this file)** - durable intent, changed at phase boundaries.
- **Working set** - `project-manifest.yaml`, sliced per checkpoint.
- **Handoff** - `PROJECT-LOG.md`, the append-only cross-feature ledger.
