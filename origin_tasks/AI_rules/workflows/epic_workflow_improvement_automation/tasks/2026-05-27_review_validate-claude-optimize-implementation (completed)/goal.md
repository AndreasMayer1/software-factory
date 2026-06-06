---
task_id: TASK-PROC-006-06
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
created: 2026-05-27
started: 2026-05-30
completed: 2026-05-30
after: [TASK-PROC-006-04, TASK-PROC-006-05, TASK-PROC-006-07, TASK-PROC-006-08, TASK-PROC-006-09, TASK-PROC-006-10, TASK-PROC-006-11, TASK-PROC-006-12, TASK-PROC-006-13, TASK-PROC-006-14, TASK-PROC-006-15, TASK-PROC-059-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Validate the fully-implemented claude-optimize system against the rounds 1-4 concept. Every item in the checklist below must be ticked or explicitly waived with a recorded reason."
release_description: ""
opus_recommended: true   # reason: holistic correctness review against a large multi-component design with subtle guardrails
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Validate the claude-optimize Implementation Against the Concept

## Objective

After **all** claude-optimize implementation tasks (created by TASK-PROC-006-04 and
TASK-PROC-006-05) are complete, validate the delivered system against the decided
concept. This is the final gate. Every checklist item below must be **ticked** (with
evidence: a file path, a command output, a git ref) or **explicitly waived** with a
one-line recorded reason in `plans_and_protocols/`.

**This task must run last.** Its `after:` list is seeded with the two derive tasks
and is extended by them with the concrete impl task IDs they create.

## MANDATORY READING — the concept (read before validating)

`requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-01_explore_redesign-claude-optimize-skill/plans_and_protocols/`

- `2026-05-16_08_opus_synthesis_round4.md` — consolidated final design
- `2026-05-16_05_opus_synthesis_round3.md` — detailed architecture
- `2026-05-16_07_decisions_applied.md` — user decisions

You cannot validate what you do not understand — read the whole concept first.

## Validation Checklist

### A. Architecture & identity
- [ ] A1. `claude-optimize` produces exactly **one** improvement task per run (or a no-op) — never a multi-finding report
- [ ] A2. The skill never applies changes itself; it only creates tasks
- [ ] A3. The three trigger paths exist and route to the same skill body: periodic (post-`task-complete`), reactive (monitors), explicit (user invocation)
- [ ] A4. Routine operation reads ≤ ~30 KB of file content; no session JSONL read in the hot path

### B. State location & memory (R1, N-D-1)
- [ ] B1. All persistent state lives under `.factory/optimize/` (NOT `automation/optimize/`, NOT OS memory)
- [ ] B2. `.factory/optimize/` contains: `state.json`, `events/`, `history/runs.tsv`, `history/audit_history.tsv`, `history/web_searches.tsv`, `reports/`, `README.md`
- [ ] B3. No code path reads or writes the per-account OS memory for optimize state
- [ ] B4. `events/` entries are consumed-then-deleted; 30-day prune exists

### C. Detection / monitors (R2, R5, §2.2)
- [ ] C1. Monitors are plain scripts under `scripts/optimize/`, invoked by `task-complete` — NOT tools an agent can call (G-INV-2)
- [ ] C2. The "2+ blocked tasks >7 days" trigger does **not** exist (R2 — removed)
- [ ] C3. Repeated-question monitor fires at S9 count ≥ 3 and is idempotent within its window
- [ ] C4. Skill-change monitor ships Stage 1 (fires on commit); Stage-2 first-use gate is gated behind the `skills_used:` instrumentation task (IMPL-H)
- [ ] C5. Skill-reversion-within-48h monitor exists
- [ ] C6. Periodic safety-net monitor fires every N completions; N defaults to 10 and is configurable in `state.json`

### D. Producer behavior
- [ ] D1. **Strict bugfix-first** (R4): if any bugfix candidate exists it is chosen; no fairness/starvation carve-out
- [ ] D2. Every produced task carries `optimization_target` + `optimization_dimension`
- [ ] D3. Every produced task declares a verifiable acceptance criterion (ground-truth or structural rubric; never single-LLM judgment)
- [ ] D4. Saturation exits cleanly with a `runs.tsv` line and **no** memory entry (R6)
- [ ] D5. Every run commits (even no-ops) — verify via git history of `.factory/optimize/`

### E. Auto-block & guardrails (R3, Part 3)
- [ ] E1. Every produced task is born `awaiting: ["user-unblock"]` — verify the create script default
- [ ] E2. **G-INV-1** (auto-block) is documented as a non-removable invariant in REQ-PROC-006
- [ ] E3. **G-INV-2** (detection outside agent tool surface) holds in the implementation
- [ ] E4. **G-INV-3** (audit skill separate from producer skill) holds
- [ ] E5. Write-surface deny-list enforced at task-create time (defense-in-depth); includes CLAUDE.md, the optimize skill itself, claude-modify-skill, task-complete, scripts/automation/tests/, factory_flows.md, INDEX.md

### F. Web research (N-D-4)
- [ ] F1. Produced tasks carry an `optimization_approach` block with `web_research_recommended` per the round-3 §2.3 heuristics
- [ ] F2. Performed web searches are logged to `.factory/optimize/history/web_searches.tsv` (IMPL-J)

### G. Audit skill (N-D-2, N-D-8, N-D-9)
- [ ] G1. A separate skill named `claude-optimize-audit` exists
- [ ] G2. It computes a deterministic rubric score + delta vs. previous run, persisted to `audit_history.tsv`
- [ ] G3. It computes BOTH metrics: user-unblock-rate (primary) and revert-rate (secondary)
- [ ] G4. It supports targeted `--monitor=<name>` sub-audits
- [ ] G5. Its report is committed to `.factory/optimize/reports/<date>_audit.md` (N-D-6)
- [ ] G6. If a DB layer was added (IMPL-M), it is optional/query-time DuckDB, `runs.tsv` stays canonical, and the audit degrades gracefully when duckdb is absent

### H. Triggering & integration
- [ ] H1. `run_monitors.py` is invoked at the tail of `task-complete` (no OS/VSCode/git hook dependency)
- [ ] H2. The optimize task created by the monitors runs autonomously (its own `awaiting:` is empty); only its downstream proposals are auto-blocked
- [ ] H3. A blocked follow-up (IMPL-I) exists to consume TASK-PROC-044 observability, `after:` that task

### I. Principles requirement (round-4 Part 5)
- [ ] I1. The cross-factory LLM-work-principles requirement exists and lists principles a–h
- [ ] I2. Principle (c) carries the irreversibility threshold
- [ ] I3. Its scope stayed tight (no factory-wide rewrite crept in)

### J. Process hygiene
- [ ] J1. All requirements pass the requirements lint/coverage scripts
- [ ] J2. Python gates pass for any new scripts (`scripts/quality/check_python_gates.sh`)
- [ ] J3. Every impl task that was created references the concept docs
- [ ] J4. No settled decision from rounds 1–4 was silently reversed during implementation

## Output

A validation report in `plans_and_protocols/[date]_validation_report.md` with each
checklist item marked ✅ (with evidence) / ⚠️ waived (with reason) / ❌ failed. Any
❌ becomes a new bugfix/impl task before this review can be marked complete.

## Acceptance Criteria

- [x] Every checklist item A1–J4 is ticked or explicitly waived with a recorded reason
- [x] A validation report exists with evidence per item
- [x] Any failures are converted into follow-up tasks (added to the override file)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-006-04 | pending | Derives + this task's `after:` is extended with its impl tasks |
| TASK-PROC-006-05 | pending | Derives + this task's `after:` is extended with its impl tasks |
| (impl tasks) | pending | Appended to `after:` by the derive tasks |
