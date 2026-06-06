## Summary for User

- All three functional scope items for 0.0.1 now map to at least one requirement assigned to the release: QR generation maps to REQ-FUNC-007-01, QR scanning/reception maps to REQ-FUNC-007-02, and plan serialization maps to REQ-FUNC-007-03.
- REQ-FUNC-007-03 (Feat Plan Serialization) is confirmed present in STATUS_NEXT_RELEASE.md with 83% task coverage and an active implementation task (TASK-FUNC-007-03-01), resolving the gap identified after iteration 01.
- The id_registry.md (generated 2026-03-06) does not yet list REQ-FUNC-007-03 as a named entry — it shows only REQ-FUNC-007 at the epic level — but STATUS_NEXT_RELEASE.md confirms the sub-requirement exists and has tasks assigned to 0.0.1, so this is a registry staleness issue, not a missing requirement.

### Open Questions

1. The id_registry.md was generated on 2026-03-06 and does not show REQ-FUNC-007-01, REQ-FUNC-007-02, or REQ-FUNC-007-03 as distinct entries (only the parent REQ-FUNC-007 appears). Should the registry be regenerated to reflect these sub-requirements, or is the current flat listing intentional?
=> the skills that create tasks should run the id_registry... strange. Well doesn't matter now. Do nothing.

2. REQ-FUNC-007-02 (Plan Receiving / QR scanning, client side) has only 14% task coverage with most acceptance criteria still GAP. Is this coverage level acceptable for the 0.0.1 milestone, or do additional tasks need to be created?
=> see phase 2 answer.

---

# Scope Coverage Check — 0.0.1 (Iteration 02)

## Scope Item Mapping

| Scope Item | Mapped Requirement(s) | Status |
|---|---|---|
| QR code generation (therapist side) | REQ-FUNC-007-01 (Feat Therapist Transfer UI) | Covered — assigned to 0.0.1; TASK-FUNC-007-01-01 pending, 59% coverage |
| QR code scanning and plan reception (client side) | REQ-FUNC-007-02 (Feat Plan Receiving) | Covered — assigned to 0.0.1; TASK-FUNC-007-02-02 pending, 14% coverage |
| Basic plan serialization/deserialization | REQ-FUNC-007-03 (Feat Plan Serialization) | Covered — assigned to 0.0.1; TASK-FUNC-007-03-01 pending, 83% coverage |
| Role selection (Client / Therapist) | No requirement needed — confirmed implemented in iteration 01 | N/A |

## Gaps Found

**No scope gaps.** All three functional scope items that require requirements coverage are mapped to at least one 0.0.1-assigned requirement with at least one active task.

Minor observations (not blockers):

- **id_registry.md staleness**: The registry (generated 2026-03-06) lists only REQ-FUNC-007 at the epic level; sub-requirements REQ-FUNC-007-01, REQ-FUNC-007-02, REQ-FUNC-007-03 do not appear as separate rows. STATUS_NEXT_RELEASE.md (generated 2026-03-07) shows all three sub-requirements with tasks, confirming they exist. The registry should be regenerated.
- **REQ-FUNC-007-02 low coverage (14%)**: The client-side scanning requirement has most acceptance criteria unaddressed. This may be intentional if the current task scope is intentionally narrow for the alpha, but warrants confirmation.

## Notes

- Iteration 01 identified plan serialization as a potential gap. REQ-FUNC-007-03 has since been created and appears in STATUS_NEXT_RELEASE.md with task TASK-FUNC-007-03-01 (Impl Plan-Serialization-Pipeline) assigned to 0.0.1. The gap is resolved.
- STATUS_NEXT_RELEASE.md was generated 2026-03-07 13:09 — current as of today.
- id_registry.md was generated 2026-03-06 — one day stale; does not affect scope coverage conclusions since STATUS_NEXT_RELEASE.md is the authoritative source for release assignment.
- The parent epic REQ-FUNC-007 (Epic Data Transfer) shows 0% coverage (0/8 items), but this refers to the epic-level acceptance criteria, not the sub-requirement tasks. The sub-requirements carry the actual task coverage.
