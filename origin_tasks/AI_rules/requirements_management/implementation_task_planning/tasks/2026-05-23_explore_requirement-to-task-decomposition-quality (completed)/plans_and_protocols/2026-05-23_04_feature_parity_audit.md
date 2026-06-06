# Feature Parity Audit: Old Mechanism → New Design

Date: 2026-05-23
Purpose: Line-by-line mapping of every step in the old task creation mechanism
to where it lives in the new design. Verify nothing is lost, degraded, or orphaned.

---

## Part 1: task-create-code — Step-by-Step Mapping

### Phase 0A: Plan-Driven Discovery

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| Check plan_path in orchestration task | Determines if a plan exists | Unchanged — task-create-code Phase 0A still runs | Same |
| parse_task_creation_plan.py --next-uncreated | Gets next task from plan | Unchanged — same script, same consumption | Same |
| Use plan values as authoritative defaults | ACs, effort, layer, after, opus_recommended | Unchanged — plan values come from task-derive-from-requ (new upstream) or release-begin-impl (as before) | **Improved** — plan now includes coverage matrix and verification task |
| Print confirmation | User sees what's being created | Unchanged | Same |
| Automated mode: question.md on error | Escalation | Unchanged | Same |
| propose_after.py (requirement_then_implementation only) | Supplement plan's after-chains | Unchanged — still called, still supplements | Same |

**Verdict**: Phase 0A is UNCHANGED. The only difference is the upstream source
of the plan: before, only release-begin-impl Phase 2c produced plans. Now
task-derive-from-requ also produces plans in the same format. task-create-code doesn't care
who produced the plan — it consumes the same format.

### Phase 0B: RELEASE_BACKLOG Discovery (standalone mode)

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| next_tasks.py | Find active package | **Only runs in standalone mode** | Same (when reached) |
| Read RELEASE_BACKLOG.md | Package list | Standalone mode only | Same |
| Classify packages (skip flow-derived) | Filter to requirement-sourced | Standalone mode only | Same |
| Pick candidate by priority | Select package | Standalone mode only | Same |
| Resolve to requirement path | Find requirements.md | Standalone mode only | Same |
| Confirm with user | User gate | Standalone mode only | Same |

**Verdict**: Phase 0B is UNCHANGED but only reached in standalone mode. When
task-derive-from-requ or release-begin-impl provides a plan, Phase 0B is skipped entirely.

**Risk**: Standalone mode now has the AC-10 redirect. If user invokes
task-create-code directly for an impl task and the requirement has uncovered ACs,
Phase 0B won't even run — the redirect fires first. Is this correct?

**Analysis**: Yes. The redirect says "you have uncovered ACs, use task-derive-from-requ."
If the user overrides (e.g., explicitly says "create one task for AC-X"), quick
mode handles it. If no override, full mode plans everything. Phase 0B is for
the case where the user comes from RELEASE_BACKLOG context, which implies a
release flow — and in the new design, the release flow goes through Phase 2c →
task-derive-from-requ → plan-driven mode, not through standalone Phase 0B.

**Remaining valid use of Phase 0B**: User invokes task-create-code in
zero-parameter mode WITHOUT a release plan. This is a quick "what's the next
thing I can code?" path. The redirect fires if uncovered ACs exist. If all ACs
are covered or the user creates an additional task beyond the AC set, Phase 0B
runs normally.

### Phase 1: Understand Requirement

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| Read requirement file | Extract goal, ACs, dependencies | **task-derive-from-requ Phase 1** (in plan-driven mode); task-create-code Phase 1 (in standalone) | **Improved in plan-driven** — task-derive-from-requ reads once, passes values. No redundant re-read. |
| Gather additional details from user | UI sketches, business rules | **Still task-create-code** — domain-specific details that task-derive-from-requ can't gather | Same |

**Risk**: In plan-driven mode, task-create-code skips Phase 1 requirement
reading. But what if the plan is stale? (Requirement was modified after the plan
was created.)

**Mitigation**: The plan includes a requirements_version commit hash. 
task-create-code can check: "Has requirements.md been modified since the plan
was created?" If yes, warn. This is the same check that goal.md already has
(requirements_version.commit). The plan should carry the same field.

**⚠ ISSUE FOUND**: The unified plan format (SEC-04) does NOT include
requirements_version. It should, so task-create-code can detect stale plans.

