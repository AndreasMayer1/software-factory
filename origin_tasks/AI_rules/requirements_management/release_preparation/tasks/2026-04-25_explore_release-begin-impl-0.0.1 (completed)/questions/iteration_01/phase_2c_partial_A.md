## Partial Plan A — Features: feat_therapist_transfer_ui, feat_adaptive_transfer_settings, feat_plan_serialization

---

## Architecture Notes

### Cross-Cutting Concerns

**Encryption boundary**: Several ACs in all three features are marked `target_package: "Transfer Encryption"` — these belong to 0.0.2, not 0.0.1. This partial plan deliberately excludes AC-03, AC-04, AC-07 (feat_therapist_transfer_ui), and AC-08–13 (feat_plan_serialization). Tasks would be created in 0.0.2 scope.

**Time-based detection model** (REQ-FUNC-007-01 Section 10): The *specification* was authored in TASK-FUNC-007-01-04 (completed). The *implementation* of AC-14–20 is the 0.0.1 gap. This is the largest remaining block for the "QR Transfer Receive" package.

**Bidirectional serialization pipeline** (REQ-FUNC-007-03 AC-06–07): These ACs bridge the serialization pipeline (REQ-FUNC-007-03) and adaptive settings (REQ-FUNC-007-04). They must be implemented to complete the spike and are correctly assigned to the "Adaptive Scanner Settings" target_package.

**Windows screen capture path** (REQ-FUNC-007-04 AC-15–17): These ACs depend on the `screen_capturer_qr` plugin that was implemented in TASK-FUNC-007-04-07/08 (spike-cleanup). The gaps are about the production-quality overlay UI (AC-16 compact bar, AC-26 content states, AC-27 dismissal) and the remote-mode activation paths (AC-25). Some AC numbers from the "Adaptive Scanner Settings" package scope (AC-22–27, AC-28–36) are EITHER out of 0.0.1 scope OR assigned to later packages ("Transfer Adaptive UI" in 0.2.1, "Remote QR Sessions" in 0.2.1). See Phase 2 reopener note below.

**DataBeam Reverse Validation**: Spike result is PASSED (2026-03-15). ACs 18–21 are validated. A verify task is needed to close formal coverage — no new implementation required.

**Data Bundle Versioning** (REQ-FUNC-007-03 AC-14–17): These ACs are explicitly scoped to 0.1.0+ by the requirements text ("0.0.1: client→therapist transfer not yet built"). No tasks are created for them here. Coverage gap is intentional.

### Phase 2 Reopener

- **AC-15–17 vs. package boundary**: AC-15 (Windows screen capture mode activation) and AC-16 (compact floating overlay bar) are in `target_package: "Adaptive Scanner Settings"` (0.0.1). However, AC-25 (remote mode activation paths) and AC-26–27 (overlay content states and dismissal) — which are the *completion* of AC-15–16 — are not listed in RELEASE_BACKLOG.md's "Adaptive Scanner Settings" scope description (which says "AC-06–17"). The scope description mentions "Windows screen capture for remote sessions" but the boundary between "Adaptive Scanner Settings" (0.0.1) and "Remote QR Sessions" (0.2.1) for AC-25–27 is ambiguous. Tasks below cover AC-15–17 strictly per the 0.0.1 scope boundary and note AC-25–27 as a reopener for the aggregation agent.

- **AC-28–36 (Transfer Speed Preference / Photosensitivity Safety)**: These ACs were added 2026-04-05, assigned to "Adaptive Scanner Settings" target_package, but are not present in RELEASE_BACKLOG.md's scope description for that package. The "Transfer Adaptive UI" package (0.2.1) covers "fast-transfer consent" in FLOW-003 context. Whether AC-28–36 belong in 0.0.1 or 0.2.1 is ambiguous. Conservative decision: excluded from 0.0.1 task plan. Flagged for human confirmation.

---

## Package: QR Transfer Receive

### Task QTR-1

```yaml
task_name: "Impl Time-Based Detection Domain Model"
task_type: impl
target_package: "QR Transfer Receive"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui"
req_id: "REQ-FUNC-007-01"
covers_acs: [AC-14, AC-15, AC-16]
covers_sections: [SEC-10]
effort: M
layer: domain
after: []
opus_recommended: false
implementation_notes: >
  Implement the TransferDetectionModel domain entity/service (pure Dart, no UI imports).
  Must model: (1) minimum_duration = ceil(chunk_count / frame_rate); (2) the five detection zones
  (c=under-duration, d=over-duration, e=grey-zone) from Section 10.3–10.4;
  (3) the two control buttons (Discard always active; Complete active after min_duration elapses);
  (4) recalculation of minimum_duration when animation speed changes. Write unit tests for all
  zone boundary conditions and the recalculation behavior.
```

