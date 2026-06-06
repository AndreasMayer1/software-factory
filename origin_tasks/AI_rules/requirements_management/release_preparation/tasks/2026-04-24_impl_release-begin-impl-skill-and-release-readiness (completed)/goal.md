---
task_id: TASK-PROC-035-06
type: impl
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-24
started: 2026-04-24
completed: 2026-04-24
after: []
awaiting: []
awaiting_note: ""
target_package: "Transfer Data Model"
covers:
  acceptance_criteria: []
  sections: [SEC-06]
scope_description: "Rename requ-prep-release → release-begin-impl; integrate orchestration task creation; delete task-create-code-orchestrator skill; add release_readiness.py script + release-status skill; fix create_orchestration_task.py template; update INDEX.md / factory_flows.md / RELEASES.md docs"
release_description: ""
opus_recommended: false
requirements_version:
  commit: unknown
  file: ../requirements.md
---

# Goal: release-begin-impl Skill + Release Readiness Refactor

## Vision (abstract goal — use this for final verification)

A developer returning after a multi-week break should be able to answer "what do I do next
for the release?" with a single command, and then execute that step without needing to
remember skill names or sequences.

Concretely, after this task is done:

1. **`/release-status`** — shows exactly which stage the release is at and recommends the
   next command. No guessing required.
2. **`/release-begin-impl`** — is the single, obviously-named entry point for "I have
   verified requirements, now start the implementation phase." It does everything in one
   step: activates the release, creates the orchestration task, and tells the user to start
   the autorun. The developer cannot accidentally skip a step.
3. **The autorun finds orchestration tasks automatically** — because they now have
   `target_release` set. No manual intervention needed to restart a broken orchestration chain.
4. **Setting `status: active` manually in RELEASES.md is visibly prohibited** — the
   lifecycle definition says so, and there is a skill to do it correctly.

**Final verification question** (ask at the end of implementation):
> "If a developer returns after 4 weeks with no memory of where they were, can they run
> `/release-status`, understand the situation, and execute the correct next step — without
> reading any other documentation?"

If the answer is yes for all stages (0–5), the task is done. If any stage leaves the
developer confused or requires them to remember something, there is a gap to fix.

---

## Context (do not re-research — read this instead)

This task results from a deep analysis session on 2026-04-24. The full analysis is in:
`requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-24_explore_release-active-status-analysis/plans_and_protocols/`

### What was discovered

1. **`requ-prep-release` is badly named and incomplete.** The name is ambiguous ("prepare" could
   mean preparing the implementation OR preparing the release for shipping). The skill sets
   `status: active` in RELEASES.md at Phase 6 but then stops — it does NOT create the
   orchestration task that tells the autorun to start creating impl tasks. The user therefore
   had to manually set the release to `active` and manually call `task-create-code-orchestrator`,
   because they didn't know `requ-prep-release` was the right skill.

2. **`task-create-code-orchestrator` is a redundant wrapper.** It wraps
   `scripts/create_orchestration_task.py` in a skill. But since `requ-prep-release` Phase 6
   is the only place this should ever be called, the standalone skill has no independent use
   case. It should be deleted; the script call moves into `requ-prep-release` (renamed).

3. **`create_orchestration_task.py` template is missing `target_release`.** Orchestration tasks
   created by the script have no `target_release` in their frontmatter. This makes them
   invisible to `next_tasks.py` (which only shows tasks with `target_package` or
   `target_release`). The autorun therefore cannot find them. Fix: add `target_release: {version}`
   to the `_GOAL_TEMPLATE`.

4. **RELEASES.md lifecycle definition is inaccurate.** It says `active = "At least one task is
   in_progress"` — but in practice `active` is set by `requ-prep-release` Phase 6 BEFORE any
   impl task exists, as a signal that implementation is approved to begin. The definition
   should reflect the actual semantics.

5. **No status overview exists.** After a multi-week break, the user has no way to quickly
   see where they stand in the release workflow (do requirements exist? are tasks created?
   are all tasks done?). A script + skill would provide this.

