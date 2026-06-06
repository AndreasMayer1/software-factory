# Opus Plan v3: Distributed Architecture with Quality Gates

**Supersedes** `2026-04-25_02_opus_plan_distributed_architecture.md`. v2 solved
the distribution problem; v3 adds the quality gates needed to ensure
"good requirements → good implementation" survives the multi-session split.

## Objective

Build a release implementation pipeline that:

1. **Distributes task creation across many sessions** (no monolithic context).
2. **Works fully manually** — no autorun dependency, no hidden bootstrap magic.
3. **Preserves holistic understanding** that the old single-session approach
   provided — even though work is split across sessions.
4. **Enforces quality gates** at every transition: requirements → impl tasks →
   code. The chain must not silently degrade.

---

## Direct Answers to the Three Questions

### Q1 — Manual operation without autorun

**Answer**: Yes — and it must be the default mental model. Autorun is just a
loop runner; the chain itself must be self-contained.

**Mechanism**: Each orchestration task's `goal.md` ends with explicit, ordered
steps:

```markdown
## Acceptance Criteria
- [ ] Step 1: Run `task-create-code` zero-parameter (creates one impl task)
- [ ] Step 2: Run `python3 scripts/create_orchestration_task.py`
        (creates next orchestration task OR finalization task)
- [ ] Step 3: Run `task-complete` on this orchestration task
```

In manual mode the user runs `Do TASK-XXX` (or `claude-route TASK-XXX/goal.md`)
once per package; the chain fires by itself because each task creates the next.

In automated mode, autorun runs the same task. **There is no autorun-only
codepath.**

**Bootstrap rule cleanup**: `claude-automated-mode` Case A currently has its
own inline `task-create` logic that duplicates `create_orchestration_task.py`.
After this change, **remove Case A entirely** — the chain is self-perpetuating,
no bootstrap needed. Cases B and C stay (they handle validation + completion
that no per-task script can produce on its own).

---

### Q2 — What information do we lose by distributing?

The old monolithic Phase 3 (5 feature agents in parallel, each reading full
requirements.md) had **emergent insight from cross-feature visibility**.
Per-package one-shot creation loses:

| Information | Why it matters | Loss severity |
|-------------|----------------|---------------|
| Cross-package `after:` chains | Layer ordering: data must precede UI | **High** |
| Holistic AC grouping decisions | "AC-01..05 belong in one task; AC-06 is its own" | **High** |
| Common pattern detection | Shared abstractions across features | Medium |
| Naming consistency | Tasks should use coherent vocabulary | Medium |
| Test strategy | Which features need integration vs unit | Medium |
| Architectural smell detection | "These 3 ACs imply a missing repository" | **High** |
| Effort distribution sanity | "10 XS tasks vs 1 XL — is split right?" | Medium |

**Solution: Task Creation Plan (NEW, single session, before activation)**

After Phase 2 (epic agents confirm scope) and before activation (Phase 6),
spawn ONE agent — the **Task Creation Planner** — that:

1. Reads ALL in-scope feature `requirements.md` files (one Read per file).
2. Reads `RELEASE_BACKLOG.md` and `RELEASES.md`.
3. Produces `[task_path]/task_creation_plan.md`:
   - Ordered list of planned impl tasks
   - Each entry: `name`, `target_package`, `covers.acceptance_criteria`,
     `effort` estimate, `layer` (data/domain/presentation/integration),
     suggested `after:` (cross-package), `opus_recommended` flag, rationale
   - Architectural notes (shared abstractions, common patterns)
   - Test strategy notes (which tasks need unit vs widget vs integration)

This plan becomes the **single source of holistic understanding**. It's small
(say 200 lines for a 30-task release), persists, and is consulted by every
subsequent per-package session.

The plan IS the holistic view, written down once when the context is rich
enough to produce it — then re-used cheaply.

**User reviews and approves the plan** before activation. This is the
high-value user gate: the user sees the whole release as a coherent piece
before any code task gets a folder.

---

### Q3 — Other problems I see + quality gates

I've identified 8 quality risks beyond the three you raised. Each gets an
explicit gate.

#### Risk 1 — Scope creep / drift during task creation

`task-create-code` could (a) include ACs not in scope, (b) drop ACs that are
in scope, (c) misclassify the layer. No current check catches this.

