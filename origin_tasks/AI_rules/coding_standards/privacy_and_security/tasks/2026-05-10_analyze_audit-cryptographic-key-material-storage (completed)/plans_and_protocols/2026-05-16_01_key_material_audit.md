# Key Material Audit — REQ-PROC-052 AC-08

**Task:** TASK-PROC-052-04
**Date:** 2026-05-16
**Scope:** `lib/` only (248 Dart files)
**Verdict overall:** ✅ Zero violations — AC-08 vacuously satisfied at 0.0.1.

## TL;DR

The 0.0.1 codebase contains **no cryptographic key material** of the kind AC-08
targets (master keys, derived keys, key-encryption keys). Encryption is an
explicitly deferred feature for 0.0.2:

- `pubspec.yaml` declares **no** cryptographic dependency
  (`flutter_secure_storage`, `cryptography`, `pointycastle`, `encrypt`, `argon2`,
  `sqlite_cipher` — all absent).
- `lib/core/data/database/database_opener.dart:5–8` documents the deferral:
  `NativeDatabase` is opened unencrypted, SQLCipher + KEK auth land in 0.0.2.
- `lib/features/therapist/data_transfer/domain/services/plan_transfer_pipeline.dart`
  defines explicit `_encryptNoOp` / `_decryptNoOp` placeholders for the
  AES-256-GCM stage planned for 0.0.2.

No master key, derived key, KEK, password, Argon2/PBKDF/HKDF/scrypt invocation,
biometric integration, or platform-Keystore call exists anywhere in `lib/`.
Therefore there is no key material whose persistence could violate AC-08.

## Methodology

Pattern sweeps run against `lib/`:

| Sweep | Pattern | Result |
|---|---|---|
| Crypto package imports | `^import.*package:(cryptography\|pointycastle\|encrypt\|crypto\|flutter_secure_storage\|sqlite_cipher\|sqlcipher\|argon2)` | **0 hits** |
| Key-typed classes/typedefs | `(class\|typedef)\s+\w*(Key\|KeyMaterial\|MasterKey\|DerivedKey\|EncryptionKey\|Argon2\|Vault\|Secret\|Cipher\|Crypto\|Encrypt)\w*` | **0 hits** |
| KDF / secure-random calls | `Argon2\|HKDF\|PBKDF\|scrypt\|crypto.*Random\|secureRandom` (case-insensitive) | **0 hits** |
| Secure-storage / platform-key APIs | `flutter_secure_storage\|Keystore\|Keychain\|DPAPI\|KeyVault` | **0 hits** |
| Auth/secret terminology | `password\|secret\|kdf\|keystore\|keychain\|biometric\|sqlcipher` | 2 hits, both **WHY-comment text only** (logging-rule preamble, deferred-encryption WHY comment) |
| Key-derivation hints | `argon2\|pbkdf2\|deriveKey\|derive_key\|Uint8List.*key` | 24 hits, **all** about `encryptedTransferKey` (see candidate analysis below) |
| `SharedPreferences` usage | `SharedPreferences` | 2 files, **non-crypto** (notice dismissal flag, transfer-flow UI state) |

## Candidate analysis

### Candidate 1 — `encryptedTransferKey` (the only `*Key`-named field in `lib/`)

**Files**
- `lib/core/domain/entities/contact.dart:14`
  `final List<int> encryptedTransferKey;`
- `lib/core/data/database/tables/contacts_table.dart:10`
  `BlobColumn get encryptedTransferKey => blob()();`
- `lib/core/data/repositories/drift_contact_repository.dart:91, 103`
  (Drift ↔ domain mapping only)
- `lib/core/data/models/pairing_qr_payload.dart:26, 56, 67, 82, 94`
  (QR-payload field + base64 ↔ bytes)
- `lib/core/data/database/app_database.g.dart` (Drift-generated; not hand-edited)

**Origin**
External — produced by the *therapist* app, transmitted in the pairing QR code
(`pairing_qr_payload.dart:56–67`), decoded from base64, stored as a blob in the
client's `contacts` table.

