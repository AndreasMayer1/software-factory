---
task_id: TASK-PROC-035-08
type: impl
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-25
started: 2026-04-25
effort: XL
created: 2026-04-25
after: [TASK-PROC-035-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-05, SEC-06, SEC-07]
target_package: "Transfer Data Model"
scope_description: "Implement distributed-pipeline redesign: 7 new scripts, create_orchestration_task.py changes, release-begin-impl rewrite, task-create-code zero-mode plan integration, new release-begin-impl-finalize skill, claude-automated-mode simplification, CLAUDE.md rule"
release_description: ""
opus_recommended: true   # reason: urgency 4 + impact 4; cross-cutting pipeline redesign touching scripts, 4 skills, and CLAUDE.md
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: d357041e
  file: ../requirements.md
---

# Goal: Implement Distributed Release Pipeline Redesign

## Objective

Implement the full distributed-pipeline redesign documented in
`plans_and_protocols/protocol.md` of TASK-PROC-035-07.

The redesign replaces the monolithic `release-begin-impl` skill and the
`claude-automated-mode` Bootstrap Rule with a distributed self-perpetuating
orchestration chain. Implementation is divided into five dependency-ordered
groups; Groups 1 and 5 are independent and may be started without waiting
for the others.

For complete requirements at task creation time:
```
git show d357041e:requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md
```

Current requirements: ../requirements.md

Source of truth for all design decisions:
`requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-25_explore_release-active-status-analysis/plans_and_protocols/protocol.md`

---

## Scope

### In Scope

**Group 1 — New Python scripts** (independent, no dependencies):

| Script | Purpose |
|--------|---------|
| `scripts/parse_task_creation_plan.py` | Parse `task_creation_plan.md` → JSON; shared infrastructure used by all scripts below |
| `scripts/check_task_against_plan.py --task T --plan P` | Compare task goal.md frontmatter vs plan entry; exit 0 (match), 1 (mismatch + diff), 2 (no plan entry) |
| `scripts/reconcile_after_chains.py --release V [--plan P] [--apply]` | Build dependency graph from all impl task `after:` fields; compare with plan; optionally apply missing entries |
| `scripts/summarize_plan.py --plan P` | Generate 1-page plan summary (task count, effort distribution, coverage, risk flags) for Phase 5 user gate |
| `scripts/check_requirement_implementation.py --requirement R` | Grep `lib/` for per-AC implementation traces; output per-AC verdict: `likely_implemented` / `likely_missing` / `uncertain` |
| `scripts/find_orchestration_tasks.py --status S` | Detect orchestration tasks by structural signature (`target_release` set AND `scope_description` begins with "Orchestration:") |
| `scripts/should_use_agents.py --release V` | Compute total requirement file bytes for release; output JSON with `verdict: agents_required / orchestrator_direct` at 30KB/5-file threshold |

**Group 2 — Script and skill changes** (depends on Group 1):

- `scripts/create_orchestration_task.py`: add `--dry-run` flag (same exit codes, no file writes), `--after-task TASK-ID` (appends to `after:` in template), `--plan-path PATH` (adds `plan_path:` to template frontmatter); replace Exit 3 with validation orchestration task creation; add `fcntl.flock` concurrency lock on `.create_orchestration_task.lock`
- `.claude/skills/release-begin-impl/skill.md`: full rewrite — phases 0/1/2/2b/2c/5/6 as specified in `protocol.md §2a`; remove old phases 3/4/5; add Decision Domains table; Phase 2c Planner spec; Phase 5 user gate with `summarize_plan.py`; Phase 6 complete sequence with dry-run pre-check

**Group 3 — Template and skill integration** (depends on Group 2):

- Orchestration task `goal.md` template inside `create_orchestration_task.py`: add `plan_path:` and `after:` frontmatter fields; replace acceptance criteria with 3-step self-perpetuating ACs (task-type-aware: `task-create-code` for implement/verify/scribble_to_flutter; `ui-create-scribble` for scribble)
- `.claude/skills/task-create-code/skill.md`: zero-parameter mode reads plan via `plan_path` from orchestration task frontmatter; uses plan's `covers_acs`, `effort`, `layer`, `after`, `task_type` as authoritative defaults; skips user confirmation when plan entry exists; adds Phase 6 plan conformance check via `check_task_against_plan.py`

**Group 4 — New skill and simplification** (depends on Groups 1–3):

- `.claude/skills/release-begin-impl-finalize/skill.md`: NEW skill with 5 phases as specified in `protocol.md §2b` (coverage audit + plan conformance, after-chain reconciliation, semantic validation per feature, user review gate, finalize + commit)
- `.claude/skills/claude-automated-mode/skill.md`: remove Case A (bootstrap orchestration task creation) and Case B (bootstrap validation task); retain Cases C (completion summary) and D (runnable tasks, proceed); add transition note: do NOT remove Case A until all in-flight old-template orchestration tasks reach terminal status

