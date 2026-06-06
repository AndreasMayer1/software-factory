# Pilot baseline — TASK-PROC-052-01 grep-gate scripts

**Date:** 2026-05-10
**Task:** TASK-PROC-052-01 — Set up forbidden-pattern grep scripts
**Scope:** Six grep/script gates plus an aggregate entry point under
`scripts/quality/`, run once each against `develop` HEAD as the baseline.

This report is a derisking pilot: the question it answers is *not* "do the
gates work in principle" but "do they survive contact with the actual
codebase, or do they produce so many false positives / requirement drift
that the grep approach is the wrong tool".

---

## 1. Inventory

All scripts live under `/workspaces/private_mood_tracker/flutter_app/scripts/quality/`.

| Script | Gate | One-line description |
|---|---|---|
| `check_no_network_io.sh` | REQ-PROC-052 SP1 | Greps `lib/` for HTTP / socket / WebSocket entry points (`package:http`, `package:dio`, `package:web_socket_channel`, `HttpClient(`, `Socket.connect`, `WebSocket.connect`, `HttpServer.bind`, etc.). Bare `import 'dart:io';` is intentionally NOT flagged because it also exposes File / Directory / Platform; the gate targets only the network surfaces of `dart:io`. |
| `check_no_telemetry_sdks.py` | REQ-PROC-052 SP2 | Parses `pubspec.yaml`'s three dependency sections and asserts no entry matches the AC-02 forbidden-SDK list (Firebase Analytics / Crashlytics, Sentry, Mixpanel, Amplitude, Adjust, AppsFlyer, OneSignal, Bugsnag). The list is encoded verbatim as the constant `FORBIDDEN_SDKS` so divergence from the requirement is impossible. |
| `check_no_hardcoded_secrets.sh` | REQ-PROC-052 SP3 | Regex-scans `lib/`, `test/`, `integration_test/`, `pubspec.yaml`, `analysis_options.yaml` for AWS access keys, PEM/SSH private-key headers, JWT three-part tokens, generic `api_key=` / `client_secret=` patterns, Google API keys, Stripe live secrets, Slack tokens, GitHub PATs. Defers to `gitleaks` when available; falls back to in-script regex set. |
| `check_weak_crypto.sh` | REQ-PROC-052 SP4 | Greps `lib/` for `sha1` / `md5` / `Sha1` / `Md5` from `package:crypto`. For each match, requires an adjacent justification comment (within 2 lines, or trailing the same line) naming a non-security purpose. |
| `check_suppression_justification.sh` | REQ-PROC-046 AC-11 | Greps `lib/`, `test/`, `integration_test/` for `// ignore:` and `// ignore_for_file:` directives. Each must carry either a same-line trailing comment of ≥12 chars of content, or a preceding comment of similar substance within 2 lines. |
| `check_no_debug_artifacts.sh` | REQ-PROC-046 AC-12 | Greps `lib/` for bare `print(`, `debugPrint(` without a `[DIAG-*]` prefix in the message, and `// TEMPORARY:` markers. Comment-line mentions of these tokens are excluded. Does NOT consult `automation/state.json` for active bugfixes; the accepted limitation is that an in-flight bugfix uses `exclusions.txt` to silence the gate temporarily. |
| `check_quality_gates.sh` | (entry point) | Runs all six gates in sequence, streams each gate's full output, prints a single PASS/FAIL summary block. Exits 0 if all passed, 1 if any failed, 2 on a runner error. |
| `_lib.sh` | (helper) | Shared bash helpers: argument parsing for `--exclude-paths`, loading of `scripts/quality/exclusions.txt`, substring-match `is_excluded`. Sourced by every shell gate. |
| `exclusions.txt` | (config) | Canonical exclusion list. Empty by design at baseline — each future entry is documented technical debt against the gate's authority. |
| `README.md` | (docs) | One-paragraph description per gate plus exit-code convention and exclusion semantics. |

All scripts are executable (`chmod +x`) and accept the `--exclude-paths
<file>` flag. The Python script accepts it via argparse; shell scripts
parse it through `_lib.sh`.

---

## 2. Baseline results against current `develop` HEAD

