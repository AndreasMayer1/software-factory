---
plan_id: "PLAN-0.0.1-001"
release: "0.0.1"
created: "2026-04-26"
status: draft
explore_task: "TASK-PROC-035-09"
total_tasks: 12
---

# Task Creation Plan — Release 0.0.1

## Layer Dependency Rules

- Domain tasks must complete before Data tasks that depend on them
- Data tasks must complete before Presentation tasks that depend on them
- Verify tasks can run after their target impl task completes
- Cross-layer tasks carry their own internal sequencing

## Execution Order

Ordered by package, respecting layer dependencies within each package:

1. Transfer Data Model (domain → data → cross-layer)
2. Transfer Pairing (domain → data)
3. QR Transfer Receive (domain → presentation)
4. Adaptive Scanner Settings (presentation, cross-layer)
5. DataBeam Reverse Validation (verify)
6. QR Transfer Send (presentation — existing pending tasks, no new tasks)

## Architecture Notes

**Serialization use case boundary**: TDM-1 (AC-06/AC-07 of feat_plan_serialization) implements the low-level bidirectional pipeline and configurable chunk-size wiring. It does NOT implement `SerializePlanForExportUseCase`. That use case takes a `QuestionnairePlan` as input and produces versioned JSON — a different abstraction layer (domain/application). Therefore Task 5 (B-03, Plan Export QR Screen) remains cross-layer effort M and implements the use case itself, delegating to the pipeline from TDM-1.

**Shared OS Reduce Motion utility**: Task 2 (QTR-1 / Time-Based Detection Domain Model) and Task 7 (ASS-1 / Windows Screen Capture Session Path) both need to query the OS Reduce Motion accessibility flag. Implement as a shared platform-channel utility (e.g., `AccessibilityPreferencesService`) in the presentation layer or shared infrastructure. Coordinate in the after-chain: ASS-1 should reuse the utility created for QTR-2.

**AC-25–27 scope decision**: User confirmed AC-25 (remote mode activation from Transfer Detail and QR Receive Screens), AC-26 (overlay content states), and AC-27 (overlay dismissal) are in 0.0.1 scope. These are split into a sibling task (Task 8) to keep ASS-1 (AC-15/16 production geometry) focused and independently testable.

**AC-28–36 scope decision**: User confirmed AC-28–36 (transfer speed preference / photosensitivity safety) are in 0.0.1 scope. These are consolidated into Task 9 (single UI-heavy task covering fast-transfer consent and photosensitivity warning screens).

**Data versioning dependency**: Task 5 (Plan Export QR Screen) and Task 6 (Data Version Migration Infrastructure) both touch the serialized `QuestionnairePlan` output format. Task 6 must ensure `currentDataVersion` is embedded before Task 5 finalizes its output contract; however, since Task 5 notes the security/versioning contract must accommodate later additions, they can proceed in parallel — Task 7 (Data Version Rejection UX) must follow Task 6.

**Client data model blocks transfer pipeline**: Task 3 (B-01 / Client Data Domain Model) provides the real `TransferBundle` payload. The existing TASK-FUNC-007-12-01 uses a `Uint8List` placeholder; Task 3 must complete before the fountain code pipeline switches to real data.

**Existing task TASK-FUNC-007-07** (feat_pairing_management, completed): The `PairingIdentity` UUID is the partition key for per-client repositories. Task 3 (B-01) depends on this being complete — confirmed already done.

## Planned Tasks

### PKG: Transfer Data Model

#### Task 1: Impl Bidirectional Pipeline + Configurable Chunk Size

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
  AC-06: Validate bidirectionality of the existing serialization pipeline (TASK-FUNC-007-03-01):
  confirm that the same serialize()/deserialize() functions work for both therapist→client and
  client→therapist directions. The DataBeam reverse spike (REQ-FUNC-007-04 AC-18–21, PASSED) already
  exercised this path; add explicit contract tests for the bidirectional invariant and record
  coverage in the requirement.
  AC-07: Ensure chunk size and EC level are caller-supplied parameters (TransferSettings), not
  hardcoded constants. If TASK-FUNC-007-04-01 (domain-model-scanner-tiers) already defined
  TransferSettings, confirm the pipeline correctly reads from it and add regression tests for each
  tier's parameter values. If the wiring is missing, wire the pipeline to accept TransferSettings
  as an input argument.
  Note: AC-08–13 (encrypted header block) are 0.0.2 scope — excluded. AC-14–17 (data bundle
  versioning) are 0.1.0 scope — excluded.
