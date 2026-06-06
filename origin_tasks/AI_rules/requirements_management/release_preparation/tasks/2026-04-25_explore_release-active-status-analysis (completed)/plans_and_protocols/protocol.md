# Protocol: Release Implementation Pipeline Redesign
## TASK-PROC-035-07 — Consolidated Design (authoritative, supersedes all plan files)

Date: 2026-04-25 | Status: analysis complete, requirements updates pending

---

## 1. Chosen Architecture

**Plan v3 (distributed pipeline with quality gates)** is the selected design.

Core principle: `release-begin-impl` handles scope only. Task creation is
distributed across many autorun sessions, one package per session. A holistic
Task Creation Plan bridges the gap between the distributed execution and the
understanding that a single session would have had.

### Pipeline Overview

```
/release-begin-impl  (interactive, user present)
  Phase 0    Bootstrap: detect mode (package / release), build work list
  Phase 1    Scope coverage check (agent OR inline — see §6)
  Phase 2    Epic agents: requirements vs. features (N agents, parallel)
  Phase 2b   Remediation: fix gaps found in Phase 2
  Phase 2c   Task Creation Planner: one agent reads ALL in-scope feature
             requirements.md files → produces task_creation_plan.md
  Phase 5    USER GATE: approve scope findings + full plan
  Phase 6    Activate + hand off (see §3 for full sequence)

autorun / manual  (one session per package)
  Each orchestration task: task-create-code → create next orch task → task-complete

autorun / manual  (validation)
  Validation orchestration task (created by chain when all packages covered):
  structural checks, AC coverage, after-chains

/release-begin-impl-finalize  (interactive, user present)
  Phase 1    Coverage re-verification (scripts)
  Phase 2    After-chain reconciliation (script: reconcile_after_chains.py)
  Phase 3    Semantic validation (N agents, one per feature)
  Phase 4    USER GATE: consolidated report, user approval
  Phase 5    Finalize RELEASES.md, regenerate STATUS.md, commit

/release  (interactive)
  Cuts the release; archives task_creation_plan.md (adds archived: true frontmatter)
```

Two user gates total: scope+plan approval (Phase 5 of release-begin-impl),
and final review (Phase 4 of release-begin-impl-finalize).

---

## 2. Skill Changes

### 2a. `release-begin-impl` — Substantial Rewrite

**Remove**: Phases 3, 4, 5 (old), Key Constraints rows for phases 3/4/5.

**Phase 1 (Scope Coverage)**: Agent (or inline) reads RELEASES.md +
STATUS_NEXT_RELEASE.md + RELEASE_BACKLOG.md. Three checks:
1. Package coverage: every package in the release's `packages:` array has
   ≥1 requirement assigned (via target_package).
2. Includes coverage: only if `scope_boundaries.includes` non-empty; each item
   maps to ≥1 requirement. If empty: valid — `packages:` IS the scope. Note
   this explicitly in the output (do NOT say "nothing to check").
3. Contradiction check: any package whose theme appears in
   `scope_boundaries.excludes` → surface as explicit contradiction.
Output: `questions/iteration_NN/phase_1/scope_gaps.md`
Output quality standard: file must begin with `## Summary for User` (≤3 bullets +
numbered open questions) — same standard as Phase 2 agent outputs (Round 2 §7).
Context rule: call `should_use_agents.py`; ≤30KB/5 files → inline; else → agent.

**Phase 2 (Epic Agents)**: Unchanged structurally. Each agent reads epic +
child feature requirements.md (max 5 files). Must start findings with
`## Summary for User` (≤3 bullets + numbered open questions).

**Phase 2b (Remediation)**: Replace `_agent_state.md` agent-ID tracking with
output-file polling. Each remediation agent writes to a unique pre-assigned
path `phase_2b/gap_N/output.md`. Orchestrator scans for output files after
all agents complete. Resume = re-spawn fresh agent with answered question +
context, not resume by agent ID.

