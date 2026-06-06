---
requirement: REQ-PROC-032-05
requirements_version: 85ed6d20
created: 2026-06-06
mode: full
source: task-derive-from-requ run under TASK-PROC-032-30 (developer-approved next step)
---

# Task Creation Plan for REQ-PROC-032-05 (Consistency & Scribble-Layer Model — F05)

Decomposes the 14 ACs (AC-01…AC-14) of `feat_consistency_sci_layer/requirements.md` into the
manifest consistency-layer impl tasks **T-C8…C14, C17** plus one verification task. Source of truth
for task shape + dependency edges: the redesign manifest
`…/2026-06-04_explore_redesign-implementation-workflow-scribble-gate (completed)/plans_and_protocols/2026-06-05_13_implementation-task-manifest.md`
(Phase-C table).

## Cross-reference handling (Phase 1.5)
Developer directive (2026-06-06 feedback-checkpoint) resolved the defer/proceed blocker and instructed
"CONTINUE — run task-derive-from-requ", post-dating the unanswered cross-ref classification question.
Per that directive the Phase 1.5 escalation is NOT re-raised. The one load-bearing upstream relationship
(REQ-PROC-035 two-wave spine) is carried as the cross-slice `after` edge on the affected tasks
(T-C8 → spine T-C2; T-C13/T-C17 → spine T-C1) and recorded in `implementation_notes` for
`task-repair-meta`, since the REQ-PROC-035 spine impl tasks are not yet derived. Semantic links
(REQ-PROC-058/069/030-01) are left to a future cross-ref pass / task-repair-meta.

## Cross-slice dependency note
The spine impl tasks **T-C1** (`task-derive-from-requ --scope {presentation,code}`) and **T-C2**
(`release-begin-impl` Wave-1 split), both derived from REQ-PROC-035, do **not exist yet**. Tasks that
depend on them (T-C8, T-C13, T-C17) record the edge in `implementation_notes` as an unresolved
cross-slice dependency for `task-repair-meta` to reconcile once REQ-PROC-035 is decomposed. Within-slice
edges use the real allocated TASK-IDs.

## Tasks

- task_name: "derive-f05-sci-invariant-audit-and-rot-graph"
  handle: T-C8
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md"
  requirements_version: "85ed6d20"
  covers_acs: [AC-01, AC-02, AC-03, AC-14]
  effort: L
  layer: process
  after: []          # + cross-slice: spine T-C2 (record in notes)
  task_type: impl
  opus_recommended: true
  target_package: ""
  implementation_notes: >
    SCI machinery: set `stale_since` on a LOCKED-IN requirement edit; auto-create scribble-refresh
    tasks; the five-edge staleness rot-graph + detectors; the standing script-driven SCI audit
    (`check_scribble_currency.py`, new) blocking at release finalization, additive to the storage-mirror
    parity check; soft-SCI configurable sign-off-gated mode default OFF; emit the stall report (E1 probe).
    Skills/scripts: claude-modify-skill (requ-explore / task-derive-from-requ) + claude-write-script
    (new currency script). CROSS-SLICE after: the REQ-PROC-035 spine task implementing T-C2
    (release-begin-impl Wave-1 split) — not yet derived; reconcile via task-repair-meta.

- task_name: "derive-f05-verify-flutter-stale-block-and-override"
  handle: T-C9
  covers_acs: [AC-13]
  effort: M
  layer: process
  after: [T-C8]
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    ui-verify-flutter hard-blocks on a stale scribble (generative reader) with an explicit advisory
    override that runs and labels its verdict as made against a stale target; referential readers flag
    only. claude-modify-skill (ui-verify-flutter). After the SCI machinery task (T-C8).

- task_name: "derive-f05-loopback-as-task"
  handle: T-C10
  covers_acs: [AC-04]
  effort: M
  layer: process
  after: [T-C8]
  task_type: impl
  opus_recommended: false
  implementation_notes: >
    Loopback-as-task L1–L6: stop inline requ-explore, create blocking tasks for normative-upstream
    loopbacks; un-approved scribble ⇒ same task, new version. claude-modify-skill
    (ui-scribble-feedback-classify). After T-C8.

- task_name: "derive-f05-lazy-wavefront-cascade-and-width-breaker"
  handle: T-C11
  covers_acs: [AC-05, AC-06]
  effort: L
  layer: process
  after: [T-C8]
  task_type: impl
  opus_recommended: true
  implementation_notes: >
    Lazy-wavefront depth-1 cascade detector (live flow_positions, per-cascade visited set) + two-stage
    width breaker (configurable, soft 3 / hard 7 measured-on-fixture defaults, hard escalates via
    back-pressure) + PROP-10 mode-independent entry-reference integrity check & bounded recovery; emit
    the cascade log (E2 probe). claude-modify-agent (ui-scribble-cross-feature-checker) +
    claude-modify-skill (ui-scribble-auto-review). After T-C8.

