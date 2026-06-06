# Phase 2c Reopeners — Release 0.0.1

Source: Sub-Agent A (feat_adaptive_transfer_settings)

---

## Reopener 1 — AC-25–27: Remote Overlay Activation & Content States

**Epic**: REQ-FUNC-007, feat_adaptive_transfer_settings
**Affected package boundary**: "Adaptive Scanner Settings" (0.0.1) vs. "Remote QR Sessions" (0.2.1)

RELEASE_BACKLOG.md scope for "Adaptive Scanner Settings" says: "AC-06–17" and mentions "Windows screen capture for remote sessions".

- AC-15 (Windows screen capture mode activation) → in scope per RELEASE_BACKLOG → task planned
- AC-16 (compact floating overlay bar) → in scope → task planned
- AC-25 (remote mode activation paths — full implementation) → NOT in RELEASE_BACKLOG scope description
- AC-26 (overlay content states) → NOT in scope description
- AC-27 (overlay dismissal) → NOT in scope description

**Question**: Are AC-25–27 in 0.0.1 or deferred to 0.2.1 ("Remote QR Sessions")?

User answer: 0.0.1 — AC-25–27 stay in scope for "Adaptive Scanner Settings"

---

## Reopener 2 — AC-28–36: Transfer Speed Preference / Photosensitivity Safety

**Epic**: REQ-FUNC-007, feat_adaptive_transfer_settings
**Added**: 2026-04-05 (after original scope was defined)
**target_package in requirements**: "Adaptive Scanner Settings"
**RELEASE_BACKLOG scope description**: Does NOT mention these ACs

These ACs cover fast-transfer consent UI and photosensitivity safety warnings — a UI-heavy feature block added after the original 0.0.1 scope was written.

**Question**: Are AC-28–36 in 0.0.1 or moved to 0.2.1 ("Transfer Adaptive UI")?

User answer: 0.0.1 — AC-28–36 stay in scope for "Adaptive Scanner Settings"
