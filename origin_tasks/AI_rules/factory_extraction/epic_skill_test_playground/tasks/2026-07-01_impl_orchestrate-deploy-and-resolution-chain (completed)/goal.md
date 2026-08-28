---
task_id: TASK-PROC-068-15
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-07-01
started: 2026-07-02
completed: 2026-07-02
expected_tool_calls: 45
skill_chain_depth: 4
orchestration_task: true
after: [TASK-PROC-041-04-06, TASK-PROC-041-04-07, TASK-PROC-041-04-08, TASK-PROC-041-04-09, TASK-PROC-068-14]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Orchestration: once the whole-factory-deploy AC (068-14) and the resolution-channel ACs (041-04-05) exist, create the grounded impl tasks T-B (deploy) / T-R2 (resolution impl) / T-C (layer-derivation reuse) / T-D (bridge), wire their after: edges, rewire 068-11 and 068-12, and add the new tasks to the priority override."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: e52b1147-1990-404a-b38d-353435a80512
session_account: gmail
---
# Goal: Orchestrate the deploy + machine-resolution + anchor-unblock chain

## Objective

Impl tasks cannot be grounded until their acceptance criteria exist. Two predecessor tasks author those
ACs: **TASK-PROC-068-14** (whole-factory-deploy AC on REQ-PROC-068) and **TASK-PROC-041-04-05**
(resolution-channel ACs on REQ-PROC-041-04). When BOTH are complete, this task creates the now-grounded
impl tasks and wires the full chain — with no dangling edges (the orchestration-task pattern).

Sizing: this task **splits into child tasks** (T-B/T-R2/T-C/T-D) — that is its deliverable — satisfying
the creation-time sizing gate by decomposition.

## Requirements Summary

Read the authoritative seed/spec before doing anything (full findings, corrected grounding, the exclude
set, and open items D3/D4):
`../2026-06-11_explore_llm-verifiable-open-ended-skill-tests (completed)/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`
(§§ "Continuation (2026-07-01)", "Revision (2026-07-01, developer)", "Pre-extraction exclude set").

Current requirements: ../requirements.md

## Scope

### In Scope — steps to perform (in order)

1. **Pre-flight:** confirm TASK-PROC-068-14 and TASK-PROC-041-04-05 are `completed` and that their ACs now
   exist in the respective `requirements.md`. If not, stop (dependency not met).

2. **Create T-B `extend-harness-deploy-full-factory`** (via `task-create`; execution skill
   `claude-write-script`): `type: impl`, `parent_requirement: REQ-PROC-068`, `covers` = the new
   whole-factory-deploy AC (from 068-14), `after: []`. Deliverable: extend `scripts/playground/deploy.py`
   (+ reset/launch as needed) to copy the whole factory into the harness — **not just `.claude/skills/`** —
   using a **coarse, `// TEMPORARY:` exclude rule** (the developer-approved NON-exhaustive exclude set in
   the plan; err toward over-inclusion — safe because the harness is isolated + git-reset). Prove a
   **contained** child (`containment.py`) runs a script-calling skill end-to-end (e.g.
   `generate_id_registry.py`, which anchors on `script_dir.parent.parent`). **Must NOT** treat
   `test_harness_app/` as factory content (it is the target); needs sub-folder boundaries for the entangled
   trees (`requirements_tasks/`, `scripts/`, `doc/`, `requirements_user_needs/`).