**Phase 2c (Task Creation Planner) — NEW**:
Spawn one agent. Agent reads ALL in-scope feature requirements.md files (one
Read per file), RELEASE_BACKLOG.md, RELEASES.md. Optionally calls
`check_requirement_implementation.py` per feature to detect already-implemented
ACs. Produces `task_creation_plan.md` (see §5 for schema).
The plan contains: ordered task list, per-task ACs/effort/layer/after-chains,
architecture notes, test strategy, layer ordering declaration.
**Already-implemented ACs** (verdict `likely_implemented` from the script) →
Planner sets `task_type: verify` instead of `implement`. Verify tasks are quick:
read existing code, confirm AC conformance, add tests if missing. (Round 3 Gap M)

**Phase 5 (User Gate) — Repurposed**: Single gate. Orchestrator calls
`summarize_plan.py` and shows the 1-page summary alongside paths to full plan
and all findings files. User reads directly and approves or requests revisions.
Only when user says "approved": proceed to Phase 6.

**Phase 6 (Activate + Hand Off) — see §3 for full sequence.**

**Decision Domains section (add after `## Inputs`, before Phase 0)**: This
is the single most important fix to prevent phase-leakage of questions.
Insert verbatim into the skill:

```
## Decision Domains (Read This Before Anything Else)

Three kinds of questions surface during release prep. Each has a designated
phase. Mixing them up wastes user time and burns context.

| Domain | Examples | Where it belongs |
|--------|----------|------------------|
| Scope — does X belong in this release? | "Transfer Notifications in 0.0.1?", "Move AC-28–36 to 0.2.0?" | Phase 2 ONLY. Once Phase 2 ends, scope is frozen for this iteration. |
| Coverage — does in-scope work have requirements + impl tasks? | "Does feat_pairing have an impl task?" | Phase 2c Planner. Agents create tasks or flag blockers, never scope questions. |
| Investigation — answer obtainable by reading more files? | "Are these 2 open analyze tasks still relevant?", "Does this task cover AC-28?" | Inside the agent. NEVER escalate to user. Read the files first. |

Phase 2b and Phase 2c must NOT contain Scope-domain questions. If a Phase 2c
agent identifies scope ambiguity, it flags it as a Phase 2 reopener — the
orchestrator re-runs Phase 2 for that epic before the plan can be finalized.
```

Add introductory note to skill:
> "This skill covers scope verification and planning only. Task creation runs
> in autorun. /release-begin-impl-finalize handles post-creation review. This
> skill never reads a feature's requirements.md in the orchestrator's main
> context — only Phase 2 epic agents and Phase 2c planner do."

### 2b. `release-begin-impl-finalize` — New Skill

**Name**: `release-begin-impl-finalize` (not `release-finalize` — that implies
cutting the release).

**Trigger**: User runs `/release-begin-impl-finalize` after autorun reports
all packages covered. Or: the validation orchestration task (last in chain)
instructs the user to run it.

**Phase 1**: Run `python3 scripts/generate_status_overview.py --release [v]`,
read output. Verify all in-scope packages have ≥1 non-terminal impl task.
If gaps remain: list them and stop.
Additionally: run `python3 scripts/check_task_against_plan.py` for each impl task
as a structural audit (are tasks conformant to the approved plan?). Surfaces
mismatches as a report; does not block. (Round 3 §3: "Called by
release-begin-impl-finalize Phase 1 (audit)".)

**Phase 2**: Run `python3 scripts/reconcile_after_chains.py --release [v]
--plan [plan_path]`. Read output. If missing after-entries found: run with
`--apply` flag to auto-fix. Confirm to user.

**Phase 3**: Spawn N agents (one per feature), each reading:
- Feature's requirements.md (ACs)
- All impl task goal.md files for that feature
Agent checks: does each goal.md's Objective + Scope address the AC's intent?
Flags high-confidence semantic mismatches only. Output per agent:
`release_finalize_semantic/feat_[REQ-ID].md`.

**Phase 4**: Orchestrator reads all semantic reports, presents consolidated
summary. User approves or requests fixes.

**Phase 5**: On user approval — update RELEASES.md (add `tasks_complete_date`
if desired), run `generate_status_overview.py`, `claude-commit`.
Print: "Implementation tasks complete. Run /release to cut the release."

Skill never reads a feature's requirements.md directly in orchestrator context.

**Finding the plan**: reads RELEASES.md → active release version → searches
`requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/`
for an explore task with matching `target_release` and `status: completed` →
`task_creation_plan.md` in that folder.

### 2c. `task-create-code` — Zero-Parameter Mode Changes

**Phase 0 addition**: After picking the next package, check for
`task_creation_plan.md` (via `plan_path` field in the orchestration task's
frontmatter).

If plan exists:
- Use plan's `## Execution Order` for package sequencing (overrides next_tasks.py
  semver ranking).
