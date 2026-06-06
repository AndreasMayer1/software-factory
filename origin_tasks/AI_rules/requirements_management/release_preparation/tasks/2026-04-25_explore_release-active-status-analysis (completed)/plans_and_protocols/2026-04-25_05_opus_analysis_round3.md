# Opus Analysis Round 3: Phase 6 Sequence, Script vs. LLM, New Gaps

Date: 2026-04-25
Builds on: Round 2 (`2026-04-25_04_opus_analysis_round2.md`) + Plans v1–v3
Verified against codebase: `create_orchestration_task.py`, `propose_after.py`,
`task-create-code` skill, `claude-automated-mode` skill, `release_readiness.py`.

---

## 1. Phase 6 Sequence (Option B, Auto-Closing Explore Task)

### Confirmed Decision

The user prefers: Phase 6 closes the explore task automatically when everything
succeeds. **This is the right design** — and Option B's `after:` chain makes it
safe even on partial failures.

### Why Auto-Closing Is Safe Here (the key insight)

The `after: [explore_task_id]` reference on the orchestration task is a STATIC
dependency. It points to the explore task by ID, not by status snapshot. As
long as the explore task exists in any non-terminal state, the orchestration
task is blocked. Once the explore task is terminal (completed/cancelled), the
orchestration task becomes runnable.

This means partial failures of Phase 6 cannot cause incorrect execution:
even if step N fails, the worst case is "user must manually finish what's
left", not "autorun runs the wrong thing."

### Detailed Phase 6 Sequence

```
PHASE 6 — Activate + Hand Off (orchestrator inline; no agents)

Pre-checks (no mutations):
  6.0  Verify Phase 5 user gate passed (user said "approved")
  6.1  Verify task_creation_plan.md exists at expected path
  6.2  Run create_orchestration_task.py --dry-run --after-task <explore_task_id>
       → must exit 0; if not, stop and report stderr to user
  6.3  Verify explore task ID is known (set in Phase 0; cross-check goal.md exists)

Mutations (atomic intent — one commit at the end):
  6.4  Edit RELEASES.md (or RELEASE_BACKLOG.md): status: planned → active
       (no commit yet)
  6.5  Run create_orchestration_task.py --after-task <explore_task_id>
       → creates orch task goal.md with after: [explore_task_id]
       (the script doesn't commit; orchestrator commits later)
  6.6  Edit explore task goal.md: status: in_progress → completed
       Mark all acceptance criteria as checked
  6.7  Call task-complete skill on the explore task
       → task-complete handles: STATUS.md regeneration + ONE atomic commit
         covering RELEASES.md + new orch task + explore task goal.md

Post-success:
  6.8  Print handoff message:

       "Release [version] is now active. The implementation pipeline is set up.
        Orchestration task [TASK-ID] created at [PATH] (blocked until the
        explore task completes — it has just been completed in this step,
        so the orchestration task is ready to run).
        Next: run /autorun to begin distributed task creation, OR run
        `Do [TASK-ID]` to manually create the next impl task."
```

### Failure Recovery Matrix

