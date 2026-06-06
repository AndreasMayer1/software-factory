# Audit Findings — REQ-PROC-052 Forbidden-Pattern Gates

Date: 2026-05-18
Task: TASK-PROC-052-02
Auditor: automated session 42e99c84
Raw gate output: [2026-05-18_quality_gates_raw_output.txt](2026-05-18_quality_gates_raw_output.txt)

## Summary

| Gate | Status | Violations | Notes |
|---|---|---|---|
| SP1 No network I/O | PASS | 0 | `lib/` clean |
| SP2 No telemetry SDKs | PASS | 0 | `pubspec.yaml` clean |
| SP3 No hardcoded secrets | PASS | 0 | 0 candidate matches |
| SP4 No weak crypto in security paths | PASS | 0 | No unjustified SHA-1/MD5 in `lib/` |
| SP6 Synthetic test data only | **FAIL** | 4 sites (≈12 occurrences) | Real-looking German/English personal names paired with mental-health labels; details below |
| SP5 PII redaction in `toString()` | (out of scope here — handled by TASK-PROC-052-03) | — | — |

Out-of-scope sibling gates that the aggregator also reported (REQ-PROC-046, not REQ-PROC-052): AC11 suppression-justification FAIL (6); AC12 no-debug-artifacts FAIL (5). Recorded for awareness only — remediation is a REQ-PROC-046 concern.

## SP1 — No network I/O

PASS. `check_no_network_io.sh` reports 0 matches in `lib/` for `package:http`, `package:dio`, `dart:io` `HttpClient`/`Socket`/`WebSocket`, `package:web_socket_channel`. The QR-only architecture holds.

No remediation needed.

## SP2 — No telemetry SDKs

PASS. `check_no_telemetry_sdks.py` reports `pubspec.yaml` clean against the named SDK list (Firebase Analytics/Crashlytics, Sentry, Mixpanel, Amplitude, Adjust, AppsFlyer, OneSignal, Bugsnag).

No remediation needed.

## SP3 — No hardcoded secrets

PASS. `check_no_hardcoded_secrets.sh` reports 0 candidate matches against the regex set (API keys, JWT, RSA/SSH private keys, AWS access keys, OAuth tokens).

No remediation needed.

## SP4 — No weak crypto in security paths

PASS. `check_weak_crypto.sh` reports 0 unjustified uses of SHA-1 / MD5 from `package:crypto` in `lib/`. There are no security-context uses today; the gate runs forward-looking against REQ-FUNC-006's encryption code once it lands.

No remediation needed.

## SP6 — Synthetic test data only — FAIL

The aggregator does not run an automated SP6 gate (no script exists yet); this is a manual review per the task scope. Findings below.

REQ-PROC-052 §Forbidden-Pattern Gates row SP6 and §Examples Example 5 define the test: fixtures must be **visibly synthetic**. The canonical pass example is `Lorem Ipsum`; the canonical fail example is `Sarah Müller` with a real-looking DOB. The findings below all match the fail-pattern shape: realistic Western/German personal names, in some cases paired with mental-health condition labels.

Persona cross-reference: none of the names below match persona file names under `requirements_user_needs/personas/` — these are not persona-derived test data; they appear to be plausibly-realistic names invented by the LLM/developer during scaffolding.

### V1 — In-app demo data: `lib/features/therapist/clients/presentation/bloc/therapist_clients_bloc.dart` (LINES 41, 48, 55)

```dart
final dummyClients = [
  { 'id': '1', 'title': 'Peter Wummer',        'description': 'Anxiety Management Client',   ... },
  { 'id': '2', 'title': 'Frederike Sorgenfrei','description': 'Depression Recovery Client',  ... },
  { 'id': '3', 'title': 'Klaus Winter',        'description': 'Stress Reduction Client',     ... },
];
```

Severity: **HIGH** — this is the worst single finding in the audit.
- The data lives in `lib/` (in-app demo path), not `test/`.
- Each name is a plausible German person identity (`Peter Wummer`, `Klaus Winter`) or surname (`Frederike Sorgenfrei`).
- Each is **paired with a mental-health condition label** — exactly the production-data shape that SP6 was written to keep out of the repository. A reader cannot distinguish this fixture from production data visually.
- Three integration tests assert against `find.text('Peter Wummer')` — they will need a parallel update when the source data is replaced (see V4).

