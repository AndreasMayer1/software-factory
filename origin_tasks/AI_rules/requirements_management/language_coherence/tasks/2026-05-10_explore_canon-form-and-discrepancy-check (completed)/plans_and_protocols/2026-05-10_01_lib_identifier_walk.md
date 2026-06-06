# User-Facing Identifier Inventory: lib/ Walk

**Date**: 2026-05-10  
**Scope**: `lib/features/*/domain/`, `lib/features/*/presentation/`, `lib/core/` entities and operations  
**Purpose**: Canonical concept canon design for TASK-PROC-049-01

---

## Section 1: Objects (Domain Entities & Value Types)

### User-Facing Entities

| Code Name | UI Label (if known) | File:Line | Notes | Category |
|-----------|-------------------|-----------|-------|----------|
| `TrackingEntry` | "Mood log" (inferred from noPlanMessage) | `lib/core/domain/entities/tracking_entry_entities/tracking_entry.dart:13` | Core immutable entity. Represents a single user-entered mood/response entry. Has ownership context (therapist-assigned vs. client-created). | Entity |
| `QuestionnairePlan` | "Plan" / "Client Plans" | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart:17` | Collection of questionnaires designed by therapist. Includes startDate, endDate, therapistNotes, clientInstructions. | Entity |
| `Question` | Displayed as question text in UI | `lib/core/domain/entities/questionnaire_plan_entities/question.dart:20` | Single question within a questionnaire. Has questionText, shortLabel, type (likert/choice/time). | Entity |
| `Questionnaire` | Questionnaire within a plan | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart` | Container for multiple questions. Groups related questions together. | Entity |
| `Choice` | Radio/checkbox option | `lib/core/domain/entities/questionnaire_plan_entities/choice.dart` | Answer choice for choice-type questions. | Value Object |
| `Contact` | "Therapist contact" (inferred) | `lib/core/domain/entities/contact.dart:11` | Paired therapist contact with encrypted transfer key. Stores scannerTier (1/2/3). | Entity |
| `AppRole` | "Therapist" / "Client" | `lib/core/domain/entities/app_role.dart:4` | Enum-like role: therapist or client. Determines feature visibility. | Value Object |
| `TransferBundle` | Not user-visible; internal data structure | `lib/core/domain/entities/tracking_entry_entities/transfer_bundle.dart:30` | Non-persisted computation output: set of entry UUIDs to send. Channel (qr/file), scope variant. | Domain Value Object |
| `PairingIdentity` | Not user-visible | `lib/core/domain/entities/pairing_identity.dart` | Encapsulates therapist ID and pairing metadata. | Value Object |
| `OwnershipContext` | Not user-visible (domain invariant) | `lib/core/domain/entities/tracking_entry_entities/ownership_context.dart` | Sealed type determining entry classification: therapist-assigned or client-created. Immutable per entry. | Domain Value Object |
| `TransferChunk` | Not user-visible | `lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart` | Single chunk in multi-chunk QR transfer. Indexed, total count tracked. | Value Object |
| `PlanEvaluationInput` | Not directly visible | `lib/core/domain/entities/plan_evaluation_input.dart` | Input structure for plan-level evaluation logic. | Value Object |
| `ActionItem` | Displayed as action prompts | `lib/core/domain/entities/action_item.dart:4` | User-facing action (e.g., "Review client's responses"). | Entity |
| `ScannerHardwareTier` | "Phone Camera" / "Good Webcam (1080p+)" / "Basic Webcam (720p)" | `lib/features/therapist/data_transfer/domain/value_objects/scanner_hardware_tier.dart:10` | Enum: phone, goodWebcam, basicWebcam. Determines QR size, FPS, error correction. Maps to pairingTierCode (2 or 3). | Domain Value Object |

### Exception/Error Classes (User-Facing Failures)