```

**Rationale**: AC-06 and AC-07 are the only 0.0.1-relevant gaps in feat_plan_serialization after excluding encryption (0.0.2) and bundle versioning (0.1.0). Effort is S because the groundwork exists — primarily wiring and regression test writing.

---

#### Task 2: Impl Therapist Storage Guard

```yaml
task_name: "Impl Therapist Storage Guard"
task_type: impl
target_package: "Transfer Data Model"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_storage_management"
req_id: "REQ-FUNC-007-08"
covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05]
covers_sections: []
effort: S
layer: cross-layer
after:
  - TASK-FUNC-007-12-03
opus_recommended: false
implementation_notes: >
  Domain: StoragePolicy value object (available bytes vs. required bytes → policy decision enum:
  ok / warn / in-memory / block).
  Data: StorageProbeService (platform storage query; returns available persistent bytes and free
  RAM estimate). Device range lower bound: 2 GB RAM (2017 Android) — only offer in-memory fallback
  when free RAM > data size + safety margin.
  Presentation: pre-transfer storage check hook on TherapistQrReceiveBloc and file import path;
  InMemoryIndicatorBanner widget (non-dismissible, always-visible per AC-03, persists across
  navigation); same-session commit trigger when storage freed (AC-04 — poll or platform storage
  change stream). Hard-block path (AC-05) must prevent any partial write — atomic bundle persist
  or nothing.
  Integration point: TherapistQrReceiveScreen (TASK-FUNC-007-12-03) must exist before the
  pre-transfer check can be wired in — hence the after dependency.
```

**Rationale**: All five ACs are uncovered. The therapist receive path (TASK-FUNC-007-12-03) is the integration point for the pre-transfer check and must exist first. The always-visible in-memory indicator (AC-03) must be non-dismissible and persist across navigation.

---

#### Task 3: Impl Data Version Migration Infrastructure

```yaml
task_name: "Impl Data Version Migration Infrastructure"
task_type: impl
target_package: "Transfer Data Model"
req_path: "requirements_tasks/non-functional/architecture/data_versioning"
req_id: "REQ-NFUNC-001"
covers_acs: [AC-01, AC-02, AC-03, AC-04]
covers_sections: []
effort: S
layer: data
after: []
opus_recommended: false
implementation_notes: >
  Embed currentDataVersion in serialized QuestionnairePlan export (AC-01).
  Implement import-time version check: exact-match path (AC-02), older-version migration chain
  (AC-03 / AC-04).
  Migration function infrastructure in the data/infrastructure layer of the plan_templates feature
  (lib/features/therapist/plan_templates/data/ or equivalent).
  Files: version_constants.dart for the currentDataVersion constant; MigrationService for step
  functions. Follow doc/architecture/ for layer placement.
```

**Rationale**: No tasks exist for REQ-NFUNC-001. Tasks 3 and 4 are split by layer boundary — Task 3 covers data-layer migration infrastructure (AC-01–04), independently testable; Task 4 covers the presentation-layer rejection UX (AC-05) and depends on Task 3.

---

#### Task 4: Impl Data Version Rejection UX

```yaml
task_name: "Impl Data Version Rejection UX"
task_type: impl
target_package: "Transfer Data Model"
req_path: "requirements_tasks/non-functional/architecture/data_versioning"
req_id: "REQ-NFUNC-001"
covers_acs: [AC-05]
covers_sections: []
effort: S
layer: presentation
after:
  - "Impl Data Version Migration Infrastructure"
