# Protocol: claude-optimize skill rewrite (IMPL-E)

Date: 2026-05-28
Session: c09e24d5-e933-4353-8fe3-1ee046df839e (web, automated)
Skill: claude-modify-skill → claude-write-script
Task: TASK-PROC-006-10

## What was done

### 1. Rewrote `.claude/skills/claude-optimize/SKILL.md` (228 LOC, under ~300 cap)

Replaced the old generic "analyze history" prompt with a deterministic
event-consumer. Steps:

1. Setup — cd to repo root, prune events older than 30 days (filename
   timestamp), list remaining events.
2. Classify + select — delegates to `scripts/optimize/select_candidate.py`
   (bugfix strictly first, then priority order). Classification table is
   mirrored in the skill body for human reference.
3. Derive `optimization_target` (from payload path) + `optimization_dimension`
   (from helper) + `optimization_approach` (SEC-03 first-match-wins heuristic
   table inline).
4. Compose objective + target_path (the only LLM judgment step).
5. Produce the task via `scripts/optimize/create_optimize_task.py`; scope text
   must declare a verification mode (AC-08 allowed modes listed in skill body).
   Exit-code handling: 0 continue, 2 deny-list → no-op, 3 invalid → escalate.
6. Consume selected event, overwrite state.json, append runs.tsv.
7. Commit via claude-commit (`chore(optimize): run <id> <outcome> <dim>`).

Plus standing sections: "Allowed verification modes" (AC-08), "Guardrails"
(G-INV-1/2/3, AC-01, AC-07), "When to run".

### 2. Added `scripts/optimize/select_candidate.py` (tier B)

Pure-Python selector so AC-07 ("bugfix always selected") is covered by a
fixture-driven test rather than relying on LLM adherence. Provides:
- `load_events()` — reads + tolerates malformed event files
- `classify(event) -> (klass, dimension)` — the SEC-01/SEC-02 table
- `select_candidate(events)` — bugfix-first + intra-class priority sort
- CLI emitting a JSON contract consumed by SKILL.md Step 2

### 3. Added `scripts/tests/test_select_candidate.py` (14 tests, all pass)

Fixture-driven; synthesizes events on tmp_path. Covers: bugfix-first over a
higher-priority optimization, intra-class priority, optimization fallback,
empty queue, the full classification parametrize table, corrupt-file
robustness, and the CLI JSON shape (candidate + no-op).

### 4. Synced registries

- `.claude/skills/INDEX.md` — updated quick-ref + category descriptions.
- `.claude/factory_flows.md` — updated the diagram edge label and the feedback-
  loop bullet (event-driven, one auto-blocked task per run).

## AC coverage

| AC | Where satisfied |
|---|---|
| AC-01 (≤1 task/run, no-op commits) | SKILL.md Steps 5–7 |
| AC-07 (bugfix strictly first) | `select_candidate.py` + 4 selection tests |
| AC-08 (verification mode, no sole-LLM) | SKILL.md "Allowed verification modes" + Step 5 scope clause |
| AC-09 (every run commits runs.tsv+state.json) | SKILL.md Steps 6–7 |
| SEC-02 two-field taxonomy | SKILL.md Step 3 + create_optimize_task.py choices |
| SEC-03 optimization_approach | SKILL.md Step 3 heuristic table |
| Soft LOC cap | 228 LOC |

## Quality gates

- New selector tests: 14 passed.
- Python gates G1 (ruff), G2 (mypy), G4 (no-handrolled-yaml), G5 (print) PASS.
- G3: one failure — `test_orchestrate.py::TestBuildEnv::test_no_session_id_when_empty`.
  Pre-existing, environment-sensitive (the test asserts `CLAUDE_SESSION_ID`
  absent from `build_env` output, but the automated session sets it in the real
  env). In `scripts/automation/`, untouched by this task. NOT a regression —
  confirmed it fails the same way independent of this change.

## Out of scope (untouched, per goal.md)

Monitors (IMPL-C), create_optimize_task.py internals (IMPL-D), task-complete
wiring (IMPL-F), audit skill (IMPL-G).