- Load the plan entry for this package: use `covers_acs`, `effort`, `layer`,
  `after`, `task_type`, `implementation_notes` as authoritative defaults.
- **Skip user confirmation** (Phase 0 step 6). Print: "Using approved plan
  entry: [task_name] for [package]" and continue.
- In automated mode: never override. Mismatch → write question.md, stop.
- In interactive mode: user may override with explicit signal
  `--override-plan`.

**Phase 6 addition (Plan Conformance Check)**: After writing goal.md, run:
`python3 scripts/check_task_against_plan.py --task [task_id] --plan [plan_path]`
Exit 0: proceed. Exit 1 (mismatch): show diff to user (interactive) or write
question.md (automated). Exit 2 (no plan entry): skip silently.

Conformance rules (what counts as a match):
- `target_package`: exact match
- `covers_acs`: set equality (order irrelevant)
- `effort`: ±1 size is acceptable (XS↔S, S↔M, M↔L, L↔XL) — flag but do NOT block
- `layer`: exact match
(Source: Round 3 §3 script spec for check_task_against_plan.py)

### 2d. `claude-automated-mode` — Simplification

**Remove Case A entirely.** The chain self-perpetuates: each orchestration
task calls `create_orchestration_task.py` as part of its own ACs. No bootstrap
needed to trigger orchestration task creation.

**Transition sequencing for Case A removal (Round 3 S4)**: Do NOT remove Case A
until: (1) the new self-perpetuating orchestration task template (Group 3, §10)
is deployed, AND (2) all in-flight orchestration tasks using the OLD template have
completed. Keep both code paths active during the transition cycle. After the last
old-template task reaches terminal status, remove Case A.

**Remove Case B entirely.** When all packages are covered,
`create_orchestration_task.py` (Exit 3 → now replaced) creates a validation
orchestration task instead. The chain handles it.

**Retain Case C**: queue empty + validation report exists + no open questions
→ write completion summary to `automation/release_status/<version>_complete.md`
with instruction: "Run /release-begin-impl-finalize for final review, then
/release to cut the release."

**Retain Case D**: runnable tasks exist → proceed normally.

The bootstrap code shrinks from ~80 lines to ~20 lines.

### 2e. `release-status` (minor extension, optional)

Extend `release_readiness.py` to show per-package status in Stage 4 output:
`[✓] PKG-A: 1 impl task (TASK-FUNC-007-12)` /
`[ ] PKG-B: planned, not yet created` /
`[~] PKG-C: orchestration task pending`.
Data sourced from task_creation_plan.md (if present) + STATUS.md.
Defer if not immediately needed.

---

## 3. Phase 6 Sequence (Complete Specification)

```
Pre-checks (no mutations):
  6.0  User has said "approved" in Phase 5
  6.1  task_creation_plan.md exists at [explore_task_folder]/task_creation_plan.md
  6.2  python3 scripts/create_orchestration_task.py --dry-run --after-task <explore_task_id>
       must exit 0; if not: show stderr, stop
  6.3  Verify explore task ID is known (set in Phase 0)

Mutations (committed atomically by task-complete in step 6.7):
  6.4  Edit RELEASES.md (or RELEASE_BACKLOG.md): status: planned → active
  6.5  python3 scripts/create_orchestration_task.py \
         --after-task <explore_task_id> \
         --plan-path <path_to_task_creation_plan.md>
       → creates orch task goal.md with after: [explore_task_id] and plan_path
       Script does NOT commit
  6.6  Edit explore task goal.md inline: status: in_progress → completed;
       check all completed ACs
  6.7  Call task-complete skill on the explore task
       → task-complete handles: STATUS.md regeneration + ONE atomic commit
         (RELEASES.md + new orch task goal.md + explore task goal.md)

Post-success:
  6.8  Print:
       "Release [version] is now active. Orchestration task [ID] is ready.
       Next: run /autorun to begin distributed task creation, or run
       `Do [TASK-ID]` manually. Each session creates exactly one impl task."
```

