# Analysis scope plan (approved 2026-05-30)

Brought in-project from the (now-forbidden) native plan tool's external file, per the
CLAUDE.md rule added this session. This is the approved scope for TASK-PROC-006-20.

## Current-state findings (inputs)

**Bugs** (TASK-PROC-006-06 validation report — `../../2026-05-27_review_validate-claude-optimize-implementation (completed)/plans_and_protocols/2026-05-30_validation_report.md`):
- **F-1** — no autonomous optimize-task creation; reactive/periodic trigger paths inert.
  First implementation HELD in git stash; now treated as a design problem (Seed 2).
- **F-2** — deny-list `SKILL.md` case mismatch defeated AC-10. **Fixed & committed**
  (TASK-PROC-006-18, commit 314ba714).
- **F-3** — audit `--monitor` exit-code discrepancy (minor).
- **F-4** — IMPL-I / TASK-PROC-044 dependency gate (investigation task TASK-PROC-006-19).

**Design issues** (surfaced during 006-18):
- One-event-per-cycle consumption → queue domination with a backlog.
- Preempt-all surfacing (`type: optimize` ranks ahead of everything, incl. the override) —
  contradicts the concept's "just a regular task the orchestrator runs when the queue gives
  it" (rounds-1 synthesis ~line 237).
- Unbounded event accumulation — 247 queued (207 `skill_changed_and_used` across 34 commits
  / 96 skill paths; 40 `high_read_file`); only ~15 exact dupes → cause is "nothing consumed
  them (F-1) + wide commit-window scan", not a dedup bug. Monitor window/cooldown tuning is
  an open question.
- `skills_used:` Stage-2 trigger gap — `task-complete` step 3.4b writes `skills_used:` only
  when a `*_protocol.md` exists; other `plans_and_protocols/` filenames silently skip it,
  leaving skill-change events stuck at Stage-1 / `confidence: low`.

## Four workstreams (A first — it frames the rest)

- **A — Targets & alignment** (the crux): north-star = app quality, made actionable via
  per-stage scope-local proxy metrics that ladder up; + token-budget guardrail; +
  meta-work-subordination guardrail. Deterministic computation (G-INV-3). Decide which
  become requirement-level vs tuning constants. (goal.md Seed 1.)
- **B — Design critique & redesign** (goal.md Seed 2).
- **C — Bug reconciliation** — fold F-1/F-3/F-4 + skills_used gap + event explosion into
  the redesign; F-2 already done (goal.md Seed 3).
- **D — Efficacy & self-optimization** — controlled "optimizer runs on itself" experiment
  + token kill-switch (goal.md Seed 4).

## Task restructuring (status)

- ✅ F-2 committed standalone (314ba714); TASK-PROC-006-18 re-scoped to F-2-only & completed.
- ✅ F-1 implementation parked in `git stash` (reference artifact for the redesign).
- ✅ CLAUDE.md updated to forbid the native plan tool (commit f256867e).
- ✅ This task (TASK-PROC-006-20) created and added to the priority-override so it surfaces.
- ↪ TASK-PROC-006-19 (F-4) kept as-is — feeds Seed 3, does not block.
- ⏭ After the synthesis: if targets become normative, amend REQ-PROC-006 / REQ-PROC-059 via
  `requ-explore`, then `task-derive-from-requ` to mint the redesign tasks; then run the
  self-optimization experiment under the kill-switch.

## Decisions the developer owns (surface during the analysis, don't assume)

- The north-star target's operationalization + the weekly token-budget number(s).
- F-1 disposition — redesign vs revive-as-built (stash is the starting artifact).
- Self-run aggressiveness + the token kill-switch threshold.

## Verification bar

A synthesis matching the original redesign exploration's quality: explicit measurable
targets with sources; a redesign proposal reconciled with the bug list; a self-optimization
experiment + kill-switch; value-laden decisions framed for the developer; honest about
residual uncertainty.