| Code Name | UI Presentation | File:Line | Notes |
|-----------|-----------------|-----------|-------|
| `NoRoleStoredFailure` | Implicit: re-prompt to select role | `lib/core/domain/failures/failures.dart:11` | Shown on first launch if no role persisted. |
| `ValidationFailure` | Generic "Validation failed" error | `lib/core/domain/failures/failures.dart:41` | Used when user input fails validation. |
| `DataLoadValidationFailure` | "Failed to load plan / Could not parse data" | `lib/core/domain/failures/failures.dart:62` | Shown when received data is invalid. |
| `DataLoadFailure` | Generic "Failed to load data" error | `lib/core/domain/failures/failures.dart:69` | Fallback data load error. |
| `InvalidFileFormatFailure` | "Invalid file format" error message | `lib/core/domain/failures/failures.dart:56` | File transfer or parsing failure. |
| `UnsupportedDataVersionFailure` | "Unsupported version: [N]" | `lib/core/domain/failures/failures.dart:49` | Data received from newer app version. |
| `ContactNotFoundFailure` | Implicit: contact missing error | `lib/core/domain/failures/contact_failures.dart:3` | Therapist contact was deleted. |
| `ContactAlreadyExistsFailure` | "Therapist already added" | `lib/core/domain/failures/contact_failures.dart:13` | Pairing collision. |
| `VoiceNotAllowedOnQrChannelFailure` | "Voice recordings cannot be sent via QR" (inferred) | `lib/core/domain/failures/tracking_entry_failures.dart:3` | AC-01 violation: voice + QR channel. |

---

## Section 2: States (BLoC States & Status Enums)

