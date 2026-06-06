## feat_pairing_management

- Coverage: MISSING

### ACs in 0.0.1 packages

All 8 ACs (AC-01 through AC-08) have `target_package: "Transfer Pairing"`, which is in the 0.0.1 package list.

### Tasks Found

None — the `tasks/` folder does not exist for this feature.

### Gaps

- **AC-01**: Pairing entity attribute set (add `argon2Salt`, `therapistEmail`, `transferSpeedPreference` to `Contact` entity and DB table) — no impl task
- **AC-02**: Many-to-many relationship model documentation/assertion in domain — no impl task
- **AC-03**: Client-identification trial-decryption lookup algorithm (`ContactRepository.getAll()` + trial decrypt) — no impl task
- **AC-04**: Re-pairing key-renewal semantics (replace `encryptedTransferKey` + `argon2Salt`, preserve rest) — no impl task
- **AC-05**: Pairing dissolution (delete Contact row, no cascade to plans) — no impl task
- **AC-06**: `therapistEmail` transmission from pairing QR payload, null-vs-empty invariant — no impl task
- **AC-07**: `therapistId` as sole stable identifier (no `name`/`email` as lookup key) — no impl task
- **AC-08**: Atomic re-pairing write (single DB transaction for both fields) — no impl task

All 8 ACs are unimplemented and have no corresponding impl tasks.

---

## feat_client_data_model

- Coverage: PARTIAL

### ACs in 0.0.1 packages

- AC-01: `target_package: "Transfer Pairing"` — in 0.0.1
- AC-02: `target_package: "Transfer Pairing"` — in 0.0.1
- AC-03: `target_package: "Transfer Encryption"` — in 0.0.1
- AC-04: `target_package: "Transfer Pairing"` — in 0.0.1
- AC-05: `target_package: "Transfer Pairing"` — in 0.0.1

All 5 ACs are in 0.0.1 packages (4 in "Transfer Pairing", 1 in "Transfer Encryption").

### Tasks Found

- `2026-03-29_explore_client_data_model` — **completed** (explore task, not an impl task)

### Gaps

The only existing task is an **explore** task (completed). No impl tasks exist for any of the 5 ACs:

- **AC-01**: Tracking entry entity with ownership field (immutable at creation; therapist-assigned vs. client-created) — no impl task
- **AC-02**: Plan-level privacy flag; architectural exclusion of private entries from all transfer scopes at domain layer — no impl task
- **AC-03**: Per-client encrypted partition on therapist device with mandatory client identity parameter at repository interface — no impl task
- **AC-04**: Two independent boolean markers (`isShared`, `isExcluded`) with independence invariant, grey-zone handling, and no cross-reset — no impl task
- **AC-05**: Transfer bundle value object (therapist pairing context, scoped entry collection, scope variants: default/widened/narrowed; QR vs. file channel support) — no impl task

The explore task likely produced design decisions that should feed into impl tasks, but no impl tasks have been created yet.
