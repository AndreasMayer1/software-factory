# Planning decision — clean re-run, no backward-compat constraint (2026-06-04)

Developer decision recorded at the close of the evaluation task TASK-PROC-032-28, before this redesign begins:

- **There will be NO further run of the currently-existing scribble workflow.** It is being redesigned (this
  task, TASK-PROC-032-29). The current workflow is frozen as-is; do not invest in iterating it further.
- **The pilot TASK-FUNC-007-01-05 will be reset and re-executed from scratch** with the redesigned workflow.
  Planned sequence (developer-owned, future work — NOT part of executing this design task):
  1. Create a new branch that **archives the current result** of TASK-FUNC-007-01-05.
  2. **Remove what TASK-FUNC-007-01-05 created on `develop`** (its scribble artifacts under
     `requirements_tasks/scribbles/therapist/data_transfer/`, its task-state, and any pending_feedback gate).
  3. **Re-execute TASK-FUNC-007-01-05 from scratch** using the new scribble workflow once it exists.

## Consequence for this redesign (TASK-PROC-032-29)

- **No backward-compatibility requirement with in-flight pilot artifacts.** The redesign does NOT have to
  migrate or preserve the existing v1/v2 scribbles, the current `question.md` gate, or any half-iterated state.
  It gets a clean greenfield re-run of the pilot. Design for the right end-state, not for migrating the
  current artifacts.
- The redesign still must account for the *brownfield retro-scribble* reality in general (Round-1 F10 — many
  screens are already implemented and awaiting refinement); "clean re-run" applies to the **pilot's** scribble
  artifacts, not to the whole app's implemented-first situation.
- The comment-nesting render-leak (Round-2 §1) need not be hot-patched on the existing pilot artifacts — it is
  fixed in the redesigned generator, and the pilot is re-run through it.
