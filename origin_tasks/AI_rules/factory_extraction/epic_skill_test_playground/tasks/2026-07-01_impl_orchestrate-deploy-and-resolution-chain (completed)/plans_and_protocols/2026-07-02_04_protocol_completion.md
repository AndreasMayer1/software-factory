# Protocol — TASK-PROC-068-15 completion (2026-07-02, interactive resume)

Session e52b1147 (gmail), interactive resume of the parked orchestration task. Developer answered the
three parked questions (standalone authorized; T-C under layer-derivation; mint the T-D obligation), then
in discussion refined the DEPLOY track into five capabilities and surfaced the build-mode/harvest gap.

## Delivered

**Requirement ACs (via requ-explore Direct-Edit Flow, commit 18c7d415):**
- REQ-PROC-041-01 **AC-39** — orchestrator relocatable/project-agnostic (EGP F, MEDIUM).
- REQ-PROC-071-06 **AC-07** — layer-derivation project-relative, harness-unaware (EGP F, MEDIUM).
- REQ-PROC-068 **AC-11** — build/maintain run: isolated-copy derivation + registry-driven harvest back to
  `test_harness_app/`, no reset of derived layers (EGP F, MEDIUM).

**Tasks created:**
| Task | ID | Home | covers | after |
|------|----|------|--------|-------|
| T-B | TASK-PROC-068-16 | REQ-PROC-068 | AC-10 | [] |
| T-E | TASK-PROC-041-01-12 | REQ-PROC-041-01 | AC-39 | [] |
| T-C | TASK-PROC-071-06-06 | REQ-PROC-071-06 | AC-07 | [068-16, 041-01-12] |
| T-F | TASK-PROC-068-18 | REQ-PROC-068 | AC-11 | [068-16, 041-01-12, 071-06-06] |
| T-D | TASK-PROC-068-17 | REQ-PROC-068 | — (bridge) | [068-16, 041-04-06..09] |

T-D holds `resolves_parked_task: TASK-PROC-068-11` (developer-minted, interactive — the authority to author
068-11's resolution.md). T-R2 (original plan step 3) remained superseded by 041-04-06..09.

**Rewires:** 068-11 → `after: [068-16]`; 068-12 → `after: [071-05-05, 068-11, 071-06-06, 041-01-12, 068-18]`.

**Override:** T-B, T-E, T-C, T-F, T-D all registered in `.claude/task_ordering_priority_override.txt`
(recursive standing rule carried into each created goal.md).

## Architecture principle held (developer)

Layer-derivation (T-C) and the orchestrator (T-E) are **project-agnostic / harness-unaware** — they operate
on "the current project," resolved from cwd. Only the **playground** (T-B deploy, T-F build-mode/harvest,
reset policy) knows about the harness. Harness-internal runtime tasks created by a derivation run live in
the harness's own tree and are governed by *its* orchestrator — never registered in this project's override.

## Flags
- **D4:** TASK-PROC-071-05-05 is itself parked/in_progress and independently gates 068-12 — out of scope.
- No successor orchestration task created (the known gaps are closed).

## Investigation artifacts
- `2026-07-02_03_investigation_target-project-autorun.md` — dispatch mechanics + orchestrator hardcoding
  (grounded T-E and the D3/harvest decisions).