**Gate: Plan Conformance Check** (added to `task-create-code` Phase 4).
After writing goal.md, the skill verifies:
- Task name matches the planned name (or user explicitly chose to deviate)
- `covers.acceptance_criteria` matches the plan entry
- `target_package` matches
- `effort` is within ±1 size of the planned estimate (XS↔S, S↔M, etc.)

Mismatch → flag for user review (interactive) or write `question.md`
(automated). Never silent.

#### Risk 2 — Holistic test strategy missing

If each task creates its own tests in isolation, integration tests for
cross-feature flows (e.g., FLOW-002 spanning 4 features) may never be
written.

**Gate: Test Strategy in Task Creation Plan**. The Planner agent (above)
explicitly lists:
- Integration test tasks needed (separate impl tasks, type=impl, scope=test)
- Which flows each integration test covers
- These appear as their own entries in the plan and become their own
  `task-create-code` runs.

#### Risk 3 — Architectural drift / unnoticed pattern divergence

Three features each invent slightly different repository patterns because
no agent ever sees all three side by side.

**Gate: Pre-Activation Architecture Review** (added to Task Creation Planner).
The Planner flags:
- ACs across features that look like they should share an abstraction
- Feature requirements that contradict each other (silently)
- Layer assignments that look wrong (UI logic implied by an AC labelled
  data-layer)

These flags appear in `task_creation_plan.md` as a `## Architecture Notes`
section that the user reviews.

#### Risk 4 — Cross-task `after:` chain incompleteness

`propose_after.py` works per-task. It can miss chains when two tasks created
in different sessions both depend on a third that hasn't been created yet.

**Gate: Final After-Chain Reconciliation** (added to `release-finalize`).
After all tasks are created, run a single agent that:
- Reads all created `goal.md` files for the release
- Verifies each task's `after:` chain is consistent with the plan's order
- Flags missing dependencies
- For confirmed misses, the agent updates `after:` directly (it's a
  metadata-only edit; safe).

#### Risk 5 — Failure recovery is opaque

Mid-release, a task creation session fails. State is partially complete.
The user has no clear "where am I?" view.

**Gate: Release State View** (extend `release-status` skill).
Add a per-package status table to `release_readiness.py` output:
- `[✓] PKG-A: 1 impl task (TASK-FUNC-007-12)`
- `[ ] PKG-B: planned in task creation plan, not yet created`
- `[!] PKG-C: orchestration task in progress (TASK-PROC-035-09)`

`release-status` becomes the single source of truth for "what's done, what's
next, what's stuck".

#### Risk 6 — Requirements mutate between scope-phase and creation-phase

A user edits a feature's requirements.md after Phase 2 but before
`task-create-code` runs for that feature. The created task may not match
what was reviewed.

**Gate: Requirements Snapshot in Plan**. The plan stores a `req_commit` per
feature. Each `task-create-code` session verifies the current file matches
that commit; if not, it stops and writes a `requirements_drifted_question.md`.

This was already partially in place (`requirements_version.commit` in
goal.md), but the plan never had a counterpart.

#### Risk 7 — Validation in Case B is structural-only

Case B in `claude-automated-mode` checks AC coverage, after-chains, opus
flags. These are structural. It doesn't ask: "does the goal.md actually
describe an implementation that addresses the AC's intent?"