**Failure recovery** (the after-chain is the safety net):

| Step | Failure | Safe? | Recovery |
|------|---------|-------|----------|
| 6.2 | dry-run fails | ✓ | Fix issue, re-run Phase 6 |
| 6.4 | RELEASES write fails | ✓ | Re-run Phase 6 |
| 6.5 | script fails | partial (RELEASES activated, no orch task) | Re-run script manually |
| 6.6 | status edit fails | ✓ | Orch task exists but blocked by after-chain; user runs task-complete manually |
| 6.7 | task-complete fails | ✓ | Files mutated, uncommitted; `git status` shows all; commit manually |

At no point can the orchestration task execute prematurely (after-chain blocks
until explore task is terminal).

### `create_orchestration_task.py` Changes Required

1. **`--dry-run` flag**: skip steps 4–6 (allocate ID, create folder, remove
   reserve), same exit codes.
2. **`--after-task TASK-ID` argument**: append to `after:` list in template.
3. **`--plan-path PATH` argument**: add `plan_path: "..."` field to template
   frontmatter.
4. **Exit 3 replacement**: when all packages covered, create a validation
   orchestration task instead of returning Exit 3. Goal: "Run structural
   validation for release [v]: AC coverage, after-chains, target_package,
   opus_recommended flags. Write validation_report.md. Call task-complete."
5. **Concurrency lock**: wrap entire `create_orchestration_task` function
   body with `fcntl.flock` on `.create_orchestration_task.lock` to prevent
   race between two concurrent autorun sessions.
6. **Note**: `target_release: "{version}"` is already in the template ✓

### Orchestration Task `goal.md` Template Changes Required

Add frontmatter fields:
```yaml
plan_path: "{plan_path}"   # path to task_creation_plan.md; empty if no plan
after: ["{after_task}"]    # explore task ID; empty string omitted
```

Replace acceptance criteria with 3-step self-perpetuating ACs.
The skill invoked in Step 1 depends on `task_type` from the plan entry
(`create_orchestration_task.py` inserts the correct text via a switch):

```markdown
## Acceptance Criteria
- [ ] Run `task-create-code` in zero-parameter mode      ← task_type: implement | verify | scribble_to_flutter
  OR: Run `ui-create-scribble` skill                     ← task_type: scribble
  (reads plan_path if set; plan entry determines which skill to call)
- [ ] Run `python3 scripts/create_orchestration_task.py --after-task {task_id}
      --plan-path {plan_path}` — creates next orch task OR validation task
- [ ] Run `task-complete` on this orchestration task ({task_id})
```

`create_orchestration_task.py` receives `task_type` from the plan entry and
writes type-specific Step 1 text into the goal.md template (plan v3 §5, Round 3 Gap O).
Add a `task_type` frontmatter field to the orchestration task goal.md so autorun
can verify the correct skill was invoked.

---

## 4. New Scripts

| Script | Purpose | Replaces |
|--------|---------|---------|
| `parse_task_creation_plan.py` | Parse plan.md → JSON; shared by all below | — |
| `check_task_against_plan.py --task T --plan P` | Compare goal.md vs plan entry; exit 0/1/2 | Plan conformance agent |
| `reconcile_after_chains.py --release V [--plan P] [--apply]` | Find + fix missing after-entries | After-chain reconciliation agent |
| `summarize_plan.py --plan P` | 1-page stats summary for user gate | — |
| `check_requirement_implementation.py --requirement R` | Grep lib/ for per-AC implementation traces; outputs per-AC verdict: `likely_implemented` \| `likely_missing` \| `uncertain` | — |
| `find_orchestration_tasks.py --status S` | Deterministic orch task detection by structural signature (target_release set + scope_description "Orchestration:") | Fragile grep formerly used in Case A guard (now deleted); used by create_orchestration_task.py duplicate-check |
| `should_use_agents.py --release V` | Compute total req file size; output agents_required / orchestrator_direct | — |

