## Partial Plan B — Features: feat_qr_data_transfer, feat_client_data_model, feat_storage_management, feat_plan_export, REQ-NFUNC-001, REQ-NFUNC-017

---

## Architecture Notes

### feat_qr_data_transfer — existing task coverage is complete for 0.0.1 scope
Four tasks already exist and together cover all in-scope ACs:
- TASK-FUNC-007-12-01 (foundation, pending) — pipeline sections, no ACs
- TASK-FUNC-007-12-02 (pending) — AC-01–05, AC-07
- TASK-FUNC-007-12-03 (pending) — AC-10–14
- TASK-FUNC-007-12-04 (pending) — AC-15–19
- AC-06, AC-08, AC-09 are tagged `target_package: "Adaptive Scanner Settings"` — handled by Sub-Agent A

**No new tasks are needed for feat_qr_data_transfer.** The four pending tasks are the correct 0.0.1 scope.

### feat_client_data_model — domain-first, blocks transfer pipeline
One completed explore task (TASK-FUNC-007-05-01) produced the `requirements.md`. No impl tasks exist. All five ACs are domain-layer work (entity, value object, repository interface). Must precede fountain code tasks that consume the `Uint8List` bundle placeholder.

### feat_storage_management — therapist-side only, cross-layer
Small feature (effort S). Spans domain (storage policy) + data (storage probe service) + presentation (indicator widget). All five ACs are uncovered. The feature is a guard layer over FLOW-003 Step 6 and FLOW-004 Step 8 — both already have pending tasks, so this guard must ship in 0.0.1.

### feat_plan_export — bridges serialization to therapist UI
The export button and QR display belong to the therapist plan editor (`PlanTemplateDetailContent`). Depends on `SerializePlanForExportUseCase` which is either in `feat_plan_serialization` (Sub-Agent A scope) or a thin wrapper here. AC-05 depends on the client-side import (feat_plan_receiving — already 100% covered). Security (AC note) is deferred to 0.0.2.

### REQ-NFUNC-001 — data versioning for plan serialization
Targets the `QuestionnairePlan` serialization pipeline. AC-01/02 are export/import path integration; AC-03/04 are migration function infrastructure; AC-05 is the version-rejection UX. These are cross-layer (domain version constants + data migration logic + presentation error message). Should run after feat_plan_serialization foundation tasks (Sub-Agent A).

### REQ-NFUNC-017 — logging
All seven ACs are covered by three completed tasks (2026-03-08). **No new tasks required.**

---

## Package: "QR Transfer Send" — feat_qr_data_transfer

**All ACs are already covered by existing pending tasks. No new tasks to plan.**

Existing task summary for aggregation reference:

| Task ID | Covers | Status |
|---|---|---|
| TASK-FUNC-007-12-01 | Foundation (pipeline sections) | pending |
| TASK-FUNC-007-12-02 | AC-01–05, AC-07 | pending |
| TASK-FUNC-007-12-03 | AC-10–14 | pending |
| TASK-FUNC-007-12-04 | AC-15–19 | pending |
| (Sub-Agent A) | AC-06, AC-08, AC-09 | handled by Adaptive Scanner Settings package |

---

## Package: "Transfer Pairing" — feat_client_data_model

### Task B-01

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
  - TASK-FUNC-007-07  # feat_pairing_management completed — PairingIdentity UUID is the partition key (AC-03)
opus_recommended: true
implementation_notes: >
  Implement TrackingEntry entity with immutable ownershipContext field (AC-01),
  plan-level privacy flag enforced at domain bundle assembly (AC-02),
  per-client partition repository interface with mandatory clientIdentity param (AC-03),
  isShared + isExcluded two-marker system with copyWith independence (AC-04),
  TransferBundle value object (non-persisted computation output, supports QR+file channels) (AC-05).
  Follow doc/domain/entities.md, doc/domain/repositories.md, doc/domain/value_objects.md.
  TASK-FUNC-007-12-01 uses a Uint8List placeholder — this task provides the real bundle payload.
```

**Rationale**: The completed explore task (TASK-FUNC-007-05-01) produced the requirements specification but no Dart code. The transfer pipeline tasks (TASK-FUNC-007-12-01/02/03) already use a `Uint8List` placeholder with a documented swap point. This impl task fulfils all five ACs and unblocks the fountain code pipeline from using real client data. Opus recommended because the ownership immutability invariant and two-marker independence are high-stakes domain constraints with clinical consequences (wrong marker state = re-transferred or lost data).

---

## Package: "Transfer Data Model" — feat_storage_management

### Task B-02

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
  - TASK-FUNC-007-12-03  # Therapist QR Receive Screen must exist to integrate the pre-transfer check (AC-01 QR path)
opus_recommended: false
implementation_notes: >
  Domain: StoragePolicy value object (available bytes vs. required bytes → policy decision enum: ok/warn/in-memory/block).
  Data: StorageProbeService (platform storage query; returns available persistent bytes and free RAM estimate).
  Presentation: pre-transfer storage check hook on TherapistQrReceiveBloc + file import path;
  InMemoryIndicatorBanner widget (non-dismissible, always-visible per AC-03);
  same-session commit trigger when storage freed (AC-04, poll or platform storage change stream).
  Hard-block path (AC-05) must prevent any partial write — atomic bundle persist or nothing.
  Device range: 2 GB RAM lower bound (2017 Android) — only offer in-memory fallback when free RAM > data size + margin.
```