opus_recommended: false
implementation_notes: >
  When importedVersion > currentDataVersion, surface a user-friendly error:
  "This plan was created with a newer version of the app. Please update your app to import it."
  Wire into the import result handling in the plan receiving presentation layer (feat_plan_receiving
  — already completed). Use the domain Failure system (doc/domain/failures.md):
  UnsupportedVersionFailure → error dialog or inline error state.
  Do not use debugPrint() for this path; log at warning level via ILogger.
```

**Rationale**: AC-05 is the UX surface for the version rejection logic implemented in Task 3. Separating it keeps each task single-responsibility and enables the after-chain.

---

#### Task 5: Impl Plan Export QR Screen

```yaml
task_name: "Impl Plan Export QR Screen"
task_type: impl
target_package: "Transfer Data Model"
req_path: "requirements_tasks/functional/therapist/epic_plan_management/feat_plan_export"
req_id: "REQ-FUNC-014-06"
covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05]
covers_sections: []
effort: M
layer: cross-layer
after:
  - "Impl Bidirectional Pipeline + Configurable Chunk Size"
opus_recommended: false
implementation_notes: >
  Domain/Data: SerializePlanForExportUseCase — input QuestionnairePlan, output versioned JSON string.
  This is a distinct use-case abstraction from the low-level bidirectional pipeline (Task 1 / TDM-1).
  Delegate to the pipeline from Task 1 for chunk serialization; the use case adds the QuestionnairePlan
  → JSON mapping layer and versioning envelope.
  Presentation: Export/Share action button in PlanTemplateDetailContent AppBar (AC-01);
  ExportPlanScreen or modal dialog showing the generated QR code + therapist instruction text (AC-03).
  QR code rendered via qr_flutter v4.x from the serialized string (AC-02 / AC-04).
  Security (encryption) is deferred to 0.0.2 per RELEASE_BACKLOG.md — serialization contract must
  accommodate an encryption wrapper without breaking existing consumers.
  AC-05 (client can scan) verified via integration test against feat_plan_receiving (already covered).
```

**Rationale**: No tasks exist for this feature. The `SerializePlanForExportUseCase` is a higher-level use-case abstraction than the pipeline work in Task 1 — Task 1 does not implement it, so this task remains cross-layer effort M. Security is explicitly deferred to 0.0.2.

---

### PKG: Transfer Pairing

#### Task 6: Impl Client Data Domain Model

```yaml
task_name: "Impl Client Data Domain Model"
task_type: impl
target_package: "Transfer Pairing"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_client_data_model"
req_id: "REQ-FUNC-007-05"
covers_acs: [AC-01, AC-02, AC-03, AC-04, AC-05]
covers_sections: []
effort: M
layer: domain
after:
  - TASK-FUNC-007-07
opus_recommended: true
implementation_notes: >
  Implement TrackingEntry entity with immutable ownershipContext field (AC-01).
  Plan-level privacy flag enforced at domain bundle assembly — flag state is immutable once set
  (AC-02).
  Per-client partition repository interface with mandatory clientIdentity param; clientIdentity
  is the PairingIdentity UUID established by TASK-FUNC-007-07 (AC-03).
  isShared + isExcluded two-marker system with copyWith independence — changing one marker must
  never implicitly affect the other (AC-04).
  TransferBundle value object (non-persisted computation output, supports QR + file channels)
  (AC-05). The existing TASK-FUNC-007-12-01 uses a Uint8List placeholder with a documented swap
  point; this task provides the real bundle payload.
  Follow doc/domain/entities.md, doc/domain/repositories.md, doc/domain/value_objects.md.
```

**Rationale**: The completed explore task (TASK-FUNC-007-05-01) produced the requirements specification but no Dart code. Opus is recommended because the ownership immutability invariant and two-marker independence are high-stakes domain constraints with clinical consequences — wrong marker state can cause re-transferred or lost client data.

---

### PKG: QR Transfer Receive

#### Task 7: Impl Time-Based Detection Domain Model

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
  (c = under-duration, d = over-duration, e = grey-zone) from Section 10.3–10.4; (3) the two
  control buttons — Discard always active, Complete active only after minimum_duration elapses;
  (4) recalculation of minimum_duration when animation speed changes mid-transfer.
  Write unit tests for all zone boundary conditions and the recalculation behavior.
```

