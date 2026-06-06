## feat_plan_serialization

- Coverage: PARTIAL

### ACs/SECs Targeting 0.0.1 Packages

| AC | Text (abbreviated) | target_package |
|----|-------------------|----------------|
| AC-01 | Plan serialized to byte array: JSON → compress → encrypt placeholder → split into chunks | Transfer Data Model |
| AC-02 | Chunk sequence deserialized back to valid plan domain object | Transfer Data Model |
| AC-03 | Serialization is deterministic (byte-identical output for same plan) | Transfer Data Model |
| AC-04 | Each chunk carries header encoding: sequence ID, total count, chunk index, payload | Transfer Data Model |
| AC-05 | Serialized format includes 1-byte schema version prefix | Transfer Data Model |
| AC-06 | Same pipeline used bidirectionally; bidirectional capability validated in 0.0.1 spike | Adaptive Scanner Settings |
| AC-07 | Chunk size and EC level are configurable at call time, not hardcoded | Adaptive Scanner Settings |
| AC-14 | Tracking entries in client→therapist bundle carry per-entry dataVersion field | Transfer Data Model |
| AC-15 | Entries with dataVersion ≤ current are migrated transparently | Transfer Data Model |
| AC-16 | Entries with dataVersion too new: raw bytes retained, entries flagged, update prompt | Transfer Data Model |
| AC-17 | After app update, retained raw bundles are auto-re-parsed | Transfer Data Model |

**Not in scope for 0.0.1**: AC-08 through AC-13 (target_package: "Transfer Encryption") — these cover the encrypted header block mechanism which activates in 0.0.2.

**Note on AC-14 through AC-17**: These cover the client→therapist data bundle versioning contract. The requirements doc itself states: "0.0.1 (client→therapist transfer not yet built) — Not applicable — pipeline spike validates bidirectionality only; full versioning contract takes effect with the 0.1.0 data upload feature." So these ACs are technically 0.0.1-tagged but not yet actionable implementation items.

### Tasks Found

| Task | Status |
|------|--------|
| `2026-03-07_impl_plan-serialization-pipeline` | completed |
| `2026-03-29_explore_encrypted_header_block` | completed (explore only) |
| `2026-03-29_explore_update_data_bundle_versioning` | completed (explore only) |

### Gaps

- **AC-01 through AC-07**: The single impl task `2026-03-07_impl_plan-serialization-pipeline` (completed) covers the core pipeline (serialize/deserialize, chunk format, schema version byte, determinism, configurable chunk size). Appears fully covered.
- **AC-06 (bidirectional spike)**: This references REQ-FUNC-007-04 (Adaptive Scanner Settings). The explore task `2026-03-29_explore_encrypted_header_block` is not directly related; there is no explicit impl task named for the bidirectional validation spike. Needs verification whether this was folded into the main pipeline task or is a gap.
- **AC-14 through AC-17 (data bundle versioning)**: Only an explore task exists (`2026-03-29_explore_update_data_bundle_versioning`). No impl task for the versioning contract. However, per the requirements doc this is 0.1.0 scope in practice — flagged for confirmation on whether any 0.0.1 impl work is expected here.

---

## feat_plan_receiving

- Coverage: PARTIAL

### ACs/SECs Targeting 0.0.1 Packages

The requirement-level `target_package` is "Transfer Data Model". Individual ACs override this with their own packages:

| AC | Text (abbreviated) | target_package |
|----|-------------------|----------------|
| AC-03 | Client sees accurate reception progress: percentage of chunks received out of total | Transfer Data Model |
| AC-08 | Client declines a plan: data is discarded without saving; client returns to home screen | Adaptive Scanner Settings |

**ACs NOT in 0.0.1 package scope:**
- AC-01 (Transfer Encryption): Client scans static pairing QR code
- AC-02 (Transfer Encryption): Client enters BIP-39 verbal word chain
- AC-04 (Plan Transfer Full): Client imports .tplan file via file picker
- AC-05 (Plan Transfer Full): Client opens .tplan file via deep link
- AC-06 (Transfer Encryption): Receipt confirmation screen content
- AC-07 (Transfer Encryption): Client accepts plan
- AC-09 (Plan Transfer Full): Inline notification time mapping
- AC-10 (Plan Transfer Full): Re-delivered plan update UI
- AC-11 (Plan Transfer Full): Entries preserved on plan update accept
- AC-12 (Transfer Encryption): N simultaneous therapist connections
- AC-13 (Transfer Encryption): Plans attributed to correct therapist
- AC-14 (Transfer Encryption): Contact deletion with explicit confirmation

**Note**: The packages "QR Transfer Receive", "Transfer Pairing", and "DataBeam Reverse Validation" appear in the 0.0.1 package list but are not assigned to any specific AC in this feature's requirements. They may be covered through task-level work rather than AC-level assignment, or the AC package assignments may not have been updated.

### Tasks Found

| Task | Status |
|------|--------|
| `2026-02-21_explore_plan_receiving_full` | completed |
| `2026-03-06_impl_data-beam-progress-and-decline` | completed |
| `2026-03-09_impl_fix-freezed-v3-abstract-class` | completed |
| `2026-03-11_analyze_qr-scan-not-working` | open (no `completed` suffix) |
| `2026-03-11_analyze_qr-scan-pipeline-test-gaps` | completed |
| `2026-03-11_explore_android-qr-still-failing` | open (no `completed` suffix) |
| `2026-03-11_impl_data-transfer-bugfix-0.0.1` | completed |
| `2026-03-11_impl_fix-android-nv21-qr-format` | completed |
| `2026-03-11_impl_fix-qr-scan-imageformat` | completed |
| `2026-03-11_impl_fix-windows-camera-preview` | completed |
| `2026-03-11_impl_qr-library-bug-tests-and-fix` | completed |
| `2026-03-29_explore_update_protocol_receipt_confirmation` | completed |

### Gaps

- **AC-03 (progress indicator) and AC-08 (decline)**: Directly covered by `2026-03-06_impl_data-beam-progress-and-decline` (completed). These two 0.0.1-package ACs appear fully covered.
- **Open tasks**: `2026-03-11_analyze_qr-scan-not-working` and `2026-03-11_explore_android-qr-still-failing` are still open (no completed suffix). These are analyze/explore tasks, not impl tasks, but their open status warrants review — it is unclear if the underlying issues were resolved by the surrounding fix tasks or are still pending.
- **"QR Transfer Receive", "Transfer Pairing", "DataBeam Reverse Validation" packages**: No ACs in this feature's requirements are assigned to these packages. If these packages are expected to be covered here, the AC assignments are missing. Alternatively, these packages may be primarily covered by other features (e.g., feat_therapist_transfer_ui, epic_security) and the package names appear here only because the requirement-level package assignment predates granular AC-level tagging.
- **Requirement status is "implemented"**: The overall requirement is marked `status: implemented`, suggesting the 0.0.1-scoped work is considered done. The open analyze tasks may be stale or superseded by the completed fix tasks.
