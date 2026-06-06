# Process Improvement — Release Preparation Workflow
Date: 2026-03-06
Context: The current single-agent approach for release preparation is not scalable.
         This file documents a proposed multi-agent workflow for a `requ-release-prep` skill.

---

## Problem Statement

The single-agent approach used in this session required reading ~15 requirement files
sequentially in the main context window. For a release with more requirements, this
would overflow context — and even at 10 requirements, it was already risky.

Root causes:
1. One agent does all investigation (reads everything) + synthesizes + presents
2. No structured way to parallelize per-requirement work
3. No reuse of existing tooling (generate_status_overview.py was ignored)
4. No split between "find what exists" and "verify quality per item"

---

## Proposed Multi-Agent Workflow

### High-Level Phases

Phase 0: Bootstrap (orchestrator)
Phase 1: Scope coverage check (1 agent)
Phase 2: Epic-level agents (1 per epic in release scope)
Phase 3: Feature-level agents (1 per feature in release scope)
Phase 4: Gap verification agent (1 agent)
Phase 5: Orchestrator collects all question files, presents to user

---

### Phase 0 — Bootstrap (Orchestrator, main context)

Reads ONLY:
- RELEASES.md (the target release's scope_boundaries.includes list)
- requirements_tasks/STATUS.md (output of generate_status_overview.py — already generated)
- The task's goal.md

The orchestrator does NOT read any requirements.md files directly.
From STATUS.md it extracts:
- All requirements with target_release matching the release version
- Their current status (pending, in_progress, implemented, etc.)
- Which requirements have 0 tasks vs. some tasks

Output: A work list of (requirement_id, path, status, has_tasks) tuples.
This work list is passed to all downstream agents via their goal.md files.

Key tool: scripts/generate_status_overview.py
- Run this before spawning agents; its output is STATUS.md
- STATUS.md gives coverage at a glance without reading each requirements.md

---

### Phase 1 — Scope Coverage Check Agent

Task: Verify that every item in RELEASES.md scope_boundaries.includes maps to
at least one requirement assigned to the release.

Reads ONLY:
- RELEASES.md (scope_boundaries section)
- STATUS.md (to see which req IDs are assigned to the release)
- requirements_tasks/_meta/id_registry.md (to find requirement names by ID)

Does NOT read individual requirements.md files.

Output: A file `questions/scope_gaps.md` listing:
- scope_boundaries.includes items with no assigned requirement
- scope_boundaries.includes items with only epic-level coverage (no feature)
- Any includes item that seems covered but warrants confirmation

This agent is lightweight — it only reads ~3 files total.

---

### Phase 2 — Epic-Level Agents (one per epic in scope)

For each epic requirement in the work list (e.g. REQ-FUNC-007, REQ-FUNC-014):

Reads ONLY:
- The epic's requirements.md
- Its direct child feature requirements.md files (listed in the epic's Features section)
- RELEASES.md (to know the release scope)

Does NOT read grandchild files, sibling epics, or doc/ guidelines.

Tasks for each epic agent:
1. Check if all 0.0.x-scoped trackable items have feature-level requirements below them
2. If an epic trackable item has no feature requirement: flag as a new-requirement gap
3. Check if each child feature has at least one impl task for the 0.0.x items
4. Write findings to `questions/epic_[REQ_ID]_findings.md`

Output per agent: `questions/epic_[REQ_ID]_findings.md` with:
- Features that exist and are OK
- Features that are missing and need creation (including draft content)
- Open decisions needed from user before tasks can be created

Parallelization: All epic agents can run in parallel (independent reads).

---

### Phase 3 — Feature-Level Agents (one per feature in scope)

For each feature requirement in the work list (e.g. REQ-FUNC-007-01, REQ-NFUNC-001):

Reads ONLY:
- The feature's requirements.md
- The feature's tasks/ folder listing (Glob, not full reads)
- RELEASES.md (release scope section only)

Does NOT read parent epic, sibling features, or doc/ guidelines.

Tasks for each feature agent:
1. Identify which trackable items (ACs or sections) target the release
2. Check if impl tasks exist covering those items
3. If tasks are missing: create them using task-create-impl skill 
   (writes goal.md to tasks/ folder directly)
4. If requirements are incomplete for the release items: flag in questions file
5. Write questions to `questions/feat_[REQ_ID]_questions.md`

Output per agent:
- Created task files (goal.md) in the feature's tasks/ folder
- `questions/feat_[REQ_ID]_questions.md` (if decisions are needed before task creation)

Parallelization: All feature agents can run in parallel.
Exception: If feature A depends on feature B, feature A's agent waits for B's task IDs.

---

### Phase 4 — Gap Verification Agent

Runs AFTER Phase 1–3 complete.

Reads ONLY:
- All `questions/*.md` files from Phases 1–3 (these are small)
- Re-runs generate_status_overview.py and reads updated STATUS.md
- RELEASES.md

Task: Cross-check that all scope_boundaries.includes items now have:
- At least one feature-level requirement
- At least one impl task for the release
- No unresolved open questions that block task creation

Output: `questions/final_coverage_check.md` with:
- Remaining gaps (if any)
- Confirmed covered items
- Summary for user review

---

### Phase 5 — Orchestrator Presents to User

Reads ONLY:
- All `questions/*.md` files
- Updated STATUS.md

Assembles a single consolidated user-facing summary:
1. What was automatically handled (tasks created, requirements confirmed)
2. Open decisions needed from user (one clear list)
3. Next steps once decisions are made

---

## Context Budget Per Agent

| Agent | Max files read | Expected context use |
|-------|---------------|---------------------|
| Orchestrator (Phase 0) | 3 | Low |
| Scope check (Phase 1) | 3 | Low |
| Each epic agent (Phase 2) | 3-5 | Medium |
| Each feature agent (Phase 3) | 2-3 | Low-Medium |
| Gap verification (Phase 4) | 5-10 (small files) | Low |
| Orchestrator (Phase 5) | 5-10 (small files) | Low |

Total files read per agent: max 10. No agent reads the full requirement corpus.

---

## New Skill Proposal: `requ-release-prep`

This workflow is complex enough and important enough to warrant a dedicated skill.
It will be needed for every release (0.0.2, 0.0.3, ..., 0.1.0, etc.).

### Skill Responsibilities

1. Accept a release version as input (e.g. "0.0.1")
2. Run generate_status_overview.py to refresh STATUS.md
3. Spawn Phase 1 (scope check) agent
4. Spawn Phase 2 (epic) agents in parallel
5. Wait for Phase 2; spawn Phase 3 (feature) agents in parallel
6. Wait for Phase 3; spawn Phase 4 (gap verification) agent
7. Present consolidated questions to user
8. Iterate on user feedback
9. Mark task complete when user approves all items

### Skill Input Parameters

- `release_version`: "0.0.1" (required)
- `task_path`: path to the release prep task folder (for writing questions/)

### What the Skill Does NOT Do

- Read all requirements upfront (that is delegated to per-agent reads)
- Make architecture decisions (those are surfaced as questions to user)
- Create feature-level requirements without user approval

---

## Two-Level Structure: Epics First, Then Features

The two-phase approach (epics → features) is important because:
- An epic agent may determine a MISSING feature requirement
- That feature requirement must be created (with user approval) BEFORE
  a feature agent can check task coverage for it
- Therefore: epic phase completes, user approves new requirements, THEN feature phase runs

This means the workflow has a USER APPROVAL GATE between Phase 2 and Phase 3:
- Phase 2 output: any new feature requirements needed + user questions
- User approves new requirements
- Phase 3 begins (feature agents can now read the approved requirements)

---

## Open Questions About This Approach

1. Should epic agents write draft requirement text (for missing features) that
   the user can approve/edit, OR should they flag the gap and wait for a
   separate requ-explore run?

2. For the scope coverage check (Phase 1), should the agent try to match
   scope_boundaries.includes text to requirement names heuristically, or
   should it rely on explicit mapping files?

3. Should feature agents create tasks immediately (and flag overrides) or
   only create tasks after explicit user approval?
   Recommendation: create tasks immediately for clear cases (requirement is
   complete, items are well-defined), flag for approval only when requirement
   has gaps or open decisions.

4. Should generate_status_overview.py be enhanced to also output a
   "requirements assigned to release X" list with task counts, to make
   Phase 0 bootstrap cheaper?
