# Opus Analysis Round 2: Release Lifecycle — Skill Gaps & Fix Strategy

Date: 2026-04-24

---

## User's Questions (restated precisely)

1. Should the user manually set the release to `active`? Or should a skill handle this?
2. If a skill already covers it, should RELEASES.md prohibit manual editing?
3. The moment "requirements for a release are done + it's the next release" should trigger
   both: (a) set active, (b) create orchestration task. Is this already supported by skills?
4. TASK-PROC-035-06 exists but is invisible to next_tasks.py (no target_package/release).
   Should orchestration tasks get a `target_release`?
5. Bug Fix 1 (bootstrap gap) — should the fix be in `next_tasks.py` rather than
   `claude-automated-mode`? Is it wrong that next_tasks.py says "No open tasks" when
   TASK-PROC-035-06 is pending?

---

## Answers

### Q1: Was manually setting `active` correct? Should there be a skill?

**No — the user should not set this manually.** The intended path is:

`requ-prep-release` → Phase 6 sets `status: active` in RELEASES.md.

But `requ-prep-release` is a heavy multi-phase workflow (requirements gap analysis, epic
agents, feature agents). If requirements are already verified from a prior run, forcing
the user through all phases again is unnecessary friction.

**Gap confirmed**: There is no lightweight "I'm ready to implement — start the release"
skill. The user had to either (a) run the full `requ-prep-release` again, or (b) set
active manually. Neither is good UX.

**Recommended**: Create a `release-start-impl` skill (or fold into `task-create-code-
orchestrator`) that is the canonical "begin implementation" command.

---

### Q2: Should RELEASES.md prohibit manual editing of the `active` status?

Yes. The Release Lifecycle section should explicitly state:
> Do NOT set `status: active` manually. Use the `release-start-impl` skill.

Additionally, `requ-prep-release` Phase 6 should reference `release-start-impl` instead
of setting active inline — so Phase 6 becomes a thin wrapper that calls the same skill
the user can invoke directly.

---

### Q3: Is the "requirements done → activate → create orchestration task" moment supported?

Currently: **No, not as a single command.**

The journey is:
1. `requ-prep-release` Phase 6: sets RELEASES.md active ← only reachable via full prep workflow
2. `task-create-code-orchestrator`: creates orchestration task ← requires active already set
3. These two steps must be done in sequence, but no single skill chains them

The missing skill (`release-start-impl`) should do exactly this chain:
1. `python3 scripts/check_requirements_ready.py` — exit 1 → stop, tell user why
2. Check RELEASES.md — if already active, warn and confirm; if no active, set it
3. Call `python3 scripts/create_orchestration_task.py` — handle all exit codes
4. Commit (via `claude-commit`)
5. Inform: "Release X.Y.Z is now active. Orchestration task [ID] created. Start the
   autorun to begin creating impl tasks."

---

### Q4: Should orchestration tasks have `target_release`?

**Yes — this is the most important fix and the root cause of Bug Fix 1.**

TASK-PROC-035-06 has `scope_description: "...for release 0.0.1"` in its goal.md —
it IS semantically a release-0.0.1 task. It should have `target_release: "0.0.1"`.

If `create_orchestration_task.py`'s goal.md template includes `target_release: "{version}"`:
- `next_tasks.py` finds the task → shows it → autorun picks it up
- The entire orchestration chain becomes self-sustaining with no bootstrap changes needed
- The "queue_empty when work remains" bug disappears

Concern: "We can't assign a task to a package, only to a release" — correct, and
`target_release` without `target_package` is exactly right here. `next_tasks.py` already
supports this via the release-mode fallback (`find_next_release`). When there are tasks
with `target_release` but no `target_package`, it falls back to release-based ranking.

---

### Q5: Should Bug Fix 1 be in `next_tasks.py` rather than `claude-automated-mode`?

**The user is right.** The original analysis placed the fix in the bootstrap, but that
is treating a symptom rather than the cause.

The cause: `next_tasks.py` says "No open tasks" even though TASK-PROC-035-06 is pending.
This is wrong. A pending task exists. The script should show it.

The fix at source (Q4 above) is: give orchestration tasks `target_release`. Then
`next_tasks.py` correctly finds them via the release-mode fallback and shows them.
No bootstrap patching needed.

