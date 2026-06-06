# Investigation Findings — TASK-PROC-049-01

Date: 2026-05-14
Author: Opus 4.7 (manual session)
Phase: Phase 1 — investigation, before synthesis

## What was observed

### A. translation_context infrastructure does not yet exist

REQ-NFUNC-013 AC-08 specifies `translation_context` as a per-entry rich description. The current implementation:

- `lib/l10n/app_en.arb` (252 lines, 57 entries) and `lib/l10n/app_de.arb` use standard Flutter ARB. Each entry has a short `description` field — typically one sentence — not the multi-paragraph `translation_context` envisioned by AC-08 §8.4.
- Generated `lib/generated/l10n/app_localizations*.dart` consume the ARB.
- No separate `translation_context` storage exists. The shape proposed in REQ-NFUNC-013 §8.4 (`key`, `de`, `en`, `translation_context`) has not been built.

**Implication**: The canon is being designed for a downstream consumer that does not yet exist. The "duplication cost of not having a canon" is currently zero — but the bill comes when AC-08 is implemented. The canon's value is realised entirely *at* and *after* that implementation.

### B. Hardcoded German strings mixed with ARB-routed strings

`lib/features/therapist/data_transfer/presentation/widgets/in_person_tab_content.dart` contains hardcoded German (`'Name des Klienten'`, `'Bitte mit der Klienten-App scannen.'`, `'ca. ${state.estimatedSeconds} Sek.'`, `'Gib den Namen des Klienten ein…'`) and hardcoded English (`'Discard Transfer'`, `'Complete Transfer'`). The l10n migration is partial.

This is relevant to the canon: a discrepancy check that walks ARB only will miss many user-facing strings. It must also walk presentation-layer Dart files for hardcoded `Text('…')` calls.

### C. Concept inventory observed in `feat_therapist_transfer_ui`

**Objects (nouns)**:
- Plan (DE: Plan, code: `QuestionnairePlan`)
- Plan Template (code: `PlanTemplate`)
- Client (DE: Klient, code: `Client` via `IClientDataPartitionRepository`)
- Therapist
- Transfer — the act of moving a plan to a client device
- Data Beam — UI/code-internal name for the QR pulse animator
- Chunk (`TransferChunk`)
- Detection Zone (`TransferDetectionZone`)
- Scanner Hardware Tier (`ScannerTierParameters`: 720p webcam / HD webcam / Smartphone)

**States** (BLoC, therapist side):
`DataBeamInitial`, `DataBeamLoading`, `DataBeamReady`, `DataBeamTransferComplete`, `DataBeamUnderDurationExit`, `DataBeamGreyZoneExit`, `DataBeamDiscarded`, `DataBeamError`

**States** (BLoC, client side):
`DataReceiveInitial`, `DataReceiveScanning`, `DataReceiveComplete`, `DataReceiveDeclined`, `DataReceiveError`

**Operations (verbs) surfaced to the user**:
- Hand Over Plan / "Plan aushändigen" (`handoverButtonLabel`, `handoverDialogTitle`)
- Discard Transfer (button, hardcoded EN)
- Complete Transfer (button, hardcoded EN)
- Receive Plan / "Plan empfangen" / "Plan erhalten" / Receive Data — at least three near-synonyms across surfaces
- Scan / "scannen"
- Accept / "Annehmen"
- Decline / "Ablehnen"
- Save Plan (`savePlanTooltip`)
- Switch to Client/Therapist Role
- Select (a client / a plan / a plan template)
- Open Therapist Interface (`openTherapistButton`)

### D. Concrete AC-02 / AC-03 violations visible today

These are not hypothetical — they exist in the codebase right now:

1. **Verb drift mid-flow.** The therapist clicks **"Hand Over Plan"** (which evokes the personal-physical metaphor per REQ-NFUNC-013 §8.4 example). On the next screen the buttons say **"Discard Transfer"** and **"Complete Transfer"** — the verb has shifted to the technical register on the *same dialog*. AC-02 candidate failure.