### Phase 2: Scope Estimation (Quick Scan)

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| Identify affected areas | Layers, files, patterns | task-create-code (both modes) | Same |
| Spawn Quick Explore Agent | File count estimate | task-create-code (standalone mode); skippable in plan-driven mode if plan provides layer/effort | **Changed** — in plan-driven mode, plan provides rough estimate; file analysis refines |
| Estimate size (S/M/L) | Split decision | task-create-code (both modes — file analysis always runs for code tasks) | Same |

**Risk**: In plan-driven mode, if file analysis is skipped because plan provides
effort, we lose the "Split NOW" detection for Large tasks.

**Mitigation per AC-15**: File analysis ALWAYS runs for code tasks, even in
plan-driven mode. The plan's effort is a baseline; file analysis refines.
Escalation path fires if mismatch. This is already stated in the requirement.

**Verdict**: No quality loss. Plan-driven mode preserves file analysis as
refinement.

### Phase 3: Create Task

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| 3.1 Location | Determine task folder path | task-create-code (both modes) | Same |
| 3.2 Structure | Create folder + plans_and_protocols | task-create-code (both modes) | Same |
| 3.2.5 Dependency proposal | propose_after.py | Plan-driven: plan provides after-chains, supplement with requirement_then_implementation only. Standalone: full propose_after.py. | **Improved in plan-driven** — dependencies are pre-computed at the plan level with holistic view |
| 3.3a Task ID | allocate_task_id.py | task-create-code (both modes) | Same |
| 3.3b requirements_version | git log commit hash | task-create-code (both modes) | Same |
| 3.3c covers | Which ACs this task covers | Plan-driven: from plan. Standalone: ask user. | **Improved in plan-driven** — coverage pre-validated by task-derive-from-requ's matrix |
| 3.3d Priority/effort | Inherit from parent, estimate | Plan-driven: from plan. Standalone: own estimate. | Same (plan-driven skips redundant estimation) |
| 3.3e release_description | Draft suggestion | task-create-code (both modes) | Same |
| 3.3f opus_recommended | Evaluate signals | Plan-driven: from plan (S1-S4). Standalone: own heuristics. | **Improved in plan-driven** — S1-S4 signals from task-derive-from-requ are more comprehensive than standalone heuristics |
| 3.3b release_chunk | Inherit from parent | task-create-code (both modes) | Same |
| 3.4 Package inheritance | Determine target_package | Plan-driven: from plan. Standalone: own resolution. | Same |
| Write goal.md | Create the file | task-create-code (both modes) | Same |

**Verdict**: Every Phase 3 step is preserved. Plan-driven mode replaces
interactive questions with pre-computed values but the workspace creation
is identical.

### Phase 4: Verify & Commit

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| 4.1 Present goal.md | User confirms | Plan-driven: skipped (user already approved plan). Standalone: same as before. | **Changed** — plan-driven skips per-task confirmation. Justified: user approved at plan level. |
| 4.2 Commit | claude-commit | task-create-code (both modes) | Same |

### Phase 6: Plan Conformance Check

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| check_task_against_plan.py | Validate against plan | task-create-code (plan-driven only) | Same |

**Verdict**: Complete Phase 6 preserved.

### Automated Mode Checkpoints

| Old checkpoint | New behavior | Change |
|---|---|---|
| Phase 0.6 confirm candidate | Redirect to task-derive-from-requ in standalone | Changed — now goes through task-derive-from-requ |
| Phase 1.2 additional details | Same (skip in automated) | Same |
| Phase 3.2.5 dependency proposal | Plan-driven: auto-accept plan + supplement. Standalone: same | Improved |
| Phase 3.3e release_description | Same | Same |
| Phase 4.1 present goal.md | Plan-driven: skipped. Standalone: same | Improved (less friction) |
| Phase 6 conformance | Same | Same |

---

## Part 2: release-begin-impl Phase 2c — Step-by-Step Mapping

### What Phase 2c does today (from REQ-PROC-035 SEC-06)

"Phase 2c — Task Creation Planner: One agent reads ALL in-scope feature
requirements.md files and produces task_creation_plan.md. The plan contains:
ordered package execution list, per-task entries with covered ACs, effort,
layer, after-chains, and architecture notes."