All scripts exit 0 on success, non-zero with human-readable stderr on error.
`parse_task_creation_plan.py` is a shared library, not meant for direct CLI
use (though CLI entry point is fine for debugging).

---

## 5. `task_creation_plan.md` Schema

**Location**: `[explore_task_folder]/task_creation_plan.md`
(sibling to goal.md; referenced by orch tasks via `plan_path` frontmatter)

**Format**: YAML frontmatter + Markdown body with per-task YAML blocks.

```markdown
---
plan_id: PLAN-0.0.1-v1
release: 0.0.1
created: 2026-04-25
created_by: release-begin-impl Phase 2c
status: draft            # draft | approved | archived
approved_by: ""
approved_on: ""
explore_task: TASK-PROC-035-07
total_tasks: 12
total_effort: { M: 5, S: 4, L: 3 }
packages_covered: [PKG-0.0.1-data, ...]
---

# Task Creation Plan: Release 0.0.1

## Layer Dependency Rules
data → domain → presentation → test → integration
Cross-package overrides: (list any explicit deviations)

## Execution Order
1. PKG-0.0.1-data — Transfer Data Model
2. PKG-0.0.1-pairing — Transfer Pairing
...

## Architecture Notes
(Free-form: shared abstractions, screen ownership, test strategy,
 detected pre-existing implementations)

## Planned Tasks

### PKG-0.0.1-data: Transfer Data Model

#### Task 1: [task name]
​```yaml
task_name: Implement TransferSession entity and repository
task_type: implement   # implement | verify | scribble | scribble_to_flutter
target_package: PKG-0.0.1-data
covers_acs: [AC-01, AC-02, AC-03]
effort: M
layer: data            # data | domain | presentation | test | integration
after: []              # use "#PKG-X:Task N" for intra-plan references
opus_recommended: false
req_path: requirements_tasks/.../requirements.md
req_commit: d357041e
implementation_notes: |
  (optional: constraints, patterns to follow, cross-references)
​```
**Rationale**: (why this grouping of ACs)

#### Task 2: ...
```

**Rules**:
- `covers_acs` is **set-based**: order of entries is irrelevant; equality is
  determined by set comparison. (Round 3 §7)
- `effort` uses the CLAUDE.md size scale: `XS`, `S`, `M`, `L`, `XL`. (Round 3 §7)
- `task_type: scribble` → orchestration task calls `ui-create-scribble`
  instead of `task-create-code`. Must be followed by a `scribble_to_flutter`
  task with `after: ["#PKG-X:Task N"]`.
- `#PKG-X:Task N` intra-plan references are resolved to real TASK-IDs by
  `task-create-code` when each task is created (reads previously committed
  task IDs and substitutes).
- Plan is **append-only** once approved. New versions append as
  `## Plan v2 — [date]` with a `changes_from_vN` summary and own frontmatter block:
  ```yaml
  plan_id: PLAN-0.0.1-v2
  parent_plan_id: PLAN-0.0.1-v1
  created: 2026-04-26
  status: draft
  changes_from_v1: |
    - Added Task … / Modified scope of Task …
  ```
  Tools use latest non-archived version. `archived: true` set by `/release` skill at release cut.
- `parse_task_creation_plan.py` parsing algorithm (Round 3 §7):
  1. Parse top-level YAML frontmatter.
  2. Walk Markdown headings: each `### PKG-...` opens a package section;
     each `#### Task N:` opens a task entry.
  3. Extract fenced YAML block immediately below the task heading.
  4. Capture rationale prose: everything between the YAML close fence and
     the next `####` / `###` heading.
  5. Return JSON: `{ frontmatter, packages: [{ id, name, tasks: [...] }] }`.
  (~80 lines of Python; reusable across summary, conformance-check, reconciliation scripts.)