Recommended remediation: replace with visibly-synthetic Latin pseudonyms and remove diagnosis labels from the demo content. E.g. `Lorem Ipsum / Sample Client / —` (description field can read `Demo Client` rather than a clinical label). Cascade-update the three integration tests that reference the names.

Effort: **S** — single file rewrite + 3 integration-test string updates (~10–20 lines total).

### V2 — Unit test fixtures: `test/unit/core/data/repositories/drift_contact_repository_test.dart` (LINES 14, 77, 115, 166, 168, 174, 183)

```dart
String name = 'Dr. Müller',                              // line 14 — default fixture name
final updated = makeContact(name: 'Dr. Schmidt');        // line 77
final contact2 = makeContact(therapistId: 'therapist-2', name: 'Dr. Meier');   // line 115
                therapistId: 'therapist-2', name: 'Dr. Schmidt',               // line 166
                therapistId: 'therapist-3', name: 'Anna Müller',               // line 168
// Lowercase partial search that matches 'Dr. Müller' and 'Anna Müller'        // line 174
expect(names, containsAll(['Dr. Müller', 'Anna Müller']));                     // line 183
```

Severity: **HIGH** — `Anna Müller` is structurally identical to the requirement's own fail-example (`Sarah Müller`). The other names (`Müller`, `Schmidt`, `Meier`) are among the most common German surnames; combined with `Dr.` they read as real therapist identities.

Recommended remediation: replace with Latin pseudonym + role indicator. Suggested mapping:
- `Dr. Müller`  → `Dr. Ipsum`
- `Dr. Schmidt` → `Dr. Lorem`
- `Dr. Meier`   → `Dr. Dolor`
- `Anna Müller` → `Ipsum Lorem` (or `Test Client Two` — the test needs two names that share a substring for the `containsAll` assertion at line 183; pick pseudonyms that preserve the substring property used by the lowercase-partial-search test).

Effort: **S** — single test file, but the substring-search test at L174/L183 requires the replacement pair to share a substring; remediation must preserve that property.

### V3 — Unit test fixtures: `test/unit/core/domain/entities/contact_test.dart` (LINES 11, 33, 71, 122)

```dart
String name = 'Dr. Smith',                         // line 11 — default
final differentName = makeContact(name: 'Dr. Jones');   // line 33
final changedName = original.copyWith(name: 'Dr. Brown'); // line 71
name: 'Dr. Smith',                                 // line 122
```

Severity: **MEDIUM** — common English surnames, no diagnosis pairing. Less "real-looking" than V1/V2 but still ambiguous (`Dr. Smith` could be a real therapist; SP6 requires the fixture to *signal* "this is a test"). The requirement's standard is recognizably synthetic, not just statistically anonymous.

Recommended remediation: `Dr. Smith` → `Dr. Ipsum`; `Dr. Jones` → `Dr. Dolor`; `Dr. Brown` → `Dr. Lorem`.

Effort: **S** — single test file, mechanical rename.

### V4 — QR payload test: `test/unit/core/data/models/pairing_qr_payload_test.dart` (LINE 9)

```dart
const therapistName = 'Dr. Müller';
```

Severity: **MEDIUM** — same shape as V2 but isolated to a single constant.

Recommended remediation: rename to `Dr. Ipsum` (consistent with the V2 mapping).

Effort: **XS** — one-line change.

### V5 — Integration-test references to V1's demo data

```text
integration_test/impl/therapist_clients_large_screen_layout_test.dart:125
integration_test/impl/therapist_clients_placeholder_verification_test.dart:114
integration_test/impl/therapist_clients_small_screen_nav_test.dart:122
   await tester.tap(find.text('Peter Wummer').first); // Use dummy data name
```

Severity: **LOW** — these are *references* to V1's strings, not independent fixtures. They become outdated automatically when V1 is fixed. Listed for traceability.

Recommended remediation: update simultaneously with V1; the comment `// Use dummy data name` is already correctly framed and only the literal needs to change.

Effort: rolled into V1.

### SP6 items checked and CLEAR

