---
id: REQ-PROC-069
status: active
created: 2026-06-05
urgency: 3
impact: 4
effort: M
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-04
    - id: AC-05
    - id: AC-06
---

# Task Execution Entry Point

## Overview

A single canonical skill — `task-start` — is the entry point for *executing* an already-created task. It runs
universal pre-flight (reference resolution, pre-condition gating, marking the task `in_progress`), then delegates
type-detection and execution-skill dispatch to a distinct routing component (`claude-route`). "Both, separated":
`task-start` owns pre-flight + entry; `claude-route` owns routing.

## Purpose

Today the entry point is `claude-route`, invoked directly by CLAUDE.md §4 on "Do <task>". Two problems motivate a
dedicated wrapper:

1. **Scattered, uneven pre-conditions.** The only enforced entry guard (a goal.md exists + validates against the
   goal-metadata schema, REQ-PROC-044) is copy-pasted into 9 execution skills and absent from others
   (`task-resolve`, `requ-explore`). Three further guards that *should* stop a task from starting —
   it is already completed, it is awaiting a developer answer, or its `after:` dependencies are unfinished — are
   enforced only during task *selection* (`next_tasks.py` / the next-task flow), so a direct "Do <TASK-ID>"
   bypasses them entirely.
2. **No single, clean entry seam.** `claude-route` already performs pre-flight work (frontmatter validation,
   `in_progress` marking, session-identity recording in automated mode) tangled together with routing, making the
   entry point's contract implicit and the automated-mode ordering fragile.