| Step fails | State afterwards | Recovery |
|------------|------------------|----------|
| 6.2 dry-run | Nothing changed | User fixes problem, re-runs Phase 6 |
| 6.4 RELEASES write | Nothing changed | Re-run Phase 6 |
| 6.5 script | RELEASES.md activated, no orch task | Re-run script manually; or re-run Phase 6 (script's duplicate-check exits 2 cleanly) |
| 6.6 status edit | RELEASES active, orch task exists, explore task still in_progress | Orchestration task is BLOCKED by `after:` chain → autorun cannot start it. User runs `task-complete` on explore task manually. **System is safe.** |
| 6.7 task-complete | Files mutated, not committed | `git status` shows everything; user reviews and commits. Orch task still blocked. **System is safe.** |

The `after:` chain is the safety net: at no point can the orchestration task
execute prematurely.

### One Subtle Sequencing Question Resolved

> "Does step 6.5 need the explore task to already exist? Yes — it does. The
> script writes `after: [TASK-PROC-035-07]` to the orch task's goal.md,
> referencing an existing task. The explore task was created at Phase 0 and
> persists as a file throughout. Status is irrelevant for the script; only
> the file's existence matters."

So step 6.5 simply references the explore task by ID. Step 6.6 then closes it.
Order is correct.

### `--dry-run` Flag for `create_orchestration_task.py`

Add a `--dry-run` flag that performs all checks (active release detection,
duplicate check, has_uncovered_packages check) and exits with the same exit
code it WOULD use, **without** writing any files or allocating task IDs.

Implementation: skip steps 4, 5, 6 (allocate task ID, create folder, remove
reserve marker). Steps 1–3 already produce all relevant exit codes (1 = no
active release, 2 = duplicate, 3 = nothing to do).

This is ~5 lines of Python.

---

## 2. New Gaps Beyond Round 2

These were not raised in Round 2.

### Gap H — `task-create-code` Zero-Mode Doesn't Yet Read the Plan

Round 2 mentioned this in passing. Concrete specification:

When `task-create-code` runs in zero-parameter mode AND a `task_creation_plan.md`
exists for the active release, the skill must:

1. **Skip user confirmation** (Phase 0 step 6) — the user already approved the
   plan. Print: "Using approved plan entry: [task_name] for [package]" and
   continue.
2. **Use plan's authoritative data**: covered ACs, target_package, effort,
   layer, after-chain. Do NOT re-derive these.
3. **Allow override only via explicit user signal**: `Use task-create-code
   skill --override-plan` (interactive only).
4. **In automated mode (autorun)**: never override. If the plan entry seems
   wrong, write `question.md` and stop.

**Discovery**: How does `task-create-code` find the plan? Look for
`requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/*/task_creation_plan.md`
where the parent task has `status: completed` AND `target_release` matches
the active release. Most recent wins.

Or simpler: the orchestration task's goal.md includes a `plan_path:` field
that points to the plan. `task-create-code` reads this from the orchestration
task's frontmatter.

**Recommendation**: orchestration task carries the plan path explicitly.
Simpler than discovery.

### Gap I — Orchestration Task Doesn't Reference the Plan

Currently the orchestration task's `goal.md` (from `_GOAL_TEMPLATE`) has no
`plan_path` field. Add it:

```yaml
plan_path: "requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-25_explore_release-active-status-analysis/task_creation_plan.md"
```

And in the goal body, reference: "Plan: see `plan_path` in frontmatter.
Use the plan entry for the next uncovered package."

`create_orchestration_task.py --after-task` should accept a `--plan-path`
argument that gets written to the template. Phase 6 of `release-begin-impl`
passes both `--after-task` and `--plan-path`.

### Gap J — Mid-Flight Plan Deviation

Reality: requirements change mid-release. The user wants to add a task not
in the plan, or modify a planned task's scope. Without a defined process,
chaos.

**Defined process**:

| Scenario | Action |
|----------|--------|
| Add unplanned task | User runs `task-create-code` with explicit requirement path. Skill detects plan exists, marks the new task with `off_plan: true` in frontmatter. Plan is not modified. |
| Modify planned task's scope before creation | User edits the plan file directly (it's a markdown file). Re-approve in next finalize gate. |
| Modify planned task's scope after creation | User edits the goal.md AND notes "deviates from plan" in the rationale. The `release-begin-impl-finalize` semantic-validation phase flags it for user acknowledgment. |
| Replace one planned task with two | Mark original entry as superseded in plan; add new entries below. Plan grows monotonically. |

**Plan immutability rule**: once approved, the plan file is APPEND-ONLY. No
deletions. Modifications append a `## Plan v2 — [date]` section listing
changes from v1, with the original v1 content untouched above. Each version
has its own `plan_id: PLAN-X.Y.Z-vN`.

This preserves the audit trail: at any point the user can see what was
originally approved vs. what evolved.

### Gap K — Concurrency Lock on `create_orchestration_task.py`

If two autorun sessions race (rare but possible), both could pass the
duplicate check before either commits. Result: two orchestration tasks created,
one with task ID N, one with N+1.

**Fix**: file lock at script start.

```python
import fcntl
lock_file = PROJECT_ROOT / ".create_orchestration_task.lock"
with open(lock_file, 'w') as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    # ... entire create_orchestration_task body ...
```

5 lines of Python. Eliminates the race.