6. **The release workflow sequence is not documented in `factory_flows.md`.** The file has
   the information-flow diagram but not the sequential "which skill to run when" guide.

### The complete intended release workflow (as designed)

```
Phase A — Requirements (done once per release):
  1. requ-explore              Document requirements
  2. release-plan              Assign ACs/sections to packages in RELEASE_BACKLOG.md
  3. requ-derive-from-flow     (if needed) derive requirements from user flows
  4. requ-assign-packages      Bulk-assign target_package to unassigned ACs

Phase B — Begin Implementation (THIS SKILL):
  5. release-begin-impl        ← was: requ-prep-release
     - Verifies requirements are ready (check_requirements_ready.py exits 0)
     - Checks scope coverage (existing multi-phase workflow, Phases 0–5)
     - Sets RELEASES.md status: active (Phase 6)
     - Calls create_orchestration_task.py (NEW in Phase 6)
     - Informs user: "Next step: start autorun with /autorun"

Phase C — Autorun creates and executes impl tasks:
  6. /autorun (start)          Bootstrap detects uncovered ACs → orchestration task created
     → task-create-code        (per package, iterative)
     → code-simple/complex     (per impl task)
     → task-complete           (per impl task)

Phase D — Release execution:
  7. /release                  Pre-flight → smoke test → merge/tag/push → release notes
```

### Files to read before implementing

- `.claude/skills/requ-prep-release/skill.md` — current skill (rename + extend)
- `.claude/skills/task-create-code-orchestrator/skill.md` — skill to delete
- `scripts/create_orchestration_task.py` — template to fix
- `.claude/skills/INDEX.md` — update table + add workflow sequence section
- `.claude/factory_flows.md` — add release workflow sequence section
- `requirements_tasks/RELEASES.md` — fix lifecycle definition
- `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md`
  (REQ-PROC-035) — update SEC-06 to reflect new skill name
- `requirements_tasks/process/AI_rules/workflows/release_workflow/requirements.md`
  (REQ-PROC-036) — update SEC-06 (requ-prep-release Integration) to reflect new name/behavior

---

## Acceptance Criteria

### AC-1 — Rename and extend the skill

- [ ] Directory renamed: `.claude/skills/requ-prep-release/` → `.claude/skills/release-begin-impl/`
- [ ] `skill.md` updated: name, description, all internal references
- [ ] Phase 6 extended:
  - After setting `status: active` in RELEASES.md
  - Call `python3 scripts/create_orchestration_task.py`
  - Handle exit codes: 0 (success, show task ID), 1 (no active release — impossible here, but handle), 2 (task already exists — tell user, do not error), 3 (nothing to do — all packages covered, tell user), 4 (error — show stderr)
  - On exit 0: commit the orchestration task using `claude-commit` skill
  - Final message to user: "Release X.Y.Z is now active. Orchestration task [ID] created at [PATH]. **Next step**: start the autorun with `/autorun` to begin creating implementation tasks. You can also do other work first — the orchestration task will wait."

### AC-2 — Delete `task-create-code-orchestrator`

- [ ] Directory deleted: `.claude/skills/task-create-code-orchestrator/`
- [ ] All references in INDEX.md and factory_flows.md removed

### AC-3 — Fix `create_orchestration_task.py` template

- [ ] `_GOAL_TEMPLATE` in `scripts/create_orchestration_task.py` includes `target_release: {version}`
  - Field goes between `scope_description` and `release_description` (or wherever fits the standard order)
  - `version` is already in the format call — just add the field
- [ ] Verify: after the fix, a task created by the script has `target_release` set
- [ ] Verify: `python3 scripts/next_tasks.py` shows the task after it's created

### AC-4 — Create `scripts/release_readiness.py`

New script that reads system state and prints a human-readable summary of where the
project stands for the NEXT (lowest planned or active) release.