**Rationale**: AC-14–16 define discrete behaviors with domain logic (the minimum_duration formula and zone boundaries). Implementing this as a testable domain service first allows the presentation layer (Task 8) to be pure UI wiring with no business logic inline.

---

#### Task 8: Impl QR Transfer Screen Detection UX

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
after:
  - "Impl Time-Based Detection Domain Model"
opus_recommended: false
implementation_notes: >
  Wire the detection model from Task 7 into the QR Transfer Screen BLoC and UI.
  AC-17: non-shaming notice for under-duration exit (zone c) — non-blocking, neutral copy per
  Section 10.5; no animation for zone c or Discard.
  AC-18: success animation for over-duration / grey-zone exits (zones d/e) — WCAG 2.3.1 compliant
  (≤3Hz, no strobing).
  AC-19: OS Reduce Motion check at transfer start — replace animation with static "Transfer
  complete" indicator when active. Implement as a shared AccessibilityPreferencesService in
  presentation infrastructure so the same utility can be reused by Task 9 (ASS-1).
  AC-20: grey-zone notice persistence (zone e) — stored across sessions, shown at top of next
  relevant detail screen; optimistic marking behavior for zones d and e.
  Tests must cover: Reduce Motion active/inactive, grey-zone notice persistence, Discard at each
  zone.
```

**Rationale**: AC-17–20 are the UX output side of the detection model, separated from Task 7 to keep domain logic testable in isolation. AC-19 specifically requires platform accessibility API integration, which belongs in the presentation layer. The shared AccessibilityPreferencesService also unblocks Task 9 (ASS-1).

---

### PKG: Adaptive Scanner Settings

#### Task 9: Impl Windows Screen Capture Session Path

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
after:
  - "Impl QR Transfer Screen Detection UX"
opus_recommended: false
implementation_notes: >
  Implement the production-quality Windows remote screen-capture session path.
  AC-15: Remote session mode on Windows uses screen_capturer_qr (WinRT plugin, already implemented
  in spike via TASK-FUNC-007-04-07/08) — wire it into the main transfer flow with the session-type
  toggle. The toggle may already exist from TASK-FUNC-007-04-04/05 (AC-11–14); this task connects
  it to the Windows-specific screen capture path.
  AC-16: Replace the current spike overlay (multi-line, top-right debug layout) with the production
  compact floating overlay bar: single content line, bottom-of-screen anchored above taskbar, 50%
  screen width centered, DPI-aware (tested at 96/125/150 DPI), draggable, Win32 always-on-top.
  The spike overlay implementation exists; this task is about production-polishing its geometry and
  layout.
  Reuse the AccessibilityPreferencesService from Task 8 (QTR-2) for the OS Reduce Motion check
  within the overlay animation path.
  Note: AC-17 (stall detection) is assigned to target_package "Transfer Encryption" and is 0.0.2
  scope — excluded.
```

**Rationale**: The spike validated the WinRT approach but left a multi-line debug overlay. AC-15–16 require production-ready UI. This is Windows-platform-specific work touching both native plugin integration and the overlay widget, hence L effort. After dependency on Task 8 ensures the shared OS accessibility utility is available.

---

#### Task 10: Impl Remote Overlay Activation and Content States