**Rationale**: AC-14–16 define discrete behaviors that have domain logic (the minimum_duration formula and zone boundaries). Implementing this as a testable domain service first allows the presentation layer (QTR-2) to be pure UI wiring with no business logic inline.

---

### Task QTR-2

```yaml
task_name: "Impl QR Transfer Screen Detection UX"
task_type: impl
target_package: "QR Transfer Receive"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui"
req_id: "REQ-FUNC-007-01"
covers_acs: [AC-17, AC-18, AC-19, AC-20]
covers_sections: []
effort: M
layer: presentation
after: ["Impl Time-Based Detection Domain Model"]
opus_recommended: false
implementation_notes: >
  Wire the detection model from QTR-1 into the QR Transfer Screen BLoC and UI.
  Implement: (1) non-shaming notice for under-duration exit (zone c) — non-blocking, neutral
  copy per Section 10.5; (2) success animation for over-duration / grey-zone exits (zones d/e)
  — WCAG 2.3.1 compliant (≤3Hz, no strobing); (3) OS Reduce Motion check at transfer start —
  replace animation with static "Transfer complete" indicator; (4) grey-zone notice persistence
  (zone e) — stored across sessions, shown at top of next relevant detail screen;
  (5) optimistic marking behavior for zones d and e. No animation for zone c or Discard button.
  Tests must cover: Reduce Motion active/inactive, grey-zone notice persistence, Discard at
  each zone.
```

**Rationale**: AC-17–20 are the UX output side of the detection model. They are separated from QTR-1 to keep domain logic testable in isolation. AC-20 specifically requires platform accessibility API integration (OS Reduce Motion), which belongs in the presentation layer.

---

## Package: Adaptive Scanner Settings

### Task ASS-1

```yaml
task_name: "Impl Windows Screen Capture Session Path"
task_type: impl
target_package: "Adaptive Scanner Settings"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_adaptive_transfer_settings"
req_id: "REQ-FUNC-007-04"
covers_acs: [AC-15, AC-16]
covers_sections: []
effort: L
layer: presentation
after: []
opus_recommended: false
implementation_notes: >
  Implement the production-quality Windows remote screen-capture session path.
  AC-15: Remote session mode on Windows uses screen_capturer_qr (WinRT, already implemented
  in spike) — wire it into the main transfer flow with session-type toggle. The toggle itself
  may already exist (TASK-FUNC-007-04-04/05 covered AC-11–14); this task connects it to the
  Windows-specific screen capture path.
  AC-16: Replace the current spike overlay (multi-line, top-right) with the production compact
  floating overlay bar: single content line, bottom-of-screen anchored above taskbar, 50% screen
  width centered, DPI-aware (96/125/150 DPI tested), draggable. Win32 always-on-top. The spike
  overlay implementation exists; this task is about production-polishing its geometry and
  layout.
  Note: AC-25 (remote mode activation from Transfer Detail Screen + QR Receive Screen), AC-26
  (overlay content states), and AC-27 (overlay dismissal) are not in the RELEASE_BACKLOG scope
  description for "Adaptive Scanner Settings" (which says AC-06–17). If the aggregation agent
  confirms AC-25–27 are 0.0.1, they should be merged into this task or a sibling task.
```

**Rationale**: The spike validated the WinRT approach but left a multi-line debug overlay. AC-15–16 require production-ready UI. This is Windows-platform-specific work touching both the native plugin integration and the overlay widget, so it is L effort.

---

### Task ASS-2

```yaml
task_name: "Verify DataBeam Reverse Validation Spike"
task_type: verify
target_package: "DataBeam Reverse Validation"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_adaptive_transfer_settings"
req_id: "REQ-FUNC-007-04"
covers_acs: [AC-18, AC-19, AC-20, AC-21]
covers_sections: []
effort: XS
layer: cross-layer
after: []
opus_recommended: false
implementation_notes: >
  The spike PASSED on 2026-03-15 (development laptop, 720p webcam, vid_30c9&pid_00ac).
  AC-18 (client as sender), AC-19 (therapist as scanner), AC-20 (Scenario A ~70KB < 4min),
  AC-21 (pass/fail gate) are all satisfied per the spike outcome documented in
  feat_adaptive_transfer_settings/requirements.md Section 6 and
  plans_and_protocols/2026-03-20_35_results_and_next_requirements.md.
  This task verifies that the formal coverage record is correct and that the spike artifacts
  (AdaptiveScanController, AIMD algorithm, Android continuous Y-plane stream, Windows C++ decode
  path) are present and clean in the codebase. No new implementation. Run existing spike-related
  tests; confirm no regressions from TASK-FUNC-007-04-08 spike-cleanup.
```