**Gate: Semantic Validation Pass** (added to Case B's validation task).
The validation task spawns 1 agent per feature that:
- Reads each created goal.md for that feature
- Reads the corresponding ACs from requirements.md
- Verifies the goal.md's "Goal" + "Scope Overview" sections actually
  describe what the AC asks for (no missing scope, no extra scope, no
  misinterpretation)
- Flags semantic mismatches in the validation report

This is the gate that catches "tasks that look right structurally but
actually don't implement what was asked".

#### Risk 8 — `next_tasks.py` may have the same target_package bug we just fixed

We fixed `generate_status_overview.py` to resolve `target_package` →
release. `next_tasks.py` is used by `task-create-code` zero-parameter mode
and by Case A. If it has the same bug, the entire distributed flow breaks.

**Gate: Verify `next_tasks.py` package→release resolution**. Part of
implementation: read `next_tasks.py`, confirm it resolves correctly, fix
if needed.

---

## Revised Architecture (v3)

```
USER SESSION 1 — release-begin-impl (interactive, scope phase)
┌──────────────────────────────────────────────────────────────────┐
│ Phase 0: Bootstrap                                                │
│ Phase 1: Package coverage check (1 agent)                        │
│ Phase 2: Epic requirements check (N agents, 1 per epic)          │
│ Phase 2b: Remediation                                             │
│ Phase 2c: TASK CREATION PLANNER (1 agent — NEW)  ◄── KEY ADDITION │
│   Reads all in-scope feature requirements.md                     │
│   Produces task_creation_plan.md                                  │
│   Includes architecture notes + test strategy                    │
│ Phase 5: USER GATE (review + approve task_creation_plan.md)      │
│ Phase 6: Activate RELEASES.md + create first orchestration task  │
│   Print: "Run /autorun OR run `Do TASK-XXX` manually."           │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼  (manual: user runs `Do TASK-XXX`)
                          ▼  (automated: autorun)
SESSIONS 2..N+1 — orchestration tasks (one per package)
┌──────────────────────────────────────────────────────────────────┐
│ Run task-create-code zero-parameter                              │
│   - Reads task_creation_plan.md to get planned name/scope         │
│   - Reads ONE feature's requirements.md (its own context)        │
│   - Verifies requirements_version.commit matches plan            │
│   - Writes goal.md                                                │
│   - PLAN CONFORMANCE CHECK (NEW — see Risk 1)                    │
│ Run create_orchestration_task.py                                 │
│   - More packages remain → creates next orchestration task       │
│   - All packages covered → creates FINALIZATION task             │
│ Run task-complete on this orchestration task                     │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼ (last orchestration task chains to:)
SESSION N+2 — finalization (manual or autorun)
┌──────────────────────────────────────────────────────────────────┐
│ Run /release-finalize                                             │
│ Phase 1: Re-run gap verification                                 │
│ Phase 2: AFTER-CHAIN RECONCILIATION (NEW — see Risk 4)           │
│ Phase 3: SEMANTIC VALIDATION (1 agent per feature — NEW Risk 7)  │
│ Phase 4: USER GATE — present consolidated report                 │
│ Phase 5: Finalize RELEASES.md (status / dates)                   │
└──────────────────────────────────────────────────────────────────┘
```

Two user gates total: scope+plan approval (session 1), final review
(session N+2). Everything in between is mechanical and traceable.

---

## What Each File / Skill Does

### `.claude/skills/release-begin-impl/SKILL.md` (substantial rewrite)

**Phases retained**: 0, 1, 2, 2b.
**Phase 2c — NEW**: Task Creation Planner (see above).
**Phase 5 — REPURPOSED**: Single user gate showing scope findings + the task
creation plan. User approves (or asks for plan revisions).
**Phase 6 — REPURPOSED**: Activate release in RELEASES.md, then call
`create_orchestration_task.py`. Print clear handoff message describing both
manual and automated paths.
**Phases 3, 4 — REMOVED**: That work is now distributed across orchestration
sessions (Phase 3) and the finalize skill (Phase 4).

The file should also document explicitly: "This skill never reads a feature's
requirements.md in the orchestrator. Only Phase 2 epic agents and the Phase 2c
planner do."

### `scripts/create_orchestration_task.py` (moderate change)

**Behavior changes**:
- Exit 3 (all packages covered) → instead, create a finalization
  orchestration task with goal "Run `/release-finalize`". Exit 0.
- Goal template for impl-creation orchestration tasks: explicit 3-step
  acceptance criteria (run task-create-code, run create_orchestration_task,
  run task-complete) — making it self-perpetuating in manual mode.
- Add a new `--finalization-only` flag (used by `release-finalize` to
  re-trigger if needed during recovery).

**No change**: The script is still the single source for orchestration task
templates.

### `scripts/next_tasks.py` (verify, fix if needed)

Verify package→release resolution works the same way as the fix applied to
`generate_status_overview.py`. If not, apply equivalent fix. Report explicitly
what was found.

### `.claude/skills/task-create-code/SKILL.md` (small additions)

**Phase 0 (zero-parameter mode)**: Add a step that reads
`task_creation_plan.md` from the active release task folder if it exists,
and uses the planned entry for the picked package as authoritative scope.

**Phase 4 (Verify & Commit)**: Add the **Plan Conformance Check** (Risk 1) —
compare written goal.md against the plan entry, surface mismatches before
commit.

**Bottom of skill**: Document that Plan Conformance is mandatory when a
plan exists; tasks created without a plan (e.g., off-cycle additions) skip
this step.

### `.claude/skills/release-finalize/SKILL.md` (NEW)

Phases:
1. **Coverage verification** — re-run status overview, confirm all in-scope
   packages have impl tasks.
2. **After-chain reconciliation** — single agent reads all created goal.md
   files and fixes missing `after:` entries based on the plan's expected
   order.
3. **Semantic validation** — N agents (one per feature) verify each goal.md
   semantically matches its ACs.
4. **User review** — orchestrator presents consolidated report:
   coverage / gaps / chain issues / semantic issues / overall verdict.
5. **Finalization** — on user approval: update RELEASES.md (e.g., add
   `tasks_complete_date`), regenerate STATUS.md, commit.

This skill never reads a feature's requirements.md directly — only via
agents.

### `.claude/skills/release-status/SKILL.md` (small extension)

Add the per-package status table (Risk 5). The script
`release_readiness.py` already handles staging — extend it to include
per-package state pulled from `task_creation_plan.md` + status overview.

### `.claude/skills/claude-automated-mode/SKILL.md` (cleanup)

- **Remove Case A entirely** — task chain self-perpetuates now.
- **Keep Case B** but extend the validation task to include semantic
  validation (Risk 7).
- **Keep Case C** — completion summary, point to `/release-finalize`.

---

## Specific Anti-Quality-Loss Mechanisms

To make sure "good requirements → good code" doesn't break:

1. **Plan as durable holistic view** (Q2 mitigation). Written once, read many.
2. **Plan Conformance Check** at task creation. Drift is loud, not silent.
3. **After-chain reconciliation** at finalize. Cross-task dependencies caught.
4. **Semantic validation** at finalize. "Does the task implement the AC?"
   not just "does the task reference the AC?"
5. **Requirements snapshot** in plan and goal.md. If the source moved,
   we know.
6. **Two user gates total** — scope+plan, and final review. Each gate is
   high-information-density. Avoid the death-by-a-thousand-prompts pattern.
7. **No silent escalation skipping** — agents that hit ambiguity write
   `question.md`; orchestrator surfaces them; user answers.
8. **Self-perpetuating chain** — manual mode is first-class, no hidden
   automation.

---

## Execution Plan

### Order of operations (must be sequential between phases, parallel within)

#### Phase A — Investigate (sequential, blocks B)
1. **Single agent**: read `next_tasks.py`, confirm package→release resolution
   works correctly for `target_package`-only requirements. If broken, write
   exact diff. (Output: `next_tasks_findings.md`.)

#### Phase B — Implement scripts and core skills (parallel, 3 agents)

**Agent B1 — `next_tasks.py` fix** (skip if Phase A found no bug)
- Apply the diff from Phase A.
- Run `python3 scripts/next_tasks.py` to verify.

**Agent B2 — `create_orchestration_task.py` enhancements**
- Replace Exit 3 branch with finalization-task creation.
- Update impl-creation goal template to include the 3-step self-perpetuating
  acceptance criteria.
- Add `--finalization-only` flag.
- Run existing tests; add tests for the new branch.

**Agent B3 — `release-begin-impl` rewrite**
- Apply Edits 1, 2, 3 from plan v1
  (`2026-04-25_01_opus_plan_skill_improvements.md`) — keep what's still
  applicable (Decision Domains, Phase 1 package-aware, Phase 2b inline
  trivial edits).
- Remove old Phase 3, 4, 5 entirely.
- Add new Phase 2c (Task Creation Planner) — full prompt for the planner
  agent embedded in the skill.
- Repurpose Phase 5 as the single user gate for scope + plan approval.
- Repurpose Phase 6 with the new handoff message and self-perpetuating
  semantics.

#### Phase C — Implement skills that consume the plan (parallel, 2 agents, after B)

**Agent C1 — `task-create-code` updates**
- Phase 0 reads `task_creation_plan.md` if present.
- Phase 4 adds Plan Conformance Check.

**Agent C2 — Create new `release-finalize` skill**
- Author full SKILL.md for the new skill at
  `.claude/skills/release-finalize/SKILL.md`.
- Implement the four phases described above.

#### Phase D — Cleanup (parallel, 2 agents, after C)

**Agent D1 — `claude-automated-mode` cleanup**
- Remove Case A.
- Extend Case B validation task with semantic validation step.
- Update Case C to point to `/release-finalize`.

**Agent D2 — `release-status` extension**
- Extend `release_readiness.py` with per-package status table.
- Update SKILL.md if needed.

#### Phase E — Verification (orchestrator, inline)
- Run `python3 scripts/release_readiness.py` — verify still works.
- Read each modified SKILL.md — verify the documented changes are present.
- Run `release-status` — verify the new per-package table.
- Commit everything via `claude-commit`.

---

## Quality Criteria

- [ ] `release-begin-impl` produces a `task_creation_plan.md` and gates
      activation behind user approval of that plan.
- [ ] `task_creation_plan.md` includes architecture notes, test strategy,
      and per-task `effort`/`layer`/`opus_recommended`.
- [ ] Each orchestration task's goal.md has 3-step self-perpetuating
      acceptance criteria; works identically in manual and automated mode.
- [ ] `create_orchestration_task.py` creates a finalization task instead
      of returning Exit 3.
- [ ] `task-create-code` Phase 4 surfaces plan-conformance mismatches
      before commit.
- [ ] `release-finalize` includes after-chain reconciliation AND semantic
      validation phases.
- [ ] `claude-automated-mode` Case A is removed; chain self-perpetuates.
- [ ] `release-status` shows per-package state in its output.
- [ ] `next_tasks.py` correctly resolves `target_package` → release.
- [ ] Two user gates only (scope+plan; final review). No redundant gates.
- [ ] No skill in the chain reads a feature's `requirements.md` in the
      orchestrator's main context.

## Risks and Mitigations

- **Risk: The Task Creation Planner agent runs out of context for very
  large releases (e.g., 30 features).** Mitigation: if the in-scope
  feature count exceeds a threshold (say 10), the planner spawns sub-agents
  per feature subset and aggregates outputs. Alternatively, the plan is
  built incrementally over multiple iterations of the skill.

- **Risk: The plan becomes stale if requirements are edited after
  approval.** Mitigation: each task creation session verifies the
  feature's current commit against the plan's snapshot. On mismatch, the
  session stops and writes `question.md`.

- **Risk: Plan Conformance Check is too strict and blocks legitimate
  judgment calls.** Mitigation: mismatches are flagged, not blocked. User
  decides. In automated mode, ±1 effort size is auto-accepted; everything
  else writes `question.md`.

- **Risk: Removing Case A from `claude-automated-mode` breaks existing
  in-flight orchestration chains.** Mitigation: implement in this order:
  (1) update orchestration task template to be self-perpetuating, (2) wait
  for any in-flight orchestration tasks to drain, (3) only then remove
  Case A. Keep both code paths working for one transition cycle.

- **Risk: Semantic validation is fuzzy and produces false positives.**
  Mitigation: the validation agent is instructed to flag only
  high-confidence mismatches (e.g., "AC says A but goal.md says B"). Low-
  confidence findings are noted but not blocking.

- **Risk: User approves the plan but reality reveals issues mid-release
  (e.g., a feature turns out harder than estimated).** Mitigation: the
  flow allows re-running `release-begin-impl` to revise the plan; mid-flight
  amendments append a `task_creation_plan_v2.md` and the in-flight
  orchestration tasks check for the latest version on each session.

- **Risk: The Planner produces a poor plan.** Mitigation: the user gate
  shows the full plan; user can request revisions before activation. The
  Planner prompt should explicitly require: explicit AC mapping per task,
  explicit layer assignment, explicit dependency rationale.

---

## Summary for the Calling Skill

**Path**: `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-24_explore_release-active-status-analysis/plans_and_protocols/2026-04-25_03_opus_plan_distributed_with_quality_gates.md`

**Execution agents**: 7 agents across 5 phases (1 investigation, 3 core
implementation, 2 consumer-side, then cleanup of automated mode + status
extension). Plus the orchestrator's verification step at the end.

**Critical addition over plan v2**: the Task Creation Planner (Phase 2c)
and the four quality gates (Plan Conformance, After-Chain Reconciliation,
Semantic Validation, Requirements Snapshot). These together ensure the
distributed model preserves the holistic understanding the monolithic
model had.