### Gap L — Plan Archival When Release Is Cut

When `/release` runs (cuts the release), the `task_creation_plan.md` should
be marked archived. Otherwise future searches for "active plan" might find
stale plans.

**Simple mechanism**: `/release` skill adds frontmatter field `archived: true`
and `archived_on: [date]` to the plan file. `task-create-code` discovery
filters out plans with `archived: true`.

Belongs in `/release` skill as a cleanup step. Trivial.

### Gap M — Already-Implemented Detection (for the Planner)

When the Planner runs, it must not plan tasks for code that already exists
(e.g., features started before formal release planning).

**Detection script**: `scripts/check_requirement_implementation.py
--requirement <path>` — greps `lib/` for keyword traces of the requirement's
entities/screens/services. Outputs per-AC verdict: `likely_implemented`,
`likely_missing`, `uncertain`.

The Planner agent calls this script for each in-scope feature. ACs marked
`likely_implemented` get a planned task with `task_type: verify` instead of
`task_type: implement`. Verify tasks are quick (read code, confirm conformance,
add tests if missing).

This avoids duplicate work AND preserves audit trail (every AC has a task
even if "verify" was the actual work).

### Gap N — Plan Summary Auto-Generated Sibling

The full plan can be 200+ lines for a 30-task release. Phase 5 user gate
benefits from a 1-page summary. Generated by script, not by an LLM:

`scripts/summarize_plan.py path/to/plan.md > plan_summary.md`

Outputs:
```
Plan: PLAN-0.0.1-v1 (DRAFT)
Total: 12 tasks, estimated effort breakdown: M×5, S×4, L×3
Layer distribution: data 25%, domain 33%, presentation 33%, test 9%
Packages covered: 6/6
Cross-package dependencies: 8 after-chain entries
opus_recommended tasks: 2
Verify-only tasks: 1 (existing implementation detected)

Risk flags: none
```

Phase 5 shows BOTH: the summary (for quick read) and the full plan (for
detailed review). User skims the summary, drills into the full plan as needed.

### Gap O — Scribble/UI Tasks in the Plan

The codebase has UI scribble workflows (`ui-create-scribble`,
`ui-improve-flutter`). These produce non-code artifacts (HTML wireframes)
that gate Flutter implementation.

**Plan must distinguish**:
- `task_type: implement` — Dart code, calls `task-create-code` then
  `code-simple/code-complex`
- `task_type: scribble` — wireframe creation, calls `ui-create-scribble`
- `task_type: scribble_to_flutter` — Flutter implementation that follows
  an approved scribble, calls `code-simple/code-complex` with scribble path
- `task_type: verify` — for already-implemented ACs

The Planner decides the type based on:
- Layer is `presentation` AND no scribble exists yet → `scribble` type FIRST,
  then a follow-up `scribble_to_flutter` task with `after: [scribble_task]`
- Layer is `presentation` AND approved scribble exists → `scribble_to_flutter`
- Otherwise → `implement` or `verify`

The plan's per-task entry includes `task_type` field. The orchestration task
template adapts: `task-create-code` is called for `implement`/`verify`/
`scribble_to_flutter`; `ui-create-scribble` is called for `scribble`.

This requires the orchestration task goal.md to include `task_type` so the
autorun knows which skill to invoke. Or the orchestration task goal.md gets
type-specific text from a switch in `create_orchestration_task.py`.

### Gap P — `RELEASE_BACKLOG.md` vs. `RELEASES.md` Active Status Bifurcation

The current `release-begin-impl` skill (Phase 6) handles BOTH:
- "By package" mode → updates `RELEASE_BACKLOG.md` `status: active`
- "By release" mode → updates `RELEASES.md` `status: active`

This is two sources of truth for "what's active". The orchestration task
detection logic (`parse_release_from_releases_md`) only reads RELEASES.md.

**Risk**: in package mode, RELEASES.md may not have an active release; the
script falls back through its detection chain and may pick the wrong release.

**Recommendation**: even in package mode, the release containing the active
package should also be marked active in RELEASES.md. The two should be
synchronized. Phase 6 should set BOTH (or only RELEASES.md, with package
status derived from "package belongs to active release"). The `status` field
on packages may be redundant — better to derive it.

