# Verification Walkthrough: All Cases for Task Creation

Date: 2026-05-23
Purpose: Walk through every case where task-derive-from-requ, task-create, task-create-code,
and release-begin-impl interact. Verify the process works step by step.
Consider context windows, agents, artifacts, and efficiency.

## Case Inventory

| # | Case | Entry skill | task-derive-from-requ mode | Downstream |
|---|---|---|---|---|
| 1 | Fresh requirement, full decomposition | task-derive-from-requ | Full | task-create + task-create-code |
| 2 | Single AC gap fill | task-derive-from-requ | Quick | task-create or task-create-code |
| 3 | Multiple AC gaps discovered | task-create → redirect | Full | task-create + task-create-code |
| 4 | Dedicated explore task for decomposition | claude-route → task-derive-from-requ | Full | task-create + task-create-code |
| 5 | Release flow | release-begin-impl → task-derive-from-requ | Full (per-req agents) | task-create-code |
| 6 | Product intake landing | product-intake → user → task-derive-from-requ | Full | task-create + task-create-code |
| 7 | Standalone explore (no requirement yet) | task-create | N/A (no ACs) | — |
| 8 | Standalone task-create-code (direct) | task-create-code | N/A | — |
| 9 | Bugfix task | task-create | N/A (single fix) | — |
| 10 | Incremental decomposition (new ACs added) | task-derive-from-requ | Full | task-create + task-create-code |
| 11 | All-process requirement (no code) | task-derive-from-requ | Full | task-create only |
| 12 | Mixed requirement (code + process) | task-derive-from-requ | Full | task-create + task-create-code |
| 13 | requ-derive-from-flow output | task-create | N/A (explore tasks) | — |
| 14 | Requirement without ACs (pre-migration) | task-create | N/A (no ACs) | — |
| 15 | Epic-level task (explore/define only) | task-create | N/A (epic tasks) | — |

---

## Case 1: Fresh requirement, full decomposition

**Scenario**: requ-explore just wrote REQ-FUNC-042 with 8 ACs. User wants impl tasks.
**Real example shape**: epic_security (17 ACs, 3 tasks) or feat_donations (7 ACs, 0 tasks)

### Step-by-step

1. User invokes task-derive-from-requ on `requirements_tasks/functional/.../requirements.md`
2. **Phase 1 (Gather)**: Read requirements.md (~100–200 lines). Check for existing tasks (zero). Read 1-2 related requirements from `after:`/`blocks:`.
   - Context cost: ~300–500 lines read. Fine.
3. **Phase 2 (Analyze)**: Group 8 ACs into ~4-5 task groups. Classify each: code vs non-code. Detect enforcement patterns.
   - Context cost: thinking only, no reads. Fine.
4. **Phase 3 (Plan)**: Produce plan: 5 impl tasks + 1 verification task = 6 tasks. Coverage matrix. S1-S4 per task (rough estimates).
   - Context cost: writing to memory. Fine.
5. **Phase 4 (Review)**: Present plan + coverage matrix to user. User approves.
   - Context cost: output only. Fine.
6. **Phase 5 (Create)**: 6 tasks to create.
   - ⚠ **Context concern**: Creating 6 tasks inline means 6 × (task-create/task-create-code invocation). Each invocation allocates ID, writes goal.md. If code tasks, each does file analysis.
   - **Threshold question**: Is 6 tasks OK inline, or should we persist the plan?

7. **Phase 6 (Validate)**: Run coverage_report.py. Confirm 100%.
   - Context cost: one script run. Fine.

### Context budget analysis

Phases 1-4: ~1000 tokens of reads + thinking. Fine for Sonnet or Opus.
Phase 5 with 6 tasks:
- 6 × task-create (non-code): ~200 lines each (folder creation + goal.md) = ~1200 lines. OK.
- 6 × task-create-code (code): ~200 lines + file analysis per task. File analysis = glob + grep + maybe Quick-Explore-Agent. Each adds ~300-500 lines of tool output. 6 × 500 = ~3000 lines. Risky on Sonnet.

### Decision

**≤ 4 tasks**: create inline. Total context stays manageable.
**5-8 tasks**: create inline but skip file analysis for code tasks — persist plan as
artifact, let task-create-code do file analysis when the task is actually executed
(or in a subsequent session).
**> 8 tasks**: persist plan as file artifact. Create an orchestration task (same
pattern as release-begin-impl Phase 6). Orchestration task materializes ≤ 6 tasks
per session via task-create-code Phase 0A.

