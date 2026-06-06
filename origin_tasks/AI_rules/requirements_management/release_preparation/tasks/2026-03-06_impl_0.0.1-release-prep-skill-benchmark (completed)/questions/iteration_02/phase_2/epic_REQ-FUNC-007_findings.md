## Summary for User

- REQ-FUNC-007-03 (Plan Serialization) now exists and is properly structured: it has 5 ACs tagged `target_release: 0.0.1` (AC-01 through AC-05), covering the full serialize → compress → encrypt-placeholder → chunk pipeline, with AC-06 correctly deferred to `0.1.0`. The iteration_01 gap is closed.
- All three phase_4 blocking questions from iteration_01 were answered by the user in the final_coverage_check.md file (Q1 => (b) split into 0.0.1/0.0.2 subsections; Q3 => (b) omit client name field, show Data Beam unconditionally). REQ-FUNC-007-03 directly resolves Q1 by defining the no-op encryption slot and the schema version byte as explicit extension points — the implementer confusion risk is eliminated.
- The epic structure is now complete for 0.0.1: all three scope items that require implementation (QR generation, QR scanning/reception, serialization) map to a feature requirement with 0.0.1-tagged ACs. REQ-FUNC-007-02 coverage remains low at 14% (AC-03 and AC-08 only), which was flagged in iteration_01 as acceptable only if the in-progress explore task produces a follow-up impl task.

### Open Questions

1. **[REQ-FUNC-007-02 coverage] Is TASK-FUNC-007-02 (explore) expected to produce a follow-up impl task before 0.0.1 ships?** REQ-FUNC-007-02 still has only AC-03 and AC-08 covered. The 12 remaining ACs (pairing UI, receipt confirmation, full scanner flow) are not assigned to any impl task. If 0.0.1 requires a working end-to-end client receive flow, additional task creation is needed now.
=> 0.0.1 is only a proof of concept, I'd try to implement what the only impl task specifies and later check if it was enough.

---

# Epic REQ-FUNC-007 Findings (Iteration 02)

## Feature Coverage

| 0.0.1 Scope Item | Feature Req | Status |
|---|---|---|
| QR code generation (therapist side) | REQ-FUNC-007-01 `feat_therapist_transfer_ui` | Covered — SEC-04 is `target_release: 0.0.1`; AC-01, AC-02, AC-05, AC-12 are `0.0.1`. Q1 (encryption confusion) resolved by REQ-FUNC-007-03 no-op placeholder design. Q3 (client name field) resolved: omit field, show Data Beam unconditionally. |
| QR code scanning and plan reception (client side) | REQ-FUNC-007-02 `feat_plan_receiving` | Partially covered — AC-03 (progress indicator) and AC-08 (decline) are `0.0.1`. 12 of 14 ACs remain without impl task coverage. |
| Basic plan serialization/deserialization | REQ-FUNC-007-03 `feat_plan_serialization` | Covered (new, created 2026-03-07) — AC-01 through AC-05 are `0.0.1`; AC-06 (bidirectional) deferred to `0.1.0`. Pipeline design matches RELEASES.md exclusion of encryption: encrypt step is a documented no-op slot. |
| Role selection (Client / Therapist) | (already implemented — no feature req needed) | Accepted, no gap. |

## Gaps

### 1. REQ-FUNC-007-02 impl task coverage (unchanged from iteration 01)

AC-03 and AC-08 are the only ACs of REQ-FUNC-007-02 with task coverage. The following ACs have no assigned impl task for 0.0.1:

- AC-01 (pairing QR scan), AC-02 (verbal pairing entry), AC-04 (file picker import), AC-05 (deep link import), AC-06 (receipt confirmation screen), AC-07 (accept plan), AC-09 (inline notification time mapping), AC-10 (update detection), AC-11 (preserve entries on update), AC-12 (multi-therapist), AC-13 (plan attribution), AC-14 (contact deletion)

For a PoC QR scanning demonstration, AC-03 (progress indicator) is the critical deliverable. The receipt confirmation screen (AC-06, AC-07, AC-08) is also needed for an end-to-end flow. Whether the remaining ACs are required for 0.0.1 depends on the scope defined by TASK-FUNC-007-02 (explore, in_progress).

### 2. REQ-FUNC-007-03 AC-06 (no impl task)

AC-06 ("same pipeline used bidirectionally") is `target_release: 0.1.0` and has no 0.0.1 task. This is intentional — not a gap for 0.0.1.

### 3. Epic-level AC-07 (QR Data Beam adjustable speed) — verify task exists

REQ-FUNC-007 parent epic AC-07 ("QR Data Beam supports adjustable animation speed") is `target_release: 0.0.1`. This maps to REQ-FUNC-007-01 AC-05 ("Data Beam animation speed adjustable via slider", also `0.0.1`). TASK-FUNC-007-01-01 covers this. No gap — but worth confirming the task scope explicitly includes the slider.

## Notes

- **REQ-FUNC-007-03 structure assessment**: The new feature requirement is well-formed. It correctly declares itself as shared infrastructure blocking both -01 and -02, uses a `depends_on` reference to REQ-NFUNC-001 for schema versioning, and its AC set is minimal and testable. The no-op encryption placeholder design (with schema version byte `0x01` and zero-filled nonce) directly matches the parent epic file format spec and RELEASES.md 0.0.1 scope boundary ("Encryption of any kind" excluded).
- **SEC-04 encryption conflict (iteration_01 Q1) — resolved**: The user chose option (b): split into subsections. REQ-FUNC-007-03 implements this split at the requirement level — 0.0.1 ACs describe the no-op slot, 0.0.2 scope is documented in the "Future Scope" section. The implementer confusion risk identified in iteration_01 is eliminated.
- **Client name field (iteration_01 Q3) — resolved**: User chose option (b): omit the field, show Data Beam unconditionally. This simplifies the 0.0.1 implementation of TASK-FUNC-007-01-01. The client name/key-lookup logic is entirely deferred to 0.0.2.
- **Epic parent ACs vs. feature ACs**: REQ-FUNC-007 parent has 8 ACs. Of these, only AC-07 ("adjustable animation speed") is `0.0.1`. AC-01, AC-02, AC-05, AC-06 are `0.0.2`. AC-03, AC-04, AC-08 are `0.1.0`. This is consistent with feature-level AC tagging.
