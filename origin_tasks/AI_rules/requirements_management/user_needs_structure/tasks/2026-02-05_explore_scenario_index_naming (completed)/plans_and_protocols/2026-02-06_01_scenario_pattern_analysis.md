# Scenario Pattern Analysis

**Task**: TASK-PROC-010-12
**Date**: 2026-02-06
**Agent**: Opus (direct content creation)

## 1. Inventory of Existing Scenarios

| # | ID | Folder Name | Persona | Role | Outcome |
|---|-----|-------------|---------|------|---------|
| 1 | SCEN-001-01 | `prepare_protocol_for_client` | Dr. Sarah | therapist | success (routine) |
| 2 | SCEN-001-02 | `review_protocol_with_client` | Dr. Sarah | therapist | success (with data quality concern) |
| 3 | SCEN-002-01 | `brain_dump_at_night` | Max | client | failure (analog method fails) |
| 4 | SCEN-002-02 | `forgotten_protocol_transfer` | Max | client | failure (object forgotten) |
| 5 | SCEN-002-03 | `prepare_for_therapy_session` | Max | client | partial (preparation constrained by paper) |
| 6 | SCEN-010-01 | `successful_protocol_handover` | Sophie | client | success (fragile, ADHD-dependent) |

## 2. Deep Pattern Analysis

### What Are These Scenarios Actually About?

Looking beyond folder names to the **underlying goals** each scenario serves:

#### Pattern A: "Create/Prepare Protocol" (Therapist Side)
**Core goal**: Therapist creates or customizes a structured tracking instrument for a specific client.

- **SCEN-001-01** (Dr. Sarah): Prepares a paper anxiety protocol, writes margin notes, customizes for Anna's social anxiety triggers.
- **Key activity**: Authoring, customizing, handwriting
- **Applicable roles**: therapist (primary), possibly self_user (creating own tracking structure)

#### Pattern B: "Capture Data Spontaneously" (Client Side)
**Core goal**: Client records thoughts/feelings/data in-the-moment, driven by internal urgency rather than scheduled compliance.

- **SCEN-002-01** (Max): Brain dump at 2 AM, trying to offload circular thoughts to enable sleep.
- **Key activity**: Urgent, unstructured recording under physical/environmental constraints
- **Applicable roles**: client (primary), self_user (identical need without therapist context)

#### Pattern C: "Prepare for Therapy Session" (Client Side)
**Core goal**: Client reviews their own recorded data before a session to arrive prepared, identify talking points, and feel competent.

- **SCEN-002-03** (Max): Sunday evening review of paper protocol, struggling with context loss, illegibility, and shame about gaps.
- **Key activity**: Self-review, pattern recognition, emotional preparation
- **Applicable roles**: client (primary)

#### Pattern D: "Transfer Data to Therapist" (Client → Therapist)
**Core goal**: Client brings/delivers their tracked data to the therapist at session time.

This pattern has **two distinct outcomes** already documented:
- **SCEN-002-02** (Max): **Failure case** — forgot protocol at home, reconstructs from memory, session time wasted.
- **SCEN-010-01** (Sophie): **Success case** — brings filled protocol, experiences competence, data enables insight.
- **Key activity**: Physical transport of data artifact, handover ritual
- **Applicable roles**: client (primary)

#### Pattern E: "Review Data Collaboratively" (Therapist + Client)
**Core goal**: Therapist and client analyze tracked data together during a session to identify patterns and derive therapeutic insights.

- **SCEN-001-02** (Dr. Sarah): Reviews Anna's anxiety protocol, identifies anticipatory anxiety pattern, discusses gaps therapeutically.
- **Key activity**: Joint analysis, pattern recognition, therapeutic questioning
- **Applicable roles**: therapist (primary, drives the analysis), client (participates)

### Emergent Structure: The Therapy Data Lifecycle

These five patterns form a **lifecycle** — a chain of scenarios that represents the complete journey of therapy tracking data:

```
[A] Create Protocol  →  [B] Capture Data  →  [C] Pre-Session Review  →  [D] Transfer to Therapist  →  [E] Collaborative Review
    (therapist)           (client)              (client)                   (client → therapist)          (therapist + client)
```

This lifecycle is the fundamental unit. Every persona who participates in therapy tracking will touch **some subset** of these stages. The lifecycle also reveals a sixth pattern not yet documented:

#### Pattern F: "Routine/Scheduled Data Entry" (Client Side)
**Core goal**: Client fills out the protocol as part of a daily/regular routine (not spontaneous like Pattern B).