### Missing from current design

The requirement doesn't specify the persistence threshold. Need a new AC or
clarification in Behavior section about when the plan becomes a file artifact
vs stays in-session.

---

## Case 2: Single AC gap fill (quick mode)

**Scenario**: REQ-PROC-001 has 8 ACs, 7 covered. User says "create a task for AC-04."

### Step-by-step

1. User invokes task-create for REQ-PROC-001
2. task-create detects: requirement has ACs, 1 uncovered → redirects to task-derive-from-requ
3. task-derive-from-requ quick mode: reads requirement, computes coverage
4. Confirms: AC-04 is uncovered. Shows coverage state to user.
5. Creates one task via task-create (AC-04 is a process task, not code)
6. Post-creation coverage check: shows "AC-04 now covered. AC-07 still uncovered."

### Context budget: Minimal. One requirement read + one task creation. Fine.

### Does it work? ✅ Yes. Clean and lightweight.

---

## Case 3: Multiple gaps discovered (redirect to full mode)

**Scenario**: User invokes task-create on REQ-PROC-001. 2 ACs uncovered.

### Step-by-step

1. task-create detects: 2 uncovered ACs → redirects to task-derive-from-requ
2. **Mode selection**: 2 ACs is borderline. Rule says quick mode for 1-2 tasks when
   user names ACs explicitly. But here the user didn't name ACs — they just called
   task-create. So: ≥ 2 uncovered + user didn't name specific ACs → full mode.
   Wait — the rule says "≥ 3 uncovered ACs → full mode." 2 is below threshold.
3. Actually: quick mode handles 1-2 tasks. But should still show coverage matrix.
   Quick mode with 2 uncovered: creates 2 tasks, shows matrix. Fine.

### Refinement needed

The mode selection needs to be clearer:
- User names specific AC(s) → quick mode regardless of uncovered count
- User doesn't name ACs + ≤ 2 uncovered → quick mode (show options)
- User doesn't name ACs + ≥ 3 uncovered → full mode
- Requirement has zero existing tasks → always full mode

---

## Case 4: Dedicated explore task for decomposition

**Scenario**: Goal.md says "decompose REQ-PROC-058 into implementation tasks."
claude-route detects this and invokes task-derive-from-requ.

### Step-by-step

Same as Case 1, but entry is via claude-route instead of direct user invocation.

### Does it work? ✅ Yes.

### Additional consideration

claude-route needs a pattern to detect "decompose requirement X" goals. Currently
it matches type: explore → requ-explore. Need to add: "goal body contains 'create
tasks', 'decompose', 'implementation tasks for'" → task-derive-from-requ.

---

## Case 5: Release flow (release-begin-impl)

**Scenario**: Release has 5 requirements, each with 3-8 ACs. Phase 2c needs to
create task plans for all of them.

### Step-by-step (current design per AC-14)

1. Phase 2c identifies 5 in-scope requirements
2. For each requirement, Phase 2c spawns a task-derive-from-requ agent
3. Each agent runs task-derive-from-requ Phases 1-3 on its requirement
4. Each agent returns: per-requirement plan with coverage matrix
5. Phase 2c assembles per-requirement plans into release plan
6. Phase 2c adds release-level concerns: package ordering, cross-requirement
   dependencies (after-chains between tasks of different requirements)
7. Phase 5 user gate: user reviews release plan with per-requirement coverage matrices
8. Phase 6: create orchestration task with the assembled plan

### Context budget analysis

**Phase 2c main session**: reads RELEASES.md, RELEASE_BACKLOG.md, spawns 5 agents.
Receives 5 distilled plans back. Assembles into release plan. Moderate context. OK.

**Per-requirement agents**: each reads one requirement (~200 lines) + existing tasks
+ related requirements. Produces plan. Each agent's context is bounded by one
requirement. Fine.

**BUT**: where does the assembled plan live? As a file (task_creation_plan.md).
Then orchestration tasks consume it via task-create-code Phase 0A. This is the
existing pattern — no new infrastructure needed.

### Does it work? ✅ Yes, with agents.

### What changes from today

Today Phase 2c uses ONE monolithic agent that reads ALL requirements. The new
design uses per-requirement agents. This is better for context budget AND
produces coverage matrices that the monolithic agent doesn't.