---

## 6. Context-Window Rule (Project-Wide)

**Script**: `scripts/should_use_agents.py --release [v]`

**Thresholds**:
- Total requirement bytes ≤30KB AND file count ≤5 → `orchestrator_direct`
- Otherwise → `agents_required`

**Application per phase/skill**:

| Context | Rule |
|---------|------|
| release-begin-impl Phase 1 | Call should_use_agents.py; branch on result |
| release-begin-impl Phase 2 (epic agents) | Always agents (fan-out + parallelism) |
| release-begin-impl Phase 2b (remediation) | Inline if ≤2 lines; agent otherwise |
| release-begin-impl Phase 2c (Planner) | Always one agent (must see all features) |
| task-create-code Phase 1 (read requirement) | Call should_use_agents.py for that single file |
| release-begin-impl-finalize Phase 1 (coverage + audit) | NO — script-driven (generate_status_overview.py + check_task_against_plan.py); no requirement files read inline |
| release-begin-impl-finalize Phase 2 (after-chain) | NO — reconcile_after_chains.py script only |
| release-begin-impl-finalize Phase 3 (semantic) | Always agents (one per feature) |

**Add to CLAUDE.md**: "Skills reading requirement files must call
`scripts/should_use_agents.py` before deciding to read inline. Hard threshold:
30KB / 5 files. Structural fan-out phases always use agents regardless of size."

---

## 7. Responsibility Boundaries

| Concern | Owner | NOT owned by |
|---------|-------|--------------|
| Scope verification (packages → requirements) | release-begin-impl Ph.1–2 | any other skill (release-begin-impl-finalize Ph.1 is a read-only audit co-owner) |
| Holistic task plan creation | release-begin-impl Ph.2c | task-create-code, autorun |
| Plan approval | release-begin-impl Ph.5 user gate | — |
| Release activation in RELEASES.md | release-begin-impl Ph.6 | user (manual edit prohibited) |
| Creating first orch task | release-begin-impl Ph.6 (calls script) | bootstrap |
| Creating subsequent orch tasks | self-perpetuating chain (script) | bootstrap (Case A deleted) |
| Individual impl task goal.md | task-create-code | orchestrator, release-begin-impl |
| Cross-task after-chain (holistic) | Planner (authoritative), reconcile script (post-fix) | propose_after.py when plan exists |
| Structural validation | validation orch task (chain end) | release-begin-impl-finalize |
| Semantic validation | release-begin-impl-finalize Ph.3 | autorun |
| Final user review | release-begin-impl-finalize Ph.4 | — |
| Release cut (tag, push, archive task_creation_plan.md) | /release | — |

**Eliminated duplications**:
1. Case A (claude-automated-mode inline task-create) → deleted; chain owns it
2. Case B (claude-automated-mode validation task) → deleted; chain creates
   validation task via script
3. propose_after.py when plan exists → plan's after entries are used directly;
   propose_after.py is fallback only when no plan entry exists for this task
4. Two orchestration entry points → only Phase 6 creates the FIRST orch task

---

## 8. Requirements to Update

| Requirement | Sections | What changes |
|-------------|----------|--------------|
| **REQ-PROC-035** SEC-05 | Task Creation Process | Replace Bootstrap Rule with self-perpetuating chain description; add task_creation_plan.md artifact; remove inline task-create from autorun |
| **REQ-PROC-035** SEC-06 | release-begin-impl Integration | Add Phase 2c (Planner); update Phase 5/6; remove Phase 3/4/5; add release-begin-impl-finalize as successor; describe explore task lifecycle (auto-close Phase 6) |
| **REQ-PROC-035** SEC-07 | Release Status Overview | Mention per-package status table (optional, Stage 4) |
| **REQ-PROC-041-03** | Automated Mode | Remove Case A and Case B from bootstrap; document simplified bootstrap (C + D only); describe self-perpetuating chain; reference find_orchestration_tasks.py for any detection logic |
| **REQ-PROC-036** | Release Workflow | Add release-begin-impl-finalize to workflow sequence between "autorun completes" and /release |
| **`requirements_tasks/RELEASES.md`** | Lifecycle definitions | Update `active` definition from "at least one task in_progress" to "requirements verified, implementation approved to begin; set by release-begin-impl Phase 6 — do NOT set manually". (Round 1 Fix 3, Round 2 April 24 Fix D) |

