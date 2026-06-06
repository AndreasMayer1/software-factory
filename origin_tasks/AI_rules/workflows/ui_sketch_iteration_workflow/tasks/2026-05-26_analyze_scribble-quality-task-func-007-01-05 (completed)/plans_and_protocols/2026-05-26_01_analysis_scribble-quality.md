# Analysis: Scribble Output Quality — TASK-FUNC-007-01-05

**Date**: 2026-05-26  
**Analyst**: Claude Sonnet 4.6 (main session)  
**Artifacts reviewed**:
- `feat_therapist_transfer_ui/scribbles/v1/` + `v2/`
- `feat_therapist_transfer_ui/tasks/2026-04-26_impl_client-send-screen-scribble/goal.md`
- `feat_therapist_transfer_ui/requirements.md` (REQ-FUNC-007-01)
- `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md` (FLOW-002)
- `lib/.../transfer_detection_zone.dart` + `transfer_detection_model.dart`
- `requirements_tasks/_scribble_components/`
- `.claude/skills/ui-create-scribble/SKILL.md`

---

## Overall Verdict

The task executed Phase 1 (generate v1) and Phase 2 (auto-review → v2) correctly. v2 is awaiting
user approval (pending question). The skill performed well on structural correctness but has
four specific gaps worth addressing. None are blocking for this task — they are process
improvement findings.

---

## a) Domain Object Names

**Verdict: PARTIAL — spec-aligned, not code-aligned**

### What the scribbles use
- `min_duration` (snake_case, matches requirements Section 10 formula notation)
- Zone c / Zone e / Zone d (requirement letter labels in the corrected c→e→d order)
- Flutter widget names: `Slider`, `FilledButton`, `TabBar`, `LinearProgressIndicator`, etc.
- No Dart class names from the domain model

### What the domain model introduced (TASK-FUNC-007-01-06, completed 2026-05-07)
The domain model was implemented *after* the scribble task was created (goal.md 2026-04-26)
but *before* the automated run (2026-05-26). The domain objects are:

| Dart name | Spec name |
|-----------|-----------|
| `TransferDetectionModel` | (service — no direct spec name) |
| `TransferDetectionZone.underDuration` | Zone c |
| `TransferDetectionZone.greyZone` | Zone e (grey-zone) |
| `TransferDetectionZone.overDuration` | Zone d (over-duration) |
| `TransferDetectionSnapshot` | (value object) |

### Discrepancy found: domain model comment labels are stale
The domain model enum uses the OLD zone letter labeling in its doc comments:
- `greyZone` is commented as "(d)" — but per the corrected spec, grey-zone = zone **e**
- `overDuration` is commented as "(e)" — but per the corrected spec, over-duration = zone **d**

The scribbles (v2) correctly use the corrected order (c→e→d). The domain model
*semantic names* are correct (underDuration, greyZone, overDuration) but the *letter labels
in comments* are stale. This is a pre-existing gap in the domain model comments, not caused
by the scribble task.

### Gap: scribble doesn't reference domain class names
The `flutter_component_mapping` in metadata.yaml and in HTML comment blocks does not reference
`TransferDetectionModel` or `TransferDetectionZone`. For the flutter_handoff.yaml (Phase 5,
not yet generated — awaiting approval), this will mean the developer implementing the BLoC
won't see the domain class names linked from the design artifact.

**Actionable proposal**: Add to the Phase 1 agent prompt: "If a domain class for the feature's
core business logic exists in `lib/features/`, reference it by full class name in the
component mapping block of the screens that depend on it (e.g., in the progress indicator
or button-enable logic, reference `TransferDetectionModel` + `TransferDetectionSnapshot`)."

---

## b) User Flow Coverage

**Verdict: PARTIAL — flow read for ordering, NOT read for behavioral completeness**

### Evidence the flow WAS read
- `flow_positions[]` is populated in metadata.yaml with FLOW-002 step numbers (1, 3, 4, 5)
- Screen labels include FLOW-002 step references
- Screen ordering respects the FLOW-002 sequence

### Evidence the flow was NOT fully read

**1. flow_positions covers only 4 of 9 screens**

