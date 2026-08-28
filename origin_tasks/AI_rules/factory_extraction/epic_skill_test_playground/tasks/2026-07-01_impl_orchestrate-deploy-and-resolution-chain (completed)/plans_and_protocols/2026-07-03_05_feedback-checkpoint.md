---
skill: task-resolve
mode: interactive
decision: "redirected"
task_id: TASK-PROC-068-15
captured_at: 2026-07-03
---

# Question

Proposed DEPLOY-track set = T-B deploy + T-C (harness-aware derivation) + T-D bridge; single deploy-run-reset cycle

# Developer Answer

"It does uh git reset because the use case for the playground is of course to test and
after the test you want to reset. But the use case we have for the layer derivation is
let's call it maintenance or creation of the playground. So of course we do not want to
reset the derived layers. We want to copy the created artifacts back to the test harness
app folder that exists in this project."

Follow-up: "In build mode it also has to run in an isolated deployed copy because we have
to make sure that the layer derivation works properly and it only works properly if it
has its own project. ... we can rely on the artifact registry of .factory/" to identify
what to copy back.

Also steered T-C framing: "the layer derivation must be unaware of this specific
situation. The session that calls or starts the layer derivation inside the skill
playground is part of the skill playground mechanism." (→ T-C is project-relative /
harness-unaware, NOT target-root-aware; the harness-aware part belongs to the playground.)

# Rationale Captured

Developer split derivation vs playground responsibilities and added a build/maintain run mode (isolated-copy derivation + registry-driven harvest back to test_harness_app/, no reset), yielding T-E + T-F and reframing T-C as harness-unaware