Use `requ-explore` skill (one agent per requirement update).
RELEASES.md lifecycle text is a direct file edit (not a REQ-PROC file); can run in parallel.

---

## 9. Deferred Items (Not Blocking Implementation)

| Item | Workaround |
|------|-----------|
| Cross-release UI screen dependency (e.g. add button to screen from prior release) | Requirements explicitly note "modifies HomeScreen (from 0.0.0)"; implementing agent reads existing screen file |
| propose_after.py full layer-awareness for plan-less tasks | Layer ordering heuristic partially captured by `same_scope_upstream_layer` rule; full UI sub-layer classification deferred to separate task |
| RELEASES.md vs. RELEASE_BACKLOG.md active-status bifurcation | Phase 6 sets both; script uses RELEASES.md as primary. Cleanup as separate requirement |
| Mid-flight plan deviation process | Core rules active (see §9a below); full formal process deferred |
| Per-package status table in release-status (Gap O) | Defer; current Stage 0–5 output is sufficient for now |

### 9a. Mid-Flight Plan Deviation — Core Rules (Gap J, Round 3)

The plan file is **append-only** once approved. No entries are ever deleted.
Deviations are handled by scenario:

| Scenario | Action |
|----------|--------|
| Add unplanned task | User runs `task-create-code` with explicit requirement path. Skill detects plan exists, writes `off_plan: true` to task frontmatter. Plan is NOT modified. |
| Modify planned task's scope *before* creation | User edits the plan file directly (it's a Markdown file). Re-approve at next finalize gate. |
| Modify planned task's scope *after* creation | User edits goal.md AND adds a rationale note "deviates from plan". The `release-begin-impl-finalize` semantic-validation phase flags it for user acknowledgment. |
| Replace one planned task with two | Mark original entry as superseded in plan (append comment); add new entries as `## Plan v2 — [date]` section below. Plan grows monotonically. |

New plan versions append as `## Plan v2 — [date]` with a `changes_from_vN` summary.
The original v1 content stays untouched above. Tools (task-create-code, scripts) use the
latest non-archived version. Formal escalation process for contested deviations is deferred.

---

## 10. Implementation Order (for follow-up tasks)

**Pre-implementation check (before Group 1)**:
Verify that `scripts/next_tasks.py` correctly resolves `target_package` → release
(the same fix that was applied to `generate_status_overview.py` in a prior session).
Read `next_tasks.py` and confirm the resolution path. If broken, apply equivalent fix
and include it in the Group 1 commit. (Source: Round 3 v3 Phase A execution plan.)

Sequence dependencies exist; not all chunks are parallel:

```
Group 1 (no dependencies, can start immediately):
  - 7 new scripts (parse_plan, check_against_plan, reconcile_after_chains,
    summarize_plan, check_impl, find_orch_tasks, should_use_agents)

Group 2 (depends on Group 1 scripts existing):
  - create_orchestration_task.py changes (--dry-run, --after-task, --plan-path,
    Exit-3 replacement, concurrency lock)
  - release-begin-impl rewrite (uses should_use_agents, summarize_plan)

Group 3 (depends on Group 2: create_orchestration_task.py must be updated):
  - orchestration task goal.md template (plan_path field, 3-step ACs)
  - task-create-code zero-mode changes (reads plan, plan conformance check)

Group 4 (depends on Groups 1–3):
  - release-begin-impl-finalize new skill (uses reconcile, check_against_plan)
  - claude-automated-mode simplification (remove Cases A, B)

Group 5 (independent, can run in parallel with any group):
  - Requirements updates (REQ-PROC-035, REQ-PROC-041-03, REQ-PROC-036)
  - release-status minor extension (optional)
  - CLAUDE.md context-window rule addition
```