The trigger is the TASK-PROC-032-29 scribble-workflow redesign (Round-2 resolved "task-start wraps claude-route,
both separated"; D-3 deferred it to its own task). It matters now because the redesigned release pipeline adds new
pre-conditions (currency invariants, dependency edges) whose enforcement needs one well-defined execution entry.

## Behavior

The entry point accepts a task reference in any documented form (a `goal.md` path, a task ID, the "next task"
selector, or a free-text description) and resolves it to a concrete `goal.md`. It then enforces the pre-conditions
in `## Developer Guidelines`. When all pass, it marks the task `in_progress` (and, in automated sessions, records
the session identity) and hands the validated, in-progress `goal.md` path to the routing component, which performs
type-detection and invokes the matching execution skill.

When a pre-condition fails, the entry point does not route: in interactive sessions it surfaces the reason (and,
for soft gates, asks the developer whether to override); in automated sessions it skips the task or escalates to a
pending-feedback question. The same entry point governs both interactive and automated execution — automated
sessions reach an execution skill through it via the "next task" flow, not through a separate path.

## Examples

**Example 1: direct execution of a named task**
- A developer says "Do TASK-PROC-069-01". The entry point resolves the ID to its `goal.md`, validates the schema,
  confirms the task is not completed / not awaiting an answer / dependencies satisfied, marks it `in_progress`, and
  routes to the matching workflow skill.

**Example 2: pre-flight ↔ routing seam**
- Pre-flight (resolve, validate, gate, mark in_progress): owned by `task-start`.
- Routing (match `type` + content → skill, opus-check, invoke): owned by `claude-route`.
- Existing entry-guard precedent being consolidated: the REQ-PROC-044 pre-check block at the head of
  `code-simple` / `code-complex` / `code-test` (`.claude/skills/<skill>/SKILL.md`).

## Acceptance Criteria

- [ ] **AC-01** — A single skill is the documented entry point for executing any already-created task; interactive
  and automated sessions reach an execution skill through this same entry point.
- [ ] **AC-02** — Before any execution skill runs for a task, the task's `goal.md` has been confirmed present and
  valid against the goal-metadata schema, the task is not already completed, the task is not awaiting a developer
  answer, and the task's declared `after:` dependencies are completed.
- [ ] **AC-03** — Pre-flight (reference resolution, pre-condition gating, marking the task `in_progress`) and
  routing (type-detection and execution-skill dispatch) are owned by two distinct components, with exactly one
  component owning routing.
- [ ] **AC-04** — In automated sessions, the task is marked `in_progress` and the session identity is recorded
  before any pending-feedback question is written for that task.
- [ ] **AC-05** — Each execution skill requiring a task `goal.md` fails loudly when invoked with a missing or
  off-schema `goal.md`, independent of whether it was reached through the canonical entry point.
- [ ] **AC-06** — No automated execution path reaches an execution skill without passing through the canonical
  entry point's pre-condition gating.

## Developer Guidelines

> Constraints/invariants of the finished system. Concrete HOW (phase scripts, exact wording) belongs in the
> follow-on impl task plan; the design synthesis is at
> `tasks/2026-06-05_explore_task-start-wrapper/plans_and_protocols/2026-06-05_01_synthesis_task-start-design.md`.

### Key Decisions
- **Clean seam (B1).** Pre-flight is owned solely by the entry point; routing is owned solely by the routing
  component. The pre-flight steps that historically lived in the router (frontmatter validation, `in_progress`
  marking, session-identity recording) reside in the entry point, not duplicated across both. Exactly one component
  owns type-detection and dispatch.
- **Verify context, do not pass it down.** The entry point confirms `goal.md` is present and schema-valid and parses
  its frontmatter for gating only. It does not read `protocol.md` or pass parsed goal/protocol content downstream —
  each execution skill and its agents read `goal.md` + latest `protocol.md` themselves (file-based-memory rule).
- **Automated-mode ordering is load-bearing.** In automated sessions the entry point marks the task `in_progress`
  and records the session identity *before* any pending-feedback question can be written for that task.
- **Defense-in-depth retained.** Each execution skill that requires a task `goal.md` still fails loudly on a
  missing or off-schema `goal.md` when invoked directly, independent of the canonical entry point.
- **Pre-condition gates and their failure mode:** schema-valid `goal.md` → hard-block; `status` not `completed` →
  warn-and-confirm (interactive) / skip (automated); not awaiting a developer answer → hard-block / skip;
  `after:` dependencies completed → warn-and-confirm (interactive) / skip (automated).
- **Out of scope:** the `.git/index.lock` staleness check is a commit-time concern owned by task-complete and the
  CLAUDE.md retry protocol — a task starts long before it commits, so the entry point does not gate on it. The
  entry point governs *starting/executing* an already-created task, not *creating* one (the orchestration creation
  chain is unchanged).

### Common Pitfalls
- An automated execution path that reaches an execution skill without passing through the entry point's gating —
  the gates would silently not apply on that path.
- Treating the wrapper as purely additive (router unchanged): both components would then touch frontmatter and
  double-write `started:` / session identity, risking an overwrite of an earlier value.
- Hard-blocking a soft gate (e.g. unfinished `after:` deps) on a *direct* task pick, which is sometimes a
  deliberate developer override.

## Related Requirements
- REQ-PROC-044 (skill input/output contracts) — the entry guard being consolidated originates here.
- REQ-PROC-035 (release preparation / orchestration chain) — the automated "next task" flow and pending-feedback
  escalation that the entry point must preserve.
- REQ-PROC-032 (scribble workflow redesign) — origin of the "both, separated" decision (TASK-PROC-032-29 §8/§9 D-3).
- REQ-PROC-058 (unified task-creation plan format) — distinguishes task *creation* (out of scope here) from task
  *execution* (this requirement).

## References
- `.claude/skills/claude-route/SKILL.md` — current entry point (Modes A/B/C) to be split.
- `.claude/skills/claude-automated-mode/SKILL.md` — the in_progress + session_id pre-condition for pending_feedback.
- `scripts/tasks/create_orchestration_task.py` — the creation chain (distinct from execution entry).
- CLAUDE.md §4 "Default Workflow" — the normative entry-point instruction to be re-pointed.