**The bootstrap gap (Bug Fix 1 from round 1)** is a real secondary concern — but it
only triggers when there are NO tasks at all AND uncovered ACs exist. Once Fix-Q4 is
implemented, orchestration tasks will always appear in next_tasks.py, so this secondary
case is largely covered. The bootstrap gap may still exist if someone creates a release
with uncovered ACs but NO orchestration task pending — but that scenario is now handled
by the `release-start-impl` skill (which creates the first orchestration task).

---

## The Clean Fix Architecture (in priority order)

### Fix A — Immediate: Add `target_release` to existing TASK-PROC-035-06
**Why now**: The task exists but the autorun can't find it. This unblocks today's work.
**Action**: Add `target_release: "0.0.1"` to the frontmatter of the existing goal.md.
**Risk**: None — this is additive metadata.
**Effort**: 1 line edit.

### Fix B — Template: `create_orchestration_task.py` adds `target_release`
**Why**: All future orchestration tasks get target_release automatically.
**Action**: Add `target_release: {version}` to the `_GOAL_TEMPLATE` in the script.
**Risk**: None — additive field. next_tasks.py already handles target_release.
**Effort**: 2 line changes (template string + format arg already has `version`).

### Fix C — New skill: `release-start-impl`
**Why**: The canonical "begin implementation for a release" command.
**Action**: Create `.claude/skills/release-start-impl/skill.md` with the 4-step chain
described in Q3 above. Update `requ-prep-release` Phase 6 to call this skill instead
of setting active inline.
**Risk**: Low — new skill, no existing behavior changed.
**Effort**: ~60 lines of skill markdown + 5-line edit to requ-prep-release.

### Fix D — Documentation: RELEASES.md lifecycle section
**Why**: Prevent future manual editing of active status.
**Action**: Update the lifecycle definition and add a "How to activate" note.
**Effort**: ~5 lines.

### Fix E — Optional: Update RELEASES.md lifecycle definition text
**Same as Round 1 Fix 3** — update "active = at least one task in_progress" to the
accurate description. Already covered by Fix D.

---

## Execution Plan

All fixes are independent and can be implemented in any order. Fix A should go first
to unblock the current autorun.

### Agent 1: Immediate unblock (Fix A)
File: `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-24_explore_create-impl-tasks-release-0.0.1/goal.md`
Action: Add `target_release: "0.0.1"` to frontmatter (after `target_package` or before `after:`).
Commit: `fix(task): add target_release to TASK-PROC-035-06 — makes it visible to next_tasks.py`

### Agent 2: Fix template (Fix B)
File: `scripts/create_orchestration_task.py`
Action: In `_GOAL_TEMPLATE`, add `target_release: {version}` as a frontmatter field.
Ensure `version` is already in the format call (it is — used in scope_description).
Commit: `fix(scripts): add target_release to orchestration task template`

### Agent 3: New skill (Fix C)
File: `.claude/skills/release-start-impl/skill.md` (new file)
Content: 4-step skill (check_requirements_ready, set active, create_orchestration_task, commit)
Also edit: `.claude/skills/requ-prep-release/skill.md` Phase 6 — replace inline active-setting
with a call to `release-start-impl`.
Commit: `feat(skills): add release-start-impl skill — canonical release activation + orchestration`

### Agent 4: Documentation (Fix D)
File: `requirements_tasks/RELEASES.md`
Action: Update lifecycle section — rewrite `active` definition, add "Use release-start-impl skill."
Commit: `docs(releases): clarify active status lifecycle — prohibit manual editing`

---

## Quality Criteria
- [ ] `python3 scripts/next_tasks.py` shows TASK-PROC-035-06 after Fix A
- [ ] A new orchestration task created via `task-create-code-orchestrator` has `target_release` set
- [ ] `release-start-impl` skill runs end-to-end without error when requirements are ready
- [ ] `release-start-impl` exits with clear message when `check_requirements_ready.py` fails
- [ ] RELEASES.md lifecycle section does not describe "active" as "at least one task in_progress"
- [ ] Autorun finds and executes TASK-PROC-035-06 after Fix A (run /autorun to verify)

## Risks
- Fix A: None — pure metadata addition
- Fix B: None — additive template field, existing tasks unaffected
- Fix C: Low — new skill only; editing requ-prep-release Phase 6 is a small contained change
- Fix D: None — documentation only