**Persistence**
Plaintext (file)? No.
SharedPreferences? No.
SQLite/Drift column? **Yes** — `contacts.encrypted_transfer_key BLOB NOT NULL`.
Hive box? No.
Logged? No (logging interface explicitly forbids byte arrays).

**AC-08 verdict: not in scope (✅ compliant).**

**Reasoning.** AC-08 targets *root key material* — keys obtained from a KDF or
generated locally and used to encrypt data. `encryptedTransferKey` is, by name
and contract, the opposite: it is **already-encrypted ciphertext bytes** of a
secret produced on the therapist side. The audit's `goal.md` notes
explicitly:

> "A common ambiguous case: a `Uint8List` that *was* derived from secure-storage
> material but is now passed around as a derived value. AC-08's intent is the
> *root* key material; intermediate derived bytes … are not the target."

`encryptedTransferKey` is even further removed: at the client it has no
plaintext form anywhere in `lib/`. There is no decrypt call site — the
key-encryption key (KEK) that would decrypt it doesn't exist in this codebase
yet. It is therefore opaque ciphertext, and storing opaque ciphertext in SQLite
is what encrypted-at-rest fields are supposed to do.

This will be revisited when 0.0.2 introduces the KEK that decrypts this field —
the KEK itself will be the AC-08-relevant artefact at that point, not the
ciphertext.

## Other observations

These are not AC-08 violations but worth noting:

1. **Privacy logging contract is already in place.**
   `lib/core/services/logging/i_logging_service.dart:1–8` declares an
   interface-level prohibition on logging encryption keys, derived secrets, or
   raw byte arrays. When real key material lands in 0.0.2 the discipline is
   pre-wired.

2. **Anchor for future AC-08 enforcement.**
   The two named placeholder points where AC-08 will become live are:
   - `lib/core/data/database/database_opener.dart` (SQLCipher / KEK plug-in)
   - `lib/features/therapist/data_transfer/domain/services/plan_transfer_pipeline.dart`
     (`_encryptNoOp` / `_decryptNoOp` slots for AES-256-GCM in 0.0.2)
   A follow-up audit task should be scheduled to re-run this sweep once
   either landing site grows real cryptographic code.

3. **`SharedPreferences` use is benign.**
   `lib/core/data/storage/grey_zone_notice_storage.dart` (UI notice flag) and
   `lib/features/therapist/data_transfer/presentation/bloc/data_beam_bloc.dart`
   (transfer-flow state) read/write small non-secret values. No key material
   is currently routed through `SharedPreferences`.

## Acceptance criteria check

- [x] `plans_and_protocols/key_material_audit.md` exists and lists every
      key-material candidate with verdict — **1 candidate (`encryptedTransferKey`),
      verdict: not in scope / compliant**.
- [x] Each non-compliant case has a recommended remediation — **N/A
      (zero non-compliant cases)**.
- [x] Each ambiguous case has a question framed for user decision — **N/A
      (zero ambiguous cases; `encryptedTransferKey` was the borderline case
      and is resolved as ciphertext, not key material).**
- [x] Remediation tasks are scheduled — **N/A**.
- [x] **If zero violations: that fact is recorded explicitly** —
      ✅ recorded above (TL;DR + this section).

## Recommended follow-up

Open a future audit task to re-run the same sweep against `lib/` once
**either** of the following lands:
- A real `flutter_secure_storage` / `Keystore` / `Keychain` / `DPAPI`
  integration replaces the WHY comments in `database_opener.dart`.
- The `_encryptNoOp` / `_decryptNoOp` placeholders in `plan_transfer_pipeline.dart`
  become real AES-256-GCM with a derived key.

That task should be created under REQ-FUNC-006 with `after:` chained to the
task that introduces real key material. **Not creating it now**: AC-08
remediation is scoped per the current goal, and a forward-looking re-audit is
not a *remediation* but a *future verification*. Scheduling it now would be
speculative; let the 0.0.2 implementation task pull it in.