| # | Gate | Result | Findings |
|---|---|---|---|
| 1 | SP1 no-network-io | **PASS** | 0 matches in `lib/`. |
| 2 | SP2 no-telemetry-sdks | **PASS** | `pubspec.yaml` clean. |
| 3 | SP3 no-hardcoded-secrets | **PASS** | 0 candidate matches across `lib/`, `test/`, `integration_test/`, `pubspec.yaml`, `analysis_options.yaml`. |
| 4 | SP4 no-weak-crypto | **PASS** | 0 unjustified uses in `lib/`. |
| 5 | AC-11 suppression-justification | **FAIL** | 1 finding. |
| 6 | AC-12 no-debug-artifacts | **FAIL** | 5 findings. |

Aggregate runner exits `1`. Full per-gate output is reproducible by running
`scripts/quality/check_quality_gates.sh` from the project root.

### 2.5 Detailed failure findings

**AC-11 (1 finding)**
- `test/unit/features/therapist/data_receive/presentation/screens/adaptive_scan_controller_test.dart:1`
  ```
  // ignore_for_file: invalid_use_of_visible_for_testing_member
  ```
  No preceding or trailing justification. The directive itself is
  reasonable (it's a test file accessing `@visibleForTesting` API), but the
  *why* is not recorded inline.

**AC-12 (5 findings, all `debugPrint` without `[DIAG-*]` prefix)**
- `lib/main.dart:66`
  ```dart
  debugPrint('Initialization error in main: $e\nStack trace:\n$s');
  ```
  Lines 61-65 already contain a multi-line `///` WHY comment justifying the
  `debugPrint` call as the sole pre-DI exception to the no-raw-print rule.
  The gate sees the call but does not understand WHY-comment justification.
- `lib/features/client/data_receive/presentation/screens/data_beam_scanner_screen.dart:240, 247, 307, 309`
  Four `debugPrint` calls using `[QR-Windows]` / `[QR-Android]` bracketed
  prefixes (clearly the same prefix-tagging discipline as `[DIAG-*]`, but
  semantically different — these are not bugfix-task diagnostics but
  long-lived runtime traces).

The two clusters are different in kind: the `main.dart` call is a justified
permanent-exception case; the four `data_beam_scanner_screen.dart` calls
are legitimately-prefixed but use a different prefix convention than
CLAUDE.md's `[DIAG-*]`.

---

## 3. Unexpected findings

**No real privacy/security violations were uncovered by the SP-gates** —
SP1, SP2, SP3, SP4 all clean. That is itself a useful result: the existing
codebase is already aligned with the persona's privacy commitments, so
landing the gates does not require remediation churn against existing code,
only enforcement going forward. The audit task TASK-PROC-052-02 will get a
green starting point.

**The two REQ-PROC-046 gates surfaced real, modest debt**:
1. One unjustified `// ignore_for_file:` in a test file.
2. The codebase has *two* prefixed-debugPrint conventions in active use —
   `[DIAG-*]` (per CLAUDE.md) and `[QR-Windows]` / `[QR-Android]` (in the
   QR-scanner screen). Either these long-lived traces should switch to
   `[DIAG-*]`, or CLAUDE.md should generalize the rule to "any bracketed
   `[TAG-*]` prefix is acceptable, with the bugfix-specific convention
   being `[DIAG-*]`". This is a doc-vs-code discrepancy worth raising
   to the user but is OUT OF SCOPE for this task — see § 6.
3. `lib/main.dart:66`'s justified `debugPrint` exception is a structural
   pattern the gate cannot encode without false positives. Adding it to
   `exclusions.txt` is the right answer; an entry of the form
   `lib/main.dart   # pre-DI initialization exception (REQ-NFUNC-..)`
   would silence the gate for that one line.

**No hardcoded-secret false positives.** This was the gate I most expected
to false-positive on (test fixtures, Drift schema strings, asset URIs,
flutter_zxing constants). Zero matches — pleasant surprise.

**No weak-crypto false positives.** Currently there's no `package:crypto`
usage in `lib/` at all (REQ-FUNC-006 cryptographic code is specified but
not yet implemented), so the gate runs against an empty target set. Its
real load-bearing test will come once Argon2id / KDF code lands.

---

## 4. Does the grep-gate approach hold up under contact with the codebase?

**Yes, with one caveat.** The pilot's findings split into three
qualitatively different categories, and each category responds to a clean
mechanism:

1. **True positives → fix the code.** AC-11's unjustified
   `// ignore_for_file:` is exactly what the gate should catch.
2. **Justified-by-context exceptions → exclusions.txt.** `lib/main.dart:66`
   is correctly debug-printing fatally-uninitialized state and the WHY is
   already documented above the call site. One exclusion entry, one line of
   reason — that's the entire cost.
3. **Convention drift → escalate.** The `[QR-Windows]` / `[QR-Android]`
   prefixes are not a bug; they're a sign that CLAUDE.md's `[DIAG-*]`
   convention has been generalized in practice without the doc following.
   The gate cannot resolve this; it correctly surfaces it for human review.

The exclusion list is empty at baseline (one entry needed once the user
approves silencing `lib/main.dart:66`). The gates are **not** producing
false-positive volume that would force the exclusion list to grow toward
unmanageability — that was the major risk this pilot was designed to test.

The one structural caveat is the `debugPrint`-prefix mismatch above. If
the project will continue to use prefix tags other than `[DIAG-*]`,
either:
- CLAUDE.md should be updated to permit any `[TAG-*]` bracketed prefix,
  in which case the gate's regex should match `\[[A-Z][A-Z0-9-]*-` instead
  of just `[DIAG-`, OR
- The four `[QR-*]` lines in `data_beam_scanner_screen.dart` should be
  retagged to `[DIAG-qr-windows]` / `[DIAG-qr-android]`.

This is a one-line decision for the user; the gate is correctly forcing it.

---

## 5. Verdict — should the user roll out the rest of the gate set the same way?

**Yes, recommend rolling out.** The pilot results support three
conclusions that make the case clear:

1. **Signal quality is high.** Six gates, six clean runs (excluding the
   two known-real findings). No spurious noise. The exclusion-list-as-debt
   model holds: at baseline it's empty, and the next entry it needs (the
   `main.dart` `debugPrint`) is genuinely the kind of one-off
   structural exception that exclusion lists are for.

