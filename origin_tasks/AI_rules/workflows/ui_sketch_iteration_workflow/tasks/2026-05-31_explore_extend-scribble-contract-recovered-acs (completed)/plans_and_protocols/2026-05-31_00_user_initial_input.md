# Initial input (seed)

Source: TASK-PROC-032-16 quality review of TASK-PROC-032-10, remediation plan §A1 + §C1b.

The TASK-PROC-032-10 scribble-contract exploration adopted a set of decisions that were never encoded as acceptance criteria — an accidentally-lost strand. The remediation plan recovers them as five new ACs (AC-37..AC-41) plus an amendment to AC-23:

- D33–D36: scribbles should mirror `lib/features/` storage layout (and `lib/core/` → `_core/`), with a parity check.
- D20: each flow a scribble participates in should capture per-flow navigation (`flow_navigation.yaml`).
- D39: before approval, the scribble should be walked per-flow in step order to verify each step's intent is supported.
- D43: on approval, an `APPROVAL_TRAIL.md` should aggregate decision history across versions.
- D29/D30/D40: a script should auto-discover `contributing_requirements` and `participating_flows` from `feature_path` + `requirements_matrix.md` (the schema fields already exist; no new frontmatter).
- D8: `design_decisions` captured in `scribble_metadata.yaml` never reach `flutter_handoff.yaml`, so the coder never sees them — AC-23 should be amended to carry a `design_decisions:` block.

Read as a seed bed, not a spec.
