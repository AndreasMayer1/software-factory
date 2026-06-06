## Summary for User

- QR code generation (REQ-FUNC-007-01 SEC-04) and QR scanning/reception (REQ-FUNC-007-02 AC-03, AC-08) are correctly scoped to 0.0.1
- Gap: "Basic plan serialization/deserialization" has no formal tracked feature requirement in this epic — it's only implicit in the transfer pipeline description
- Draft for a new feature REQ-FUNC-007-03 (transport encoding: JSON → compress → chunks → QR) is included below

### Open Questions

1. **Serialization ownership in data transfer epic**: Should serialization be formalized as a new feature requirement REQ-FUNC-007-03 (Option B), or added as ACs to existing REQ-FUNC-007-01 / REQ-FUNC-007-02 (Option A)? See draft content below.
=> Option B. Actually there will be a feature to transfer data the other way round: From client to therapist. For that the answers to the quesitonaire plan will be send, potentially including the questions, that means the plan. For that we also need serialization and maybe this new requirement can be extended then. 

---

# Epic REQ-FUNC-007 Findings

## Feature Coverage

| 0.0.1 Scope Item | Feature Req | Status |
|---|---|---|
| QR code generation (therapist side) | REQ-FUNC-007-01 SEC-04 "Transfer Flow - Local (Data Beam)" target_release: "0.0.1" | OK |
| QR code scanning and plan reception (client side) | REQ-FUNC-007-02 AC-03 (progress indicator) + AC-08 (decline = discard) target_release: "0.0.1" | OK |
| Basic plan serialization/deserialization | No dedicated feature requirement exists | MISSING |
| Role selection (Client / Therapist) | Out of scope for REQ-FUNC-007 — belongs to onboarding epic | OUT OF SCOPE |

## Gaps

### Gap 1: "Basic plan serialization/deserialization" — no feature requirement

**What exists**: The epic (REQ-FUNC-007) mentions plan serialization in two places:
1. Architecture section: "Plan (JSON) → Compress → Encrypt → Split into chunks → QR/File" pipeline
2. Unit testing requirements: "Plan serialization for transfer" and "QR chunk generation"

**What is missing**: There is no feature requirement file (and no `feat_plan_serialization/` folder) that defines the serialization/deserialization contract as a trackable requirement with acceptance criteria tagged `target_release: "0.0.1"`.

The serialization concern is embedded in both sending (REQ-FUNC-007-01) and receiving (REQ-FUNC-007-02) feature descriptions but only as implementation detail, not as a standalone feature requirement with formal ACs.

**Why this matters for 0.0.1**: The Data Beam QR loop (REQ-FUNC-007-01 SEC-04) and the client-side reception progress (REQ-FUNC-007-02 AC-03) both depend on a stable plan serialization format. Without a formal requirement, there is no trackable item confirming the format is defined, no target_release assignment for the serialization work itself, and no explicit acceptance criteria to verify against.

**Recommended approach**: Two options:

Option A — Add ACs to existing features (lightweight):
- Add AC to REQ-FUNC-007-01 for "Plan data can be serialized to a chunk sequence suitable for QR encoding (plan JSON → compress → encrypt → chunks)" with `target_release: "0.0.1"`
- Add AC to REQ-FUNC-007-02 for "Client can reassemble a chunk sequence and deserialize back to a valid plan structure" with `target_release: "0.0.1"`

Option B — Create a new feature requirement (preferred if serialization is shared infrastructure):

Draft content for `feat_plan_serialization/requirements.md`:

