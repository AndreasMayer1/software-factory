---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - requ-explore        # step 2a (planned)
  - task-derive-from-requ  # step 2b T-corpus/T-maturity (planned)
  - task-create         # step 2b T-skeleton/T-orch2 (planned)
  - claude-log
  - task-complete
---

# Protocol — T-orch1 (TASK-PROC-068-02) GREEN-branch orchestration

**Task:** TASK-PROC-068-02 · automated, Opus · 2026-06-27 · session cf1ef47f / gmail2.

## Input read (cite, not re-derived)

- **Spike verdict** (TASK-PROC-073-01-01 `…_02_verdict_disproof-spike-go-no-go.md`): **🟢 GREEN.**
  Detection 2/2 (position-robust, mechanism-precise) on the hardest clean matched pair
  (`ideation-synthesize/SKILL.md` CRITIC-ONLY defect). Real cost $0.549 / ~40 s / 0 human attention vs.
  ≈$10–60 and 10–30 min manual → cheaper ≥18× in $ and ≥16× in wall-clock even at the aggressive floor.
- **Developer approval** (`…_04_protocol_approval-and-close.md`): *"I approve. close the task and unblock
  the build."* No additional actions, no caveat concerns. → **GREEN branch taken.**
- **Build-out plan** (`…/2026-06-11_explore…/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`):
  Stage 1 GREEN batch = T-skeleton, T-corpus, T-maturity (interactive), T-orch2; ordering lives in
  the task graph (`after:` edges); the override file carries visibility only.
