<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.severity-levels severity levels

## Anti-pattern A: Generic logger call without severity

```python
log.log("something happened", extra={"data": data})
```

Why this violates logging.severity-levels: logger.log() called without
a level argument produces records with the default level
(typically WARNING); the call site provides no severity
information. Filtering and alerting cannot distinguish this
record from intentionally severity-omitted records.

## Anti-pattern B: Custom severity vocabulary

```python
log.info("event", severity="LOUD")
log.info("event", severity="QUIET")
log.info("event", severity="BOOM")
```

Why this violates logging.severity-levels: a custom severity vocabulary
forces every downstream aggregator and dashboard to translate
it. Cross-team incident response stalls while teams figure
out what "BOOM" means relative to ERROR.

## Anti-pattern C: Severity-as-prose in message body

```python
log.info("ERROR: payment failed for user " + user_id)
log.info("CRITICAL: database connection lost")
log.info("WARNING: rate limit approaching")
```

Why this violates logging.severity-levels: severity is in the message
body, not a structured field. Filters that target the
severity field find these records at INFO level. Alerting
rules that fire on ERROR records miss these because the
structured severity is INFO.

## Anti-pattern D: print as ERROR

```python
import sys
def handle_error(e):
    print(f"FATAL: {e}", file=sys.stderr)
```

Why this violates logging.severity-levels: print to stderr emits prose
with no structured severity field. The output may be
captured by the orchestrator's log collector but arrives at
the aggregator as a prose record at the orchestrator's
default level (often UNKNOWN or DEFAULT).

## Anti-pattern E: Inconsistent severity across modules

```python
# module a.py
log.warning("user not found")

# module b.py (different team)
log.info("user not found")  # ← same condition, different severity

# module c.py
log.error("user not found")  # ← same condition, third severity
```

Why this violates logging.severity-levels: the same operational condition
is logged at three different severities across modules.
Alerting based on severity is unreliable; incident response
must check all severities to be sure.

## Anti-pattern F: Logger configured without severity field

```python
# logging configuration emits prose only, no severity field
LOGGING = {
    'formatters': {
        'simple': {
            'format': '%(message)s'  # ← no level in format
        }
    }
}
```

Why this violates logging.severity-levels: the structured output omits
severity. Even though logger.info, logger.error etc. are
called with valid severity, the formatter drops it. Records
arrive at the aggregator without the severity field.

## Cross-reference

- Good patterns: examples/logging/severity-levels-good.md
- Substrate rule: logging.severity-levels