**Impact on REQ-PROC-035**: SEC-05/SEC-06 describe the monolithic planner.
Need update to reflect per-requirement agents + plan assembly.

---

## Case 6: Product intake landing

**Scenario**: product-intake routes a feature request through persona → scenario →
flow → requirement. The requirement is created/updated. User wants tasks.

### Step-by-step

1. product-intake creates/updates requirements.md
2. User invokes task-derive-from-requ on the affected requirement
3. Same as Case 1 (full mode) or Case 10 (incremental if requirement was updated)

### Does it work? ✅ Yes. product-intake is upstream; task-derive-from-requ is downstream.

---

## Case 7: Standalone explore (no requirement yet)

**Scenario**: User wants to explore a new area. No requirements.md exists.

### Step-by-step

1. User invokes task-create with type: explore
2. task-create checks: no requirements.md → pre-allocates REQ-ID
3. Creates explore task workspace
4. task-derive-from-requ is NOT involved (no ACs to check)

### Does it work? ✅ Yes. task-create handles this independently.

---

## Case 8: Standalone task-create-code (direct invocation)

**Scenario**: User says "use task-create-code for REQ-FUNC-042 AC-03"

### Step-by-step

1. User invokes task-create-code directly
2. **Should task-create-code redirect to task-derive-from-requ?**
   - If requirement has uncovered ACs → yes, redirect (same as task-create AC-10)
   - If all ACs are covered and user is creating an additional task → ??? 

### Problem identified

task-create-code currently has no redirect logic. AC-10 only mentions task-create.
Should task-create-code also redirect when uncovered ACs exist?

**Answer**: Yes. AC-10 should apply to task-create-code as well. Both creation
primitives redirect to task-derive-from-requ when the requirement has uncovered ACs.

But: task-create-code is often called from release-begin-impl's orchestration
tasks (plan-driven mode). In that case, the plan already ensures coverage — no
redirect needed. The redirect applies only in standalone mode.

### Refinement needed

AC-10 should cover both task-create AND task-create-code in standalone mode.
Plan-driven mode (Phase 0A) is exempt from the redirect.

---

## Case 9: Bugfix task

**Scenario**: User reports a bug affecting AC-03 of REQ-FUNC-007.

### Step-by-step

1. User invokes task-create with type: bugfix
2. task-create handles bugfix creation (collects bug report, sets title)
3. task-derive-from-requ is NOT involved

### Why not?

A bugfix is a single task fixing a specific AC. It's not a decomposition of a
requirement into multiple tasks. The bugfix restores already-documented behavior;
it doesn't add new coverage.

### Does it work? ✅ Yes. Bugfix tasks bypass task-derive-from-requ entirely.

### Should this be explicit?