| Screen | flow_positions entry? |
|--------|----------------------|
| 01_dialog_structure | ✓ FLOW-002 Step 1 |
| 02_client_selected_local | ✓ FLOW-002 Step 4 |
| 03_pairing_required | ✗ (HTML label says "Step 3" but not in metadata.yaml) |
| 04_pairing_overlay | ✓ FLOW-002 Step 3b |
| 05_transfer_active_local | ✓ FLOW-002 Step 5 |
| 06_transfer_detection_states | ✗ |
| 07_remote_tab | ✗ |
| 08_self_test_tab | ✗ |
| 09_app_not_installed | ✗ |

Screens 06–09 correspond to FLOW-002 exception paths (Exception 1.2 = screen 09,
Exception 1.3 = screen 07, Section 10 = screen 06, Section 6 = screen 08) but these
are not mapped to their flow exception identifiers.

**2. Fast-mode consent prompt missing**

FLOW-002 Domain Concepts states: "The preference is surfaced once during first pairing setup
— a single question in the right context, asked after role configuration and before the first
client pairing." This is a UI state on the pairing/setup screen.

No screen or state variant in the scribbles covers this consent prompt. A pure reading of
the requirements (Section on Transfer Speed Preference) mentions it, but the flow's Domain
Concepts section gives the clearest placement guidance (during first pairing setup). The
auto-review (Phase 2) did not catch this because the auto-review checks ACs but didn't
apparently read the full flow.

**3. "Transfer does not start automatically" — not visually emphasized**

FLOW-002 Step 5 explicitly states: "The transfer does NOT start automatically — the therapist
controls the timing." Screen 02 shows "Start Transfer" as a button, which is correct
structurally. But the flow's emphasis on deliberate therapist control (not auto-start) could
warrant a design annotation/note in the scribble, particularly since the pairing → transfer
sequence also requires an explicit step.

### Root cause

The skill's Phase 1 prompt reads:
> "Pass flow step list to Phase 1 agent as `flow_context` (ordered list of step labels +
> step numbers)."

This is structural ordering context only. The skill does NOT instruct the agent to:
- Verify all exception paths from the flow are covered
- Map exception-path screens back to their FLOW exception identifier
- Check the flow's Domain Concepts section for behavioral constraints

**Actionable proposals**:
1. Phase 1 prompt: "For screens covering exception paths, add `exception_id: [e.g. Exception-1.2]`
   to their flow_positions entry."
2. Phase 2 auto-review checklist: add "Every exception path mentioned in the parent flow
   with a distinct UI state → at least one screen or annotated variant?"
3. Phase 2 auto-review checklist: add "Domain Concepts section of the flow → any behavioral
   constraints (consent prompts, timing rules, opt-in flows) visible as screen states?"

---

## c) Single Resolution Version

**Verdict: ACCEPTABLE for now, but a known skill gap**

The skill produces phone-sized HTML wireframes (one resolution variant). No tablet or desktop
variant exists.

### Why it matters here
FLOW-002 Step 1 describes the therapist's device as "a display large enough for the client
to see (laptop, desktop, or tablet)." The therapist side of this feature is specifically
expected to run on larger screens. A phone-sized wireframe doesn't represent the therapist's
actual usage context accurately.

### Why one version is OK for this iteration
- The flutter widget names (TabBar, Dialog, etc.) are resolution-agnostic
- The structural decisions (tab structure, button placement) are the same at any size
- Phase 3 feedback from the developer reviewing the wireframe can catch layout concerns

### Skill gap
The skill has no concept of "role-appropriate resolution." If the requirement's
`stakeholder: therapist` (or `PERSONA-011: uses a laptop`) were checked, the skill could
generate a second variant at a larger viewport.

**Actionable proposal**: In Phase 1 prompt: "If the requirement's stakeholder is `therapist`
or any referenced persona is known to use a tablet/desktop, generate an additional `index_tablet.html`
preview note (or a second CSS breakpoint variant on screen 01 at minimum)."

---

## d) Reusable Component Creation

**Verdict: CORRECT process, ZERO new library additions**

### What was done correctly
The skill's step 13 mandates tagging. All v2 screens reference `components.js` and declare
component usage. Five component **candidates** were identified:

| Candidate | Screens | Notes |
|-----------|---------|-------|
| `c_tab_shell` | 01–09 (all) | TabBar + CenterAlignedTopAppBar shell |
| `c_client_name_field` | 01, 02, 03, 07 | TextField with client name validation states |
| `c_client_confirmed_header` | 02, 05 | Client name + status row |
| `c_pairing_required_state` | 03, 07 | Missing key / new client state panel |
| `c_pairing_qr_overlay` | 04 | Fullscreen pairing QR |

