---
id: REQ-PROC-052
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: active
effort: M
stakeholder: app_provider
created: 2026-05-10
updated: 2026-05-10
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "`lib/` contains zero direct network I/O — no use of `package:http`, `package:dio`, `dart:io`'s `HttpClient`/`Socket`/`WebSocket`, or any other library that opens a network connection. Inter-device data transfer occurs only through the QR-code mechanism (screen-to-camera). Adding any network capability is a deliberate change to this requirement."
    - id: AC-02
      text: "`pubspec.yaml` contains zero dependencies on telemetry, analytics, or crash-reporting SDKs that transmit data off-device — Firebase Analytics, Firebase Crashlytics, Sentry, Mixpanel, Amplitude, Adjust, AppsFlyer, OneSignal, Bugsnag, and equivalents. Adding any such dependency is a deliberate change to this requirement."
    - id: AC-03
      text: "`lib/`, `test/`, `integration_test/`, `pubspec.yaml`, and `analysis_options.yaml` contain zero hardcoded credentials, API keys, OAuth secrets, JWT tokens, or private keys (PEM, PKCS, SSH). The repository scan against common secret patterns (`gitleaks`-equivalent regex set) returns zero matches."
    - id: AC-04
      text: "`SHA-1` and `MD5` from `package:crypto` are not used for password hashing, key derivation, MACs, signatures, or any other security primitive. Any non-security use (e.g. file-content checksum, cache key) is accompanied by an adjacent inline justification comment naming the non-security purpose."
    - id: AC-05
      text: "Domain types that hold user-entered mental-health content (entries, notes, mood values, plans, and any value object containing user free text) override `toString()` to return a redacted form that does not include the user content. Unit tests assert that `toString()` of an instance constructed with known sentinel content does not contain that content."
    - id: AC-06
      text: "Logger calls (`debugPrint`, project logger facade, `print`-by-mistake) under `lib/` never include domain entity instances or value-object content as arguments without first passing through the redacted `toString()` of AC-05; logging arguments restricted to identifiers, counts, durations, status codes, and other non-content metadata."
    - id: AC-07
      text: "Test fixtures and seed data under `test/`, `integration_test/`, and any in-app demo/seed contain only synthetic content: no real names, real dates of birth, real addresses, or real-looking mental-health entries. Synthetic content is recognizably synthetic (Latin pseudonyms, placeholder dates, content that signals 'this is a test') so it cannot be mistaken for production data."
    - id: AC-08
      text: "Cryptographic key material (master keys, derived keys, key-encryption keys) is obtained only via the platform secure-storage abstraction (Android Keystore, iOS Keychain, Windows DPAPI, or the project's wrapper around them) and is never written to a plain file, the SQLite database, `SharedPreferences`, or any other unsecured storage."
    - id: AC-09
      text: "Code that fails any active gate in this requirement is never declared complete: gate failures trigger a revision cycle under the same five-cycle back-pressure protocol defined in REQ-PROC-046, with escalation to the user on irrecoverable failure."
    - id: AC-10
      text: "The active set of privacy / security gates and the allow-list for any deliberate exceptions (e.g. permitted non-security uses of `SHA-1`) are documented in a single authoritative location consistent with this requirement — a contributor or LLM agent can determine, without asking, what is forbidden and what is allowed."
---

# Privacy & Security Hygiene (LLM Back-Pressure Gates)

## Overview

This requirement defines what code in this project is **forbidden from doing** with respect to user privacy and cryptographic correctness. Where REQ-PROC-046 (Code Quality) describes the shape good code must have, this requirement describes the categories of code that must never exist in the repository. Gates are enforced through the same back-pressure protocol: an LLM cannot declare a code change complete while any forbidden pattern is present.

## Purpose

The app provider (PERSONA-015) holds privacy as a structural commitment, not a configurable preference. The persona's grounded values are unambiguous:

- *"Data never leaves the device unless the user explicitly exports it. No server. No 'optional' telemetry. No crash reporting that phones home."*
- *"No analytics, no usage tracking, no 'anonymized' behavioral data. The creator does not know how many users exist, and that is by design."*
- *"This app is a self-observation tool, not a medical device."* — and yet the data it stores is among the most sensitive a person produces.

The system / maintenance constraints (PERSONA-004) reinforce the same axis: *"data must be encrypted at rest (device encryption alone not sufficient for medical data)"*; *"backup encryption: any exported backups must be encrypted."*

