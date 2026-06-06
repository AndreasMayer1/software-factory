## Summary for User
- All 7 release 0.0.1 packages (`QR Transfer Send`, `QR Transfer Receive`, `Transfer Pairing`, `Transfer Data Model`, `Transfer Notifications`, `Adaptive Scanner Settings`, `DataBeam Reverse Validation`) have feature-level requirements — no coverage gaps exist at the feature level.
- One anomaly: the epic-level AC-07 (`target_package: "Adaptive Scanner Settings"`) maps perfectly to `feat_qr_data_transfer` AC-06/08/09, and AC-08 (`target_package: "Transfer Encryption"`) belongs to release 0.0.2, not 0.0.1 — both correctly tracked at feature level.
- `Transfer Notifications` (REQ-FUNC-007-06) is assigned to the 0.0.1 package but RELEASES.md explicitly excludes "Notifications" from 0.0.1 scope — this is a package-assignment conflict that needs a decision.

### Open Questions
1. **Transfer Notifications conflict**: `feat_transfer_notifications` (REQ-FUNC-007-06) has `target_package: "Transfer Notifications"` which is listed as a 0.0.1 package, but `releases[0.0.1].scope_boundaries.excludes` explicitly says "Notifications". Should the `Transfer Notifications` package be moved to a later release (0.1.0), or should the scope_boundaries exclusion be corrected?

## Detailed Findings

### Release 0.0.1 Packages vs. Epic Coverage

The epic (REQ-FUNC-007) defines 8 ACs at the top level. Their `target_package` values:

| Epic AC | Text (abbreviated) | target_package | In 0.0.1? |
|---------|-------------------|----------------|-----------|
| AC-01 | Therapist → new client via pairing + transfer | Transfer Encryption | No (0.0.2) |
| AC-02 | Therapist → existing client, skip pairing | Transfer Encryption | No (0.0.2) |
| AC-03 | Remote transfer via encrypted file + share sheet | Plan Transfer Full | No (0.1.0) |
| AC-04 | Self-test mode for therapist | Plan Transfer Full | No (0.1.0) |
| AC-05 | Privacy UI — manual name entry only | Transfer Encryption | No (0.0.2) |
| AC-06 | Known client without key → re-pairing flow | Transfer Encryption | No (0.0.2) |
| AC-07 | QR Data Beam adjustable animation speed | **Adaptive Scanner Settings** | **Yes** |
| AC-08 | Verbal pairing alternative (BIP-39 word chain) | Transfer Encryption | No (0.0.2) |

Only **1 epic-level AC** (AC-07) is scoped to a 0.0.1 package. The bulk of the epic's top-level ACs belong to 0.0.2 or 0.1.0 (encryption-dependent features).

---

### Feature-Level Coverage for 0.0.1 Packages

#### `QR Transfer Send` and `QR Transfer Receive`
- **Feature**: `feat_qr_data_transfer` (REQ-FUNC-007-12)
- `target_package: "QR Transfer Send"` at feature level
- ACs explicitly tagged `"QR Transfer Send"`: AC-01 through AC-05, AC-07, AC-10 through AC-19 (majority)
- Note: The 0.0.1 package list includes `QR Transfer Receive` but `feat_qr_data_transfer` uses only `"QR Transfer Send"` as its package label — the receive screen (therapist side) is covered by ACs AC-10 through AC-14 within the same feature, under the `QR Transfer Send` package name. `QR Transfer Receive` as a distinct package has no separate feature requirement. This is likely intentional (send and receive are bundled in one feature), but the package name discrepancy is worth noting.

#### `Transfer Pairing`
- **Feature**: `feat_pairing_management` (REQ-FUNC-007-07), all ACs tagged `"Transfer Pairing"`
- **Feature**: `feat_client_data_model` (REQ-FUNC-007-05), ACs AC-01, AC-02, AC-04, AC-05 tagged `"Transfer Pairing"`
- Full coverage confirmed.

#### `Transfer Data Model`
- **Feature**: `feat_adaptive_transfer_settings` (REQ-FUNC-007-04)
- ACs explicitly tagged `"Transfer Data Model"`: AC-01, AC-02, AC-03, AC-04, AC-05, AC-22, AC-23, AC-24, AC-28, AC-30, AC-36
- Coverage confirmed.

#### `Adaptive Scanner Settings`
- **Feature**: `feat_adaptive_transfer_settings` (REQ-FUNC-007-04)
- ACs explicitly tagged `"Adaptive Scanner Settings"`: AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-25, AC-26, AC-27, AC-29, AC-31, AC-32, AC-33, AC-34, AC-35
- Also covered in `feat_qr_data_transfer`: AC-06, AC-08, AC-09
- Coverage confirmed.

#### `DataBeam Reverse Validation`
- **Feature**: `feat_adaptive_transfer_settings` (REQ-FUNC-007-04)
- ACs explicitly tagged `"DataBeam Reverse Validation"`: AC-18, AC-19, AC-20, AC-21
- The spike was already run and PASSED (2026-03-15, documented in the feature's Overview section).
- Coverage confirmed.

#### `Transfer Notifications`
- **Feature**: `feat_transfer_notifications` (REQ-FUNC-007-06), all ACs tagged `"Transfer Notifications"`
- Feature exists and package assignment matches.
- **Conflict**: `RELEASES.md` version 0.0.1 `scope_boundaries.excludes` lists "Notifications" explicitly. The package `Transfer Notifications` is simultaneously in the 0.0.1 packages list AND in the excludes list. This is an internal inconsistency in `RELEASES.md`.

---

### Gap Assessment

**No missing feature requirements** — every 0.0.1 package has at least one feature-level requirements file covering its ACs.

**One inconsistency requiring a decision**: `Transfer Notifications` appears in both `packages` and `scope_boundaries.excludes` for release 0.0.1. The most likely intent is that the package was accidentally included in 0.0.1's `packages` list and should be moved to 0.1.0 (where "Notifications / reminders" is also excluded, suggesting it belongs even later). Alternatively, the excludes note may be stale.

---

### Draft Requirement (not needed — no gap found)

No draft requirement is needed. All 0.0.1-scoped items have feature-level requirements. The only action required is the user decision on the `Transfer Notifications` package placement.