Defer: this is a separate cleanup. For Round 3 we acknowledge the bifurcation
and recommend the cleanup as a follow-up requirement.

---

## 3. What Scripts Should Take Over from the LLM

### Principle

LLM tokens cost money and time. Pure data manipulation (no judgment) belongs
in scripts. Judgment about content semantics belongs in the LLM. The boundary:

| Task | LLM or Script? |
|------|----------------|
| "Does this AC describe a UI screen?" (semantic) | LLM |
| "Compare task's covers_acs to plan entry's covers_acs" (structural) | Script |
| "Read all goal.md files for release X and build dependency graph" (aggregation) | Script |
| "Decide whether two features should share an abstraction" (judgment) | LLM |
| "List all packages in RELEASE_BACKLOG.md with status: planned" (filtering) | Script |
| "Detect if a feature is partially implemented in lib/" (heuristic) | Script first, LLM verifies |

### Specific Scripts to Add

**(a) `scripts/check_task_against_plan.py`** — Plan Conformance Check
- Input: `--task <task_id>` + `--plan <plan_path>`
- Compares task's frontmatter against plan entry: target_package, covers_acs
  (set equality), effort (±1 size), layer
- Exit 0 (match), 1 (mismatch — print diff), 2 (no plan entry for this task)
- Replaces Round 2's "Plan Conformance Check" agent
- Called by `task-create-code` Phase 6 (verify) and by
  `release-begin-impl-finalize` Phase 1 (audit)

**(b) `scripts/reconcile_after_chains.py`** — After-Chain Reconciliation
- Input: `--release <version>` + `--plan <plan_path>` (optional)
- Reads all impl task goal.md for the release
- Builds current dependency graph from `after:` fields
- Compares with plan's expected after-chains (if plan provided)
- Outputs: missing dependencies per task
- Optional `--apply` flag edits goal.md files to add missing entries
- Replaces Round 2's "After-Chain Reconciliation" agent
- Called by `release-begin-impl-finalize` Phase 2

**(c) `scripts/summarize_plan.py`** — Plan Summary
- Input: `--plan <plan_path>`
- Output: 1-page summary (counts, distributions, flags)
- Called by `release-begin-impl` Phase 5 (user gate)

**(d) `scripts/check_requirement_implementation.py`** — Already-Implemented Detection
- Input: `--requirement <path>`
- Greps `lib/` for entity/screen names extracted from requirement
- Outputs per-AC: `likely_implemented` / `likely_missing` / `uncertain`
- Called by Planner agent (Phase 2c) for each in-scope feature
- Reduces planner's reading burden (planner doesn't need to grep code itself)

**(e) `scripts/find_orchestration_tasks.py`** — Deterministic Detection
- Input: `--status <comma-list>`
- Outputs: list of task IDs and paths matching status filter, with
  orchestration-task structural signature (target_release set, scope_description
  matches "Orchestration:")