- **Not yet a standalone scenario** — but referenced inside SCEN-002-03 (Max's entries are the product of routine tracking) and SCEN-010-01 (Sophie filled out her protocol across the week).
- **Key activity**: Habitual, low-urgency recording at regular intervals
- **Applicable roles**: client (primary), self_user (identical)

This is distinct from Pattern B ("Capture Spontaneously") because the trigger is **schedule/habit** rather than **internal urgency**. The constraints are different (less time pressure, but higher risk of abandonment/boredom).

## 3. Pattern-to-Scenario Mapping

| Pattern | Canonical Name | Existing Scenarios | Missing Coverage |
|---------|---------------|-------------------|------------------|
| A | `prepare_protocol_for_client` | SCEN-001-01 (Dr. Sarah) | self_user creating own structure? |
| B | `capture_data_spontaneously` | SCEN-002-01 (Max, night) | other contexts (commute, work break), other personas |
| C | `prepare_for_therapy_session` | SCEN-002-03 (Max) | therapist persona (preparing to review), Sophie version |
| D | `transfer_data_to_therapist` | SCEN-002-02 (Max, failure), SCEN-010-01 (Sophie, success) | other failure modes? |
| E | `review_data_collaboratively` | SCEN-001-02 (Dr. Sarah) | client perspective of same event |
| F | `routine_data_entry` | *(not yet standalone)* | all client/self_user personas |

## 4. Naming Inconsistencies Found

| Current Folder Name | Pattern | Issue |
|---------------------|---------|-------|
| `brain_dump_at_night` | B (Capture Spontaneously) | Name encodes **context** (night) rather than **goal** (capture). What about a daytime brain dump? |
| `forgotten_protocol_transfer` | D (Transfer) | Name encodes **outcome** (forgotten = failure). The pattern IS transfer — "forgotten" is a variant. |
| `successful_protocol_handover` | D (Transfer) | Same pattern as above, but name encodes **success**. Also uses "handover" while the other uses "transfer" — inconsistent synonym. |
| `prepare_protocol_for_client` | A (Create Protocol) | Good — clear action + object + recipient |
| `review_protocol_with_client` | E (Review Collaboratively) | Good — clear action + object + collaborator |
| `prepare_for_therapy_session` | C (Pre-Session Prep) | Good — clear action + purpose |

**Key insight**: The current names mix three different naming strategies:
1. **Goal-based**: `prepare_protocol_for_client`, `prepare_for_therapy_session` (good)
2. **Context-based**: `brain_dump_at_night` (encodes when, not what)
3. **Outcome-based**: `forgotten_protocol_transfer`, `successful_protocol_handover` (encodes success/failure)

A consistent convention must choose ONE primary axis and handle the others systematically.

## 5. Outcome Variants: How Success/Failure Should Be Handled

The most critical naming decision is **how to handle success/failure variants** of the same pattern.

### Option 1: Outcome in the Folder Name (Current Approach)
```
forgotten_protocol_transfer/    ← failure
successful_protocol_handover/   ← success
```
**Pro**: Immediately visible which variant it is.
**Con**: Names diverge for the same pattern. Hard to group. Uses different words ("transfer" vs "handover").

### Option 2: Outcome as Suffix
```
transfer_data_to_therapist_failure/
transfer_data_to_therapist_success/
```
**Pro**: Pattern name is stable; outcome is a modifier. Easy to find both variants.
**Con**: Long names. "Success" and "failure" are binary — what about partial outcomes?

### Option 3: Outcome in Metadata Only (Recommended)
```
transfer_data_to_therapist/     ← folder name is the PATTERN
  scenario.md                   ← YAML: outcome: failure, variant: forgotten_at_home
```
**Problem**: We have ONE folder per scenario per persona. Two scenarios of the same pattern under the same persona would collide.

### Option 4: Pattern Name + Distinguishing Context (Recommended)
```
transfer_data_to_therapist__forgotten/      ← Max's failure scenario
transfer_data_to_therapist__successful/     ← Sophie's success scenario (different persona, no collision)
```
But what if the SAME persona has both success and failure? Then we need the distinguisher.

### Recommended Approach: Canonical Pattern + Persona-Specific Qualifier

**Rule**: The folder name is `[canonical_pattern_name]` when there is only one scenario of that pattern for this persona. When a persona has **multiple scenarios of the same pattern** (e.g., success AND failure), append a double-underscore qualifier: `[canonical_pattern_name]__[qualifier]`.

For the existing scenarios, since `transfer_data_to_therapist` exists under both Max (failure) AND Sophie (success), there's no collision — they're under different persona folders. The qualifier is needed only when ONE persona has MULTIPLE scenarios of the same pattern.

However, this changes the current folder names, which is out of scope. The INDEX should track the canonical name, and the actual folder names can be reconciled later.

## 6. Role Applicability Matrix

Which patterns apply to which roles?

| Pattern | Therapist | Client | Self-User | Notes |
|---------|-----------|--------|-----------|-------|
| A: Create/Prepare Protocol | **Primary** | - | Possible (self-tracking) | Therapist creates FOR client |
| B: Capture Data Spontaneously | - | **Primary** | **Primary** | Identical need, different context |
| C: Prepare for Therapy Session | Supporting | **Primary** | - | Self-user has no therapist |
| D: Transfer Data to Therapist | Receiving | **Primary** | - | Self-user has no therapist |
| E: Review Data Collaboratively | **Primary** (drives) | **Primary** (participates) | - | Two-person scenario |
| F: Routine Data Entry | - | **Primary** | **Primary** | Scheduled/habitual tracking |

**Self-user gap**: Self-users have no therapist, so patterns C, D, E don't apply. But they likely need:
- **G: Self-Review / Reflect on Patterns** — reviewing own data alone (no therapist)
- **H: Share Data with External Party** — optionally sharing with a friend, coach, or doctor (non-therapy context)

These are **predicted patterns** that will emerge when self-user scenarios are written.

## 7. Summary of Findings

1. **Five clear patterns exist** in the current 6 scenarios, forming a **Therapy Data Lifecycle**: Create → Capture → Prepare → Transfer → Review.
2. **One missing pattern** (Routine Data Entry) is implicit in multiple scenarios but not standalone.
3. **Two future patterns** are predicted for self-user personas (Self-Review, Share Externally).
4. **Naming is inconsistent** — current names mix goal-based, context-based, and outcome-based approaches.
5. **Success/failure variants** are the hardest naming challenge. Recommendation: use canonical pattern name as primary, with qualifier only when the same persona has multiple variants.
6. **Role applicability varies** — not every pattern applies to every role, which the index must capture.
