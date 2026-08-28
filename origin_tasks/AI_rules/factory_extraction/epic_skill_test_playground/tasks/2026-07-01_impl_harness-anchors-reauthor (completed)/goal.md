---
task_id: TASK-PROC-068-11
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-07-08
session_completed_at: 2026-07-08T09:29:27Z
effort: M
created: 2026-07-01
started: 2026-07-06
expected_tool_calls: 40
skill_chain_depth: 3
after: [TASK-PROC-068-16, TASK-PROC-066-13, TASK-PROC-041-06-05]  # 068-16 + 066-13 (both complete) gate on the corrected harness baseline. 041-06-05 (added 2026-07-06) gates on the delegated-LLM-work fix being VERIFIED in place: this task's re-derivation runs the expensive/rate-limit-prone nested-`claude` playground child, which is exactly what REQ-PROC-041-06 (delegated-work state + configurable-capacity pool semaphore + verified-artifact completion + idempotent re-entry) makes safe. Reset to pending 2026-07-06 (see protocol 20) so it gets a clean run once the fix lands.
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Clean-slate the non-conformant harness product-definition artifacts and re-author the ANCHOR layers (personas + scenarios) via the real factory authoring skills, README_3/README_4-conformant. Hard developer-approval gate before completion."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: ec060365-1ed5-4d49-98ce-cce64740eaf8
session_account: web
---
# Goal: Re-author the Harness Anchor Layers (Personas + Scenarios)

## Objective

Replace the non-conformant harness product-definition artifacts with **README-conformant anchor
layers** — personas and scenarios — authored by the **real factory authoring skills**, so the
downstream derivation (TASK-PROC-068 flows + requirements) runs against valid anchors.

## Background

TASK-PROC-068-07 generated the entire harness product-definition stack via a hand-rolled ID-coverage
driver + freehand markdown (`task-resolve`), never invoking the authoring skills. The result does not
conform to the artifact-type definitions:
- **Scenarios** violate the README_4 CRITICAL RULE (they describe the app instead of the status quo),
  use a flat-file layout instead of `personas/<p>/scenarios/<name>/scenario.md`, and lack the mandated
  sections and frontmatter.
- **Personas** lack the README_3 VCD stack, sections, and frontmatter.

Per REQ-PROC-068 AC-06 the harness product definition MUST be authored **via the factory skill chain**.
The type definitions are binding on the harness because the factory (skills + artifact types) is being
extracted to stand alone and the harness consumes it as its base.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

1. **Clean-slate** the non-conformant harness product-definition artifacts under
   `test_harness_app/requirements_user_needs/` and `test_harness_app/requirements_tasks/` (personas,
   scenarios, flows, requirements) via `git rm` — they cannot be incrementally fixed. (Flows +
   requirements are re-created by the downstream derivation task.)
2. Author the **personas** with `ux-write-persona` — the value-conflict pair from REQ-PROC-068:
   **Archivist** (completeness) vs **Quick-Logger** (speed), meeting on the single rating-entry form.
   Full README_3 conformance (VCD stack, sections, frontmatter, folder layout).
3. Author the **scenarios** with `ux-write-scenario` — **status-quo / pre-app** per README_4 (how these
   users rate & journal movies/books *today, without the app*), folder-per-scenario layout, all mandated
   sections; seed `test_harness_app/requirements_user_needs/SCENARIO_INDEX.md` as needed.
4. Ensure the harness structural mirror carries its own `CLAUDE.md` and `doc/` if the authoring skills
   require them (AC-01 mirror).

## Scope

### In Scope
- Remove the non-conformant harness product-definition artifacts.
- Author README_3-conformant personas (Archivist, Quick-Logger) via `ux-write-persona`.
- Author README_4-conformant, **status-quo** scenarios via `ux-write-scenario`; seed SCENARIO_INDEX.
- The minimum personas/scenarios the harness's coupling test cases need — not a believable product's
  worth (REQ-PROC-068 build order): enough to anchor the flow/requirement derivation and fire P-E/P-F/T4.

### Out of Scope
- Flows and requirements — derived by the downstream derivation task via the fixed mechanism.
- The mechanism fix itself (TASK-PROC-071-05-05).

## Developer Approval Gate (HARD — blocks completion)

**This task MUST NOT complete until the developer has personally reviewed and approved the authored
personas and scenarios.** Before invoking `task-complete`:
- Present every authored persona and scenario to the developer for review.
- In automated mode: write the artifacts for review and park via `automation/pending_feedback/<TASK_ID>/`
  requesting explicit approval; do NOT self-approve, do NOT complete until the developer records approval.
- Only proceed to `task-complete` after recorded developer approval.

## Acceptance Criteria

- [x] AC-1: Non-conformant harness product-definition artifacts removed.
- [x] AC-2: Personas (Theo/Archivist, Maya/Quick-Logger) authored via `ux-write-persona`, fully
      README_3-conformant (folders renamed to real human names `theo`/`maya` per developer directive).
- [x] AC-3: Scenarios authored via `ux-write-scenario`, status-quo (pre-app), fully README_4-conformant,
      correct folder-per-scenario layout, SCENARIO_INDEX updated.
- [x] AC-4: Developer has reviewed and **explicitly approved** the authored anchors before completion
      (checkpoint 28, 2026-07-08: "You did it! Approved.").

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking predecessors; anchors are authored directly (not derived) |

## Notes

- Coordinator-derived, covers-empty process task (no `target_package`) — surfaces only via the override
  file. Relates to REQ-PROC-068 AC-06 (product definition authored via the factory skill chain).
- Downstream: TASK-PROC-068 derivation task consumes these approved anchors.