2. **The pattern set is good enough to land.** SP3's regex set produced
   zero false positives across the entire repository — the highest-risk
   pattern surface in the gate suite. SP1 and SP4 currently scan against
   essentially-empty targets but the patterns are tight (HttpClient/
   Socket/WebSocket are unambiguous identifiers; `sha1`/`md5` from
   `package:crypto` likewise). Both will become more meaningful as
   REQ-FUNC-006 (crypto) and any future networking-adjacent code land —
   exactly when they're needed.

3. **The two AC-46 findings are exactly the value proposition.** The
   gates surfaced one missing justification comment and one CLAUDE.md /
   code drift — two issues that would not have been caught by code review
   on the next unrelated PR but would silently grow the implicit
   "things-we-do-but-don't-document" surface area.

**Two follow-up actions are implied but not in scope for this task:**
- Add `lib/main.dart` (or just the specific line range) to
  `scripts/quality/exclusions.txt` once the user approves it as a
  permitted exception. Do this BEFORE wiring the gate into a hook.
- Decide the `[DIAG-*]` vs general `[TAG-*]` question and either update
  CLAUDE.md or retag the four QR-scanner `debugPrint` lines.
- TASK-PROC-046-11 (hook wiring) and TASK-PROC-052-02 (audit) can both
  proceed.

The grep-gate approach derisks cleanly. Recommend roll-out.

---

## 6. Bonus — observations on the requirement / pattern set

These are observations the implementation surfaced; they are NOT changes
to REQ-PROC-052 and have not been applied. They are recorded here so the
user can decide whether to fold any of them back into the requirement
(via `requ-explore`).

### 6.1 SP1 pattern set

The goal.md text "`dart:io HttpClient`, `dart:io Socket`, `dart:io WebSocket`"
is more precise than a literal pattern of `dart:io`. The gate as
implemented matches the *constructor* and *static-method* surfaces
(`HttpClient(`, `Socket.connect`, `WebSocket.connect`, etc.), not the bare
`import 'dart:io';` directive. This is correct but worth noting in the
requirement: `dart:io` is a multi-purpose library and an import-line
pattern would false-positive on every legitimate File / Directory /
Platform / stdout user. Consider amending REQ-PROC-052 SP1's example list
to clarify "the *network* primitives of `dart:io`: `HttpClient`,
`HttpServer`, `Socket`, `ServerSocket`, `RawSocket`, `WebSocket`,
`SecureSocket`, `RawDatagramSocket`."