Per skill design, promotion to `_scribble_components/` requires user approval via Phase 4
(user feedback cycle). Since the task is awaiting approval (Phase 3), no promotion has
happened — and that is CORRECT behavior.

### What is NOT in the library yet
The existing library has: `c_app_bar`, `c_filled_button`, `c_mood_entry_card`,
`c_navigation_bar`, `c_plan_list_item` (all from April 19-20). None of the 5 candidates
above were added during this task run.

### Gap: promotion threshold is undefined
The skill doesn't specify a candidate confidence threshold (e.g., "appears in ≥3 screens →
auto-promote without extra approval cycle"). `c_tab_shell` appears in ALL 9 screens, which
is high confidence. Requiring a full feedback round-trip to promote it adds unnecessary delay.

**Actionable proposal**: Add to skill: "After Phase 2 auto-review, scan component-candidates.
If a candidate appears in ≥3 screens AND its structure is stable (identical usage site
pattern), auto-promote it to `_scribble_components/` with a `status: provisional` flag.
Include the promotion in the Phase 3 summary for the developer to confirm or rename."

---

## Summary: Skill Improvement Proposals

| Dimension | Proposal | Priority |
|-----------|----------|----------|
| Domain names | Phase 1 agent: reference domain class names in component mapping when classes exist | Medium |
| Flow coverage | Phase 2 auto-review: check exception paths + Domain Concepts constraints | High |
| Flow coverage | flow_positions: require exception_id for non-happy-path screens | Medium |
| Resolution | Phase 1: detect stakeholder role, optionally add tablet viewport | Low |
| Components | Auto-promote candidates appearing ≥3 screens to `provisional` status after Phase 2 | Medium |
| Domain model | Separate task: fix letter labels in TransferDetectionZone comments (c↔e swap) | Low |

### On iteration count

The question was raised whether 3 iterations instead of 2 would help. The analysis shows
that most v1 gaps were caught by the Phase 2 auto-review (7 fixes). The main uncaught issue
(fast-mode consent prompt, exception flow mapping) was NOT catchable by extra iterations
of the current rubric — it requires rubric changes (flow exception coverage check). A third
iteration without rubric changes would find the same remaining gaps, not new ones.

**Recommendation**: Fix the Phase 2 rubric first. A third iteration could then serve as a
"deep flow alignment" pass with the enhanced checklist.

---

---

## e) Flow Scope Mismatch — Multi-Requirement Flows

**Verdict: STRUCTURAL GAP in skill design**

A user flow (e.g., FLOW-002) spans multiple requirements. REQ-FUNC-007-01 covers steps
[1, 2, 3, 4, 5, 8]; REQ-FUNC-007-02 covers steps 6–7 (client-side receive). The skill
reads the full flow for ordering context but gives the Phase 1 agent no instruction to
filter screens to only the steps that belong to the current requirement.

### The fix is already in the data

The requirement YAML already has the filter:
```yaml
user_needs:
  implements_flows:
    - id: FLOW-002
      steps: [1, 2, 3, 4, 5, 8]   # ← only these steps belong to this requirement
```

Phase 1 should receive the flow in two roles:
1. **Full context** (read-only): flow.md gives preconditions, what comes before/after,
   and Domain Concepts constraints — available to the agent for understanding.
2. **Scoped generation** (write-only): only generate screens for the `steps[]` listed in
   the requirement YAML. Steps outside this list are covered by other requirements.

Exception paths should be handled similarly — the requirement's ACs determine which
exceptions are in scope; the flow's exception descriptions provide behavioral detail.

