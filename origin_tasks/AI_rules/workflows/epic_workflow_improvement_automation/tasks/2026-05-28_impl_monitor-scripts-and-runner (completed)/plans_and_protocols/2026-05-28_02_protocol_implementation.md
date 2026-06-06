# Protocol — TASK-PROC-006-08 Implementation

Date: 2026-05-28
Session: 8cad6c68-bfc3-421d-8029-467558e1da39 (gmail2, Opus 4.7, automated mode)
Skill path: claude-route → task-resolve → claude-write-script (inline)

## Delivered

Production modules under `scripts/optimize/`:
- `monitor_common.py` (TIER B) — paths, injectable `Clock`, `Event` dataclass
  (JSON + filesystem-safe filename), `load_state`, `as_int`, cooldown-window
  idempotency (`recent_event_exists` / `emit_once`), and the git boundary
  (`GitRunner`, `real_git`, `skill_commits_in_window` — one `git log` call,
  parses name-status per commit via an \x01 record marker).
- `monitor_repeated_question.py` (TIER B) — fingerprints question.md bodies
  (frontmatter stripped via the allow-listed `_split_frontmatter`), fires
  `repeated_question` (High) at ≥3 repeats; 14-day cooldown.
- `monitor_skill_change_reverted.py` (TIER B) — fires `skill_change_reverted`
  (High) when a skill file has ≥2 commits in 48h whose net diff vs pre-window is
  empty; 48h cooldown.
- `monitor_skill_change_first_use.py` (TIER B) — Stage 1 fires
  `skill_changed_and_used` (Low) per (skill,commit) edit; Stage 2 gated off
  (`_STAGE2_ENABLED=False`, no-op `_stage2_used_skills`, TODO → IMPL-H /
  TASK-PROC-006-13); 48h cooldown.
- `monitor_periodic_counter.py` (TIER B) — fires `periodic` (Low) when
  state.json `completions_since_last_run` ≥ `periodic_counter_threshold`;
  single-pending-event idempotency.
- `run_monitors.py` (TIER C CLI) — imports the four `run()` fns, guards each at
  the process boundary (record-and-continue), writes events, aggregates exit
  codes, `--benchmark` flag. Event JSON schema documented inline; `Output:`
  contract in docstring (G5).

Tests in `scripts/tests/` (auto-collected; zero gate-config edits):
`test_monitor_common.py`, `test_monitor_repeated_question.py`,
`test_monitor_skill_change_reverted.py`, `test_monitor_skill_change_first_use.py`,
`test_monitor_periodic_counter.py`, `test_run_monitors.py` — 28 tests, all green.
Each monitor has an idempotency test (run twice ⇒ one event); run_monitors has a
<2s benchmark test + aggregation/boundary-guard tests.

## Verification

- Python gates: G1 lint PASS, G2 type PASS, G4 no-handrolled-YAML PASS,
  G5 print-discipline PASS. G3 tests: 28 new tests pass; the single suite
  failure is the pre-existing `test_orchestrate.py::test_no_session_id_when_empty`
  — environment-dependent (asserts CLAUDE_SESSION_ID absent; this automated
  session exports it). Proven not-a-regression: passes with the var unset.
  Untouched by this task (no edits to the orchestrator).
- G-INV-2a (no tool surface): monitor names appear in `.claude/` only as
  descriptive comments in `task_ordering_priority_override.txt`, never as
  `tools:` entries in any SKILL.md / agent. PASS.
- G-INV-2b (no session JSONL): no `.ccs/`, `~/.claude/`, session-env, or
  per-account paths anywhere in `scripts/optimize/`. PASS.
- Smoke: `run_monitors.py --help` OK; `run_all(events_dir=tmp)` against the live
  repo wrote 26 events (Stage-1 first-use over recent skill commits — expected),
  zero errors, real `.factory/optimize/events/` untouched.

## Acceptance criteria

All six goal ACs met: four monitors + runner exist; no tool registration;
no session-JSONL reads; events written to `.factory/optimize/events/` with inline
schema; idempotency unit-tested per monitor; <2s on empty queue (CLI flag + test).

## Out of scope (unchanged)

IMPL-F wiring into task-complete; Stage 2 first-use (IMPL-H); the consuming
claude-optimize skill.

## Notes for downstream

- IMPL-F (TASK-PROC-006-11) invokes `python3 scripts/optimize/run_monitors.py`
  after a successful task-complete.
- IMPL-H (TASK-PROC-006-13): flip `_STAGE2_ENABLED` and implement
  `_stage2_used_skills` once the protocol `skills_used:` field exists.
- True cross-consumption cooldown currently relies on un-consumed events in
  events/ (consume-then-delete). This satisfies the AC ("run twice ⇒ one event")
  and the in-window guard; if a fired-then-consumed trigger must stay suppressed
  for the full cooldown, a persistent fire-ledger would be the follow-up.
