# Plan — Critical-path coverage gate (TASK-PROC-046-04)

Date: 2026-05-16
Agent: main session (Opus)

## Goal recap

Set up the AC-04 coverage gate. AC-04 says safety-critical paths must reach
≥ 90 % line coverage as measured by `flutter test --coverage` filtered through
lcov to the documented path list. The path list itself is part of this task.

## Path inventory (per AC-04 category)

AC-04 enumerates five categories. REQ-PROC-046 line 217 explicitly instructs
that **categories with no current implementation stay on the list as named** so
they pick up enforcement automatically once their code lands — deleting them
would silently un-gate.

### 1. Encryption / decryption (REQ-FUNC-006)

**Status**: NOT YET IMPLEMENTED in v0.0.1.

`lib/core/data/database/database_opener.dart` is explicit: "Uses unencrypted
NativeDatabase for v0.0.1. SQLCipher encryption requires biometric/KEK
authentication (REQ-FUNC-006-F2, F4) which lands in v0.0.2."

Hive boxes opened in `storage_initializer.dart` are also unencrypted.

`grep -rli "encrypt\|decrypt\|AesGcm\|sqlcipher\|PRAGMA key" lib/` returns no
matches in implementation code (only references in comments and unrelated
features like the QR `pairing_qr_payload` which encodes, not encrypts).

**Path list**: empty (gate computes 100 % over zero LOC for this category).

### 2. Argon2id key derivation (REQ-FUNC-006)

**Status**: NOT YET IMPLEMENTED in v0.0.1.

`grep -rli "argon2\|deriveKey" lib/` returns no matches.

**Path list**: empty.

### 3. Atomic file rotation (REQ-FUNC-015)

**Status**: NOT YET IMPLEMENTED.

REQ-FUNC-015 is `requirements_tasks/functional/shared/epic_backup/feat_backup_rotation/`.
No backup-rotation code exists in `lib/` yet.

`grep -rli "renameSync\|atomicWrite\|writeAtomically\|\.tmp" lib/` returns no
matches related to atomic file write/rotation.

**Path list**: empty.

### 4. Version migration

**Status**: IMPLEMENTED (REQ data versioning).

Files:
- `lib/core/domain/services/questionnaire_plan/plan_migration_service.dart` —
  the migration orchestrator with step-wise `migrateV1toV2()`. The chained
  for-loop dispatch is non-trivial logic that this gate protects.
- `lib/core/domain/services/questionnaire_plan/serialization_utils.dart` —
  `deserializePlan()` is the version-dispatch entry point. It reads
  `dataVersion`, routes to `PlanMigrationService.migrate()` for v1, and falls
  through to direct `fromJson` for v2. Unsupported versions return
  `UnsupportedDataVersionFailure`.

Note: `lib/core/domain/entities/questionnaire_plan_entities/version_constants.dart`
is a single `const int currentDataVersion = 2;` — no branches, no risk. Not
included in the path list because lcov line coverage on a single constant is a
trivial 1/1 that contributes noise, not signal.

### 5. Data-transfer serialization pipeline (REQ-FUNC-007)

**Status**: IMPLEMENTED.

Files:
- `lib/features/therapist/data_transfer/domain/services/plan_transfer_pipeline.dart`
  — canonical serialize/deserialize entry; ZLib compression, schema version byte,
  6-byte chunk header, chunk re-assembly with sequence validation.
- `lib/features/therapist/data_transfer/data/services/plan_serialization_service.dart`
  — QR-string adapter over the pipeline.
- `lib/features/therapist/data_transfer/data/services/plan_import_service.dart`
  — receiver-side import; both legacy compressed-base64 and chunk paths.
- `lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart`
  — chunk value object with binary header packing and base64url codec.

## Doc location

`doc/testing/critical_paths.md` (new file). The README in `doc/testing/`
references `testing.md`; this new file is a sibling, linked from `testing.md`
in a follow-up under TASK-PROC-046-06 (CLAUDE.md update).

## Script design

`scripts/quality/check_critical_path_coverage.py` (Python — same pattern as
`check_no_telemetry_sdks.py`).

### Inputs

- `coverage/lcov.info` produced by `flutter test --coverage`.
- The path list, sourced from a YAML alongside the doc:
  `doc/testing/critical_paths.yaml`.

Why split YAML out from the .md: the script needs a machine-readable list, and
parsing markdown headers is brittle. The .md is human-facing; the .yaml is the
single source of truth read by both the doc generator and the script.

Wait — actually no, since the .md is hand-written and there is no doc generator
in this codebase, a YAML co-resident makes maintenance worse (two files to keep
in sync). Better: embed the path list inside a fenced ```yaml block in
`critical_paths.md` between explicit markers, parsed by the script. This keeps
the doc as the single source of truth.

Decision: single file. The script extracts the YAML block between
`<!-- critical-paths:begin -->` and `<!-- critical-paths:end -->` markers.

### Behaviour

1. Run `flutter test --coverage` (or accept a pre-existing `coverage/lcov.info`
   via `--lcov <path>` for re-use without re-running tests).
2. Parse the path list from the doc.
3. Walk `coverage/lcov.info`, retaining only records whose `SF:` line matches
   one of the listed paths (exact match; `lib/foo/bar.dart` form).
4. Sum `DA:` hit lines vs. total lines across retained records.
5. Compute coverage = hit / total. If total == 0 (all categories empty),
   report 100 % and exit 0 with an informational message ("no critical-path
   code exists yet — gate is dormant").
6. Exit 0 if coverage ≥ 90 % OR total == 0.
   Exit 1 if coverage < 90 %, printing per-file breakdown to help locate the
   shortfall.
   Exit 2 on invocation errors (missing lcov.info, malformed doc list, etc.).

### Threshold rationale (no `--threshold` flag)

AC-04 fixes 90 %. A flag would invite drift between the requirement and the
gate. Hard-code 90 % as a module constant with a comment pointing to AC-04.
A future requirement bump changes both the AC text and the constant
simultaneously — no flag-passing in CI to forget.

### Flutter test invocation

The script wraps `flutter test --coverage` only when invoked without
`--lcov`. This matches the workflow in `doc/testing/testing.md`. For local
iteration the developer typically already has `coverage/lcov.info` from a
prior run.

`--no-run` mode: accept a pre-existing lcov file and skip `flutter test`.
Pattern: `scripts/quality/check_critical_path_coverage.py --lcov coverage/lcov.info`.

## Acceptance-criteria mapping

| AC | Deliverable |
|----|-------------|
| Doc lists paths with rationale | `doc/testing/critical_paths.md` (this plan above maps each category) |
| Script exists and runs | `scripts/quality/check_critical_path_coverage.py` |
| Baseline recorded | `2026-05-16_02_protocol_baseline-coverage.md` (next file in this folder) |
| Remediation tasks if <90 % | Decision deferred until baseline is measured |
| Script invocation noted | Recorded in baseline protocol so TASK-PROC-046-06 can lift it verbatim |

## Out of scope (per goal.md)

- Writing new tests to fix any baseline shortfall.
- Mutation testing — handled by REQ-PROC-002 AC-02.
- CLAUDE.md update — TASK-PROC-046-06.
