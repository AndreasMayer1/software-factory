## Summary for User

- 2 of 4 scope items are fully covered by existing requirements
- 1 partial: "Basic plan serialization/deserialization" is implied by REQ-FUNC-007 but has no dedicated tracked requirement
- 1 gap: "Role selection (Client / Therapist)" has no requirement assigned to 0.0.1 — REQ-FUNC-011 exists but is scoped to 0.1.0

### Open Questions

1. **Role selection**: Should a subset of REQ-FUNC-011 (just "pick role on first launch") be pulled forward to 0.0.1, should a new narrow PoC requirement be created, or should "Role selection" be removed from the 0.0.1 scope boundary?
=> A basic role selection is already implemented in the app. Since this is not the focus of 0.0.1 we can just keep it as it is.

---

# Scope Coverage Check — 0.0.1

## Scope Item Mapping

| Scope Item | Mapped Requirement(s) | Status |
|---|---|---|
| QR code generation (therapist side) | REQ-FUNC-007 (Epic Data Transfer), REQ-FUNC-007-01 (Feat Therapist Transfer UI) | covered |
| QR code scanning and plan reception (client side) | REQ-FUNC-007 (Epic Data Transfer), REQ-FUNC-007-02 (Feat Plan Receiving) | covered |
| Basic plan serialization/deserialization | REQ-FUNC-007 (Epic Data Transfer) — implied by transfer flow; no dedicated serialization requirement exists | partial |
| Role selection (Client / Therapist) | None assigned to 0.0.1 — REQ-FUNC-011 (User Onboarding & Role Selection) exists but is scoped to 0.1.0 | gap |

## Gaps Found

### 1. Role selection has no 0.0.1 requirement

The scope boundary explicitly includes "Role selection (Client / Therapist)", but none of the 11 requirements assigned to release 0.0.1 cover this feature.

- REQ-FUNC-011 (User Onboarding & Role Selection) is the correct requirement for this scope item, but it is referenced only in the 0.1.0 Beta MVP scope in RELEASES.md — it has no `target_release: 0.0.1` assignment visible in STATUS_NEXT_RELEASE.md.
- REQ-NFUNC-011 (Main Navigation) covers navigation structure but not the role selection decision itself.

**Resolution options:**
1. Assign REQ-FUNC-011 (or a subset of its ACs covering role selection) to release 0.0.1.
2. Create a new, narrower feature requirement for "basic role selection UI (PoC)" scoped to 0.0.1.
3. Explicitly remove "Role selection" from the 0.0.1 scope boundary if it is only needed as a prerequisite for later releases.

### 2. Plan serialization/deserialization has no dedicated requirement

The scope boundary includes "Basic plan serialization/deserialization" as a first-class deliverable, but no requirement in the 0.0.1 set names or explicitly owns serialization logic.

- REQ-FUNC-007 (Epic Data Transfer) is the closest anchor — serialization is a necessary implementation detail of the QR transfer flow — but the epic has 0% coverage and no AC in STATUS_NEXT_RELEASE.md specifically mentions serialization or deserialization.
- REQ-FUNC-014 (Epic Plan Management) covers plan data structure but is broader (therapist-side plan management) and also has 0% coverage.

**Resolution options:**
1. Add explicit serialization/deserialization ACs to REQ-FUNC-007 or REQ-FUNC-007-01 / REQ-FUNC-007-02.
2. Create a dedicated technical requirement (e.g., REQ-FUNC-007-03 or a shared technical requirement) for plan serialization format and versioning.

## Notes

- All 11 requirements assigned to 0.0.1 exist and are confirmed in the id_registry (REQ-FUNC-007, REQ-FUNC-007-01, REQ-FUNC-007-02, REQ-FUNC-014, REQ-NFUNC-001, REQ-NFUNC-010, REQ-NFUNC-011, REQ-NFUNC-012, REQ-NFUNC-014, REQ-NFUNC-016, REQ-PROC-035).
- Overall 0.0.1 task coverage is 17% with most requirements at 0%. This is expected for a planned release, but REQ-FUNC-007 being at 0% while being the primary epic for 3 of 4 scope items is a risk indicator.
- REQ-NFUNC-001 (Architecture), REQ-NFUNC-010 (In-Detail Navigation), REQ-NFUNC-011 (Main Navigation), REQ-NFUNC-012 (Growth Tree Theme), REQ-NFUNC-014 (Responsive Layout), REQ-NFUNC-016 (Local Database Technology) do not map to any of the 4 explicit scope boundary items — they are foundational/infrastructure requirements that are preconditions for the PoC rather than user-visible deliverables. This is appropriate but worth noting: if these foundations are not met, the QR transfer PoC cannot function.
- REQ-PROC-035 (Release Preparation) is process overhead, not a scope deliverable — correctly included to track the release prep work itself.