```yaml
task_name: "Impl Remote Overlay Activation and Content States"
task_type: impl
target_package: "Adaptive Scanner Settings"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_adaptive_transfer_settings"
req_id: "REQ-FUNC-007-04"
covers_acs: [AC-25, AC-26, AC-27]
covers_sections: []
effort: M
layer: presentation
after:
  - "Impl Windows Screen Capture Session Path"
  - TASK-FUNC-007-12-03
opus_recommended: false
implementation_notes: >
  AC-25: Implement remote mode activation paths from both the Transfer Detail Screen and the QR
  Receive Screen. The session-type toggle from Task 9 (AC-15) exists; this task adds the two
  additional entry points so the user can switch to remote mode from either screen without
  navigating away.
  AC-26: Implement overlay content states for the compact floating overlay bar (built in Task 9):
  idle state, active-transfer state, error/stall state, and completion state. Each state has
  distinct copy and iconography. Transitions between states must be smooth and WCAG-compliant.
  AC-27: Implement overlay dismissal behavior — user can drag the overlay off-screen or tap a
  close control; dismissal is non-destructive (transfer continues in background); overlay can be
  re-summoned from the system tray or a floating re-open button.
  Depends on Task 9 (overlay bar widget must exist) and TASK-FUNC-007-12-03 (TherapistQrReceiveScreen
  must exist to add the remote mode activation entry point).
```

**Rationale**: AC-25–27 complete the overlay feature started in Task 9 (AC-15–16). They were confirmed as 0.0.1 scope by the user (reopener decision). Separated into a sibling task to keep Task 9's scope focused on geometry/production-polish. M effort because the overlay widget itself already exists after Task 9.

---

#### Task 11: Impl Transfer Speed Preference and Photosensitivity Safety

```yaml
task_name: "Impl Transfer Speed Preference and Photosensitivity Safety"
task_type: impl
target_package: "Adaptive Scanner Settings"
req_path: "requirements_tasks/functional/shared/epic_data_transfer/feat_adaptive_transfer_settings"
req_id: "REQ-FUNC-007-04"
covers_acs: [AC-28, AC-29, AC-30, AC-31, AC-32, AC-33, AC-34, AC-35, AC-36]
covers_sections: []
effort: L
layer: presentation
after:
  - TASK-FUNC-007-04-05
opus_recommended: false
implementation_notes: >
  Implement the fast-transfer consent UI and photosensitivity safety warning block (AC-28–36).
  AC-28–30 (transfer speed preference): user-selectable speed tier preference (conservative / balanced /
  fast) stored in TransferSettings; fast tier shows a consent notice before first use explaining
  higher flicker rate; consent is stored and not repeated after acknowledgement.
  AC-31–33 (photosensitivity safety warning): mandatory warning screen shown before any QR transfer
  session that will use animation speeds above the safe threshold; warning must be WCAG 2.3.1
  compliant (≤3Hz safe zone clearly communicated); user must actively confirm — cannot be dismissed
  by back navigation.
  AC-34–36 (photosensitivity opt-out path): user can permanently opt out of animated transfer and
  fall back to static-frame mode; opt-out stored in user preferences; opt-out must be accessible
  from both the warning screen and the settings screen.
  Depends on TASK-FUNC-007-04-05 (Impl Therapist-Tier-Override) which establishes the tier
  settings infrastructure this feature builds on.
  Note: if AC numbers in the requirements file differ from the above description, reconcile
  against requirements_tasks/functional/shared/epic_data_transfer/feat_adaptive_transfer_settings/
  requirements.md Section covering these ACs before implementation.
```

**Rationale**: AC-28–36 were confirmed as 0.0.1 scope by the user (reopener decision). Added after the original 0.0.1 scope was written (2026-04-05). Consolidated into a single L-effort task because all nine ACs form a coherent UI feature block (consent flow + safety warning + opt-out path). Depends on TASK-FUNC-007-04-05 for the tier settings infrastructure.

---

### PKG: DataBeam Reverse Validation

#### Task 12: Verify DataBeam Reverse Validation Spike

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
  AC-18 (client as sender), AC-19 (therapist as scanner), AC-20 (Scenario A ~70 KB < 4 min),
  AC-21 (pass/fail gate) are all satisfied per the spike outcome documented in
  feat_adaptive_transfer_settings/requirements.md Section 6 and
  plans_and_protocols/2026-03-20_35_results_and_next_requirements.md.
  This task verifies that the formal coverage record is correct and that the spike artifacts
  (AdaptiveScanController, AIMD algorithm, Android continuous Y-plane stream, Windows C++ decode
  path) are present and clean in the codebase after TASK-FUNC-007-04-08 spike-cleanup.
  No new implementation. Run existing spike-related tests; confirm no regressions.