**Group 5 — CLAUDE.md rule** (independent):

- `CLAUDE.md`: add context-window rule to §7 (Coding Standards): "Skills reading requirement files must call `scripts/should_use_agents.py` before deciding to read inline. Hard threshold: 30KB total OR 5 files. Structural fan-out phases always use agents regardless of size."

### Out of Scope

- Implementation of `release-begin-impl` itself (running it in production; that is a future session task)
- Changes to `scripts/next_tasks.py` beyond what is already implemented
- `propose_after.py` layer-awareness enhancement (deferred; see protocol.md §9)
- `release-status` per-package table extension (optional; see protocol.md §9)
- `RELEASES.md` lifecycle definition text update (minor edit; can be done standalone)

---

## Acceptance Criteria

### Group 1 — Scripts

- [ ] `parse_task_creation_plan.py`: given a valid `task_creation_plan.md`, outputs JSON with `frontmatter`, `packages`, and per-task entries (name, task_type, covers_acs, effort, layer, after, etc.)
- [ ] `check_task_against_plan.py`: exits 0 on exact match, 1 with diff on mismatch (target_package, covers_acs set equality, layer; effort ±1 allowed), 2 when no plan entry exists for the task
- [ ] `reconcile_after_chains.py`: without `--apply`, lists all missing `after:` entries per task; with `--apply`, edits goal.md files in-place to add them
- [ ] `summarize_plan.py`: outputs a structured summary including total tasks, effort counts (XS/S/M/L/XL), layer distribution, packages covered, opus_recommended count, verify-only count, and any risk flags
- [ ] `check_requirement_implementation.py`: for each AC in the requirement, outputs one of `likely_implemented`, `likely_missing`, `uncertain`; uses grep of `lib/` against entity/screen names extracted from the AC text
- [ ] `find_orchestration_tasks.py --status pending,in_progress`: lists matching orchestration task IDs and paths; exits 0 even when empty
- [ ] `should_use_agents.py --release V`: outputs JSON with `total_bytes`, `file_count`, `verdict` (`agents_required` above 30KB or 5 files, else `orchestrator_direct`), and per-file breakdown

### Group 2 — create_orchestration_task.py + release-begin-impl

- [ ] `create_orchestration_task.py --dry-run --after-task X`: exits with the same code it would on a real run but writes no files and allocates no IDs
- [ ] `create_orchestration_task.py --after-task TASK-ID`: created goal.md contains `after: [TASK-ID]` in frontmatter
- [ ] `create_orchestration_task.py --plan-path PATH`: created goal.md contains `plan_path: "PATH"` in frontmatter
- [ ] `create_orchestration_task.py` when all packages covered: creates a validation orchestration task (goal.md describes structural checks and writes `validation_report.md`) instead of returning Exit 3
- [ ] `create_orchestration_task.py` concurrency lock: `fcntl.flock` wraps the entire creation body; `.create_orchestration_task.lock` is created next to the script
- [ ] `release-begin-impl` skill: phases 0/1/2/2b/2c/5/6 are present; old phases 3/4/5 are absent; Decision Domains table is present; Phase 2c Planner spec matches protocol.md §2a; Phase 6 sequence matches protocol.md §3

### Group 3 — Orchestration task template + task-create-code

- [ ] Orchestration task goal.md template contains `plan_path:` and `after:` frontmatter fields
- [ ] Template acceptance criteria contain exactly 3 steps; Step 1 text is task-type-aware (task-create-code vs ui-create-scribble)
- [ ] `task-create-code` zero-parameter mode: when orchestration task frontmatter has `plan_path`, the skill reads that plan; uses plan entry's `covers_acs`, `effort`, `layer`, `after`, `task_type` as authoritative defaults; skips user confirmation step; prints "Using approved plan entry: [name] for [package]"
- [ ] `task-create-code` Phase 6 (post-write): calls `check_task_against_plan.py`; on exit 1 shows diff to user (interactive) or writes `question.md` (automated); on exit 2 skips silently

### Group 4 — release-begin-impl-finalize + claude-automated-mode

- [ ] `release-begin-impl-finalize` skill file exists at `.claude/skills/release-begin-impl-finalize/skill.md`
- [ ] Skill contains exactly phases 1–5 as described in protocol.md §2b
- [ ] Skill never reads feature requirements.md in orchestrator context (only agents do)
- [ ] `claude-automated-mode` skill: Case A logic is absent (or wrapped in a clearly labelled transition block with removal condition); Case B logic is absent; Cases C and D are present and clearly labelled
- [ ] Transition note present in claude-automated-mode: "Do NOT remove Case A until all in-flight old-template orchestration tasks have reached terminal status"