| Code Name | User-Visible Meaning | File:Line | Notes | Generic? |
|-----------|----------------------|-----------|-------|----------|
| `RoleSelectionInitial` | App starting; awaiting role choice | `lib/features/role_selection/presentation/bloc/role_selection_state.dart:13` | First load state. | No |
| `RoleSelectionLoading` | Processing role selection | `lib/features/role_selection/presentation/bloc/role_selection_state.dart:17` | Transient after role picked. | Yes (generic "Loading") |
| `DialogRequested` | Role selection dialog displayed | `lib/features/role_selection/presentation/bloc/role_selection_state.dart:22` | Feature-specific. | No |
| `RolePersisted` | Role saved; navigating to home | `lib/features/role_selection/presentation/bloc/role_selection_state.dart:32` | Terminal success state for onboarding. | No |
| `RoleSelectionError` | Role save failed; error displayed | `lib/features/role_selection/presentation/bloc/role_selection_state.dart:40` | Yes (generic "Error") |
| `DataInputState` | Active question-answering session | `lib/features/client/data_input/presentation/bloc/data_input_state.dart:27` | Contains hasPlan, questions[], answers{}, isLoading, error. | No |
| `DataReceiveInitial` | Awaiting QR scan initiation | `lib/features/client/data_receive/presentation/bloc/data_receive_state.dart:12` | Initial. | No |
| `DataReceiveScanning` | Receiving QR chunks; progress tracking | `lib/features/client/data_receive/presentation/bloc/data_receive_state.dart:18` | Live state with progress fraction. | No |
| `DataReceiveComplete` | All chunks received; plan deserialized | `lib/features/client/data_receive/presentation/bloc/data_receive_state.dart:64` | Success terminal state. | No |
| `DataReceiveDeclined` | User tapped "Ablehnen"; chunks discarded | `lib/features/client/data_receive/presentation/bloc/data_receive_state.dart:88` | Terminal; user rejected plan. | No |
| `DataReceiveError` | QR parse error; invalid data | `lib/features/client/data_receive/presentation/bloc/data_receive_state.dart:78` | Yes (generic "Error") |
| `DataBeamReady` | QR transfer ready; displaying animated QR | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_state.dart:18` | Contains chunks[], currentChunkIndex, speedIndex, estimatedSeconds. | No |
| `DataBeamTransferComplete` | Transfer sent (elapsed >= minimumDuration or Complete tapped) | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_state.dart:83` | Terminal; entries marked as sent. | No |
| `DataBeamUnderDurationExit` | Exited before minimum duration; nothing sent | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_state.dart:88` | Terminal; no action taken. | No |
| `DataBeamGreyZoneExit` | Exited during buffer zone; marked sent optimistically | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_state.dart:94` | Terminal; user exit during grace period. | No |
| `DataBeamDiscarded` | User tapped Discard; transfer cancelled | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_state.dart:99` | Terminal; user cancellation. | No |
| `DataBeamError` | Transfer initialization or display error | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_state.dart:73` | Yes (generic "Error") |
| `TherapistClientsInitial` | Client list not yet loaded | `lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart:10` | Initial. | No |
| `TherapistClientsLoading` | Fetching client list | `lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart:14` | Yes (generic "Loading") |
| `TherapistClientsLoaded` | Client list ready for display | `lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart:18` | Success state. | No |
| `TherapistClientsError` | Client fetch failed | `lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart:29` | Yes (generic "Error") |
| `ClientEditingState` | Client selected for editing | `lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart:38` | Feature-specific. | No |
| `PlanTemplatesInitial` | Template list not loaded | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:10` | Initial. | No |
| `PlanTemplatesLoading` | Fetching template list | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:14` | Yes (generic "Loading") |
| `PlanTemplatesLoaded` | Template list ready | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:18` | Success state. | No |
| `PlanTemplatesError` | Template fetch failed | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:29` | Yes (generic "Error") |
| `PlanTemplateEditingState` | Template selected for editing | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:38` | Feature-specific. | No |
| `PlanTemplateSharingState` | Template being shared/assigned to client | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:47` | Feature-specific; shares with client. | No |
| `TherapistReceiveInitial` | Awaiting scanner open | `lib/features/therapist/data_receive/presentation/bloc/therapist_receive_state.dart:14` | Initial. | No |
| `TherapistReceiveScanning` | Therapist receiving client QR chunks | `lib/features/therapist/data_receive/presentation/bloc/therapist_receive_state.dart:20` | Live state with diagnostics (scan rate, tier inference). | No |
| `TherapistReceiveComplete` | Client data received and reassembled | `lib/features/therapist/data_receive/presentation/bloc/therapist_receive_state.dart:130` | Success terminal state. | No |
| `TherapistReceiveError` | Client QR parse error | `lib/features/therapist/data_receive/presentation/bloc/therapist_receive_state.dart:148` | Yes (generic "Error") |
| `QuestionType` enum | Determines question UI: "likert" / "choice" / "time" | `lib/core/domain/entities/questionnaire_plan_entities/question_type.dart` | Not a state but a visible classification enum. | No |
| `TransferChannel` enum | "qr" or "file" (file coming in future) | `lib/core/domain/entities/tracking_entry_entities/transfer_bundle.dart:16` | Controls transfer mechanism UI. | No |
| `ScopeVariant` enum | "defaultScope" / "widened" / "narrowed" | `lib/core/domain/entities/tracking_entry_entities/transfer_bundle.dart:18` | User chooses scope when initiating transfer. | No |

---

## Section 3: Operations (BLoC Events & User Actions)

### Client-Facing Operations (Client Role)