```yaml
---
id: REQ-FUNC-007-03
parent: REQ-FUNC-007
status: draft
effort: S
target_release: "0.0.1"
stakeholder: therapist, client
created: 2026-03-06
depends_on: []
blocks:
  - REQ-FUNC-007-01  # therapist sending depends on serialization
  - REQ-FUNC-007-02  # client receiving depends on deserialization
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "A plan can be serialized to a byte array: plan JSON → compress (zlib/gzip) → encrypt placeholder (no-op for 0.0.1, encryption deferred to 0.0.2) → split into fixed-size chunks"
      target_release: "0.0.1"
    - id: AC-02
      text: "A chunk sequence can be deserialized back to a valid plan domain object: reassemble chunks → decrypt placeholder → decompress → parse plan JSON"
      target_release: "0.0.1"
    - id: AC-03
      text: "Serialization is deterministic: serializing the same plan twice produces the same chunk sequence (excluding nonce, which is 0.0.2 scope)"
      target_release: "0.0.1"
    - id: AC-04
      text: "Chunk header encodes: total chunk count, chunk index, and sequence ID — sufficient for the client progress indicator (REQ-FUNC-007-02 AC-03)"
      target_release: "0.0.1"
---
```

**Feature description draft**:

```markdown
# Feature: Plan Serialization / Deserialization

## Overview

This feature defines the data pipeline that converts a plan domain object into a
QR-transmittable chunk sequence and back. It is shared infrastructure used by both
the therapist sending side (REQ-FUNC-007-01) and the client receiving side (REQ-FUNC-007-02).

## 0.0.1 Scope

For the 0.0.1 alpha proof-of-concept:
- Encryption is a no-op (plain or trivially encoded). Real AES-256-GCM encryption is deferred to 0.0.2.
- Compression is included (validates chunk count reduction).
- Chunk header format is defined and stable.

## Pipeline

Sending: plan domain object → JSON → compress → [encrypt: no-op] → split into N chunks
Receiving: N chunks → reassemble → [decrypt: no-op] → decompress → JSON → plan domain object

## Chunk Header Format (0.0.1)

Each chunk carries:
- Sequence ID (random 4 bytes per transfer session, to distinguish concurrent sessions)
- Total chunk count (integer)
- Chunk index (0-based integer)
- Payload bytes

## Notes

- Encryption slot in the pipeline is reserved but inactive in 0.0.1 to keep scope small.
- The same serialization format is used bidirectionally (therapist → client and future client → therapist).
- Format must be versioned (1-byte version prefix) to allow 0.0.2 to add encryption without breaking the decompressor contract.
```

**Recommendation**: Option A is sufficient if the team wants to avoid creating a new requirement ID. Option B is better long-term because serialization is shared infrastructure that will grow in 0.0.2 (encryption is added) and beyond.

---

### Gap 2: "Role selection (Client / Therapist)" — out of scope for REQ-FUNC-007

**Finding**: Role selection is not part of the data transfer epic. It belongs to the onboarding epic. A separate check of the onboarding epic(s) is required to confirm 0.0.1 coverage for this scope item.

**Action required**: The epic coverage check for the onboarding epic should verify whether role selection has a trackable item with `target_release: "0.0.1"`. This is outside the scope of the REQ-FUNC-007 analysis.

---

## Notes

- REQ-FUNC-007-01 SEC-04 (`target_release: "0.0.1"`) covers QR code generation/display (therapist side Data Beam). All other sections of 007-01 (dialog structure, client selection, pairing flow, remote transfer, self-test) are `0.1.0` — correctly deferred.
- REQ-FUNC-007-02 AC-03 and AC-08 (`target_release: "0.0.1"`) cover minimal client reception: progress indicator and decline behavior. All pairing, file import, receipt confirmation details, and update detection are `0.0.2` or later — correctly deferred.
- The epic-level AC-07 ("QR Data Beam supports adjustable animation speed", `target_release: "0.0.1"`) is covered by 007-01 SEC-04.
- The top-level `target_release: "0.0.1"` on the epic is correct: it is the earliest among all trackable items.
- The serialization gap is the only structural gap. It is not a blocker for the 0.0.1 PoC (the work will happen regardless) but it is a tracking gap: there is no formal AC to check off when the format is stable.