- **First-build gates SG-01..04** (full-scope final report `…_008_final_report.md` + handoff `…_09_…`):
  - SG-01 — `orchestrate.py:_launch_claude_session` is NOT a reusable API → T-skeleton must budget a real
    launch **adapter** (extract launch core; parameterize the JSONL hung-detection path on the child's cwd).
  - SG-04 — worktree alone does NOT close CON-04 absolute-path cwd-escape → T-skeleton must re-instate one
    OS-level containment layer (separate OS user / namespace-unshare).
  - SG-02 — cost capture: **already PASS** in the spike (non-`--bare` `--output-format json` carries
    `total_cost_usd`). Carried as a note, not new work.
  - SG-03 — paired-fixture validity floor (~100): unreachable at skeleton stage → T-corpus accumulates
    fixtures; skeleton/early verdicts are **advisory** until N ≥ floor. Bakes into T-maturity scoping.

## State findings (pre-execution)

1. **Step 2a gap is precise.** `feat_regression_gate/requirements.md` (REQ-PROC-073-01, unchanged since the
   Stage-0 commit 9b25bde0) already carries AC-01/AC-02/AC-03 in `trackable_items` frontmatter (egp +
   consequence) and describes all three in `## Behavior` + `## Developer Guidelines`. What it lacks — unlike
   its sibling REQ-PROC-068, which has one — is an explicit **`## Acceptance Criteria`** section with checkable
   AC statements. The goal's "reopen the `## Deferred` items" phrasing is imprecise: the `## Deferred` block
   holds only "Full aggregation + admissibility" (a larger, still-deferred slice), NOT AC-01/AC-03. So step 2a
   = **author the explicit checkable `## Acceptance Criteria` section for AC-01 (corpus) and AC-03 (maturity
   walk)** (and state AC-02, already done, for completeness), grounded in the existing Behavior prose. This is
   a decided, in-bounds edit → authored via `requ-explore`.
2. **Clean slate.** No TASK-PROC-073-01-02..09 and no TASK-PROC-068-04..09 exist — the batch is created fresh.
3. **Terminus.** TASK-PROC-068-03 currently `after: [TASK-PROC-068-02]`; re-point to the new frontier T-orch2.

## Plan (GREEN branch)

| Step | Action | Skill | Coverage / flags |
|------|--------|-------|------------------|
| 2a | Add explicit `## Acceptance Criteria` (AC-01 corpus, AC-02 spike-done, AC-03 maturity walk) to REQ-PROC-073-01 | `requ-explore` | decided in-bounds edit |
| 2b-1 | T-corpus (impl) + T-maturity (verify, `interactive_required: true`) — derive against REQ-PROC-073-01 AC-01 / AC-03 | `task-derive-from-requ` | T-corpus covers AC-01; T-maturity covers AC-03 |
| 2b-2 | T-skeleton (impl, substrate) — walking skeleton deploy→run-as-cwd→git-reset→cost; bake SG-01 adapter + SG-04 OS-containment | `task-create` | parent REQ-PROC-068; no AC-cover (substrate) |
| 2b-3 | T-orch2 (`orchestration_task: true`) — next gap-filler; carries the visibility-propagation directive forward | `task-create` | parent REQ-PROC-068 |
| edges | `after:` wiring: T-maturity `after: [T-skeleton, T-corpus]`; T-orch2 `after: [T-maturity]` | — | |
| 2c | Re-point TASK-PROC-068-03 (T-finalize) `after:` → `[T-orch2]` | Edit | unbroken-edge mechanic |
| 4 | Append every created task ID to `.claude/task_ordering_priority_override.txt` | Edit | developer directive (self-propagating) |

**Acceptance-criteria mapping → goal ACs:** spike verdict read + GREEN branch (AC-1); AC-01/03 slice authored +
batch+T-orch2 with correct edges (AC-2); terminus re-pointed (AC-4); all created tasks in override (AC-5);
successor orch task exists (AC-6). RED-branch ACs (AC-3) N/A — verdict is GREEN.

## Execution log

### Step 2a — DONE (2026-06-27)
Authored the explicit `## Acceptance Criteria` section in `feat_regression_gate/requirements.md` (AC-01 corpus,
AC-02 spike-done, AC-03 maturity walk) as checkable end-state statements grounded in the existing `## Behavior`.
No new IDs minted (AC-01/02/03 already in `trackable_items`), so id_registry regeneration skipped; aggregate
`requirements.md` regenerated via `merge_requirements.py`. EGP audit clean (3 ACs, 0 missing dispositions; the 2
confirmed≠auto mismatches are pre-existing intentional records). Handled as task-backed by TASK-PROC-068-02
(this orchestration task scopes the edit in goal step 2a; audit trail = this protocol + the task commit) — not
the taskless direct-edit path, and no redundant second requirement task created.

**Finding:** the goal's "reopen the `## Deferred` items" phrasing was imprecise — AC-01/AC-03 were never in
`## Deferred` (which holds only "Full aggregation + admissibility"). They were already authored in full in
`## Behavior` + `trackable_items` at Stage 0; step 2a's real residue was surfacing the explicit checkable AC
section (now done), matching sibling REQ-PROC-068's format.

### Step 2b — task batch (delegated)
Decomposition is pre-decided by the developer-directed build-out plan (not a fresh derivation), so the four
tasks are created via `task-create` (the goal sanctions "task-derive-from-requ / task-create") with explicit
`covers:` fields for AC tracking. Delegated to one background agent (isolates 4× heavy task-create skill loads
from the main session; closed loop: create 4 → wire after-edges → append override → re-point terminus → return
the 4 allocated IDs). Batch + edges:
- T-skeleton (impl, REQ-PROC-068, covers AC-07/08/09; SG-01 adapter + SG-04 OS-containment) — after: []
- T-corpus (impl, REQ-PROC-073-01, covers AC-01; SG-03 floor note) — after: []
- T-maturity (verify, REQ-PROC-073-01, covers AC-03, `interactive_required: true`) — after: [T-skeleton, T-corpus]
- T-orch2 (`orchestration_task: true`, REQ-PROC-068) — after: [T-maturity]; carries the visibility-propagation directive + Stage-2 recipe forward
- Re-point TASK-PROC-068-03 (T-finalize) after: → [T-orch2]