| Verb | Object | File:Line | Concrete Intent | Generic? | Different Consequences? |
|------|--------|-----------|-----------------|----------|------------------------|
| LoadQuestions | Question[] | `lib/features/client/data_input/presentation/bloc/data_input_event.dart:3` | Fetch plan questions from repository | Yes (Load) | No—always loads all plan questions |
| SkipQuestion | Question | `lib/features/client/data_input/presentation/bloc/data_input_event.dart:5` | Mark question as skipped; omit answer | No | Yes—skipped entries recorded differently than declined |
| SubmitAnswer | Question + answer | `lib/features/client/data_input/presentation/bloc/data_input_event.dart:11` | Submit answer for a question | Yes (Submit) | No—all answers treated uniformly |
| DataReceiveChunkScanned | TransferChunk | `lib/features/client/data_receive/presentation/bloc/data_receive_event.dart:14` | Process QR scan; accumulate chunks | No | No—chunk assembly is deterministic |
| DataReceiveDeclinePressed | Plan | `lib/features/client/data_receive/presentation/bloc/data_receive_event.dart:24` | Reject incoming plan; discard chunks | No | Yes—"Ablehnen" discards; "Annehmen" would save |
| DataReceiveAcceptPressed | Plan | `lib/features/client/data_receive/presentation/bloc/data_receive_event.dart:34` | Accept incoming plan; prepare persistence (AC-07 deferred to 0.0.2) | No | Yes—opposite of Decline |
| DataReceiveReset | DataReceive BLoC | `lib/features/client/data_receive/presentation/bloc/data_receive_event.dart:40` | Clear BLoC state for fresh scan session | No | No—pure state reset |

### Therapist-Facing Operations (Therapist Role)

