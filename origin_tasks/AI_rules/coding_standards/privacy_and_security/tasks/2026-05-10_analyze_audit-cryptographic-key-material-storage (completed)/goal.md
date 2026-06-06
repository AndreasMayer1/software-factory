---
task_id: TASK-PROC-052-04
type: analyze
parent_requirement: REQ-PROC-052
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: completed
effort: S
created: 2026-05-10
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T15:30:44Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Audit lib/ to verify that cryptographic key material (master keys, derived keys, key-encryption keys) is obtained only via the platform secure-storage abstraction and is never written to plain files, SQLite, SharedPreferences, or any other unsecured storage."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 60f63438-0038-4891-bff8-3078425447f6
session_account: gmail
---

# Goal: Audit cryptographic key material storage (SP-AC-08)

## Objective

REQ-PROC-052 AC-08 asserts that key material is obtained only via the platform secure-storage abstraction (Android Keystore / iOS Keychain / Windows DPAPI / project wrapper) and never persists in plain files, SQLite, `SharedPreferences`, or other unsecured storage. Whether the current encryption code respects this is unverified. This task confirms the current state and produces remediation tasks for any violations.

## Requirements Summary

REQ-PROC-052 AC-08 (secure key-material storage). Linked to REQ-FUNC-006 (cryptographic specification) — that requirement defines *what* the keys are; this AC governs *where* they may live.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Inventory all types in `lib/` whose names suggest key material: `*Key`, `*KeyMaterial`, `*MasterKey`, `*DerivedKey`, `*EncryptionKey`, `*Argon2*`, plus any type holding `Uint8List` that originates from key derivation.
- For each candidate, trace its lifecycle: where is it constructed, where does it come from, where does it go.
- Verify each candidate against AC-08:
  - Construction: the only legitimate source is the platform secure-storage abstraction (or its wrapper) — `flutter_secure_storage`, project's own `KeyVault`, or platform-channel calls into Keystore / Keychain / DPAPI.
  - Persistence: must not be written to a file via `dart:io`, must not appear in any Drift / SQLite table column, must not be passed to `SharedPreferences.setString`, must not be logged.
  - In-memory lifetime: ideally cleared (`Uint8List.fillRange(0, length, 0)`) after use; not strictly mandated by AC-08 but worth flagging where absent.
- Output `plans_and_protocols/key_material_audit.md` listing each candidate type, its current source, its persistence behaviour, and a verdict (compliant / non-compliant / ambiguous).
- For each non-compliant case, recommend remediation: redirect to secure-storage abstraction, or strip persistence and re-derive on demand.
- For each ambiguous case, escalate to user with a specific question.
- If non-compliant cases are non-trivial in volume or risk, create remediation tasks via `task-create` (one per type or per fix-category) under REQ-FUNC-006 with appropriate `after:` chains. If volume is low (≤ 2), fix inline by extending this task's scope (note the extension in the protocol).

### Out of Scope

- Changing the choice of secure-storage abstraction (Keystore vs. Keychain vs. DPAPI). That decision is REQ-FUNC-006's responsibility.
- Audit of *encrypted data at rest* (the database) — that's a separate concern; AC-08 is about *keys*, not the data they protect.
- Side-channel concerns (timing attacks, memory dumps) — out of scope for this AC.
- Cleartext password handling (the password the user enters before key derivation) — different lifecycle, governed by REQ-FUNC-006.

## Acceptance Criteria

- [x] `plans_and_protocols/key_material_audit.md` exists and lists every key-material candidate with verdict. — see `plans_and_protocols/2026-05-16_01_key_material_audit.md` (1 candidate: `encryptedTransferKey`, verdict: not in scope / compliant).
- [x] Each non-compliant case has a recommended remediation. — N/A (zero non-compliant cases).
- [x] Each ambiguous case has a question framed for user decision. — N/A (zero ambiguous cases; the borderline candidate `encryptedTransferKey` is resolved as opaque ciphertext, not key material).
- [x] Remediation tasks are scheduled (via `task-create`) for all non-compliant cases, OR fixed inline if volume is low. — N/A (zero non-compliant cases).
- [x] If zero violations: that fact is recorded explicitly. — Recorded in the audit report's TL;DR and "Acceptance criteria check" sections.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

PERSONA-004 calls cryptographic-lockout a `🔴` data-loss scenario (REQ-FUNC-006-F4). The reason is precisely that platform secure-storage *can* invalidate keys (e.g. on biometric-enrollment changes), and the system needs a graceful response. AC-08 is upstream of that: keys must live in secure storage *despite* its lockout risk, because the alternative (keys in plain storage) is worse — it makes the encrypted data unencrypted in practice.

A common ambiguous case: a `Uint8List` that *was* derived from secure-storage material but is now passed around as a derived value. AC-08's intent is the *root* key material; intermediate derived bytes that are themselves used for one operation and then dropped are not the target. The audit should distinguish.