**Rationale**: The spike is complete. Formal verification closes the gap in the coverage report. The "verify" task type is specified in the brief for this exact situation. No risk of rework — only confirmation.

---

## Package: Transfer Data Model (partial — feat_plan_serialization)

### Task TDM-1

```yaml
task_name: "Impl Bidirectional Pipeline + Configurable Chunk Size"
task_type: impl
target_package: "Transfer Data Model"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_plan_serialization"
req_id: "REQ-FUNC-007-03"
covers_acs: [AC-06, AC-07]
covers_sections: []
effort: S
layer: data
after: []
opus_recommended: false
implementation_notes: >
  AC-06: Validate that the existing serialization pipeline (TASK-FUNC-007-03-01) can be used
  bidirectionally — the same serialize()/deserialize() functions work for both therapist→client
  and client→therapist directions. The spike (REQ-FUNC-007-04 AC-18–21, PASSED) already
  exercised this path; this task adds explicit tests for the bidirectional contract and documents
  the coverage in the requirement.
  AC-07: Ensure chunk size and EC level are caller-supplied parameters (TransferSettings), not
  hardcoded constants. This may already be implemented as part of TASK-FUNC-007-04-01
  (domain-model-scanner-tiers) which defined TransferSettings; if so, this task confirms the
  pipeline correctly reads from TransferSettings and adds regression tests for each tier's
  parameter values. If not yet wired, wire the pipeline to accept TransferSettings as an input
  argument.
  Note: AC-08–13 (encrypted header block) are 0.0.2 scope — excluded from this task.
  AC-14–17 (data bundle versioning) are 0.1.0 scope — excluded from this task.
```

**Rationale**: AC-06 and AC-07 are assigned `target_package: "Adaptive Scanner Settings"` in the requirements frontmatter but live in the serialization pipeline feature. They are the only 0.0.1-relevant gaps in feat_plan_serialization after excluding encryption (0.0.2) and bundle versioning (0.1.0). Effort is S because most of the groundwork exists — this is primarily wiring and test-writing.

---

## Task Dependency Graph (this partial plan)

```
ASS-2 (verify, no deps)     TDM-1 (no deps)
QTR-1 (no deps)
    └─► QTR-2
ASS-1 (no deps, but overlaps with QTR-2's OS Reduce Motion check — coordinate)
```

No circular dependencies. ASS-2 and TDM-1 are independent leaf tasks. QTR-1 must precede QTR-2. ASS-1 is independent but should coordinate with QTR-2 on the OS Reduce Motion implementation path (both read the same platform accessibility flag; shared utility function preferred).

---

## Coverage Summary (this partial plan)

| Req | ACs covered by new tasks | ACs excluded (reason) | Remaining gap |
|---|---|---|---|
| REQ-FUNC-007-01 | AC-14–20, SEC-10 | AC-03,04,07 (0.0.2 Encryption), AC-06 (0.1.0 Plan Transfer Full), SEC-01,02,03,05,06 (0.1.0+) | None for 0.0.1 QR Transfer Receive package |
| REQ-FUNC-007-04 AC-15–17 | AC-15, AC-16 | AC-17 (target_package: "Transfer Encryption" — stall detection, 0.0.2) | AC-25–27 status needs human confirmation (Phase 2 reopener above) |
| REQ-FUNC-007-04 AC-18–21 | AC-18–21 (verify) | — | None |
| REQ-FUNC-007-03 | AC-06, AC-07 | AC-08–13 (0.0.2 Encryption), AC-14–17 (0.1.0 bundle versioning) | None for 0.0.1 |

**Note on AC-17 (feat_adaptive_transfer_settings)**: The requirements file assigns AC-17 to `target_package: "Transfer Encryption"` and Section 5 explicitly marks it "Target: 0.0.2". It is correctly excluded from the 0.0.1 task plan.