- `DateTime(…)` literals in `test/`: 40+ occurrences scanned. All are plan-period dates (2024–2027 year/month boundaries) or short time-of-day values. None are DOB-shaped (`DateTime(1987, 3, 14)`) or otherwise person-identifying.
- No email-address literals (`@gmail.com`, `@web.de`, etc.) found in `lib/`, `test/`, or `integration_test/`.
- No phone-number-shaped strings in fixture contexts.
- `lib/features/therapist/plan_templates/presentation/mock/mock_plans.dart` (mock questionnaire/plan data): contains questionnaire **prompts** (`'Write a brief journal entry about your day.'`), not user *responses*. Prompts are app-authored UI content, not PII fixtures. CLEAR.
- `figma/screens/therapist/clients/{mobile,medium,large}.dart` also references `Klaus Winter`. `figma/` is design-system scaffolding outside `lib/`, `test/`, and `integration_test/` and therefore outside this audit's scope per REQ-PROC-052 §When This Requirement Applies. Flagged here for awareness — if the figma/ tree is exported into the production tree at any point, V1's remediation should be cascaded.

## SP5 — Out of scope for this audit

Handled directly by TASK-PROC-052-03 (toString redaction). One redaction test already exists for `Contact`: `test/unit/core/domain/entities/contact_tostring_redaction_test.dart`. TASK-PROC-052-03 will enumerate the full domain-type inventory and add the missing implementations and tests.

## Out-of-scope findings (sibling REQ-PROC-046 gates)

The aggregator script `scripts/quality/check_quality_gates.sh` runs gates for both REQ-PROC-052 and REQ-PROC-046. The latter reported the following — recorded here for traceability, but **not** remediation targets for this task / requirement:

- **AC11 (suppression justification)**: 6 unjustified `// ignore:` directives across `lib/features/therapist/clients/presentation/bloc/therapist_clients_bloc.dart`, `lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart`, and one test file. These should be addressed by a REQ-PROC-046 remediation task (not by this audit).
- **AC12 (no-debug-artifacts)**: 5 `debugPrint` calls without the `[DIAG-*]` bracketed prefix required by CLAUDE.md bugfix conventions. Same: REQ-PROC-046 territory.

## Backfill-creator handoff (TASK-PROC-052-04)

If TASK-PROC-052-04 exists, the following remediation tasks should be scheduled:

| # | Scope | Files | Effort | Priority |
|---|---|---|---|---|
| R1 | Replace demo-client fixture (V1) and cascade-update integration tests (V5) | `lib/features/therapist/clients/presentation/bloc/therapist_clients_bloc.dart` + 3 files under `integration_test/impl/therapist_clients_*.dart` | S | HIGH (demo data with diagnosis labels — closest to production-shaped PII) |
| R2 | Replace contact-repository fixture names (V2), preserving substring property for the partial-search test at L174/L183 | `test/unit/core/data/repositories/drift_contact_repository_test.dart` | S | HIGH |
| R3 | Replace contact-entity fixture names (V3) | `test/unit/core/domain/entities/contact_test.dart` | S | MEDIUM |
| R4 | Replace QR-payload therapist name constant (V4) | `test/unit/core/data/models/pairing_qr_payload_test.dart` | XS | MEDIUM |

Total estimated effort: **S** (all four bundled into one remediation task is reasonable — ~6 files, ~15–20 lines of edits, no logic changes).

If TASK-PROC-052-04 has not yet been created, this audit is the input it needs.

## Audit completeness statement

All four in-scope dimensions (SP1, SP2, SP3, SP4) executed via the automated gate aggregator at `scripts/quality/check_quality_gates.sh` on 2026-05-18 against the current `develop` tree. SP6 audited manually via:

- grep for `DateTime(YYYY, …)` literals across `test/`, `integration_test/`
- grep for `name:`/`title:`/`displayName`/`firstName`/`lastName` assignments to string literals across `test/`, `integration_test/`, and `lib/` mock/seed paths
- grep for common German + English first/last-name lexicon across all `.dart` files
- grep for email-, phone-, and journal-entry-shaped string literals
- cross-reference against `requirements_user_needs/personas/` directory names (no matches — names are not persona-derived)

Audit findings are recorded in this file. Raw aggregator output is preserved at `2026-05-18_quality_gates_raw_output.txt` in this directory.
