---
task_id: TASK-PROC-044-06
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-29T23:15:23Z
effort: S
created: 2026-05-29
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-04]
  sections: []
scope_description: "Define revision_target.yaml schema for skill→skill async revisions (per 09_amendments.md §A-1). Add task-create sub-procedure for creating a revision-attached task. Update automation/pending_feedback/README.md with: (a) the revision-via-task pattern; (b) the 'no cross-task scan for revision_target.yaml' rule; (c) cleanup convention — pending_feedback/{TASK_ID}/ moves to answered_feedback/{TASK_ID}/ on resolution. Write scripts/maintenance/archive_answered_feedback.py to periodically prune old answered_feedback entries (git preserves history)."
release_description: ""
opus_recommended: false   # reason: small documentation + schema + one small script; well-scoped
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-4
session_id: ce4f46f2-a47a-4fe4-b317-b0e9d1232179
session_account: web

---
# Goal: Define revision_target.yaml + Cleanup Discipline for pending_feedback

## Objective

Formalize the skill→skill async revision channel (`revision_target.yaml`) and codify cleanup discipline for `automation/pending_feedback/`. The channel design is settled (per `09_amendments.md` §A-1): `revision_target.yaml` lives inside an auto-created revision task's workspace, NOT in a separate active scan.

## Background

The exploration in TASK-PROC-044-02 initially considered Magentic-style unified queues but settled on a simpler model that fits our session-driven (not runtime-driven) architecture:

| Direction | Mechanism |
|---|---|
| skill → skill (async, fresh session) | Auto-create a revision task; attach revision_target.yaml in its plans_and_protocols/ |
| skill → developer (blocking, same session) | automation/pending_feedback/{TASK_ID}/question.md (existing channel, unchanged) |
| skill → skill (synchronous, same session) | Direct Skill invocation, no file artifact needed |

This task lands the documentation + schema + the cleanup discipline.

## How to Approach This

1. Read `09_amendments.md` §A-1 in the parent exploration's plans_and_protocols/.
2. Author the formal schema for `revision_target.yaml` (see `prototypes/example_revision_target.yaml` in the exploration workspace). Add the schema to `.claude/schemas/revision_target.yaml`.
3. Update `.claude/skills/task-create/SKILL.md`: add a sub-section "Creating a revision-attached task" that documents:
   - When to use (skill X needs skill Y to revise an upstream artifact)
   - How to author the task's goal.md referencing revision_target.yaml
   - How to attach revision_target.yaml in the new task's plans_and_protocols/
4. Update `automation/pending_feedback/README.md` with the three documented items:
   - The revision-via-task pattern (cross-reference to task-create's new sub-section)
   - The "no cross-task scan for revision_target.yaml" rule (the lifecycle IS the task's status; no separate scanner)
   - Cleanup convention: pending_feedback/{TASK_ID}/ moves to answered_feedback/{TASK_ID}/ on resolution. (This is already the de-facto pattern; this task makes it explicit.)
5. Write `scripts/maintenance/archive_answered_feedback.py` (use `claude-write-script`). The script: walks `automation/answered_feedback/`; identifies folders older than N days (configurable, default 30); deletes them (git preserves the content); reports what was deleted.
6. Test the script on the existing `answered_feedback/TASK-PROC-035-17/` if it's old enough; otherwise add a fixture.

## Acceptance Criteria

- [x] `.claude/schemas/revision_target.yaml` exists; lint passes against it
- [x] `.claude/skills/task-create/SKILL.md` has a "Creating a revision-attached task" sub-section
- [x] `automation/pending_feedback/README.md` documents all three items (pattern, no-scan rule, cleanup)
- [x] `scripts/maintenance/archive_answered_feedback.py` exists, follows tier annotation, passes Python gates
- [x] Script tested (dry-run + actual run) on at least one entry

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | This task is parallel-eligible; no hard predecessor |

## Notes

This task is in `flutter_app/.claude/task_ordering_priority_override.txt`. The revision_target.yaml schema can also be informed by what FU-1 produces (it may add a schema convention this should follow), but no hard dependency.