- Replaces fragile grep in `claude-automated-mode` Case A guard
  (or in the chain's "is there already a pending orch task?" check)
- Trivial; ~30 lines of Python

**(f) `scripts/should_use_agents.py`** — Context-Window Guard (see section 4)

**(g) `scripts/parse_task_creation_plan.py`** — Plan Parser
- Input: `--plan <path>` + optional `--task <task_id>` to extract one entry
- Output: JSON of plan entries
- Used internally by other scripts; provides a single parse implementation

### Estimated ROI

| Script | Token savings per release | Implementation effort |
|--------|---------------------------|------------------------|
| (a) check_task_against_plan | ~5K tokens × N tasks | 2 hours |
| (b) reconcile_after_chains | ~30K tokens (one big agent replaced) | 4 hours |
| (c) summarize_plan | ~5K tokens | 1 hour |
| (d) check_requirement_implementation | ~3K tokens × N features | 3 hours |
| (e) find_orchestration_tasks | ~1K tokens × bootstrap calls | 1 hour |
| (g) parse_task_creation_plan | shared infrastructure | 2 hours |

Total ~13 hours of script work saves dozens of agent invocations per release.
Strongly net positive.

---

## 4. Context-Window Protection: When Are Agents Worth It?

### The Tradeoff

Agents add latency (~5–10s startup per agent), cost (their own token usage),
and complexity (file-based handoff). The reward: orchestrator's main context
stays small, work parallelizes.

Agents are unavoidable when total context would otherwise exceed budget. They
are wasteful when context is small.

### Concrete Threshold Mechanism

**Script**: `scripts/should_use_agents.py --release <version>`

Outputs JSON:
```json
{
  "total_bytes": 84321,
  "file_count": 12,
  "verdict": "agents_required",
  "reason": "exceeds 60_000 byte threshold",
  "details": {
    "epic_files": [...],
    "feature_files": [...],
    "byte_count_per_file": [...]
  }
}
```

**Default threshold**: 30 KB total OR 5 file count → orchestrator-direct OK.
Above either → agents required. Documented in CLAUDE.md as a project rule.

These thresholds are not magic numbers — they reflect Sonnet's cumulative
context budget across a session including the skill prompts, memory, and
conversation history. 30 KB ≈ 7.5K tokens, leaving plenty of room for
follow-up reads and reasoning. 60 KB ≈ 15K tokens, which is fine in isolation
but tight if the session has already accumulated context.

### Where to Apply the Check

| Skill / Phase | Should call check? | Why |
|---------------|---------------------|-----|
| release-begin-impl Phase 1 | Yes | Reading RELEASE_BACKLOG can be small or large |
| release-begin-impl Phase 2 | No — always agents | Fan-out per epic, parallelism wins |
| release-begin-impl Phase 2c (Planner) | No — always one big agent | Must see all features at once; orchestrator stays small |
| release-begin-impl Phase 2b remediation | Yes | Trivial 1–2 line edits inline; larger work via agents |
| task-create-code Phase 1 | Yes | Single requirement can be small (5KB) or large (50KB) |
| release-begin-impl-finalize Phase 1 | No — script-driven | Coverage check via script, no requirement reading needed |
| release-begin-impl-finalize Phase 3 | Yes — agents PER FEATURE that exceeds threshold | Bulk semantic validation; agents only where context demands |

### Cumulative Budget Tracking (Optional, More Sophisticated)

A skill could maintain a running cumulative byte counter across phases.
After Phase 2 completes, the orchestrator subtracts already-read bytes from
the budget. Phase 2c then chooses based on remaining budget.

Probably overkill for now. Static per-phase thresholds are fine.

### Documenting the Rule

Add to `CLAUDE.md` Section 6 (Coding Standards) or to `doc/architecture/`:

> **Context-Window Rule**: Skills that read requirement files must call
> `scripts/should_use_agents.py` BEFORE deciding to read inline. If verdict
> is `agents_required`, dispatch an agent. Hard threshold: 30KB total OR
> 5 files. Skills with structural fan-out (multiple epics, features,
> packages) should always use agents regardless of size.

---

## 5. Responsibility Map (with Cross-Skill Boundaries)

### Skill Ownership Matrix

| Concern | Owner | Co-owners (read-only) |
|---------|-------|-----------------------|
| Scope verification (packages → requirements) | release-begin-impl Phase 1 | release-begin-impl-finalize Phase 1 (audit) |
| Requirement gap remediation | release-begin-impl Phase 2b | — |
| Holistic task plan creation | release-begin-impl Phase 2c (Planner) | task-create-code (read-only consumer) |
| Plan approval gate | release-begin-impl Phase 5 (user gate) | — |
| Release activation in RELEASES.md | release-begin-impl Phase 6 | — |
| First orchestration task creation | release-begin-impl Phase 6 (calls script) | — |
| Subsequent orchestration tasks | self-perpetuating chain (each orch task creates next via script) | — |
| Individual impl task goal.md | task-create-code | propose_after.py (called by it), check_task_against_plan.py |
| Cross-task `after:` definition | Planner (authoritative) | propose_after.py (fallback when no plan), reconcile_after_chains.py (post-fix) |
| Structural validation (AC coverage, after-chains, target_package) | validation orchestration task (created by chain when all packages covered) | — |
| Semantic validation (does goal.md address the AC's intent?) | release-begin-impl-finalize Phase 3 | — |
| Final user review | release-begin-impl-finalize Phase 4 | — |
| Release status reporting (stage 0–5) | release-status (calls release_readiness.py) | — |
| Task/requirement detail status | STATUS.md (generate_status_overview.py) | — |
| Release cut (tag, push, archive plan) | /release | — |

### Eliminated Duplications

After this round's recommendations:

1. **Case A in claude-automated-mode → DELETED.** The chain self-perpetuates;
   each orchestration task creates the next via `create_orchestration_task.py`.
   No bootstrap needed for orchestration creation.

2. **Case B in claude-automated-mode → ALSO DELETED.** When
   `create_orchestration_task.py` detects "all packages covered" (currently
   Exit 3), it instead creates a validation orchestration task. The chain
   continues until validation completes.

3. **Inline task-create vs. create_orchestration_task.py**: only the script
   exists now. Single source of truth for the template.

4. **Two orchestration entry points**: only Phase 6 of `release-begin-impl`
   creates the FIRST orch task. Subsequent ones are chain-driven. No other
   skill creates orchestration tasks directly.

### What Remains in claude-automated-mode

Only:
- **Case C**: completion summary when validation report exists, queue empty,
  no open questions. Writes `automation/release_status/<version>_complete.md`.
- **Case D**: runnable tasks exist → just proceed (default path).

The bootstrap shrinks dramatically. Documentation simplifies. Bugs disappear.

### Open Question Resolved: Where Does `release-status` Skill Sit?

`release-status` is a read-only navigation aid (stage 0–5 + recommended
next step). It's complementary to STATUS.md, not redundant. Keep as-is.

Optional enhancement (Round 2 Risk 5): extend `release_readiness.py` to
include a per-package status table. Useful but not required. Defer.

---

## 6. Round 2 Gaps Resolution Status

| Gap | Status after Round 3 |
|-----|----------------------|
| **A** — task_creation_plan.md schema | **Resolved** (section 7 below) |
| **B** — Cross-release UI screen dependency | Deferred with workaround (requirements explicitly note "modifies HomeScreen from 0.0.0"; implementing agent reads existing screen file) |
| **C** — propose_after.py UI layer awareness | **Partially resolved**: when plan exists, propose_after uses plan's after-entries directly (deterministic). Layer-aware heuristic for plan-less cases requires task_ordering_rules.yaml extension — deferred as separate task |
| **D** — _agent_state.md fragility | **Resolved**: replace with output-file polling. Each remediation agent writes to a unique path; orchestrator scans the directory for output files instead of tracking agent IDs |
| **E** — Phase 6 atomicity | **Resolved**: `--dry-run` flag + after-chain safety net (section 1) |
| **F** — Validation overlap (Case B vs. finalize) | **Resolved**: Case B → validation orchestration task (structural). release-begin-impl-finalize Phase 3 → semantic. After-chain check belongs in the validation task only (NOT in finalize) |
| **G** — task-create-code ordering vs. plan ordering | **Resolved**: plan's `## Execution Order` section is authoritative when plan exists. task-create-code zero-mode reads it before falling back to next_tasks.py semver |

Net new gaps from Round 3 (H–P) are all addressed in this document or
explicitly deferred with a stated workaround.

---

## 7. Concrete Schema for `task_creation_plan.md`

### File Location

`requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/<explore_task_folder>/task_creation_plan.md`

(Sibling to `goal.md` in the explore task folder.)

### Schema

```markdown
---
plan_id: PLAN-0.0.1-v1
release: 0.0.1
created: 2026-04-25
created_by: release-begin-impl Phase 2c
status: draft        # draft | approved | archived
approved_by: ""      # filled at Phase 5 user gate
approved_on: ""      # filled at Phase 5 user gate
explore_task: TASK-PROC-035-07
total_tasks: 12
total_effort: { M: 5, S: 4, L: 3 }
packages_covered: [PKG-0.0.1-data, PKG-0.0.1-pairing, ...]
---

# Task Creation Plan: Release 0.0.1

## Layer Dependency Rules

This release follows: **data → domain → presentation → test → integration**

Cross-package overrides (any explicit deviations):
- (none) | OR | "PKG-X must complete before PKG-Y because Y consumes X's API"

## Execution Order

Packages are created in this order (drives task-create-code zero-mode picking):

1. PKG-0.0.1-data — Transfer Data Model
2. PKG-0.0.1-pairing — Transfer Pairing
3. PKG-0.0.1-send — QR Transfer Send
4. PKG-0.0.1-receive — QR Transfer Receive

## Architecture Notes

(Free-form prose — observations the Planner made by reading all features)

- **Shared abstraction**: `TransferSession` entity used by all transfer
  packages. Created in PKG-0.0.1-data; referenced by subsequent packages.
- **HomeScreen ownership**: existing screen from release 0.0.0. Send/Receive
  tasks ADD entry points; do NOT recreate. Implementing agent must read
  `lib/presentation/screens/home_screen.dart` to learn current structure.
- **Test strategy**: unit tests per data/domain task; widget tests for new
  screens; integration test per end-to-end flow (FLOW-002, FLOW-003).
- **Detected pre-existing implementation**: AC-12 of feat_data_model
  (`TransferSession.fromJson`) is already implemented in
  `lib/domain/transfer_session.dart`. Planned as `task_type: verify`.

## Planned Tasks

### PKG-0.0.1-data: Transfer Data Model

#### Task 1: Implement TransferSession entity and repository

```yaml
task_name: Implement TransferSession entity and repository
task_type: implement              # implement | verify | scribble | scribble_to_flutter
target_package: PKG-0.0.1-data
covers_acs: [AC-01, AC-02, AC-03]
effort: M
layer: data
after: []
opus_recommended: false
req_path: requirements_tasks/functional/shared/epic_data_transfer/feat_data_model/requirements.md
req_commit: d357041e
implementation_notes: |
  Pure Dart, no Flutter deps. JSON serialization via json_annotation.
```

**Rationale**: AC-01–03 all describe the TransferSession entity. Splitting
would force shared test fixtures with no benefit.

#### Task 2: TransferSession persistence layer

```yaml
task_name: TransferSession persistence layer
task_type: implement
target_package: PKG-0.0.1-data
covers_acs: [AC-04, AC-05]
effort: S
layer: data
after: ["#PKG-0.0.1-data:Task 1"]   # internal reference; resolved to TASK-ID when created
opus_recommended: false
req_path: requirements_tasks/functional/shared/epic_data_transfer/feat_data_model/requirements.md
req_commit: d357041e
```

**Rationale**: Persistence depends on the entity model.

### PKG-0.0.1-pairing: Transfer Pairing

(...further entries follow same pattern...)
```

### Schema Notes

- **Internal references**: `#PKG-X:Task N` notation for after-chain
  references to tasks not yet created. Resolved to actual TASK-IDs by
  `task-create-code` when each task is created (it reads previously created
  task IDs and substitutes).
- **`task_type` field**: drives which skill the orchestration task invokes.
- **`covers_acs` set semantics**: order doesn't matter; equality is set-based.
- **`effort` matches CLAUDE.md size scale**: XS, S, M, L, XL.
- **`req_commit`**: snapshot of the requirement at planning time. Allows
  drift detection (Round 2 Gap F).

### Parsing Strategy (`scripts/parse_task_creation_plan.py`)

Use a lightweight Markdown + YAML parser:

1. Parse top-level frontmatter (YAML).
2. Walk Markdown headings: each `### PKG-...` opens a package section, each
   `#### Task N:` opens a task entry.
3. Extract YAML block under each task entry.
4. Capture rationale prose (everything between YAML close and next `####` /
   `###` heading).
5. Return JSON: `{ frontmatter, packages: [{ id, name, tasks: [...] }] }`.

~80 lines of Python. Reusable across (a) summary script, (b) conformance
check, (c) reconciliation script, (d) task-create-code consumer.

### Plan Versioning

Per Gap J: plan is append-only. New versions added as `## Plan v2 — [date]`
sections beneath v1. Each version has:

```yaml
plan_id: PLAN-0.0.1-v2
parent_plan_id: PLAN-0.0.1-v1
created: 2026-04-26
status: draft
changes_from_v1: |
  - Added Task TASK-FUNC-007-15 (off-plan, user added on 2026-04-26)
  - Modified scope of Task TASK-FUNC-007-12 (covers AC-01, AC-02 — was AC-01–03)
```

`task-create-code` consumes the latest non-archived version.

---

## 8. Quality Rating and Implementation Readiness

### Coverage Assessment

After Rounds 1–3, every architectural concern has either:
- A concrete spec (Phase 6 sequence, plan schema, script signatures), OR
- A defined workaround (cross-release UI dependencies, package vs. release
  status bifurcation), OR
- Been explicitly deferred with rationale.

### Quality Rating: **8.5 / 10 — Implementation-Ready**

Strengths:
- Architecture decisions are correct (distributed pipeline, self-perpetuating
  chain, plan-as-checkpoint).
- All high-severity gaps from Round 2 are resolved.
- Script vs. LLM boundaries are concrete and ROI-positive.
- Phase 6 sequence is failure-safe via after-chain.
- Responsibility matrix is unambiguous; duplications are eliminated.
- Schema for task_creation_plan.md is concrete.

Remaining minor gaps (won't block implementation):
- Cross-release UI dependency (workaround stated).
- propose_after.py full layer awareness (only plan-driven case fully fixed;
  heuristic case deferred to a separate cleanup).
- Plan versioning mid-flight (mechanism is light; will solidify during
  implementation if friction shows up).
- Package vs. release `status: active` bifurcation (separate cleanup).

### Is Another Round Needed?

**No.** The architecture is settled. The next step is implementation
planning — converting these analyses into concrete file edits, scripts,
and skill rewrites. That can be done by:

1. `architecture-advisor` agent — produce a unified implementation plan
   (which agents do what, in what order, with what file paths).
2. Alternatively: a follow-up Sonnet session inline that breaks the work
   into 5–7 implementation tasks (each with its own goal.md), tracked under
   REQ-PROC-035 as siblings to TASK-PROC-035-07.

### What This Round Delivered

1. **Phase 6 sequence locked in**, with failure recovery matrix and
   dry-run flag specification.
2. **Eight new gaps identified** beyond Round 2; all resolved or deferred
   with rationale.
3. **Seven scripts specified** that take work off the LLM, with ROI estimate.
4. **Context-window threshold mechanism** specified (script + project rule).
5. **Responsibility matrix** drawn, four duplications eliminated.
6. **Concrete schema** for task_creation_plan.md, with versioning policy.
7. **All Round 2 gaps resolved or explicitly deferred.**

### Recommended Next Action for the User

Hand the consolidated round 1–3 outputs to `architecture-advisor` and ask
for a unified implementation plan: ordered list of agents, file paths,
quality criteria. After that plan is approved, implementation can run
through normal `code-complex` / `task-resolve` workflows for each chunk.

Estimated implementation effort across all changes:
- 7 new scripts: ~13 hours
- Skill rewrites (release-begin-impl, task-create-code, claude-automated-mode,
  new release-begin-impl-finalize): ~10 hours
- Doc updates (CLAUDE.md, RELEASES.md, REQ-PROC-035): ~3 hours

Total ~26 hours of implementation work, distributed across many small
sessions via the new chain itself.

---

## Appendix A: Open Questions Answered

These questions surfaced during the gathering phase and are answered here
for record.

**Q: Should claude-automated-mode know about the plan?**
A: Indirectly. The chain reads the plan via `task-create-code`. Bootstrap
itself (the remaining Case C in automated-mode) is plan-agnostic.

**Q: Does the explore task need `writes_requirements: true` after Round 3?**
A: Optional. The after-chain protects against premature execution. The flag
is only useful as a secondary guard during the interactive session (so
unrelated impl tasks don't surface in next_tasks.py while the user is
mid-`release-begin-impl`). Keep it but it's not load-bearing.

**Q: What if the user starts a new `release-begin-impl` while one is in
progress?**
A: The skill's Phase 0 should detect an in-progress explore task with
matching target_release and offer to resume vs. abandon. Defer the resume
mechanism; for now, abandon-and-restart is acceptable (the explore task
gets cancelled).

**Q: How does `release-begin-impl-finalize` know which explore task / plan
to use?**
A: It reads RELEASES.md to find the active release, then searches the
release_preparation tasks folder for an explore task with matching
`target_release` and `status: completed`. The plan in that folder is the
one to use.