**Rationale**: All five ACs are uncovered and the feature is effort S. The therapist receive path (TASK-FUNC-007-12-03) is the integration point for the pre-transfer check — it must exist before this guard can be wired in. The always-visible in-memory indicator (AC-03) must be a non-dismissible presentation-layer widget that persists across navigation. The device range constraint (2 GB lower bound) adds a safety check before the in-memory fallback path is offered.

---

## Package: "Transfer Data Model" — feat_plan_export

### Task B-03

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
after: []
opus_recommended: false
implementation_notes: >
  Domain/Data: SerializePlanForExportUseCase — input QuestionnairePlan, output versioned JSON string.
  Reuse or delegate to plan serialization pipeline from feat_plan_serialization (Sub-Agent A scope) if available;
  otherwise implement a thin wrapper here.
  Presentation: Export/Share action button in PlanTemplateDetailContent AppBar (AC-01);
  ExportPlanScreen or modal dialog showing generated QR code + therapist instruction text (AC-03).
  QR code rendered via qr_flutter v4.x from serialized string (AC-02/AC-04).
  Security (encryption) is deferred to 0.0.2 per RELEASE_BACKLOG.md — serialization contract must accommodate it.
  AC-05 (client can scan) verified via integration test against feat_plan_receiving (already covered).
```

**Rationale**: No tasks exist for this feature. All five ACs are presentation + data layer work that is self-contained within the therapist plan editor. The serialization use case either reuses the feat_plan_serialization pipeline (Sub-Agent A) or is a thin new wrapper — the plan must confirm the reuse strategy at implementation time. Security is explicitly deferred to 0.0.2 per RELEASE_BACKLOG; the AC-note in requirements.md acknowledges this. Opus not recommended — M effort with clear scope and no architectural ambiguity.

**Phase 2 reopener**: If Sub-Agent A's feat_plan_serialization tasks already implement `SerializePlanForExportUseCase`, Task B-03 scope shrinks to presentation only (effort S). Aggregation agent should cross-check.

---

## Package: "Transfer Data Model" — REQ-NFUNC-001 (data_versioning)

### Task B-04

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
  Ensure currentDataVersion is included in serialized QuestionnairePlan export (AC-01).
  Implement import-time version check: match path (AC-02), older-version migration chain (AC-03/AC-04).
  Migration function infrastructure in data/infrastructure layer of plan_templates feature
  (lib/features/therapist/plan_templates/data/ or equivalent).
  Location: version_constants.dart for currentDataVersion constant; MigrationService for step functions.
  Reference: doc/architecture/ for layer placement.
```

### Task B-05

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
  - TASK-NFUNC-001-01  # B-04 above — version check logic must exist before UX can surface the error
opus_recommended: false
implementation_notes: >
  When importedVersion > currentDataVersion, surface user-friendly error:
  "This plan was created with a newer version of the app. Please update your app to import it."
  Wire into the import result handling in the plan receiving presentation layer (feat_plan_receiving — already completed).
  Use the domain Failure system (doc/domain/failures.md) — UnsupportedVersionFailure → error dialog or inline error state.
  Do not use raw print()/debugPrint() for this path; log at warning level via ILogger.
```

**Rationale**: All five ACs are uncovered; no tasks exist. Split into two tasks by layer boundary: B-04 covers the data-layer migration infrastructure (AC-01–04) which is straightforward and independently testable; B-05 covers the presentation-layer error UX (AC-05) which depends on the infrastructure existing. Both are effort S. Splitting enables parallel planning in the after-chain (B-05 after B-04) and keeps each task single-responsibility.

---

## Package: "Transfer Data Model" — REQ-NFUNC-017 (logging)

**All seven ACs are covered by three completed tasks (2026-03-08):**
- `2026-03-08_impl_logging-service (completed)` — AC-01, AC-02, AC-03, AC-04, AC-06, AC-07
- `2026-03-08_impl_logging-guideline (completed)` — AC-05
- `2026-03-08_impl_logging-clean-arch-refactor (completed)` — AC-01, AC-06, AC-07

**No new tasks required for REQ-NFUNC-017.**

---

## Summary Table

| Task | Req | ACs Covered | Effort | Layer | After |
|---|---|---|---|---|---|
| (existing) TASK-FUNC-007-12-01 | REQ-FUNC-007-12 | pipeline sections | M | domain+data | TASK-FUNC-007-04-05/08 |
| (existing) TASK-FUNC-007-12-02 | REQ-FUNC-007-12 | AC-01–05, AC-07 | M | presentation | -01 |
| (existing) TASK-FUNC-007-12-03 | REQ-FUNC-007-12 | AC-10–14 | M | presentation | -01 |
| (existing) TASK-FUNC-007-12-04 | REQ-FUNC-007-12 | AC-15–19 | S | presentation | -02/-03 |
| B-01 | REQ-FUNC-007-05 | AC-01–05 | M | domain | TASK-FUNC-007-07 |
| B-02 | REQ-FUNC-007-08 | AC-01–05 | S | cross-layer | TASK-FUNC-007-12-03 |
| B-03 | REQ-FUNC-014-06 | AC-01–05 | M | cross-layer | (none) |
| B-04 | REQ-NFUNC-001 | AC-01–04 | S | data | (none) |
| B-05 | REQ-NFUNC-001 | AC-05 | S | presentation | B-04 |

**New tasks this partial: 5 (B-01 through B-05)**
**Features with zero gaps: feat_qr_data_transfer (all ACs covered), REQ-NFUNC-017 (all ACs completed)**