- task_name: "derive-f05-entry-context-spine"
  handle: T-C12
  covers_acs: [AC-08]
  effort: L
  layer: process
  after: [T-C8]
  task_type: impl
  opus_recommended: true
  implementation_notes: >
    Entry-context spine (PROP-8): generator emits entry-surface type, entry-point multiplicity, back/close
    destination, container dimension + rationale, and a resolvable 3-tier entry reference; reviewers assert
    presence/consistency/size-appropriateness; bounded reconciliation against the router/screenshot only
    for already-built openers (greenfield skips). claude-modify-agent (ui-scribble-generator + reviewers)
    + claude-modify-skill (ui-scribble-auto-review). After T-C8.

- task_name: "derive-f05-coverage-ordering-and-l3-assertion"
  handle: T-C13
  covers_acs: [AC-07, AC-09]
  effort: L
  layer: process
  after: []          # + cross-slice: spine T-C1 (record in notes)
  task_type: impl
  opus_recommended: true
  implementation_notes: >
    Coverage/ordering (PROP-9/11): flow→scribble coverage report (functional + chrome-owning non-functional,
    advisory); auto task_type:scribble for presentation/both ACs; task-ordering soft-pref (primary forward
    entry path, depth-1, basis resolution); L3 coverage assertion + L3 chain-length alert; emit graph-stats
    dump. New report script + claude-modify-skill (task-derive-from-requ) + ordering rules. CROSS-SLICE
    after: REQ-PROC-035 spine task implementing T-C1 (--scope mode) — not yet derived; reconcile via
    task-repair-meta.

- task_name: "derive-f05-domain-design-edge-and-facet-tagging"
  handle: T-C14
  covers_acs: [AC-11, AC-12]
  effort: M
  layer: process
  after: [T-C13]
  task_type: impl
  opus_recommended: true
  implementation_notes: >
    Domain→design conditional edge + data-bound detector (presentation/both AC references a domain
    value-object with behaviour criteria in the same design-unit ⇒ soft ordering, hardened to blocking
    for code-first units, human override at gate) + AC facet-tagging {presentation|behaviour|both}
    (auto-heuristic + human confirm, fail-safe to presentation) + facet-tag audit (E5 probe).
    claude-modify-skill (task-derive-from-requ, requ-explore). After T-C13.

- task_name: "derive-f05-app-shell-launch-map-and-seam-detection"
  handle: T-C17
  covers_acs: [AC-10]
  effort: L
  layer: process
  after: []          # + cross-slice: spine T-C1 (record in notes)
  task_type: impl
  opus_recommended: true
  implementation_notes: >
    Design-unit map emission + two-tier entry-seam foundation_gap detection (Tier A requ-derive-from-flow
    local provisional pass / Tier B requ-verify-flow-coverage --all global authoritative dedup-and-confirm)
    + create the app-shell / feature-launch-map requirement (PROP-11 R4 / F12–F14) as the canonical Tier-1
    target. claude-modify-skill (requ-derive-from-flow, requ-verify-flow-coverage). NOTE: authoring the
    launch-map requirement is part of scope. CROSS-SLICE after: REQ-PROC-035 spine task implementing T-C1 —
    not yet derived; reconcile via task-repair-meta.

- task_name: "verify-f05-consistency-layer"
  handle: T-C-F05-V
  covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14]
  effort: M
  layer: process
  after: [T-C8, T-C9, T-C10, T-C11, T-C12, T-C13, T-C14, T-C17]
  task_type: verify
  opus_recommended: false
  implementation_notes: >
    Audit task (process verification): run check_scribble_currency.py + the SCI audit + the flow→scribble
    coverage report against a fixture; confirm each of AC-01…AC-14 is observable in the scripts/skills/agents
    outputs (SCI blocks a stale-scribble coding task; the five detectors fire; loopback creates the right
    task/version; cascade + width breaker behave; L3 assertion + chain alert surface; entry-context spine
    emitted/reviewed/reconciled; coverage report + ordering; launch-map requirement exists + seam detection;
    domain→design edge + facet tags + audit; generative-block/referential-flag; soft-SCI mode gated/off).
    Distinct from the global fixture gate T-CV. After all 8 impl tasks.

## Coverage Matrix

| AC | Task(s) | Package |
|----|---------|---------|
| AC-01 | T-C8, verify-f05 | (none) |
| AC-02 | T-C8, verify-f05 | (none) |
| AC-03 | T-C8, verify-f05 | (none) |
| AC-04 | T-C10, verify-f05 | (none) |
| AC-05 | T-C11, verify-f05 | (none) |
| AC-06 | T-C11, verify-f05 | (none) |
| AC-07 | T-C13, verify-f05 | (none) |
| AC-08 | T-C12, verify-f05 | (none) |
| AC-09 | T-C13, verify-f05 | (none) |
| AC-10 | T-C17, verify-f05 | (none) |
| AC-11 | T-C14, verify-f05 | (none) |
| AC-12 | T-C14, verify-f05 | (none) |
| AC-13 | T-C9, verify-f05 | (none) |
| AC-14 | T-C8, verify-f05 | (none) |

100% AC coverage. 8 impl tasks ⇒ separate verification task present (verify-f05-consistency-layer).
No circular within-slice dependencies. All tasks carry no target_package (process tooling) ⇒ each MUST be
appended to `.claude/task_ordering_priority_override.txt` (developer directive).