Output format (example):
```
Release Readiness: 0.0.1 (Alpha – Data Transfer)
Status: planned

Stage 3 of 5 — Requirements written, packages assigned, ready to begin implementation

✓ Stage 1: Requirements-authoring tasks exist (check_requirements_ready.py: READY)
✓ Stage 2: Package assignments complete (all ACs have target_package)
✓ Stage 3: Requirements ready (no pending/in_progress writes_requirements tasks)
○ Stage 4: Implementation in progress (release not yet active)
○ Stage 5: All impl tasks completed (0.0.1 not yet released)

Recommended next step: Run /release-begin-impl to activate release 0.0.1
  and create the first orchestration task.
```

Stages to detect:
- Stage 0: No requirements-authoring tasks exist for the next release
  → "Run /requ-derive-from-flow or /requ-explore to create requirements"
- Stage 1: Requirements-authoring tasks exist but not all completed
  → list blocking tasks
- Stage 2: Requirements complete, but packages not all assigned
  → "Run /requ-assign-packages"
- Stage 3: Packages assigned, release not yet active
  → "Run /release-begin-impl"
- Stage 4: Release active, impl tasks being created/executed
  → show N completed / M total impl tasks, note if autorun is running
- Stage 5: All impl tasks done
  → "Run /release to cut the release"

Implementation notes:
- Read `requirements_tasks/RELEASES.md` for active/planned release
- Reuse `check_requirements_ready.py` logic (import or subprocess)
- Use `scripts/next_tasks.py` output or direct task scanning for impl task counts
- Check `RELEASE_BACKLOG.md` for package assignment completeness
- Check `automation/.automated_mode` to detect if autorun is running

### AC-5 — Create `release-status` skill

New file: `.claude/skills/release-status/skill.md`

Simple skill: run `python3 scripts/release_readiness.py`, show output to user. No other logic.

### AC-6 — Update `scripts/INDEX.md`

- [ ] Remove row for `task-create-code-orchestrator`
- [ ] Rename `requ-prep-release` → `release-begin-impl` with updated description:
  "Begin implementation of a release: verify requirements, activate release, create orchestration task"
- [ ] Add `release-status` row: "Show where you are in the release workflow"
- [ ] Add a **Release Workflow** section with the sequential skill list (see Phase A–D above)

### AC-7 — Update `factory_flows.md`

- [ ] Add a **Release Workflow Sequence** section (after the existing information flow diagram)
  with a simple table or numbered list showing Phase A → B → C → D skills in order
- [ ] Remove reference to `task-create-code-orchestrator` from any diagram or table
- [ ] Update any reference to `requ-prep-release` → `release-begin-impl`

### AC-8 — Update `requirements_tasks/RELEASES.md` lifecycle definition

Replace:
```
- **active**: At least one task for this release is `in_progress`
```
With:
```
- **active**: Requirements verified, implementation approved to begin. Set by `/release-begin-impl`.
  Do NOT set manually. One release may have `status: active` at a time.
```

### AC-9 — Update requirements files

- `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md`
  (REQ-PROC-035):
  - Update any reference to `requ-prep-release` → `release-begin-impl`
  - Update SEC-06 heading "requ-prep-release Integration" → "release-begin-impl Integration"
  - Update SEC-06 body: Phase 6 now also calls `create_orchestration_task.py` and informs
    the user to start the autorun
  - **Add a new section** (SEC-07 or append) documenting `release_readiness.py` and the
    `release-status` skill: what they do, when to use them, what stages they detect
    (Stages 0–5 as described in AC-4 above)

- `requirements_tasks/process/AI_rules/workflows/release_workflow/requirements.md` (REQ-PROC-036):
  - Update SEC-06 frontmatter: `name: "release-begin-impl Integration"`,
    `heading: "## release-begin-impl Integration"`
  - Update all references to `requ-prep-release` → `release-begin-impl` throughout the file,
    including: "When to Use" section, "When NOT to Use" section, SEC-06 body, Developer
    Guidelines / Common Pitfalls section
  - The "Common Pitfalls" entry currently says:
    "`status: active` not set: If `requ-prep-release` was not run, the pre-flight script will
    abort. Do not work around this by manually editing RELEASES.md mid-release."
    → Update to reference `release-begin-impl`

