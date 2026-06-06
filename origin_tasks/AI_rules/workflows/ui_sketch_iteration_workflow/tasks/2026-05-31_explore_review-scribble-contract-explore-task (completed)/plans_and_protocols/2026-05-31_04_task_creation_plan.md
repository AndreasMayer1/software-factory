---
requirement: REQ-PROC-032
requirements_version: 6ece1dc7
created: 2026-05-31
mode: full
scope: incremental — only uncovered AC-37..AC-41 (AC-01..AC-36 already covered by TASK-PROC-032-11..-20)
---

# Task Creation Plan for REQ-PROC-032 (incremental: AC-37..AC-41)

Derived per the remediation plan §B (S1–S5) at
`tasks/2026-05-31_explore_review-scribble-contract-explore-task/plans_and_protocols/2026-05-31_03_remediation_plan.md`.

Process requirement — NO `target_package` on any task.

NOTE: NO new verification task created. TASK-PROC-032-20 (verify) already exists for
AC-21..36 and the orchestrator will WIDEN it to AC-37..41 (per §C2 of the remediation
plan). Creating a duplicate verify task here is explicitly forbidden by the orchestration brief.

`after:` lists are deliberately minimal (intra-S only; none are real). The orchestrator
wires the external dependencies it owns:
- `after: claude-modify-agent` (the new capability-authoring skill task, N1) — S1, S2, S3, S5 edit `ui-scribble-*` agents
- `after: lib-features-policy` (P0) — S1 only (parity vs lib/features/ tree)
- TASK-PROC-032-20 verify widening to AC-37..41

## Tasks

- task_name: "scribble-storage-mirror-lib-features"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-37]
  effort: M
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  target_package: null
  sizing: {S1: ~7 files, S2: closed, S3: true (agents+script+docs), S4: false}
  implementation_notes: >-
    git mv the existing scribble to requirements_tasks/scribbles/<feature_path> (path mirrors
    lib/features/ 1:1 by name/hierarchy; lib/core/ -> _core/). Update path-discovery in
    ui-scribble-generator + ui-scribble-iterate, ui-verify-flutter, and the code-simple /
    code-complex Sketch Gate to locate the scribble via the feature_path mirror instead of the
    hard-coded [category]/[requirement]/scribbles/ path. Add a parity lint (via claude-write-script)
    that flags divergence in either direction (scribble feature_path with no matching lib/features/
    node; expected feature with no covering scribble). Add a folder-structure section to
    requirements_tasks/SKETCHES_README.md. Run the parity lint and fix any divergence (enforcement
    creates remediation — fold the cleanup into this task). Edits ui-scribble-* AGENTS -> orchestrator
    adds after:claude-modify-agent. Parity is checked against the lib/features/ structure policy ->
    orchestrator adds after:lib-features-policy (P0). Keep each edited skill/agent contract.yaml in sync.

- task_name: "scribble-flow-navigation-yaml"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-38]
  effort: M
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  target_package: null
  sizing: {S1: ~4 files, S2: closed, S3: true (emitter+schema+consumers), S4: false}
  implementation_notes: >-
    ui-scribble-handoff-emitter emits and keeps current a flow_navigation.yaml in each
    participating flow's folder, describing screen-to-screen edges, each edge's trigger, escape
    paths, and the back-stack policy. Add a schema for flow_navigation.yaml under .claude/schemas/.
    flutter_handoff.yaml points to the relevant flow_navigation.yaml file(s); update
    .claude/schemas/flutter_handoff.yaml accordingly. ui-verify-flutter and the coding consumer
    read flow_navigation.yaml to verify and implement navigation. Edits ui-scribble-* AGENT ->
    orchestrator adds after:claude-modify-agent. Keep contract.yaml in sync.

