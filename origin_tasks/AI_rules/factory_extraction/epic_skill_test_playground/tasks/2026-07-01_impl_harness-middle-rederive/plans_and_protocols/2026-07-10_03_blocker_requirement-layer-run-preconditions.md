# Blocker — TASK-PROC-068-12 requirement-layer run pre-conditions

Date: 2026-07-10 · session c3601a41 · model Opus 4.8 · automated mode

## State verified this session

**Flow layer (AC-1) — materially done, but DRAFT + review-gated.**
- Two conformant flows landed in `test_harness_app/`: `detailed_entry_after_movie/flow.md`
  (FLOW-001, theo/SCEN-001-01) and `quick_rating_after_movie/flow.md` (FLOW-002, maya/SCEN-002-01),
  plus `FLOW_INDEX.md`. Committed by predecessor **TASK-PROC-071-06-09** (da1541b1) as the
  deliberately-bounded "flow layer only (2 units)" slice of 068-12's middle-layer derivation.
- Those flows are `review_status: draft` (authored autonomously). 071-06-09 records, per the
  071-06-08 developer decision: **"Developer reviews the harvested flow artifacts for quality
  before TASK-PROC-068-12 is accepted."** → an unmet developer-review gate.

**Requirement layer (AC-2) — NOT derived.**
- `test_harness_app/requirements_tasks/functional/flow_layer/requirements.md` (REQ-HARNESS-01) is
  only a derivation *bucket*, not a requirement derived from the flows. No `flow_requirement` output exists.

## Why I did not launch the requirement-layer build-mode run

1. **Filed blocker TASK-PROC-068-23 (`pending`) explicitly "Blocks 068-12".** `build_resume.py`
   reuses the run's `session_uuid` on relaunch; the Claude CLI rejects an already-used id → empty
   stdout → resume dies. So a preserved build-mode run **cannot be relaunched** until 068-23 lands
   (fresh child session-uuid per relaunch). On the current `pro` tight-tier window an interrupt is
   likely, and the run would be unrecoverable (only a manual stale-CCS-state workaround exists).
   Note: 068-23 is NOT in 068-12's `after:` (it was filed after `after:` was last set).

2. **No approved requirement-boundary spec or budget.** The flow run used a *validated* spec
   (071-06-08) with *explicit* developer budget approval. For `flow_requirement` there is none:
   `unit_task_req_id`/`unit_task_req_path` for the requirement layer are undecided (no REQ-HARNESS-02,
   no `requirement_layer` path exists), and the authoring skill is the heavier two-step
   `requ-derive-from-flow` + `requ-explore` chain (a flow may yield multiple requirements, or
   requirements may span flows — "one flow_requirement unit per flow" is an unverified decomposition).
   Inventing these autonomously re-creates 068-07's exact failure mode (mis-scoped driver authoring
   non-conformant content into the harness tree).

3. Mechanism is otherwise ready: `flow_requirement` → `requ-derive-from-flow+requ-explore` is wired
   (`backfill_orchestration.py:705`); `build.py` contract confirmed; flow-run driver artifacts exist
   under 071-06-09 as a template.

## What unblocks this task (developer decisions requested — see pending_feedback)

- **A** Land TASK-PROC-068-23 first (build-resume fix), and add it to 068-12's `after:`.
- **B** Confirm the DRAFT flow artifacts pass developer quality review (071-06-09 gate).
- **C** Approve the requirement-layer run: target req id/path (e.g. REQ-HARNESS-02 /
  `requirements_tasks/functional/requirement_layer`), decomposition (per-flow vs consolidated),
  budget, and whether to reuse the existing flows as the anchor.