### Group 5 — CLAUDE.md

- [ ] CLAUDE.md §7 contains the context-window rule referencing `should_use_agents.py`, the 30KB/5-file threshold, and the fan-out exception

---

## Verification

The following verification steps must be run after implementation and before calling `task-complete`. Due to the pipeline's central role in the autorun workflow, all steps are mandatory.

### V1 — Unit verification per Group 1 script

For each of the 7 scripts, run with a valid fixture and confirm exit 0:
```bash
# parse_task_creation_plan.py
python3 scripts/parse_task_creation_plan.py --plan <path-to-sample-plan> | python3 -m json.tool > /dev/null && echo "PASS"

# check_task_against_plan.py — matching case
python3 scripts/check_task_against_plan.py --task TASK-PROC-035-07 --plan <plan> && echo "exit 0 PASS"

# find_orchestration_tasks.py — no matches is still exit 0
python3 scripts/find_orchestration_tasks.py --status pending,in_progress && echo "exit 0 PASS"

# should_use_agents.py
python3 scripts/should_use_agents.py --release 0.0.1 | python3 -m json.tool | grep verdict && echo "PASS"
```
Also verify each script exits non-zero on invalid input:
```bash
python3 scripts/parse_task_creation_plan.py --plan /nonexistent; [ $? -ne 0 ] && echo "non-zero PASS"
```

### V2 — Regression: existing autorun behavior (Case D) unchanged

Verify that `claude-automated-mode` still proceeds normally when runnable tasks exist:
1. Confirm Case D block is present and its behavior description is unchanged from the pre-redesign skill.
2. Verify no code path in Case D calls `create_orchestration_task.py`.

### V3 — Integration: Phase 6 dry-run sequence

Simulate Phase 6 steps 6.2–6.5 in isolation on a test fixture:
```bash
# Step 6.2: dry-run must exit 0 when no active release conflicts exist
python3 scripts/create_orchestration_task.py --dry-run --after-task TASK-PROC-035-07 \
  && echo "6.2 dry-run PASS"

# Step 6.5: real run produces a goal.md with correct fields
python3 scripts/create_orchestration_task.py \
  --after-task TASK-PROC-035-07 \
  --plan-path "requirements_tasks/.../task_creation_plan.md"
# Verify produced goal.md:
grep "after: \[TASK-PROC-035-07\]" <new-task-goal.md> && echo "after-field PASS"
grep "plan_path:" <new-task-goal.md> && echo "plan_path-field PASS"
```
Clean up the test task after verification.

### V4 — Chain integrity

After running V3, confirm:
- The created orchestration task has exactly 3 acceptance criteria steps
- Step 2 contains `create_orchestration_task.py --after-task`
- Step 3 contains `task-complete`

### V5 — Skill structure check: release-begin-impl-finalize

Read the new skill file and verify:
```bash
# Forbidden sections must be absent
grep -i "## Testing\|## Open Questions\|## Version History\|## Implementation Roadmap" \
  .claude/skills/release-begin-impl-finalize/skill.md && echo "FORBIDDEN SECTION FOUND" || echo "V5 PASS"
```
Also confirm the skill contains Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 headings.

### V6 — Transition safety: Case A removal guard

Before removing Case A from `claude-automated-mode`:
```bash
grep -i "transition\|old.template\|do not remove" \
  .claude/skills/claude-automated-mode/skill.md && echo "transition note PASS" || echo "MISSING - do not remove Case A yet"
```
Case A may only be removed after this check prints "transition note PASS" AND the operator confirms all in-flight old-template orchestration tasks are terminal.

### V7 — CLAUDE.md rule present

```bash
grep "should_use_agents" CLAUDE.md && echo "V7 PASS" || echo "MISSING context-window rule"
```

---

## Notes

- **Group ordering is strict**: Groups 2–4 must not be started before Group 1 scripts exist and are importable. Group 5 is independent.
- **Script tests**: place any fixture files needed by V1–V4 under `plans_and_protocols/test_fixtures/` for this task. Clean them up as part of `task-complete`.
- **Token-sensitive files**: `.claude/skills/` files must use inline `(reason)` parentheticals for context, NOT `///` Dart-style WHY comments.
- **`release-begin-impl-finalize` INDEX.md**: after creating the new skill, update `.claude/skills/INDEX.md` and `.claude/factory_flows.md` via the `claude-modify-skill` skill.
- **Implementation approach**: use `task-resolve` skill for Groups 1 and 5 (script/doc work); use `claude-modify-skill` for Groups 2–4 (skill file rewrites). A single impl session can cover one Group; multiple sessions expected across Groups.