Estimated effort: ~26 hours total across all groups.

---

## 11. Clarifications and Edge Cases

### 11a. `writes_requirements: true` on the Explore Task — Keep It

The `after:` chain (§3) is the primary safety guard. `writes_requirements: true`
on the explore task is a **secondary guard** with a different purpose: it
prevents unrelated impl tasks from surfacing at the top of `next_tasks.py`
rankings while the user is mid-session in `release-begin-impl` (rule #1 in
next_tasks.py: "critical-path explores always first"). It also visually
signals to the developer that requirement work is in progress.

It is NOT load-bearing for the bootstrap (Case A is deleted). Keep it.

### 11b. Phase 0 Must Detect an Already-In-Progress Explore Task

If the user runs `/release-begin-impl` while a prior run's explore task is
still `in_progress` for the same release:

Phase 0 checks: scan the release_preparation tasks folder for an explore task
with `target_release` matching the current release AND `status: in_progress`.
If found, offer: "A prior release-begin-impl session is in progress (TASK-ID).
Resume it, or abandon and start fresh?"

- Resume: read existing `questions/` folder, set `current_iteration` based
  on existing `iteration_NN/` folders, proceed from where work was.
- Abandon: set prior task status to `cancelled`, start new explore task.

Without this check, two explore tasks end up racing for the same release.

### 11c. Phase 2c Planner for Large Releases (>10 Features)

The Planner agent must read ALL in-scope feature requirements.md files in one
context. For large releases (>10 features), this could exceed context budget.

**Mitigation**: if `should_use_agents.py` returns total bytes >100KB for all
in-scope feature files, split into sub-agents:

1. Spawn N/2 agents in parallel, each reading half the feature files.
   Each produces a partial plan.
2. One aggregation agent reads all partial plans and produces the final
   `task_creation_plan.md`, resolving cross-feature dependencies.

The threshold for splitting is 100KB (not the 30KB threshold for inline reads —
the Planner agent has its own fresh context, so 30KB is no longer the limit;
100KB ≈ 25K tokens is a reasonable budget for the Planner's core reading).

For most releases (≤10 features, ≤100KB total), a single Planner agent suffices.

### 11d. propose_after.py Interaction with the Plan

When `task-create-code` creates a task and a plan entry exists:

1. **Use plan's `after:` directly** — do NOT call `propose_after.py` for
   dependency detection. The plan is the authoritative source; re-deriving
   would risk false additions.
2. **Still call `propose_after.py`** for the `requirement_then_implementation`
   heuristic only (detect if a requirements-authoring task precedes this impl
   task). This is mechanical and plan-agnostic.
3. **Merge results**: plan-specified `after:` entries + any additional
   `propose_after.py` results that are NOT already in the plan.

When no plan entry exists (off-plan or plan-less task):
Call `propose_after.py` normally with full heuristic set.

### 11e. Validation Orch Task vs. Finalize After-Chain — Not a Duplication

These two interact in a pipeline, not in parallel:

1. **Validation orch task** (automated, runs at chain end): runs structural
   checks. Calls `reconcile_after_chains.py` WITHOUT `--apply` → DETECTS
   missing after-entries, writes them to `validation_report.md`.
2. **release-begin-impl-finalize Phase 2** (interactive, user present):
   reads `validation_report.md`, then calls `reconcile_after_chains.py --apply`
   to FIX the detected issues. User reviews the applied fixes.

Detection is automated; fixing is user-supervised. No duplication of work.
The validation report is the handoff document between the two.

**`validation_report.md` quality standard** (Round 2 April 25 §7): machine-generated,
must be reproducible. Every failure entry must include:
- The exact failing task ID
- Expected vs. actual value
- The remediation command to run (e.g., `python3 scripts/reconcile_after_chains.py --apply`)

Semantic correctness is NOT in this report — that belongs to `release-begin-impl-finalize` Phase 3.