```

**Rationale**: The spike is complete. Formal verification closes the gap in the coverage report. The "verify" task type is specified for exactly this situation. No risk of rework — only confirmation.

---

### PKG: QR Transfer Send

#### (No new tasks)

```
All ACs are already covered by existing pending tasks:
- TASK-FUNC-007-12-01: Foundation (pipeline sections) — pending
- TASK-FUNC-007-12-02: AC-01–05, AC-07 — pending
- TASK-FUNC-007-12-03: AC-10–14 — pending
- TASK-FUNC-007-12-04: AC-15–19 — pending
- AC-06, AC-08, AC-09 are tagged target_package "Adaptive Scanner Settings" — handled above

No new tasks are required for feat_qr_data_transfer.
```

---

## Task Summary Table

| # | Task Name | Package | Req | ACs | Effort | Layer | After |
|---|---|---|---|---|---|---|---|
| 1 | Impl Bidirectional Pipeline + Configurable Chunk Size | Transfer Data Model | REQ-FUNC-007-03 | AC-06, AC-07 | S | data | — |
| 2 | Impl Therapist Storage Guard | Transfer Data Model | REQ-FUNC-007-08 | AC-01–05 | S | cross-layer | TASK-FUNC-007-12-03 |
| 3 | Impl Data Version Migration Infrastructure | Transfer Data Model | REQ-NFUNC-001 | AC-01–04 | S | data | — |
| 4 | Impl Data Version Rejection UX | Transfer Data Model | REQ-NFUNC-001 | AC-05 | S | presentation | Task 3 |
| 5 | Impl Plan Export QR Screen | Transfer Data Model | REQ-FUNC-014-06 | AC-01–05 | M | cross-layer | Task 1 |
| 6 | Impl Client Data Domain Model | Transfer Pairing | REQ-FUNC-007-05 | AC-01–05 | M | domain | TASK-FUNC-007-07 |
| 7 | Impl Time-Based Detection Domain Model | QR Transfer Receive | REQ-FUNC-007-01 | AC-14–16, SEC-10 | M | domain | — |
| 8 | Impl QR Transfer Screen Detection UX | QR Transfer Receive | REQ-FUNC-007-01 | AC-17–20 | M | presentation | Task 7 |
| 9 | Impl Windows Screen Capture Session Path | Adaptive Scanner Settings | REQ-FUNC-007-04 | AC-15, AC-16 | L | presentation | Task 8 |
| 10 | Impl Remote Overlay Activation and Content States | Adaptive Scanner Settings | REQ-FUNC-007-04 | AC-25, AC-26, AC-27 | M | presentation | Task 9, TASK-FUNC-007-12-03 |
| 11 | Impl Transfer Speed Preference and Photosensitivity Safety | Adaptive Scanner Settings | REQ-FUNC-007-04 | AC-28–36 | L | presentation | TASK-FUNC-007-04-05 |
| 12 | Verify DataBeam Reverse Validation Spike | DataBeam Reverse Validation | REQ-FUNC-007-04 | AC-18–21 | XS | cross-layer | — |

**Total new tasks: 12**

---

## Coverage Gaps Intentionally Excluded

| Req | ACs excluded | Reason |
|---|---|---|
| REQ-FUNC-007-01 | AC-03, AC-04, AC-07 | 0.0.2 scope (Transfer Encryption) |
| REQ-FUNC-007-01 | AC-06, SEC-01/02/03/05/06 | 0.1.0+ scope (Plan Transfer Full) |
| REQ-FUNC-007-03 | AC-08–13 | 0.0.2 scope (Transfer Encryption — encrypted header block) |
| REQ-FUNC-007-03 | AC-14–17 | 0.1.0 scope (data bundle versioning) |
| REQ-FUNC-007-04 | AC-17 | 0.0.2 scope (Transfer Encryption — stall detection) |
| REQ-NFUNC-017 | all ACs | Already completed (3 tasks, 2026-03-08) |
| REQ-FUNC-007-12 | all ACs | Already covered by 4 existing pending tasks |