Yes. The requirement should note that bugfix tasks are exempt from task-derive-from-requ
(they're repairs, not decompositions).

---

## Case 10: Incremental decomposition (new ACs added)

**Scenario**: REQ-PROC-046 had 13 ACs, all covered. requ-explore adds AC-14, AC-15.

### Step-by-step

1. User invokes task-derive-from-requ on REQ-PROC-046
2. Phase 1: reads requirement, finds 14 tasks covering AC-01 through AC-13.
   AC-14 and AC-15 are uncovered.
3. Phase 2: analyzes new ACs only. Groups them.
4. Phase 3: plans 2-3 new tasks. Coverage matrix shows 15 ACs total: 13 existing + 2 planned.
5. Phase 4: user reviews. Approves.
6. Phase 5: creates 2-3 new tasks.
7. Phase 6: validates 100% coverage.

### Context budget: manageable — reads requirement + scans existing task frontmatter (not full goal.md bodies).

### Does it work? ✅ Yes. AC-09 covers this case.

### Efficiency note

Phase 1 needs to scan existing tasks. With 14 tasks, that means reading 14
goal.md frontmatter sections. Should NOT read full goal.md bodies — only YAML
frontmatter (to extract `covers:` field). This is a grep operation, not 14 full reads.

```bash
for f in $(find tasks/ -name "goal.md"); do
  head -30 "$f" | grep -A3 "covers:"
done
```

---

## Case 11: All-process requirement (no code)

**Scenario**: REQ-PROC-058 itself — 15 ACs, all process/skill/doc tasks.

### Step-by-step

1. task-derive-from-requ full mode
2. Phase 2: all tasks classified as non-code (skills, docs, scripts, requirements)
3. Phase 5: all tasks created via task-create (not task-create-code)
4. task-create in plan-driven mode: accepts ACs, effort, dependencies from plan.
   Does NOT re-read requirement (AC-15).

### Context budget

Creating ~8-10 non-code tasks via task-create. Each is lightweight (folder + goal.md).
But 10 × task-create invocations inline is heavy.

### Decision: Same threshold as Case 1.

≤ 6 tasks: inline. > 6 tasks: persist plan + orchestration task.

### Does it work? ✅ Yes, with the threshold.

---

## Case 12: Mixed requirement (code + process)

**Scenario**: REQ-PROC-001 — some ACs need skill modifications (process), some need
CLAUDE.md updates (doc), some need script changes (code? process?).

### Step-by-step

1. task-derive-from-requ full mode
2. Phase 2: classifies each task:
   - AC-01, AC-02, AC-03 (task-create sizing gate) → process (skill modification)
   - AC-05 (should-use-agents per-task mode) → script (Python, uses task-create)
   - AC-06 (requ-explore reentry guard) → process (skill modification)
   - AC-07 (iterative-fix Opus default) → process (skill modification)
   - AC-08 (CLAUDE.md docs) → doc (task-create)
   - Verification task → process (audit task)
3. Phase 5: all via task-create (none touch lib/test/integration_test)
4. No task-create-code invocations needed

### Wait — what about scripts?

Python scripts under scripts/ are NOT Dart code. task-create-code is for
lib/test/integration_test only. Script tasks go through task-create + the
claude-write-script skill at execution time.

### Does it work? ✅ Yes.

---

## Case 13: requ-derive-from-flow output

**Scenario**: requ-derive-from-flow analyzes 3 user flows, finds 7 gaps, creates
7 explore tasks via task-create.

### Step-by-step

1. requ-derive-from-flow identifies gaps
2. Phase 4.2: spawns agents that call task-create for each gap
3. Each task-create call creates an explore task (type: explore)
4. task-derive-from-requ is NOT involved (these are explore tasks, not impl decompositions)

### After the explore tasks complete

5. Each explore task runs requ-explore → creates/updates requirements.md
6. THEN task-derive-from-requ can be invoked on the new requirements to create impl tasks

### Does it work? ✅ Yes. requ-derive-from-flow → task-create → explore → requ-explore → requirements → task-derive-from-requ → impl tasks. Clean pipeline.

---

## Case 14: Requirement without ACs (pre-migration)

**Scenario**: Old requirement with no trackable_items. User wants to create a task.

### Step-by-step

1. User invokes task-create
2. task-create checks: no trackable_items.acceptance_criteria → no redirect
3. Creates task normally
4. task-derive-from-requ is NOT involved (nothing to check coverage against)

### Does it work? ✅ Yes. task-derive-from-requ only activates when ACs exist.

---

## Case 15: Epic-level task

**Scenario**: User wants to create a define task on epic_security to break it into features.

### Step-by-step

1. User invokes task-create with type: define
2. task-create checks: epic has ACs (17 for epic_security)
3. **Should this trigger task-derive-from-requ?**

### Problem

Epic-level tasks are limited to explore/define/review/analyze — NOT impl. task-derive-from-requ
is designed for implementation task decomposition. A define task on an epic is about
breaking the epic into features, not creating impl tasks.

### Decision

task-derive-from-requ activates only for impl/verify task creation, not for explore/define
tasks. The redirect logic checks: requirement has uncovered ACs AND the task type
is impl (or the user didn't specify a type and the goal is implementation).

---

## Cross-Cutting Concerns

### A. Context Window Budget Table

| Case | Phase 1-4 reads | Phase 5 creates | Total budget | Risk |
|---|---|---|---|---|
| Quick mode (1-2 tasks) | ~200 lines | 1-2 × task-create | ~500 lines | None |
| Full mode, small req (3-5 ACs) | ~300 lines | 3-4 tasks inline | ~1500 lines | Low |
| Full mode, medium req (6-10 ACs) | ~400 lines | 5-8 tasks | ~3000 lines | Medium |
| Full mode, large req (11+ ACs) | ~600 lines | 8+ tasks → orchestration | ~1500 lines (plan only) | Low (delegated) |
| Release flow (5 reqs) | per-agent: ~300 | per-agent: plan only | ~300 per agent | None |

### B. Agent Strategy

| Phase | Agent needed? | Condition |
|---|---|---|
| Phase 1 gather (related reqs) | Optional | > 3 related requirements → spawn gather agent |
| Phase 2-3 analyze + plan | Never | Synthesis — must be monolithic |
| Phase 4 review | Never | User interaction in main session |
| Phase 5 create, ≤ 6 tasks | Never | Inline creation |
| Phase 5 create, > 6 tasks | Orchestration task | Separate sessions, ≤ 6 per session |
| Release flow (per-requirement) | Always | Per-requirement task-derive-from-requ agents |

### C. Artifact Flow

```
[requirements.md]  ←── exists before task-derive-from-requ is invoked
       ↓
  task-derive-from-requ Phase 1: reads requirement + existing tasks (frontmatter only)
       ↓
  task-derive-from-requ Phase 2-3: produces plan (in-memory for ≤ 6 tasks, file for > 6)
       ↓
  task-derive-from-requ Phase 4: user reviews coverage matrix + plan
       ↓ (user approved)
  task-derive-from-requ Phase 5:
       ├── ≤ 6 tasks: create inline
       │     ├── non-code → task-create (plan-driven: accepts values, no re-read)
       │     └── code → task-create-code (plan-driven: accepts values, refines with file analysis)
       │
       └── > 6 tasks: write plan to file → create orchestration task
             └── orchestration task runs task-create-code Phase 0A per batch
       ↓
  task-derive-from-requ Phase 6: coverage_report.py validates 100%
       ↓
  [goal.md files]  ←── permanent artifacts
```

### D. Information at Each Point

| Point | What's available | What's NOT available |
|---|---|---|
| task-derive-from-requ Phase 1 | requirements.md, existing tasks (covers: fields), related reqs | File-level scope of code tasks |
| task-derive-from-requ Phase 3 | AC groupings, rough S1-S4, logical dependencies | Precise file counts, layer analysis |
| task-derive-from-requ Phase 5 (plan-driven) | Plan values (ACs, effort, dependencies) | — |
| task-create-code Phase 0A | Plan values from task-derive-from-requ | — |
| task-create-code file analysis | Actual file counts, layers, patterns | — (but can escalate to task-derive-from-requ if mismatch) |

### E. Escalation Path (bottom-up)

task-create-code discovers task is larger than plan estimated:
1. File analysis shows Large (8+ files) but plan said effort: S
2. task-create-code does NOT silently create the task
3. Options:
   a. Interactive: ask user "Plan estimated S but file analysis shows Large. Split? Promote to Opus? Override?"
   b. Automated: write question.md and stop (same pattern as verify-quality cycle 5)
4. If split: return to task-derive-from-requ with a split proposal. task-derive-from-requ re-plans that AC group.

---

## Issues Found

### Issue 1: Plan persistence threshold not in requirement

The requirement doesn't specify when the plan becomes a file artifact vs stays
in-session. Need to add.

**Proposed**: "When full mode produces > 6 tasks, the plan is persisted as a file
artifact and an orchestration task is created for batch creation."

### Issue 2: AC-10 should cover task-create-code too

AC-10 only mentions task-create. task-create-code in standalone mode should also
redirect to task-derive-from-requ when uncovered ACs exist.

### Issue 3: Bugfix exemption not stated

Bugfix tasks (type: bugfix) should be explicitly exempt from task-derive-from-requ redirect.
They're repairs of existing behavior, not decompositions.

### Issue 4: Epic/explore/define exemption not stated

task-derive-from-requ activates only for impl/verify decomposition, not for explore/define
tasks on epics. The redirect condition should check task type.

### Issue 5: claude-route detection pattern needed

claude-route needs to detect "decompose/plan tasks for requirement X" goal shapes
and route to task-derive-from-requ. Currently not in the skill's match table.

### Issue 6: Phase 1 efficiency — frontmatter-only scanning

When checking existing task coverage, Phase 1 should read goal.md frontmatter
only (first ~30 lines for covers: field), not full goal.md bodies. Important
for requirements with many existing tasks (like REQ-PROC-046 with 14+ tasks).

### Issue 7: task-create plan-driven mode not defined

task-create (non-code) doesn't have a plan-driven mode today. It would need one
so it accepts pre-computed values from task-derive-from-requ and skips redundant steps
(requirement reading, coverage asking, user confirmation).

### Issue 8: Escalation path for size mismatch

When task-create-code's file analysis contradicts the plan estimate, the escalation
path is not defined in the requirement. Need to specify: interactive → ask user;
automated → write question.md.
