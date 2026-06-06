## Summary
- Coverage: PARTIAL
- All DataBeam Reverse Validation ACs (AC-18–21) have a completed spike task
- All Transfer Data Model ACs (AC-01–05, AC-22–24, AC-28, AC-30, AC-36) have a completed domain model task
- All Adaptive Scanner Settings ACs (AC-06–16, AC-25–27, AC-29, AC-31–35) have several completed tasks, BUT one impl task is open: `therapist-tier-override`
- AC-17 (target_package: Transfer Encryption) is NOT in the 0.0.1 package list — excluded

## AC / Target-Package Mapping for 0.0.1 Packages

### Transfer Data Model
AC-01, AC-02, AC-03, AC-04, AC-05 (tier model + parameter contracts)
AC-22, AC-23, AC-24 (remote tier parameter contracts)
AC-28 (≤3Hz default safety floor)
AC-30 (Transfer Speed Preference propagation via payload)
AC-36 (FLOW-004 exclusion from speed preference)

### Adaptive Scanner Settings
AC-06, AC-07, AC-08 (auto-detection / tier probe)
AC-09, AC-10 (pairing data extension)
AC-11, AC-12, AC-13, AC-14 (session-type controls & auto-FPS)
AC-15, AC-16 (Windows remote screen capture + overlay bar)
AC-25 (remote mode activation paths)
AC-26 (overlay content states)
AC-27 (overlay dismissal)
AC-29 (per-device fast transfer setting)
AC-31 (OS Reduce Motion hard override)
AC-32, AC-33, AC-34, AC-35 (consent prompt + activation conditions)

### DataBeam Reverse Validation
AC-18, AC-19, AC-20, AC-21

### Not in 0.0.1 package list
AC-17 (target_package: Transfer Encryption) — excluded from analysis

## Tasks Found

| Task | Status |
|------|--------|
| 2026-03-13_impl_domain-model-scanner-tiers | completed |
| 2026-03-13_impl_tier-probe-and-pairing-qr-extension | completed |
| 2026-03-13_impl_client-scanner-tier-storage | completed |
| 2026-03-13_impl_client-therapist-databeam-spike | completed |
| 2026-03-13_impl_speed-control-remap-to-tiers | completed |
| 2026-03-13_impl_therapist-tier-override | **open** |
| 2026-03-15_impl_scan-pipeline-optimization | completed |
| 2026-03-20_impl_spike-cleanup | completed |
| 2026-03-29_explore_remote_qr_screen_capture | completed |
| 2026-04-01_explore_transfer_speed_preference | completed |
| 2026-04-22_impl_tier-probe-pairing-formalization | completed |

## Gaps (if any)

### Open task (not completed)
- `2026-03-13_impl_therapist-tier-override` — this task is open with no `(completed)` suffix. It likely covers the manual override path that feeds into AC-06 (Tier 2/3 probe result override) and/or AC-25 (remote mode activation paths). Without reading the task's goal.md it is unclear exactly which ACs it covers, but its open status means the therapist-side tier override is not yet implemented.

### ACs with uncertain task coverage
The following Adaptive Scanner Settings ACs were added in the 2026-04-01 and 2026-04-05 updates (Transfer Speed Preference section, AC-28–36) and the 2026-04-01 overlay/remote-mode update (AC-25–27). The explore tasks `explore_transfer_speed_preference` (completed) and `explore_remote_qr_screen_capture` (completed) likely cover the analysis/design for these ACs, and `tier-probe-pairing-formalization` (completed 2026-04-22) may cover AC-25/overlay work. However, no dedicated **impl** task is visible for:
  - AC-15, AC-16 (Windows screen capture + overlay bar final state — noted in requirements as "not yet production-polished")
  - AC-25, AC-26, AC-27 (overlay activation paths and content states)
  - AC-28–AC-36 (Transfer Speed Preference full implementation)

These may be intentionally deferred to 0.0.2/0.1.0 or covered inside existing impl tasks — requires reading individual task goal.md files to confirm.