3. **Create T-R2 `impl-machine-resolution-channel`** (via `task-create`; `claude-write-script`):
   `type: impl`, `parent_requirement: REQ-PROC-041-04`, `covers` = the new resolution-channel ACs (from
   041-04-05), `after: []`. Deliverable: orchestrator detects `resolution.md` → resumes with it as the
   prompt → archives (mirroring the `answer.md` path); a guard blocks ANY task from writing `answer.md`;
   tests. Honor the discriminator (machine resolution only for "mechanism did not exist, another task built
   it").

4. **Create T-C `layer-derivation-reuse-of-deploy`** (via `task-create`; execution `claude-modify-skill`):
   `type: impl`, `after: [<T-B id>]`. Deliverable: `layer-derivation-start` can run its unit skills under
   the deployed harness so TASK-PROC-068-12 consumes the same mechanism. **Resolve D3** at creation:
   ground under REQ-PROC-071 (layer derivation) vs REQ-PROC-068 — pick per where the behavior is owned; if
   it needs a new AC, route through `requ-explore` first.

5. **Create T-D `resolve-068-11-targeting`** (via `task-create`): `type: impl`,
   `after: [<T-B id>, <T-R2 id>]`. Deliverable: write `resolution.md` into
   `automation/pending_feedback/TASK-PROC-068-11/` stating the harness-targeting deploy mechanism now
   exists (path `scripts/playground/…`) and 068-11 should author its anchors via the deployed harness —
   with provenance (T-B completion). This uses the machine channel built by T-R2; it must NOT touch
   `answer.md`.

6. **Rewire existing tasks** (edit their `goal.md` `after:` only):
   - TASK-PROC-068-11: `after: [] → [<T-B id>]`.
   - TASK-PROC-068-12: `after: [TASK-PROC-071-05-05, TASK-PROC-068-11] → [TASK-PROC-071-05-05, TASK-PROC-068-11, <T-C id>]`.

7. **Register in the priority override — MANDATORY, RECURSIVE rule.** Add T-B, T-R2, T-C, T-D to
   `.claude/task_ordering_priority_override.txt` (visibility only — order is the `after:` graph). **Standing
   rule (developer, 2026-07-01): every task that creates other tasks MUST add the tasks it creates to this
   file.** Therefore, in the `goal.md` of each of T-B/T-R2/T-C/T-D, if that task itself creates any further
   tasks, it MUST (a) add them to this override file and (b) carry this same instruction forward — the rule
   propagates recursively down the chain. Include this instruction verbatim in any created task's goal.

8. **Terminate the chain:** create NO successor orchestration task for this batch (the known gaps are
   closed). Note D4 (TASK-PROC-071-05-05 is itself parked and independently gates 068-12) as a flag only.

### Out of Scope
- Executing T-B/T-R2/T-C/T-D themselves (they run when dispatched).
- Editing the whole-factory-deploy AC or resolution-channel ACs (owned by 068-14 / 041-04-05).

## Acceptance Criteria

- [x] T-B / T-C / T-D created and grounded, with `after:` edges (T-R2 superseded by 041-04-06..09 per the
      Notes flag; **T-E and T-F added** during the interactive resume — see Notes "Scope refinement"). T-B=068-16,
      T-C=071-06-06, T-D=068-17, T-E=041-01-12, T-F=068-18.
- [x] TASK-PROC-068-11 (`after: [068-16]`) and TASK-PROC-068-12 (`after: [071-05-05, 068-11, 071-06-06, 041-01-12, 068-18]`) rewired.
- [x] The new tasks (T-B/T-E/T-C/T-F + bridge T-D) are listed in `task_ordering_priority_override.txt`.
- [x] No successor orchestration task created; D4 recorded as a flag (see Notes "D4").

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-14 | pending | Authors the whole-factory-deploy AC that T-B covers |
| TASK-PROC-041-04-05 | pending | Authors the resolution-channel ACs that T-R2 covers |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-14](../2026-07-01_explore_whole-factory-deploy-ac/goal.md) | Predecessor — authors the AC T-B covers |
| [TASK-PROC-041-04-05](../../../../workflows/epic_autonomous_task_execution/feat_feedback_pause_resume/tasks/2026-07-01_explore_machine-resolution-channel/goal.md) | Predecessor — authors the ACs T-R2 covers |
| [TASK-PROC-068-11](../2026-07-01_impl_harness-anchors-reauthor/goal.md) | Rewired + unparked via the bridge T-D |
| [TASK-PROC-068-12](../2026-07-01_impl_harness-middle-rederive/goal.md) | Rewired to depend on T-C |

## Notes

**FLAG (2026-07-02, from TASK-PROC-041-04-05):** Step 3 (create **T-R2 `impl-machine-resolution-channel`**)
is now **superseded** — the resolution-channel ACs (REQ-PROC-041-04 AC-10–AC-17) were approved on the
*obligation model* and already decomposed into concrete impl+verify tasks **TASK-PROC-041-04-06 / -07 /
-08 / -09** via `task-derive-from-requ`. Do NOT re-create T-R2; skip step 3. This task's remaining scope is
the **DEPLOY track** (T-B / T-C / T-D) and the 068-11/068-12 rewiring. T-D (the bridge that writes
`resolution.md` for 068-11) must depend on the now-created resolution impl tasks (04-06..09) rather than a
fresh T-R2. `after:` was rewired to depend on 04-06..09 + 068-14. The machine channel is now the
developer-approved obligation model (authority planted by `task-create` at the developer gate, propagated
to the terminal verifying task) — honor that when authoring T-D.

**Scope refinement (2026-07-02, interactive resume with developer).** The DEPLOY track was refined into
five clean, independently-grounded capabilities (developer authorized standalone creation + the T-D
obligation mint):
- **T-B** (068-16) — whole-factory deploy → REQ-PROC-068 AC-10.
- **T-E** (041-01-12) — session orchestrator relocatable/project-agnostic → REQ-PROC-041-01 AC-39 (new).
- **T-C** (071-06-06) — layer-derivation project-relative, harness-unaware → REQ-PROC-071-06 AC-07 (new).
- **T-F** (068-18) — playground build/maintain run + registry-driven artifact harvest back to
  `test_harness_app/`, no reset of derived layers → REQ-PROC-068 AC-11 (new). *Added this resume* after the
  developer flagged that the derivation use case (create/maintain) must keep the derived layers and copy
  them back, unlike the test-and-reset use case.
- **T-D** (068-17) — bridge: machine-resolve 068-11 via the developer-minted `resolves_parked_task` obligation.
Principle held throughout (developer): layer-derivation and the orchestrator stay **unaware** of the
harness (they operate on "the current project"); only the **playground** knows about the harness (deploy +
harvest + reset policy). The three new ACs were authored via `requ-explore` Direct-Edit Flow (commit that
introduced them: 18c7d415).

**D4 (flag only):** TASK-PROC-071-05-05 is itself parked/`in_progress` and independently gates 068-12; it
is out of scope for this chain and is not cleared by this task.

Grounding rationale (from the plan): the full-factory deploy is scoped under REQ-PROC-068 (playground),
independent of REQ-PROC-066; REQ-PROC-066 may consume it later as a realization of its AC-02. No governed
"what is the factory" manifest is authored — the requirement stays intent-level ("the whole factory"); the
file boundary lives only in T-B's temporary code and is replaced post-extraction by "copy whatever the
extracted factory project provides."