- task_name: "scribble-per-flow-walk-validation"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-39]
  effort: M
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  target_package: null
  sizing: {S1: ~3 files, S2: closed, S3: true (walk logic + brief + revision routing), S4: false}
  implementation_notes: >-
    Before a scribble version is approved, ui-scribble-auto-review walks the scribble's screens in
    each participating flow's step order and verifies each step's intent is supported by a screen
    and its elements. A step unsupported because the flow itself is flawed is routed UPSTREAM via
    the revision channel (not patched in the scribble). The auto-review brief carries, per
    participating flow, one-line human walk instructions (which file to open, which screens in
    which order). STANDALONE task (developer decision O3 — does not fold into 032-12). Edits
    ui-scribble-auto-review AGENT -> orchestrator adds after:claude-modify-agent. Keep contract.yaml in sync.

- task_name: "scribble-approval-trail"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-40]
  effort: S
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  target_package: null
  sizing: {S1: ~2 files, S2: closed, S3: true (synthesizes feedback+briefs+diffs), S4: false}
  implementation_notes: >-
    On approval, ui-scribble-approve-handoff emits an APPROVAL_TRAIL.md for the scribble that
    aggregates the decision history across all versions — rejected alternatives, key trade-offs,
    and the rationale behind locked decisions — synthesized from the per-version feedback.md, the
    auto-review briefs, and the inter-version diffs. STANDALONE task (developer decision O3). Edits
    ui-scribble-approve-handoff (skill or agent) -> if it edits the agent, orchestrator adds
    after:claude-modify-agent. Keep contract.yaml in sync.

- task_name: "scribble-contributing-requirements-discovery"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md"
  requirements_version: "6ece1dc7"
  covers_acs: [AC-41]
  effort: M
  layer: process
  after: []
  task_type: impl
  opus_recommended: false
  target_package: null
  sizing: {S1: ~4 files, S2: closed, S3: true (script + generator wiring + lint), S4: false}
  implementation_notes: >-
    A discovery script (via claude-write-script) auto-discovers a scribble's
    contributing_requirements (primary owning requirement + cross-cutting) and participating_flows
    from its feature_path, the requirements matrix, and a UI-scope heuristic, and writes them into
    the EXISTING scribble_metadata.yaml fields. NO new frontmatter fields — these fields already
    exist in .claude/schemas/scribble_metadata.yaml. Where discovery is ambiguous, flag for human
    review rather than silently leaving the field empty. Add a consistency lint requiring the
    primary contributing requirement to correspond to the scribble's feature_path. Wire the script
    into ui-scribble-generator. Run the lint and fix violations. Edits ui-scribble-generator AGENT
    -> orchestrator adds after:claude-modify-agent. Keep contract.yaml in sync.

## Coverage Matrix (AC-37..AC-41 only)

| AC | Task(s) | Package |
|----|---------|---------|
| AC-37 | scribble-storage-mirror-lib-features | — (process) |
| AC-38 | scribble-flow-navigation-yaml | — (process) |
| AC-39 | scribble-per-flow-walk-validation | — (process) |
| AC-40 | scribble-approval-trail | — (process) |
| AC-41 | scribble-contributing-requirements-discovery | — (process) |

100% coverage of the in-scope ACs. AC-01..AC-36 are out of scope (already covered).

## Verification

NO new verification task. TASK-PROC-032-20 (verify, currently AC-21..36) is widened to
AC-37..41 by the orchestrator (remediation plan §C2). This satisfies the ">=3 impl tasks =>
mandatory separate verification task" rule because a separate verify task already exists and
will cover these ACs.

## Cross-Reference Gate (Phase 1.5)

Ran scripts/requirements/check_cross_refs.py with terms: scribble, flow_navigation, feature_path.
Candidates: REQ-PROC-035, -036, -042, -043 (all match only the generic word "scribble" in
incidental contexts — release prep, task ordering, scripts org) and REQ-PROC-044-01 (the new
capability-authoring-skills feature whose dependency the ORCHESTRATOR already owns via
after:claude-modify-agent). All classified `ignore` (false positives / orchestrator-owned).
Genuinely related requirements (REQ-PROC-044, REQ-PROC-026) are already in the requirement's
## Related Requirements. Gate passes via waiver — no requirement edits made.