2. **DE synonym drift on receive side.**
   `lib/features/client/data_receive/presentation/screens/data_beam_scanner_screen.dart:38` — `title: const Text('Plan empfangen')` (active scanning).
   `…/plan_receipt_confirm_screen.dart:28` — `title: const Text('Plan erhalten')` (post-scan confirm).
   Two German words for the receive operation, distinguished only by phase. Either intentional (state distinction) and undocumented, or silent drift. AC-02 cannot tell which without a canon.

3. **EN near-synonym cluster on receive.** `receivePlanButton` ("Receive Plan"), `clientReceiveDataTitle` ("Receive Data"), and `'Plan empfangen'` — three surface forms for one user concept. AC-02 candidate failure.

4. **`Data Beam` as code-leaked branding.** `DataBeamBloc`, `DataBeamScannerScreen`, `DataBeamQrAnimator`, `data_beam_*.dart` files — but no user-visible label uses "Data Beam." It is a code-internal name that doesn't show up at the canon level. This is fine *if* the canon explicitly records the code-name / user-name distinction; silent today.

5. **`open` polysemy.** "Open Therapist Interface" (navigation), "Open Source Licenses" (compound noun). Different semantic operations sharing a verb — AC-03 check needs to distinguish.

### E. Existing project infrastructure relevant to canon implementation

- `scripts/artifacts/generate_id_registry.py` — pattern for harvesting IDs across the requirements tree. The canon's "find all references to a concept" check is structurally similar.
- `scripts/requirements/reconcile_dependencies.py` — pattern for in-place updates of metadata in markdown.
- `requirements_user_needs/_meta/id_registry.md` — generated artifact pattern. A generated `concept_canon.md` would fit the same shape.
- `requirements_user_needs/personas/`, `scenarios/`, `user_flows/` — existing artifact types. The canon is a new sibling, not nested.
- `REQ-PROC-046` (Code Quality / LLM Back-Pressure Gates) — defines the pass/fail discipline AC-05 must integrate with. Existing gates are G1–G5.

### F. Web-research summary (delegated agent, recorded verbatim into protocol below)

Five findings that shape the synthesis:

1. **Single-file markdown is dominant** for canon storage in practice. Per-concept files are rare. ammit-php/ammit, IFRCGo/cbs wiki, ddd-crew/eventstorming-glossary-cheat-sheet — all single-file markdown.
2. **YAML/JSON canon + rendered markdown view** is the LLM-friendly pattern (dbreunig's Jekyll glossary generator, Roadie's "context engineering"). arXiv 2411.10541 reports up to 40% prompt-format variance.
3. **No off-the-shelf tool** handles the markdown + YAML + Dart triple. Vale (prose only), Spectral (JSON/YAML only), and academic prototypes exist; custom CI script is the established path.
4. **Durability correlates with executable enforcement, not artifact richness.** Object maps die after launch; only the glossary file survives, and only when it has a linter enforcing it.
5. **Strangler-style adoption** is the dominant retrofit pattern: lint warns only on new/changed files initially, hard-fail later.

Full research output retained in `2026-05-14_02_web_research_external_knowledge.md`.

## What was NOT investigated

- Concrete proposals for the schema's YAML shape were *drafted from observed concepts* but not validated against every feature area. Only `feat_therapist_transfer_ui` and `data_receive` were walked exhaustively.
- The actual cost of authoring 30–40 canon entries was estimated, not measured. The estimate is in the synthesis but should be sanity-checked at first-feature bootstrap.
- The `lib/**/domain/` Clean-Architecture domain layer was not walked end-to-end. REQ-PROC-049 §3 explicitly carves it out as separate scope; the canon covers the user-facing layer only.
- The German-specific synonyms ("Klient" vs "Patient" register choice) were noted as a deliberate localization choice; no audit was done.