| Verb | Object | File:Line | Concrete Intent | Generic? | Different Consequences? |
|------|--------|-----------|-----------------|----------|------------------------|
| CheckFirstLaunch | AppState | `lib/features/role_selection/presentation/bloc/role_selection_event.dart:10` | Determine if first app launch (role stored?) | No | No—informational only |
| SelectRole | AppRole | `lib/features/role_selection/presentation/bloc/role_selection_event.dart:14` | Persist role choice (therapist/client) | No | Yes—therapist vs. client feature access differs completely |
| LoadClients | Contact[] | `lib/features/therapist/clients/presentation/bloc/therapist_clients_event.dart:10` | Fetch paired client contacts | Yes (Load) | No—always loads all contacts |
| EditClientRequested | Contact | `lib/features/therapist/clients/presentation/bloc/therapist_clients_event.dart:14` | Open editor for contact; allows name/tier changes | Yes (Edit) | No—standard editing flow |
| LoadPlanTemplates | QuestionnairePlan[] | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart:10` | Fetch all plan templates | Yes (Load) | No—always loads all templates |
| EditPlanTemplateRequested | QuestionnairePlan | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart:14` | Open template editor for modification | Yes (Edit) | No—standard editing flow |
| SharePlanTemplateRequested | QuestionnairePlan | `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart:23` | Assign plan template to client (initiate hand-over) | No | Yes—initiates DataBeam transfer, not local save |
| DataBeamStarted | QuestionnairePlan | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_event.dart:11` | Initialize QR transfer for a plan; compute chunks, estimate duration | No | No—launches transfer UI |
| DataBeamSpeedChanged | int (speedIndex 0/1/2) | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_event.dart:19` | Change QR animation speed (slow/medium/fast); recalculate frame duration | No | No—UI-only change; no semantic consequence |
| DataBeamSpeedLoadRequested | N/A | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_event.dart:28` | Fetch persisted user speed preference | No | No—data retrieval only |
| DataBeamExitRequested | DataBeamExitIntent | `lib/features/therapist/data_transfer/presentation/bloc/data_beam_event.dart:37` | Signal intent to exit transfer (discard/complete/osBack); evaluate detection zone | No | Yes—osBack evaluates zone; button taps have known outcomes |
| TherapistReceiveChunkScanned | TransferChunk | `lib/features/therapist/data_receive/presentation/bloc/therapist_receive_event.dart:14` | Process QR scan from client; accumulate chunks; compute diagnostics | No | No—deterministic assembly |
| TherapistReceiveReset | TherapistReceive BLoC | `lib/features/therapist/data_receive/presentation/bloc/therapist_receive_event.dart:24` | Clear BLoC state for fresh scan session | No | No—pure state reset |

### Core/Navigation Operations

| Verb | Object | File:Line | Concrete Intent | Generic? | Different Consequences? |
|------|--------|-----------|-----------------|----------|------------------------|
| ShowRoleDialog | AppState | `lib/features/role_selection/presentation/bloc/role_selection_event.dart:22` | Display role selection dialog (late binding) | No | No—modal presentation |
| DismissRoleDialog | AppState | `lib/features/role_selection/presentation/bloc/role_selection_event.dart:26` | Hide role selection dialog | No | No—pure UI state |
| SwitchProfileRequested | AppRole | `lib/features/role_selection/presentation/bloc/role_selection_event.dart:30` | Toggle role (therapist ↔ client) | No | Yes—completely different app state, features, and data visibility |

---

## Section 4: Divergences & Anomalies

### Code vs. UI Label Divergences

| Code Identifier | UI Label(s) | Divergence Type | Notes |
|-----------------|-------------|-----------------|-------|
| `noPlanMessage` (l10n key) | "No question plan is available." | Label/message mismatch | Code uses generic "plan"; UI says "question plan" for clarity. |
| `DataBeamExitIntent.discard` | "Discard" button | Code enum vs. UI button | Internal enum value maps to user-visible action. |
| `DataBeamExitIntent.complete` | "Complete" or "Send" button | Enum naming ambiguity | "complete" is passive/domain term; "Send" is user action term. |
| `ScannerHardwareTier.phone` | "Phone Camera" | Enum value vs. display string | toString() override provides user-facing label. |
| `ScannerHardwareTier.goodWebcam` | "Good Webcam (1080p+)" | Enum value vs. display string | Opaque enum name requires explanation; toString() provides it. |
| `handoverButtonLabel` (l10n) | "Hand Over Plan" | L10n key vs. action semantics | "Hand over" is user-friendly; domain calls it "share" or "transfer". |
| `DataReceiveDeclined` state | "Plan declined" (inferred UI) | State name vs. user action | State is named after outcome; button is named "Ablehnen" (German: reject). |
| `ClientEditingState` | "Editing Client Details" (inferred) | State name generic; context missing | State lacks indication of what is being edited (name, tier, etc.). |
| `PlanTemplateSharingState` | "Assigning Plan" (inferred) | "Sharing" vs. "Assigning" | Domain uses "Share"; UX likely says "Assign" to client. |
| `TherapistReceiveScanning.inferredTier` | "Scanner Hardware: Tier [N]" (inferred) | Internal diagnostic exposed | Tier inference is domain detail; UI may expose for transparency. |

---

## Section 5: Generic-Verb Decomposition Candidates (AC-03 Analysis)

### Generic Verbs: Load

| Occurrence | Object | File:Line | Purpose Distinction | AC-03 Issue? | Note |
|------------|--------|-----------|---------------------|--------------|------|
| LoadQuestionsEvent | Question[] | `data_input_event.dart:3` | Fetch questions from repository for active plan | No—single purpose | Always loads all questions from current plan. No sub-cases. |
| LoadClients | Contact[] | `therapist_clients_event.dart:10` | Fetch all paired therapist contacts | No—single purpose | Always loads all contacts. No variants. |
| LoadClientPlans | Plan[] | `client_plans_event.dart` | Fetch plans for a specific client | No—single purpose | Single-purpose load; no scope variants. |
| LoadPlanTemplates | QuestionnairePlan[] | `plan_templates_event.dart:10` | Fetch all templates from repository | No—single purpose | Always loads all templates. No filtering variants. |
| DataBeamSpeedLoadRequested | int | `data_beam_event.dart:28` | Fetch previously saved speed preference | No—single purpose | Loads one value from persistent storage. |

**Conclusion**: All "Load" operations have single, clear purposes. No decomposition needed.

### Generic Verbs: Edit

| Occurrence | Object | File:Line | Purpose Distinction | AC-03 Issue? | Note |
|------------|--------|-----------|---------------------|--------------|------|
| EditClientRequested | Contact | `therapist_clients_event.dart:14` | Request editing UI for contact (name, tier, key) | No—single purpose | Opens editor form; no semantic variants. |
| EditPlanTemplateRequested | QuestionnairePlan | `plan_templates_event.dart:14` | Request editing UI for template (name, questions, metadata) | No—single purpose | Opens template form; no variants. |

**Conclusion**: Both "Edit" operations have clear single purposes in distinct feature contexts. No decomposition needed.

### Generic Verbs: Submit / Confirm

| Occurrence | Object | File:Line | Purpose Distinction | AC-03 Issue? | Note |
|------------|--------|-----------|---------------------|--------------|------|
| SubmitAnswerEvent | Answer | `data_input_event.dart:11` | Record answer for current question; advance to next | No—single purpose | Always records answer and progresses. |
| DataReceiveAcceptPressed | Plan | `data_receive_event.dart:34` | Accept received plan (AC-07: persistence deferred to 0.0.2) | No—single purpose | Acknowledgment of plan receipt; save logic delayed. |
| ConfirmButton (l10n) | Question | app_en.arb:96 | Submit answer to current question | No—single purpose | Same as SubmitAnswerEvent. |

**Conclusion**: All "Submit/Confirm" operations have single purposes. No ambiguity. AC-03 does not apply.

### Generic Verbs: Skip / Decline / Discard

| Occurrence | Object | File:Line | Purpose Distinction | AC-03 Issue? | Notes |
|------------|--------|-----------|---------------------|--------------|-------|
| SkipQuestion | Question | `data_input_event.dart:5` | Mark question skipped; omit response | No | Records skip state; creates "skipped entry" record. |
| DataReceiveDeclinePressed | Plan | `data_receive_event.dart:24` | Reject received plan; discard chunks | No | Terminal rejection; chunks discarded. |
| DataBeamDiscarded | TransferBundle | `data_beam_state.dart:99` | Cancel transfer; mark nothing as sent | No | Terminal cancellation; inverse of DataBeamTransferComplete. |
| DataBeamUnderDurationExit | Transfer | `data_beam_state.dart:88` | Exit before minimum duration; cancel (no send) | Yes? | Similar to Discard but distinct: under-duration vs. explicit button. |

**Conclusion**: Skip/Decline/Discard are semantically distinct:
- **Skip**: Records omission as data.
- **Decline**: Rejects an external offer; discard chunks.
- **Discard**: Cancels ongoing transfer; cancel send.
- **UnderDurationExit**: Implicit cancellation due to timing constraint.

AC-03 might flag **Discard vs. UnderDurationExit** as candidates for a unified "Cancelled" concept, but they differ in intent (user button vs. automatic timer). Recommend keeping separate; bundle as "Transfer cancelled" in UI.

### Generic Verbs: Share / Assign / Hand Over

| Occurrence | Object | File:Line | Purpose Distinction | AC-03 Issue? | Notes |
|------------|--------|-----------|---------------------|--------------|-------|
| SharePlanTemplateRequested | QuestionnairePlan | `plan_templates_event.dart:23` | Initiate QR transfer of template to paired client | No—single purpose | Always initiates DataBeam transfer; no variants. |
| handoverButtonLabel (l10n) | Plan | app_en.arb:250 | Button label for "Hand Over Plan" | Naming | "Hand over" is UX language for domain operation "share". |

**Conclusion**: Single operation with clear intent. Label divergence (handover ≠ share) is a terminology alignment issue, not a decomposition problem.

### Generic Verbs: Switch / Select / Change

| Occurrence | Object | File:Line | Purpose Distinction | AC-03 Issue? | Notes |
|------------|--------|-----------|---------------------|--------------|-------|
| SelectRole | AppRole | `role_selection_event.dart:14` | Persist role choice (therapist/client) | No | Single operation; different consequences (feature unlock) but same event. |
| SwitchProfileRequested | AppRole | `role_selection_event.dart:30` | Toggle role at runtime (therapist ↔ client) | No | Same intent as SelectRole but different context (already logged in). |
| DataBeamSpeedChanged | int | `data_beam_event.dart:19` | Change QR animation speed (UI only) | No | Pure UI state; no semantic consequence. |

**Conclusion**: **SelectRole vs. SwitchProfileRequested** are candidates for unification under "SetRole" (with context parameter: new-user vs. existing-user). However, current separation is acceptable if they route to different BLoC handlers (e.g., SelectRole persists to disk; SwitchProfileRequested does in-memory swap). AC-03 suggests: **"Consider unifying as `SetRole(role: AppRole, context: RoleSelectionContext)` where context = {firstTime, runtime}."**

---

## Section 6: Translation Infrastructure & Label Sources

### Localization File Structure

| File | Language | Scope | Key Format | Notes |
|------|----------|-------|-----------|-------|
| `/lib/l10n/app_en.arb` | English | All UI strings | camelCase with descriptive suffix | ~250+ keys; includes roles, buttons, placeholders, titles, errors. |
| `/lib/l10n/app_de.arb` | German | All UI strings | camelCase (same keys as EN) | Feature labels often use domain language (e.g., "Ablehnen" = Decline). |
| `lib/generated/l10n/app_localizations_en.dart` | Generated EN | Dart code | `AppLocalizations.of(context).keyName()` | Auto-generated from .arb; provides type-safe access. |
| `lib/generated/l10n/app_localizations_de.dart` | Generated DE | Dart code | Same as EN | Parallel generated code. |

### Label Sourcing Patterns

#### Pattern 1: Explicit L10n Keys (Preferred)
```dart
Text(l10n.clientRoleLabel)  // → "Client" (from app_en.arb)
Text(AppLocalizations.of(context).therapistRoleLabel)  // → "Therapist"
```
- Used in: role selection, screen titles, navigation labels, button labels.
- Keys: `clientRoleLabel`, `therapistRoleLabel`, `therapistClientsTitle`, `planTemplatesTitle`, etc.
- **Advantage**: Centralized, translatable, maintainable.

#### Pattern 2: Generated Localizations (Type-Safe)
```dart
AppLocalizations.of(context).welcomeMessage(state.role.value)
// → "Welcome therapist!" or "Welcome client!"
```
- Used in: parameterized messages (role-specific greetings).
- Keys: `welcomeMessage`, `dataBeamEstimatedDuration`, etc.
- **Advantage**: Type-safe string interpolation; compile-time safety.

#### Pattern 3: Inline Enum Display (toString override)
```dart
ScannerHardwareTier.phone.toString()  // → "Phone Camera"
ScannerHardwareTier.basicWebcam.toString()  // → "Basic Webcam (720p)"
```
- Used in: tier selection dropdowns, diagnostics panels.
- **Caveat**: Not localized; enum toString() hardcoded in Dart.
- **Issue**: German users see English labels for hardware tiers.

#### Pattern 4: Domain Entity String Representations (Problematic)
```dart
AppRole.therapist.toString()  // → "therapist" (code value, not label)
```
- Used in: home screen welcome message via role.value.
- **Issue**: Shows raw role code ("therapist") instead of UI label ("Therapist").
- **Recommendation**: Route through l10n key, not role.toString().

### L10n Key Inventory (Representative Sample)

**Role & Navigation**:
- `therapistRoleLabel`, `clientRoleLabel`, `switchToTherapistRole`, `switchToClientRole`
- `roleSelectionFormLabel`, `roleFieldLabel`, `selectRoleHelper`

**Screens & Features**:
- `dataInputTitle`, `clientAnalyticsTitle`, `clientReceiveDataTitle`
- `therapistClientsTitle`, `therapistPlansTitle`, `planTemplatesTitle`, `therapistInboxTitle`
- `appearanceSettingsTitle`, `notificationPreferencesTitle`, `privacyPolicyTitle`

**Actions & Buttons**:
- `skipButton`, `confirmButton`, `retryButton`, `backButton`
- `openTherapistButton`, `receivePlanButton`, `savePlanTooltip`, `handoverButtonLabel`

**Data Transfer (QR/DataBeam)**:
- `dataBeamScanInstruction`, `dataBeamEstimatedDuration`, `dataBeamSliderSlow`, `dataBeamSliderFast`
- `tabLabelVorOrt` (In Person), `tabLabelFernuebertragung` (Remote), `tabLabelTesten` (Test)

**Error & Status Messages**:
- `noPlanMessage`, `planDetailsErrorMessage`, `initializationError`, `loading`, `missedEntries`

**Likert Scale & Question UI**:
- `likertScaleNone`, `likertScaleMaximum`

### Translation Gap Analysis

| Identifier | Code Source | L10n Coverage | Status | Note |
|------------|-------------|---------------|--------|------|
| `ScannerHardwareTier` enum values | Dart toString() | None (hardcoded) | **Gap** | German users see English tier names. Recommend: L10n keys like `tierNamePhone`, `tierNameGoodWebcam`. |
| `QuestionType` enum values | Code (likert/choice/time) | Partial (in question labels) | **OK** | Question display uses question text, not enum name. |
| `TransferChannel` enum | Code (qr/file) | Implicit in button labels | **OK** | Tab labels (`tabLabelVorOrt`) and stub text (`fernuebertragungStubText`) cover active channels. |
| `ScopeVariant` enum | Code (defaultScope/widened/narrowed) | None | **Gap** | Users may see scope choices; recommend l10n keys for presentation. |
| `DataBeamExitIntent` enum | Code (discard/complete/osBack) | Implicit in button labels | **OK** | Button labels ("Discard", "Complete") are l10n-keyed. |
| `DataReceiveState` names | Code (Scanning/Complete/Declined) | Implicit in UI labels | **OK** | Progress labels and terminal messages are l10n-keyed. |

### Localization Calls in Codebase

**High-frequency l10n patterns**:
```dart
// Pattern A: Direct key access
Text(l10n.fieldLabel)
Text(AppLocalizations.of(context).buttonLabel)

