# Plan — TASK-PROC-006-08 Monitor Scripts and Runner (IMPL-C)

Date: 2026-05-28
Session: 8cad6c68-bfc3-421d-8029-467558e1da39 (gmail2, Opus 4.7, automated mode)

## Objective

Build four cheap structural-signal monitors + one runner under `scripts/optimize/`.
They run as plain Python after every successful `task-complete` (wired later by
IMPL-F), write JSON candidate events to `.factory/optimize/events/`, and are NOT
callable as tools by any agent (G-INV-2).

## Context gathered

- IMPL-B (TASK-PROC-006-07) scaffolding is in place: `.factory/optimize/`
  with `events/`, `state.json` (has `completions_since_last_run`,
  `periodic_counter_threshold`=10), `history/runs.tsv`, README documenting the
  event filename schema `<ISO8601-ts>-<event-type>-<fingerprint>.json` and the
  consume-then-delete + 30-day-prune invariant.
- Monitor Taxonomy (requirements.md SEC-01) — 4 monitors, event types, confidence,
  cooldown (14d repeated_question; others configurable). G-INV-2 is a hard
  constraint: monitors are plain Python, never on any tool surface.
- doc/python/: tier model. Monitors are imported by the runner ⇒ TIER B (no
  hand-rolled YAML, print discipline, direct tests, suppressions carry code+reason).
  Clock read is injected (recommended for B, needed for frozen-clock idempotency tests).
- pytest `testpaths` = `scripts/automation/tests`, `scripts/tests`. Place tests in
  `scripts/tests/` (already collected; S101 + mypy globs already cover it) → ZERO
  gate-config edits. Import monitors via `sys.path.insert(scripts/optimize)`.

## File layout

- `scripts/optimize/monitor_common.py` (TIER B) — paths, `Clock` (injectable, UTC
  for machine-exchange event content per timezone rule), `Event` dataclass,
  `event_filename`, `write_event`, `pending_events_of_type`, `recent_event_exists`
  (idempotency: same type+fingerprint event in events/ within cooldown ⇒ skip).
- `scripts/optimize/monitor_repeated_question.py` (TIER B) — fingerprint all
  `automation/pending_feedback/*/question.md` (normalized text → sha1); fire
  `repeated_question` (High) for any fingerprint with count ≥3; cooldown 14d.
- `scripts/optimize/monitor_skill_change_reverted.py` (TIER B) — git log of
  `.claude/skills/**` over last 48h; fire `skill_change_reverted` (High) when a
  skill file's recent edits net back to ~its pre-window content (substantially
  undone). Fingerprint = skill path. Cooldown configurable (default 48h).
- `scripts/optimize/monitor_skill_change_first_use.py` (TIER B) — Stage 1: fire
  `skill_changed_and_used` (Low) on a recent skill-file commit (fingerprint =
  path+sha). Stage 2 = no-op code path + TODO pointing to IMPL-H (TASK-PROC-006-13)
  `skills_used:` protocol field.
- `scripts/optimize/monitor_periodic_counter.py` (TIER B) — read state.json; fire
  `periodic` (Low) when `completions_since_last_run` ≥ `periodic_counter_threshold`.
  Idempotency: only one pending `periodic` event at a time.
- `scripts/optimize/run_monitors.py` (CLI) — imports the 4 check() fns, runs each
  guarded (named-exception boundary), writes events, aggregates exit codes,
  `--benchmark` prints elapsed (target <2s on empty queue). Event JSON schema
  documented inline at top.

## Tests (in scripts/tests/, auto-collected)

- `test_monitor_common.py` — event write + filename + idempotency window.
- `test_monitor_<each>.py` — fire condition + idempotency (run twice ⇒ one event).
- `test_run_monitors.py` — aggregation + <2s benchmark on empty queue.

## Idempotency model

Within a cooldown window, before writing, scan `events/` for an existing
un-consumed event of the same `event_type`+`fingerprint` whose `created_ts` is
within `now - cooldown`; if present, skip. This satisfies AC "run twice ⇒ one
event" using only committed project-local sources (no session JSONL — G-INV-2 /
AC-02 honored: monitors read runs.tsv, git, protocol/question files, state.json).

## Out of scope

IMPL-F wiring into task-complete; Stage 2 first-use; the consuming claude-optimize skill.

## Execution

Inline via `claude-write-script` (mandatory entry point for scripts/**/*.py):
create files → run `scripts/quality/check_python_gates.sh` → fix to green →
static grep checks for G-INV-2 (monitor names never appear as `tools:` entries;
no `.ccs/`/`~/.claude/` reads) → claude-log → doc-update-guidelines → task-complete.