### 6.2 SP3 pattern improvements (not yet applied)

The current pattern set covers the most common shapes. Reasonable
additions for a future tightening pass:
- Slack webhook URLs (`https://hooks.slack.com/services/T[A-Z0-9]+/...`)
- Generic Bearer token in test fixtures (`Bearer [A-Za-z0-9_\-\.=]{30,}`)
- Base64-encoded private-key bodies (>200 chars of pure base64 inside a
  single-quoted Dart string)
- Twilio account SIDs / auth tokens

I have NOT added these — the current set already catches the AC-03
enumeration ("API keys, OAuth secrets, JWT tokens, private keys"), and
expanding the regex set without a real-world false-positive sample is
likely to over-fit. Surface here for the user's awareness.

### 6.3 SP4 justification keywords

The "is this a non-security justification?" check uses a regex on the
preceding two lines for keywords like `non-security`, `cache key`,
`checksum`, `integrity`, `fingerprint`. This is permissive by design (low
false-negative rate matters more than precision here — a false negative
ships a real weak-crypto-in-security-context bug). If the project's
naming evolves to use different phrasing, the keyword list will need to
grow; consider documenting the recognized phrases in REQ-PROC-052 SP4 so
contributors / LLMs use one of them deliberately rather than free-form.

### 6.4 AC-11 minimum justification length

Set to 12 characters. Filters `// x` and `// ok` but accepts any
real-content comment. If the team finds this too lenient (e.g.
`// fix that`-style placeholders slipping through), raising to 20-25
characters is a one-line edit. Document the threshold in REQ-PROC-046 if
it becomes load-bearing.

### 6.5 AC-12 prefix convention

As noted in §3, the codebase has both `[DIAG-*]` and `[QR-*]` prefixes in
active use. CLAUDE.md only specifies `[DIAG-*]`. Either:
- Generalize CLAUDE.md to "any bracketed `[TAG-*]` prefix where TAG names
  the diagnostic context", and update the gate's regex to
  `\[[A-Z][A-Z0-9_-]*-` (still fails bare `debugPrint`, still passes
  prefixed ones).
- Or rename the four `[QR-Windows]` / `[QR-Android]` lines to use
  `[DIAG-qr-windows]` / `[DIAG-qr-android]`.

Either is fine; both would close the convention drift.

### 6.6 AC-12 / `automation/state.json` integration

The goal.md note "read from `automation/state.json` or similar; or
accept the limitation that this only catches violations outside bugfix
tasks" was implemented as the latter. Reading active-bugfix paths from
the orchestrator state would be a one-day enhancement and is worth
considering once the gate is wired into the pre-commit hook —
specifically, the hook would consult `state.json` to know which task is
in flight and apply a temporary path-allowlist for that task's files
without polluting `exclusions.txt`. Out of scope here, but a clear
follow-up.

---

## 7. Files created / modified by this task

Created:
- `scripts/quality/_lib.sh`
- `scripts/quality/exclusions.txt`
- `scripts/quality/check_no_network_io.sh`
- `scripts/quality/check_no_telemetry_sdks.py`
- `scripts/quality/check_no_hardcoded_secrets.sh`
- `scripts/quality/check_weak_crypto.sh`
- `scripts/quality/check_suppression_justification.sh`
- `scripts/quality/check_no_debug_artifacts.sh`
- `scripts/quality/check_quality_gates.sh`
- `scripts/quality/README.md`
- `requirements_tasks/process/AI_rules/coding_standards/privacy_and_security/tasks/2026-05-10_impl_setup-forbidden-pattern-grep-scripts/plans_and_protocols/2026-05-10_01_pilot_baseline.md` (this file)

Modified: none.

Per task instructions, no commit was created and no hooks / settings /
CLAUDE.md were wired up — those belong to TASK-PROC-046-11.
