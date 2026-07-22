# falsification - mutation-testing orchestrator (Cap 1)

A green test proves nothing unless it can be made to go red. The 003 run's most
expensive class was "green but not exercised": a tripwire that never fired, a
fixture that never ran, a check whose neutralization no test noticed. The
`test-architect` agent already preaches this (it lists "mutation testing readiness"
and demands a negative counterpart for every happy path) but nothing mechanized it.
This does: it mutates the code under a path, runs that code's tests, and reports the
mutants that survived. A surviving mutant is a green that was never exercised.

Mutation testing parses each language's AST, so this is an orchestrator over the
real per-language tools, the same shape as the quality gate:

| language | mutation tool |
|---|---|
| python | mutmut |
| typescript / javascript | Stryker |

## Positive evidence only

It reports `VERIFIED` for a language only with positive proof: mutants were
generated, the test runner actually ran, and no mutant survived or went unchecked.
The absence of a reported survivor is not proof of a kill, a broken test runner
leaves every mutant "not checked", which is not a pass. That situation is reported
as `COULD NOT VERIFY`, never green. (This rule exists because the first draft of
this tool had exactly that false-green bug; its own weak-test teeth caught it.)

## Loud, never silent

- `TOOL MISSING`: the mutation tool is not installed. A prominent banner with an
  install hint; under `--strict` it BLOCKS. "I could not check" is not "it passed".
- `COULD NOT VERIFY`: the tool ran but did not establish kills (broken runner, no
  mutants, unchecked mutants). Loud; blocks under `--strict`.
- `UNSUPPORTED`: the framework has no mutation tool for this language (shell, HCL).
  Loud, but does not block, there is nothing to install.

## Posture

On-demand and advisory (exits 0), for the post-impl checkpoint or CI. `--strict`
exits 1 on surviving mutants, a missing installable tool, or a could-not-verify run.
Mutation runs the suite once per mutant, too slow for a per-commit gate. The mutmut
adapter clears mutmut's `mutants/` state before each run so the verdict is
deterministic across re-runs.

## Setup the consumer owns

Each mutation tool needs its own config, exactly as it would outside this framework:
mutmut needs a `[mutmut]` section (`source_paths` + `runner`), Stryker needs
`stryker.conf.js`. The framework ships the orchestrator, the loud-skip discipline,
and the verdict; it does not ship the heavy tools or their config.

```
python3 tooling/falsification/check.py --paths tooling --text     # self-test the framework
python3 tooling/falsification/check.py --paths src --strict        # a consumer, in CI
```

The pure core (detection, classification, verdict, rendering, strict semantics) is
stdlib-only and unit-tested with injected adapters. Tests:
`python3 tooling/falsification/test_check.py`

## Adapter maturity (read before trusting a verdict)

The orchestration is language-agnostic: language detection, adapter routing, and
the loud-skip behaviour are proven for every language (the live `.ts`-with-Stryker-
absent run produced the correct TOOL MISSING and blocked under `--strict`). But the
execution-and-parse layer is only proven end-to-end for one tool so far:

| language | tool | adapter status |
|---|---|---|
| python | mutmut | exercised end-to-end (strong->verified, weak->survivors, broken-runner->could-not-verify, deterministic across re-runs) |
| typescript / javascript | Stryker | written to Stryker's documented JSON report schema; routing and loud-skip proven, but NOT yet exercised against a real Stryker run |

So "multi-language" is true in routing and design, and proven in execution only for
Python today. The Stryker parse will get its first real exercise against a TypeScript
consumer (e.g. a downstream application). Until then, treat a Stryker VERIFIED with the same
caution this tool teaches: a verdict from an unexercised path is not yet evidence.