**Actionable proposal**: Phase 1 prompt change — "The requirement declares steps
`[1, 2, 3, 4, 5, 8]` from FLOW-002. Read the full flow for context and behavioral
constraints, but generate screens only for those steps and their directly associated
exception paths (as documented in the requirement's ACs/sections). Do not generate
screens for steps belonging to other requirements."

---

## f) Impossible System States

**Verdict: CRITICAL QUALITY GAP — not caught by any current check**

The scribbles may show UI states that the system cannot actually render because the
required information is not available on that app side. Example: the therapist's app
shows a unidirectional QR channel (documented in FLOW-002 Step 5 and the requirement's
Section 4). The therapist side CANNOT know the client's reception state — it can only
track elapsed time against a calculated minimum duration.

If any screen shows a "client received X%" indicator or similar bidirectional state,
that is an impossible state. The auto-review does not catch this because it checks
AC coverage, not information-model consistency.

### Root cause

The Phase 1 agent does not extract "what information does this app side have?" from the
flow or requirement before designing screens. The FLOW-002 Domain Concepts section
explicitly states:
> "the therapist's app cannot confirm the client's reception state"

But the skill reads the flow for step ORDER only, not for technical constraints.

### Proposed fix: information model check in Phase 1 and Phase 2

**Phase 1 addition**: Before generating screens, agent MUST read:
- The flow's Domain Concepts section (technical constraints, channel model)
- Any requirement section that describes system behavior (SEC-10 here)

Then derive an **information constraints list**: "On this app side, the following
information is NOT available: [...]." Each generated screen state must be consistent
with this list.

**Phase 2 addition**: Auto-review checklist item — "For every non-trivial state panel
(non-error, non-empty states), is the data required to render that state available on
this app side given the channel model documented in the flow or requirement?"

This check cannot be fully automated — it requires genuine reasoning. But making it
an explicit rubric item forces the auto-review agent to reason about it.

---

## g) Implementation Notes Co-Located with Flows

**Verdict: NOT READ — future-proofing needed**

The flow folder currently contains only `flow.md` and `requirements_matrix.md`. No
`implementation_notes.md` exists yet. The skill has no mechanism to read such a file.

When implementation notes are introduced (containing details too granular for the flow
itself — e.g., "the therapist side is unidirectional, do not show client reception
state"), the skill will silently ignore them.

### Proposed fix

Add to Phase 1 and Phase 2 prompts:
> "Check the flow folder (`requirements_user_needs/user_flows/<flow_id>/`) for a file
> named `implementation_notes.md`. If present, read it before generating screens and
> treat its constraints as authoritative technical context alongside the flow itself."

This needs to be added before the first such file is created, otherwise there is no
guarantee the skill will pick it up automatically.

---

## Summary: Skill Improvement Proposals (updated)

| Dimension | Proposal | Priority |
|-----------|----------|----------|
| Flow scope | Phase 1: scope screen generation to `steps[]` from requirement YAML; use full flow as context only | High |
| Impossible states | Phase 1: derive information constraints list from Domain Concepts before designing screens | High |
| Impossible states | Phase 2: add rubric item — information-model consistency per state panel | High |
| Flow coverage | Phase 2 auto-review: check exception paths + Domain Concepts constraints | High |
| Impl notes | Phase 1 + Phase 2: check flow folder for `implementation_notes.md` and read if present | Medium |
| Flow coverage | flow_positions: require exception_id for non-happy-path screens | Medium |
| Domain names | Phase 1 agent: reference domain class names in component mapping when classes exist | Medium |
| Components | Auto-promote candidates appearing ≥3 screens to `provisional` status after Phase 2 | Medium |
| Resolution | Phase 1: detect stakeholder role, optionally add tablet viewport | Low |
| Domain model | Separate task: fix letter labels in TransferDetectionZone comments (c↔e swap) | Low |

### On iteration count

The question was raised whether 3 iterations instead of 2 would help. The analysis shows
that most v1 gaps were caught by the Phase 2 auto-review (7 fixes). The main uncaught
issues (flow scope, impossible states, exception mapping) are NOT catchable by extra
iterations of the current rubric — they require rubric changes. A third iteration without
rubric changes would find the same remaining gaps, not new ones.

**Recommendation**: Fix the Phase 1 and Phase 2 rubric first (items marked High above).
A third iteration could then serve as a "deep flow alignment" pass with the enhanced
checklist. Do not add a third iteration pass without first fixing the rubric.

---

## Next Steps

1. Create a follow-up impl task to update the `ui-create-scribble` skill with the
   proposals above (priority: flow scope + impossible states + impl notes).
2. Create a separate (small) task to fix the stale letter labels in
   `transfer_detection_zone.dart` comments.
3. Answer the pending question for TASK-FUNC-007-01-05 (approve or request changes to v2).