| Old step | What it does | New owner | Quality change |
|---|---|---|---|
| One monolithic agent | Reads ALL requirements | **Per-requirement task-derive-from-requ agents** spawned by Phase 2c | **Improved** — each agent has focused context; no cross-contamination between unrelated requirements |
| Reads all requirements.md files | Input gathering | Each task-derive-from-requ agent reads its own requirement | Same information, better scoped |
| Groups ACs into tasks | Per-requirement decomposition | task-derive-from-requ Phase 2-3 | **Improved** — coverage matrix, verification task, enforcement detection |
| Determines effort/layer | Sizing | task-derive-from-requ Phase 3 (rough estimate) + task-create-code (file analysis refinement) | **Improved** — S1-S4 signals added |
| Determines after-chains | Dependencies | task-derive-from-requ Phase 3 (AC-level) + task-create-code (codebase-level supplement) | Same quality, better structured |
| Produces task_creation_plan.md | Output artifact | Phase 2c assembles per-requirement plans into release plan | **Improved** — per-requirement coverage matrices included |
| No coverage matrix | (missing) | task-derive-from-requ produces per-requirement coverage matrix | **NEW** — catches AC gaps at plan time |
| No verification tasks | (missing) | task-derive-from-requ mandates verification task per requirement | **NEW** — catches missing verification |
| No enforcement detection | (missing) | task-derive-from-requ detects enforcement-creates-violations pattern | **NEW** — prevents gate-without-baseline |
| Marks already-implemented ACs as task_type: verify | Detects existing code | task-derive-from-requ Phase 1 reads existing tasks; check_requirement_implementation.py may still run | **Preserved** — but responsibility shifts from Phase 2c agent to task-derive-from-requ |

### What Phase 2c KEEPS in the new design

| Concern | Still Phase 2c's job |
|---|---|
| Package execution ordering | Yes — release-level concern |
| Cross-requirement after-chains | Yes — dependencies between tasks of different requirements |
| Scope completeness check | Yes — every package has ≥1 requirement |
| Assembling release plan from per-requirement plans | Yes — new responsibility |
| Orchestration task creation | Yes — Phase 6 |
| User gate (Phase 5) | Yes — release-level review |

### What Phase 2c LOSES

| Concern | Why removed | Replaced by |
|---|---|---|
| Per-requirement AC grouping | Duplication of task-derive-from-requ | task-derive-from-requ Phase 2-3 |
| Per-requirement effort estimation | Duplication of task-derive-from-requ | task-derive-from-requ Phase 3 |
| Reading ALL requirements in one agent | Context blowup risk | Per-requirement agents |