- `.claude/skills/release/skill.md`:
  - Line 10 currently says: "Use this skill when you are ready to cut a release that has
    already been prepared with `/requ-prep-release`."
  - Update to: "Use this skill when you are ready to cut a release that has already been
    prepared with `/release-begin-impl`."

- **Do NOT edit `requirements.md`** (project root) — it is auto-generated by
  `scripts/merge_requirements.ps1` and will be regenerated automatically.

### AC-10 — Verify `next_tasks.py` output after AC-3

After fixing the `create_orchestration_task.py` template:
- [ ] Run `python3 scripts/create_orchestration_task.py` (requires active release — set
  RELEASES.md 0.0.1 to `active` temporarily, run script, then reset to `planned`)
- [ ] Confirm the created task's goal.md contains `target_release: "0.0.1"`
- [ ] Confirm `python3 scripts/next_tasks.py` lists the task
- [ ] Delete the test task; reset RELEASES.md back to `planned`

---

## Implementation Notes

- **Skill writing rules**: Skills are token-sensitive. Descriptions must be as short as possible.
  No `///` WHY comments. Use inline `(reason)` if needed. Each line costs tokens.
- **Skill name in frontmatter**: Must match directory name exactly (`release-begin-impl`).
- **Delete skill directory**: Use `rm -rf .claude/skills/task-create-code-orchestrator/`
- **Commit strategy**: One commit per logical group:
  1. Script fix (`create_orchestration_task.py`) + AC-10 verification
  2. Skill rename + extension (`release-begin-impl` skill.md)
  3. Skill deletion (`task-create-code-orchestrator/`)
  4. New script + skill (`scripts/release_readiness.py` + `.claude/skills/release-status/`)
  5. Documentation + requirements (INDEX.md, factory_flows.md, RELEASES.md lifecycle,
     REQ-PROC-035, REQ-PROC-036, `.claude/skills/release/skill.md`)
- **Do NOT implement `release-begin-impl` in a worktree** — this is a process/skill task,
  not Flutter/Dart code. Work directly in the main tree.
- **Use `task-complete` skill when done.**

---

## Final Verification Protocol

Before calling `task-complete`, step back from the ACs and answer the Vision question:

> "If a developer returns after 4 weeks with no memory of where they were, can they run
> `/release-status`, understand the situation, and execute the correct next step — without
> reading any other documentation?"

Walk through each stage mentally:
- **Stage 0** (no requirements yet): Does `/release-status` tell them to run `/requ-derive-from-flow`?
- **Stage 3** (requirements done, not yet active): Does `/release-status` tell them to run `/release-begin-impl`?
- **Stage 4** (active, autorun needed): Does `/release-status` tell them to start `/autorun`?
- **Stage 5** (all done): Does `/release-status` tell them to run `/release`?

Also verify:
- [ ] The old skill name `requ-prep-release` does not appear in any file the developer
  would encounter during normal use (skills, INDEX.md, factory_flows.md, RELEASES.md,
  REQ-PROC-035, REQ-PROC-036). Historical task goal.md files (completed tasks) are exempt.
- [ ] `task-create-code-orchestrator` does not appear in INDEX.md or factory_flows.md.
- [ ] Manually setting `status: active` in RELEASES.md is explicitly discouraged at the
  point where a developer would encounter it (the lifecycle section).

**Note on gaps**: The ACs are detailed but not exhaustive. If during implementation you
discover something that serves the Vision but is not listed as an AC, implement it and
document it in the protocol. If you discover a conflict or ambiguity, write a `question.md`
rather than guessing.

---

## Out of Scope

- Changes to `requ-prep-release` Phases 0–5 (the multi-phase requirements check workflow)
- Changes to the `release` skill (release execution)
- Changes to `release-plan` skill
- Changing how `check_requirements_ready.py` works
- Any Dart/Flutter code changes