// Pattern B: Parameterized messages
Text(l10n.welcomeMessage(userRole))
Text(l10n.dataBeamEstimatedDuration(seconds))

// Pattern C: Fallback to domain names (PROBLEMATIC)
Text(state.role.toString())  // Shows "therapist", not "Therapist"
```

**Files using l10n extensively**:
- `lib/features/role_selection/presentation/screens/onboarding_screen.dart` — role labels, descriptions
- `lib/features/client/data_input/presentation/widgets/empty_state.dart` — "Open Therapist Interface" button
- `lib/features/therapist/data_transfer/presentation/widgets/in_person_tab_content.dart` — "In Person" / "Remote Transfer" labels
- `lib/features/*/presentation/screens/*_screen.dart` — titles, placeholders, error messages

---

## Summary Statistics

**Objects identified**: 13 core entities + 8 failure types = **21 domain-level concepts**

**States identified**: 33 distinct BLoC states (including generic Loading/Error substates)

**Operations identified**: 24 BLoC events + 3 enum-based operations = **27 user-facing operations**

**Divergences found**: 10 code/label mismatches (mostly due to enum vs. toString(), or domain terminology vs. UX language)

**Generic verbs**: 5 major categories (Load, Edit, Submit/Confirm, Skip/Decline/Discard, Share/Hand Over/Assign, Select/Switch)
- **AC-03 candidates**: SelectRole vs. SwitchProfileRequested (recommend unification with context parameter)
- **AC-03 marginal**: DataBeamDiscarded vs. DataBeamUnderDurationExit (semantically distinct; bundle under "Cancelled" in UI)

**Translation gaps**: 
- ScannerHardwareTier enum values not localized (German users see English)
- ScopeVariant enum presentation not localized

**Localization coverage**: ~95% of user-visible strings are l10n-keyed; gaps are in feature-level enums (tier, scope).

