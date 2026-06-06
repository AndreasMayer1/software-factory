## Summary for User

- Only SEC-07 "Export a Plan for a Client" is tagged `target_release: "0.0.1"` in REQ-FUNC-014 — the rest is 0.2.0 (correctly scoped)
- Gap: SEC-07 has no feature requirements file and no formal AC IDs — tasks cannot be assigned against it
- Draft for a new feature requirement (domain serialization: plan → versioned JSON, round-trip) is included below

### Open Questions

1. **Serialization ownership in plan management epic**: Should a feature requirement be created under `epic_plan_management/` for the domain serialization layer (separate from the transport/QR chunking layer owned by REQ-FUNC-007)? Or should all serialization live under REQ-FUNC-007?
=> Answered for REQ-FUNC-007.

---

# Epic REQ-FUNC-014 Findings

## Feature Coverage

| 0.0.1 Scope Item | Feature Req | Status |
|---|---|---|
| Basic plan serialization/deserialization (therapist side — SEC-07 "Export a Plan for a Client") | No dedicated feature requirements file under `epic_plan_management/` | Missing |
| QR code generation (therapist side — SEC-07) | No dedicated feature requirements file | Missing |

Only one section of REQ-FUNC-014 carries `target_release: "0.0.1"`: **SEC-07 "Export a Plan for a Client"** (line 78 of frontmatter, body at line 645). All other sections (SEC-01 through SEC-06, SEC-08, SEC-09) are tagged `"0.2.0"`.

The epic's top-level `target_release: "0.0.1"` is correctly derived from SEC-07 being the earliest trackable item — this matches the release assignment rules in RELEASES.md.

There is no feature-level requirements file (`feat_*/requirements.md`) for the export/serialization functionality. The `epic_plan_management/` folder contains only:
- `requirements.md` (the epic itself)
- `plan_preview/requirements.md` (for 0.2.0 plan preview)
- Task folders (completed exploration tasks)

## Gaps

### Gap 1: No feature requirements file for plan serialization/export

**What is missing**: A `feat_plan_serialization/requirements.md` (or equivalent) under `requirements_tasks/functional/therapist/epic_plan_management/` or `requirements_tasks/functional/shared/` that specifies the 0.0.1-scoped serialization behavior as a standalone feature requirement.

SEC-07 in the epic document covers the intent at a sketch level but is not structured as a proper feature requirement. It has informal acceptance criteria (checkbox list without AC IDs or `target_release` fields) and a "Data Transfer Security (TBD)" note — indicating it is a placeholder, not a complete specification.

**Draft content for `feat_plan_serialization/requirements.md`**:

```markdown
---
id: REQ-FUNC-014-S07
parent: REQ-FUNC-014
status: defined
effort: M
target_release: "0.0.1"
stakeholder: therapist, client
depends_on:
  - REQ-NFUNC-001  # Architecture (versioned plan schema)
blocks:
  - REQ-FUNC-007   # Data Transfer (needs serialized plan as input)
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "A plan object and all its nested contents (questionnaires, questions) can be serialized to a versioned JSON format."
      target_release: "0.0.1"
    - id: AC-02
      text: "The serialized JSON can be deserialized back to the original plan object with no data loss."
      target_release: "0.0.1"
    - id: AC-03
      text: "The serialized format includes a schema version field to enable future forward/backward compatibility."
      target_release: "0.0.1"
    - id: AC-04
      text: "The therapist can trigger QR code generation from within the plan editor (Export button in PlanTemplateDetailContent)."
      target_release: "0.0.1"
    - id: AC-05
      text: "The generated QR code encodes the complete serialized plan data and is displayed in an export screen/dialog."
      target_release: "0.0.1"
    - id: AC-06
      text: "The client app can scan the QR code and parse the plan data successfully (round-trip validation)."
      target_release: "0.0.1"
---

# Feature: Plan Serialization & QR Export (0.0.1 Scope)

This feature covers the minimum serialization/deserialization capability needed
for the 0.0.1 Alpha Data Transfer proof-of-concept. Security (encryption) is
explicitly out of scope for 0.0.1 — the transfer is unencrypted as per RELEASES.md.

## Scope Boundary

**In scope (0.0.1)**:
- Plan → JSON serialization (versioned schema)
- JSON → Plan deserialization
- QR code generation from serialized plan
- Export trigger UI (button in plan editor)

**Out of scope (deferred)**:
- Encryption of serialized data (0.0.2)
- Animated multi-chunk QR Data Beam (0.0.1 may use single-QR if plan is small
  enough; chunked animation per REQ-FUNC-007 AC-07 is 0.0.1 but owned by the
  data transfer epic)
- Client name entry, pairing, key management (0.0.2)

## Relationship to REQ-FUNC-007

The `feat_therapist_transfer_ui` (REQ-FUNC-007) owns the QR animation/Data Beam
UX (AC-07, target_release: "0.0.1"). This feature owns the upstream serialization
that produces the payload fed into that animation.
```

## Scope Alignment Note

The assignment of REQ-FUNC-014 to 0.0.1 is **technically correct but misleading** if read at the epic level. The epic as a whole is a 0.2.0 deliverable (plan creation, editing, duplication, client copy architecture). Only SEC-07 "Export a Plan for a Client" is needed for 0.0.1, and specifically only the serialization/QR-generation part of it — not the full transfer dialog or encryption.

The RELEASES.md 0.2.0 entry explicitly lists `"Full therapist plan management: create, edit, duplicate plans (REQ-FUNC-014)"` — confirming that 0.2.0 is the primary release for this epic. The 0.0.1 assignment is narrowly scoped to SEC-07 only.

**Recommendation**: The scope is correctly modeled in the trackable_items (only SEC-07 is tagged 0.0.1). No change is needed to the epic's frontmatter. What is missing is a dedicated feature requirements file for the serialization work so that 0.0.1 tasks can be scoped against it cleanly.

## Notes

- File examined: `requirements_tasks/functional/therapist/epic_plan_management/requirements.md`
- Only trackable item tagged 0.0.1: SEC-07 (line 78 frontmatter, body at line 645)
- SEC-07's ACs are informal (no AC IDs, no per-AC target_release) — they need to be formalized if tasks are to be assigned against them
- The `feat_plan_receiving/requirements.md` (client side, under `epic_data_transfer`) covers the client-side scanning/import for 0.0.1 — that epic (REQ-FUNC-007) is the correct home for the QR animation UX; REQ-FUNC-014 SEC-07 owns only the serialization/export trigger
- No feature file currently exists under `epic_plan_management/` for serialization
- `plan_preview/requirements.md` exists but is for the plan preview feature (0.2.0 scope)
