---
task_id: TASK-PROC-052-01
type: impl
parent_requirement: REQ-PROC-052
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: completed
effort: M
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T11:57:43Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-11]
  sections: []
scope_description: "Add a set of grep / script gates that enforce the forbidden patterns of REQ-PROC-052 — no network I/O, no telemetry SDKs, no hardcoded secrets, no weak crypto in security paths — plus REQ-PROC-046's suppression-justification check and debug-artifact check, all under scripts/quality/."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 0d14ba6e-71af-4032-8373-440b871c0185
session_account: gmail
---
# Goal: Set up forbidden-pattern grep scripts

## Objective

REQ-PROC-052 SP1, SP2, SP3, SP4 — and REQ-PROC-046 G5 (suppression discipline, AC-11) and AC-12 (no leftover debug artifacts) — are all best detected by grep / pattern scans rather than the analyzer. This task creates the script set under `scripts/quality/` and produces a single `check_quality_gates.sh` (or `.py`) entry point that runs them all and reports pass/fail per gate.

## Requirements Summary

REQ-PROC-052 SP1 (no network I/O), SP2 (no telemetry SDKs), SP3 (no hardcoded secrets), SP4 (no weak crypto in security paths).
REQ-PROC-046 AC-11 (suppression-justification), AC-12 (no leftover debug artifacts).

Current requirements: ../../requirements.md

## Scope

### In Scope

Create individual scripts in `scripts/quality/`:

- **`check_no_network_io.sh`** — grep `lib/` for the Dart network-class entry points: `HttpClient(`, `Socket.connect`, `WebSocket.connect`, `package:http`, `package:dio`, `package:web_socket_channel`. Also grep our native source — `android/app/src/`, `ios/Runner/`, `windows/runner/`, **`packages/`** (custom C++ / native plugin code lives here per the project's monorepo layout) — for `OkHttp`, `URLSession`, `WinHTTP`, `libcurl`, `<winsock`, `boost::asio` (network includes). Skip vendor / pub-cache paths. Exits non-zero on any match.
- **`check_no_telemetry_sdks.py`** — parse `pubspec.yaml`, `android/app/build.gradle`, `android/build.gradle`, and `ios/Podfile`; assert no dependency / pod / Gradle entry matches the named SDK list (Firebase Analytics, Firebase Crashlytics, Sentry, Mixpanel, Amplitude, Adjust, AppsFlyer, OneSignal, Bugsnag) in any of the four. The forbidden list is a constant in the script.
- **`check_no_hardcoded_secrets.sh`** — adopt `gitleaks` if convenient; else regex scan against common patterns (API key prefixes, JWT shapes, RSA/SSH private key headers, AWS access keys, OAuth client IDs/secrets). Scans Dart sources, native sources (Kotlin / Swift / C++), and native config (`AndroidManifest.xml`, `Info.plist`, `*.gradle`, `Podfile`). Exits non-zero on any match.
- **`check_weak_crypto.sh`** — grep `lib/` for Dart-side weak-crypto patterns: `sha1.convert`, `md5.convert`, `Sha1`, `Md5`. Also grep our native source for: `MessageDigest.getInstance("SHA1"|"MD5")` (Kotlin/Java), `CC_MD5` / `CC_SHA1` (Obj-C), `MD5_*` / `SHA1_*` from OpenSSL or `<openssl/md5.h>` / `<openssl/sha.h>` (C++). For each match, verify an adjacent justification comment exists (per SP4 rule). Exits non-zero on missing justification.
- **`check_suppression_justification.sh`** — grep `lib/`, `test/`, `integration_test/` for `// ignore:` and `// ignore_for_file:`; for each, verify an adjacent comment line exists with non-trivial content. Exits non-zero on any unjustified suppression.
- **`check_no_debug_artifacts.sh`** — grep `lib/` for `print(`, `debugPrint(` (without `[DIAG-*]` prefix), `// TEMPORARY:`. Exclude files whose paths match an active bugfix-task allow-list (read from `automation/state.json` or similar; or accept the limitation that this only catches violations outside bugfix tasks).
- **`check_quality_gates.sh`** — entry point that runs all the above and produces a summary report (pass/fail per gate).

### Out of Scope

- Running the full audit and resolving findings — that's TASK-PROC-052-02 (audit) and any remediation tasks it spawns.
- Hooking these into pre-commit hooks. The scripts must be stable and runnable; how they're invoked is part of TASK-PROC-046-06 (CLAUDE.md update).

## Acceptance Criteria

- [x] All six individual scripts exist under `scripts/quality/` and are executable.
- [x] `check_quality_gates.sh` runs all six and produces a clear pass/fail summary.
- [x] Each script exits 0 on pass and non-zero with a clear failure message on fail.
- [x] The forbidden-SDK list inside `check_no_telemetry_sdks.py` matches the list in REQ-PROC-052 AC-02 verbatim (so divergence is impossible).
- [x] Scripts are documented in `scripts/quality/README.md` (one paragraph per script: what it checks, exit codes, how to read the output).
- [x] The scripts are added to `.claude/settings.json` permissions allow-list if needed (so the LLM can run them without prompting).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

These are pattern-matching gates. They will produce false positives (e.g. a `package:http` import inside `test/helpers/` for a mock server). Each script should support an `--exclude-paths` flag or read an exclusion config file so legitimate exceptions can be encoded once.

Per `claude-write-script` skill, scripts go under `scripts/[domain]/`. The right domain folder is debatable — `scripts/quality/` is suggested but `scripts/util/` is also reasonable. Pick consistently with the existing script structure (`scripts/validate_scripts_org.py` reports current organization).