In a project where most code is now produced by LLM agents, these commitments are systemically at risk. An LLM trained on conventional industry codebases has seen Firebase Analytics, Crashlytics, Sentry, and `http.get` thousands of times more often than it has seen the explicit *absence* of those things. Without a contractual gate, an LLM will eventually — in good faith — add a "helpful" crash reporter, a "lightweight" telemetry hook, or a `print(entry.text)` for debugging that never gets removed. Each of these would silently violate the persona's most fundamental promise to its users.

This requirement turns the persona's privacy commitments into machine-checkable forbidden patterns. The gates do not prevent functionality; they prevent inadvertent erosion of the architectural privacy guarantee that the app's users — many of whom are reluctant to engage with mental-health technology in the first place — are relying on.

## When This Requirement Applies

- Any change to Dart code under `lib/`, `test/`, or `integration_test/`.
- Any change to native source we write or modify: Kotlin/Java under `android/app/src/`, Swift/Obj-C under `ios/Runner/`, C++ under `windows/runner/`, and any custom native code under `packages/` (the project's monorepo layout for custom plugin / native modifications).
- Any change to native build files we configure: `android/app/build.gradle`, `android/build.gradle`, `ios/Podfile`, `ios/Runner/Info.plist`, `windows/CMakeLists.txt`.
- Any change to `pubspec.yaml`, `pubspec.lock`, or `analysis_options.yaml`.
- Any change to test fixtures and seed data.
- Before a task is marked complete (via `task-complete` or otherwise).
- Before a commit is created on `develop`.

## When This Requirement Does NOT Apply

- Documentation under `doc/`, `requirements_tasks/`, `requirements_user_needs/`, `.claude/`.
- Process artifacts (skills, plans, protocols).
- Generated files (`*.g.dart`, `*.freezed.dart`).
- Synthetic example data presented in `doc/` examples (these are not loaded into the app).

## Behavior

### The Forbidden-Pattern Gates

Six gates are active. Each is binary (pass / fail) and detectable from a clean checkout via grep, dependency inspection, or targeted unit tests:

| Gate | Detection | Pass condition |
|---|---|---|
| **SP1 No network I/O** | grep `lib/` for `package:http`, `package:dio`, `dart:io` `HttpClient` / `Socket` / `WebSocket`, `package:web_socket_channel`, etc. | Zero matches in `lib/`. Inter-device transfer is QR-only. |
| **SP2 No telemetry SDKs** | parse `pubspec.yaml` against the named SDK list (Firebase Analytics, Firebase Crashlytics, Sentry, Mixpanel, Amplitude, Adjust, AppsFlyer, OneSignal, Bugsnag, and any future entries added to the list). | Zero matches. |
| **SP3 No hardcoded secrets** | regex scan of repository for common credential patterns (API keys, JWT, RSA / SSH private keys, AWS access keys, OAuth tokens). | Zero matches. |
| **SP4 No weak crypto in security paths** | grep for `sha1` / `md5` from `package:crypto` in any file. Each match reviewed for security-context use. | No security-context use; non-security use justified inline. |
| **SP5 PII redaction in `toString()`** | unit tests on domain types asserting that `toString()` of a sentinel-content instance does not contain that content. | All affected types pass. |
| **SP6 Synthetic test data only** | review of test fixtures and seed data; named patterns that flag real-looking PII (real-looking names, real-looking dates of birth, real-looking journal entries). | All fixtures recognizably synthetic. |

The gate set is closed: a privacy / security property is either represented by one of these gates or by another active requirement. Adding or removing a gate is itself a change that must update this document.

### The Back-Pressure Protocol

The same protocol as REQ-PROC-046 applies: per-change self-check, all gates re-run after each revision, five-cycle iteration bound, escalation on unresolved failure. This requirement does not redefine the protocol; it inherits it.

### Native Code Scope

The forbidden-pattern gates apply to native source we write or modify in exactly the same spirit as Dart code, with these clarifications:

- **SP1 (no network I/O)**: in our native source (Kotlin / Swift / C++ under the paths in §When This Requirement Applies), no `OkHttp`, `URLSession`, `WinHTTP`, `libcurl`, `boost::asio` (network), or `<winsock>` usage. Plugin source code outside our control lives in `~/.pub-cache/` and is governed by SP2 at the dependency level rather than line-by-line.
- **SP2 (no telemetry SDKs)**: extends to direct Android dependencies declared in `android/app/build.gradle` and direct iOS pods in `ios/Podfile` that bypass `pubspec.yaml`. The forbidden-SDK list is the same — Firebase Analytics, Crashlytics, Sentry, etc. — applied to whichever build file declares them.
- **SP3 (no hardcoded secrets)**: applies to all source files regardless of language. API keys leaked in `AndroidManifest.xml`, `Info.plist`, `*.gradle`, or C++ headers are gate failures.
- **SP4 (no weak crypto in security paths)**: extends to native crypto APIs (`javax.crypto.MessageDigest.getInstance("SHA1")` in Kotlin, `CC_MD5` in iOS, OpenSSL `MD5_*` in C++). The "non-security use with justification" exception applies the same way.
- **SP5 (PII redaction in `toString()`)**: Dart-only — native types do not log Dart-side mental-health content under normal architecture (method-channel boundaries don't carry it through).
- **SP6 (synthetic test data)**: native test fixtures (Espresso, XCTest, Google Test) are subject to the same rule. In practice we have none today; the rule applies if/when they're added.

### Exception Handling

Each forbidden pattern has a precise semantics for exceptions:

- **SP1 (network I/O)**: there is currently no allow-list. If a future feature legitimately requires a network call, the requirement is updated to define the allow-list scope (path, host, purpose) and the gate is reconfigured. Adding network code without that update is a gate failure.
- **SP2 (telemetry SDKs)**: no exceptions. Any SDK that transmits data off-device — even "optional crash reporting" — is forbidden.
- **SP3 (hardcoded secrets)**: no exceptions. Test fixtures may include patterns that *resemble* credentials only if they are obviously synthetic (e.g. `"sk-test-XXXXXXXX"`) and the file is excluded from the secret scan via a documented pattern.
- **SP4 (weak crypto)**: SHA-1 / MD5 are permissible for non-security purposes (file-content checksums, cache keys). The use must carry an adjacent justification comment naming the non-security purpose, or it fails the gate.
- **SP5 (PII in `toString()`)**: domain types whose constructors are unreachable in production (e.g. test-only types, debugging-only types) are exempt. The exemption must be visible in the type's documentation, and the type must not be referenced from `lib/`.
- **SP6 (synthetic test data)**: no exceptions. If real data is needed for a specific reproduction (e.g. a bug report submitted by a user), it lives only in the `plans_and_protocols/` of the relevant bugfix task and is destroyed on task completion — never in `test/` or `integration_test/`.

## Examples

**Example 1: SP1 — the QR transfer pipeline is the boundary**

The data-transfer pipeline (REQ-FUNC-007) moves plans and entries between therapist and client devices through animated QR codes — screen-to-camera optical transmission, not network. This is the deliberate architectural choice that makes SP1 enforceable: there is no permitted code path in `lib/` that opens a TCP connection. If a future feature were to require, for example, optional cloud backup, that would not be a small implementation choice — it would be a contractual change to this requirement's allow-list, visible to any reviewer.

**Example 2: SP2 — the absence of crash reporting is the contract**

Industry default is to ship a crash reporter (Crashlytics, Sentry) with every app. PERSONA-015 explicitly rejects this: *"no crash reporting that phones home."* SP2 keeps the contract enforceable: an LLM that adds Crashlytics to `pubspec.yaml` to "improve reliability" fails SP2 immediately, before the code ever runs.

**Example 3: SP4 — SHA-1 is fine for cache keys, not for password hashing**

`final cacheKey = sha1.convert(utf8.encode(query)).toString();` is permissible if accompanied by `// SHA-1 used for cache key (non-security: collision resistance not required)`. `final passwordHash = sha1.convert(utf8.encode(password));` is a gate failure — that is a security context where SHA-1 is broken.

**Example 4: SP5 — `toString()` redaction makes logging safe**

The redaction pattern (illustrative — applied to whichever concrete domain types end up holding user-entered content; the inventory is the responsibility of TASK-PROC-052-03):

```dart
@override
String toString() =>
    '$runtimeType(id: $id, createdAt: $createdAt, contentLength: ${content.length})';
```

A unit test constructs an instance with content `'__SENTINEL_CONTENT_DO_NOT_LEAK__'` and asserts `instance.toString()` does not contain that string. Once SP5 is satisfied, AC-06 logging restrictions become enforceable in practice — the developer (or the LLM) does not have to remember to redact at every call site, because the type already does.

**Example 5: SP6 — fixtures are visibly synthetic**

```dart
final testEntries = [
  JournalEntry(authorName: 'Lorem Ipsum', dob: DateTime(2000, 1, 1), content: 'Sample mood content for testing.'),
  JournalEntry(authorName: 'Test User Two', dob: DateTime(2000, 1, 2), content: 'Another sample entry.'),
];
```

A fixture using a real-looking name (`'Sarah Müller'`), a real-looking DOB (`DateTime(1987, 3, 14)`), and prose that reads like a real journal entry would fail SP6 — even if the data is technically fabricated, the fixture cannot be visually distinguished from real production data, and the cost of that ambiguity is high.

## Developer Guidelines

> Constraints and invariants the final code must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **Privacy is enforced by absence, not by configuration.** SP1 and SP2 work because the forbidden code does not exist in the repository. There is no "production switch" that turns telemetry on; turning it on would require modifying the gate, which would be visible.
- **The QR-transfer pipeline is the only data-export channel in code.** Anything that looks like a network call is a gate failure unless this requirement has been updated to permit it.
- **`toString()` redaction is a structural defense, not a per-call-site discipline.** AC-05 makes the type itself safe to log; AC-06 keeps the discipline at call sites. Both layers exist because either alone has known failure modes.
- **Test fixtures are read by the LLM as examples to emulate.** A fixture that contains real-looking journal content would prime the LLM to produce more such content elsewhere. Fixtures must be visibly synthetic so the LLM, when looking for examples, sees the convention.
- **Gates inherit REQ-PROC-046's back-pressure mechanism.** This requirement does not duplicate the five-cycle protocol; failures here trigger the same revision loop.

### Common Pitfalls

- **"Optional" telemetry**: an LLM may add a flag-gated SDK (`if (kDebugMode) Sentry.init(...)`) on the assumption that a debug-only crash reporter is harmless. SP2 is unconditional — the SDK in `pubspec.yaml` is the gate failure, not the runtime use.
- **`debugPrint(entry.toString())` after a typed `toString()` is added but not yet redacted**: AC-05 must land before AC-06 is meaningful. Adding a logging convention before the types are safe to log is the wrong order.
- **Cache keys vs MAC**: SHA-1 of a query string for a cache key is fine; SHA-1 of a session token to detect tampering is not. The distinction is the use, not the algorithm — AC-04 requires an inline justification that names the non-security purpose so the use is auditable.
- **Synthetic-looking data that is actually real**: a bug report from a real user is real PII even if it's been "lightly modified." Such data belongs in `plans_and_protocols/` of the bugfix task, never in `test/`, and is destroyed when the task completes.
- **Adding `dart:io` `HttpClient` for "local server" testing**: a local development server is still network code under SP1. Test infrastructure that needs an HTTP server lives outside `lib/` (e.g. `test/helpers/` with a clear isolation), not in production code.

## Related Requirements

- **REQ-PROC-046 (Code Quality Standard)** — sibling. Together they form the full code-correctness contract for LLM-produced code: REQ-PROC-046 covers what good code *looks like*; this requirement covers what code is *forbidden from doing*.
- **REQ-FUNC-006 (Cryptographic specification — Argon2id)** — the source of the project's cryptographic primitives; AC-04 and AC-08 align with its choices. Note: REQ-FUNC-006 is specified but not yet implemented in `lib/`; AC-04 and AC-08 are forward-looking until that code lands. Their gates run today against the (currently empty) set of security-context files and become more meaningful as encryption and key-derivation are implemented.
- **REQ-FUNC-007 (Data transfer)** — the QR-only inter-device transfer mechanism that makes SP1 enforceable.
- **REQ-NFUNC-009 (Immediate destruction / no-undo)** — relates to the data-destruction angle that complements SP6 (synthetic test data).

## References

- `requirements_user_needs/personas/app_provider/persona.md` — source of the privacy commitments encoded as gates here
- `requirements_user_needs/personas/system_maintenance/persona.md` — source of the data-sensitivity constraints
- `pubspec.yaml` — the dependency set whose composition AC-02 governs
- `analysis_options.yaml` — host of the static-detection rules where automated portions of these gates live
- `CLAUDE.md` — operational checklist; bugfix conventions referenced for SP6 exception