**Risk**: The monolithic agent had ONE advantage: it could see cross-requirement
interactions directly (e.g., "AC-02 of REQ-A depends on the data model from
REQ-B"). Per-requirement agents lose this cross-visibility.

**Mitigation**: Phase 2c adds cross-requirement after-chains AFTER assembling
the per-requirement plans. It can see: "task-derive-from-requ for REQ-A produced a task
covering AC-02 that mentions data model X; task-derive-from-requ for REQ-B produced a task
creating data model X. Add after-chain: REQ-A's task depends on REQ-B's task."
This is a release-level concern and stays with Phase 2c.

**⚠ But**: This requires Phase 2c to understand the semantic content of the
per-requirement plans to detect cross-requirement dependencies. The monolithic
agent got this for free (it had all requirements in context). The new design
requires Phase 2c to do a cross-referencing pass on the assembled plans.

**Quality comparison**: Slightly different, not worse. The monolithic agent's
cross-visibility came at the cost of context blowup (reading everything in one
agent = overflow risk on large releases). The per-requirement approach trades
implicit cross-visibility for explicit cross-referencing, which is more reliable
and auditable.

---

## Part 3: What's New (not in old mechanism)

| New feature | AC | Value |
|---|---|---|
| Coverage matrix at plan time | AC-01 | Catches AC gaps before tasks are created |
| Mandatory verification task | AC-02 | Prevents "mostly done" without verification |
| S1-S4 sizing signals | AC-03 | Better context-window budgeting |
| Plan-before-create gate | AC-04 | User sees holistic view before any task exists |
| Enforcement-creates-violations detection | AC-06 | Prevents gate-without-baseline pattern |
| Post-creation coverage validation | AC-08 | Double-check after creation |
| Incremental decomposition | AC-09 | Handles partial coverage gracefully |
| Redirect on uncovered ACs | AC-10 | Prevents ad-hoc task creation that misses ACs |
| No-duplication principle | AC-15 | Each concern computed once, refined downstream |

---

## Part 4: Issues Found

### P1. Plan format missing requirements_version

The unified plan format (SEC-04) lists plan entry fields but does NOT include
`requirements_version` (the commit hash of requirements.md at plan creation time).
Without this, task-create-code can't detect if the requirement was modified after
the plan was created. Stale plans could produce mismatched tasks.

**Fix**: Add `requirements_version` to the plan entry format in SEC-04.

### P2. check_requirement_implementation.py usage unclear

release-begin-impl Phase 2c currently uses `check_requirement_implementation.py`
to detect already-implemented ACs (marking them `task_type: verify`). In the new
design, task-derive-from-requ Phase 1 reads existing tasks to compute coverage. These are
similar but different:
- task-derive-from-requ checks: does a task EXIST covering this AC?
- check_requirement_implementation.py checks: does CODE implementing this AC exist?

A task may exist but the code may not (task pending). Code may exist but no task
covers it (orphaned implementation).

**Fix**: task-derive-from-requ should do BOTH: check task coverage (from goal.md covers:
fields) AND optionally run check_requirement_implementation.py for code
requirements. The latter adds the "already implemented without a task" detection
that task-derive-from-requ's task scan alone misses.

### P3. Automated mode behavior of task-derive-from-requ not defined

task-create-code has a detailed automated mode table (what to auto-accept vs
escalate). task-derive-from-requ has no automated mode specification yet. When the automation
orchestrator runs task-derive-from-requ, it needs to know:
- Phase 4 (user review): auto-accept or escalate?
- Phase 5 (create): inline or orchestration task?
- Escalation paths?

**Fix**: Add automated mode section to task-derive-from-requ's specification. Phase 4 should
auto-accept in automated mode (plan quality is enforced by coverage matrix, not
user review). Phase 5 should always use orchestration tasks in automated mode
(predictable context budget).

### P4. Quick mode boundaries need tightening

Current rule: "1-2 tasks, user names ACs explicitly → quick mode."
But what if the user names 2 ACs and one of them needs a code task (file analysis)
while the other needs a process task? Quick mode would create both inline.
The code task's file analysis adds non-trivial context.

**Fix**: Quick mode creates at most 2 tasks and at most 1 code task (file
analysis is the expensive step). If the plan would create 2 code tasks, escalate
to full mode.

### P5. task-create plan-driven mode needs specification

AC-11 states task-create accepts plan-driven inputs, but the task-create SKILL.md
has no plan-driven mode today. The specification needs: what fields are accepted,
what phases are skipped, what the goal.md output looks like.

This is an implementation concern (task for the future), not a requirement gap.
The requirement (AC-11) states the end state; the skill needs to be updated to
match.

### P6. Orchestration task pattern reuse

When task-derive-from-requ produces > 6 tasks and creates an orchestration task, it reuses the
release-begin-impl orchestration infrastructure (create_orchestration_task.py).
But that script is designed for release-scope orchestration — it reads
task_creation_plan.md and RELEASES.md.

**Fix**: Either generalize create_orchestration_task.py to handle per-requirement
plans (new --mode flag), or create a simpler script for per-requirement
orchestration. The simpler option: task-derive-from-requ writes a plan file in the same
format as task_creation_plan.md, then calls create_orchestration_task.py with
a mode flag that skips release-specific checks.

---

## Part 5: Quality Comparison Summary

| Concern | Old quality | New quality | Change |
|---|---|---|---|
| AC coverage at plan time | ❌ Not checked | ✅ Blocking gate | **Major improvement** |
| Verification task | ❌ Not required | ✅ Mandatory | **Major improvement** |
| Sizing | ⚠ Heuristic (file count) | ✅ S1-S4 + file analysis | **Improvement** |
| Dependencies | ⚠ propose_after.py only | ✅ Plan-level + supplement | **Improvement** |
| Enforcement detection | ❌ Not done | ✅ Auto-proposed remediation | **Major improvement** |
| Context budget | ⚠ Monolithic agent risk | ✅ Per-requirement agents | **Improvement** |
| File analysis | ✅ Quick-Explore-Agent | ✅ Preserved (refine step) | **Same** |
| Plan conformance | ✅ check_task_against_plan.py | ✅ Preserved | **Same** |
| Automated mode | ✅ Detailed spec | ⚠ Not yet specified for task-derive-from-requ | **Gap — P3** |
| Stale plan detection | ⚠ Implicit (requirements_version in goal.md) | ⚠ Plan format lacks field | **Gap — P1** |
| Orphaned implementation detection | ✅ check_requirement_implementation.py | ⚠ Unclear ownership | **Gap — P2** |
| WHAT not HOW principle | ✅ Enforced | ✅ Preserved (AC-13) | **Same** |
| Cross-requirement dependencies | ✅ Monolithic agent sees all | ⚠ Explicit cross-ref pass needed | **Different, not worse** |

**Overall**: 4 major improvements, 3 improvements, 4 same, 3 gaps to fix, 1
changed-but-equivalent. No quality degradation on any existing concern.
