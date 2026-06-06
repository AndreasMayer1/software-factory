---
id: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: active
effort: L
stakeholder: app_provider
created: 2025-10-02
updated: 2026-05-10
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Every `test(...)` and `testWidgets(...)` body under `test/` and `integration_test/` contains at least one assertion (`expect`, `verify`, or equivalent matcher); zero `group(...)` bodies are empty; every exception assertion uses the `throwsA(...)` matcher form rather than a try/catch with a `fail()` call. Enforced by the custom test-smells script `scripts/quality/check_test_smells.sh` (TASK-PROC-046-14, post-DCM-removal) plus Dart's built-in `use_test_throws_matchers` lint via the analyzer."
    - id: AC-02
      text: "Code paths subject to REQ-PROC-046 AC-04 (encryption / decryption, Argon2id key derivation, atomic file rotation, version migration, data-transfer serialization) achieve ≥ 80 % mutation kill rate when measured by an AST-aware mutation tool (`mutation_test` or `dart_mutant`) scoped via lcov to those paths. Surviving mutants are either addressed by additional or stronger assertions, or documented in `doc/testing/` with a rationale that names why the mutant is benign."
    - id: AC-03
      text: "Every value object and entity in `lib/core/domain/` and `lib/features/*/domain/` whose contract includes any of (a) a bounded numeric range, (b) enum totality, (c) string length or format constraints, (d) ordering or comparison contract, (e) serialization round-trip, or (f) algebraic laws on aggregates (associativity, identity, commutativity), has at least one property-based test using `glados` (or an equivalent generator-based framework) exercising the relevant invariant."
    - id: AC-04
      text: "The full test suite (`flutter test`) passes when run with `--test-randomize-ordering-seed=random` (no test depends on ordering) and on 10 consecutive identical runs of the same revision (no flakes); both checks are exercised before any release-candidate is approved."
    - id: AC-05
      text: "Test names describe the behaviour under verification (`returns null when the entry is empty`, `rejects payloads larger than 64 KB`), not the method invoked (`testParseEntry`, `testEncrypt`); naming is the property of the test as written, not a separate documentation surface."
    - id: AC-06
      text: "Tests in `test/unit/` and `test/widget/` do not depend on real network I/O, real file system writes outside `path_provider`'s test mock or a per-test temp directory, real platform channels other than the standard mock, or wall-clock time without a controllable clock fake. Failure of any of these dependencies in CI never produces a green run on broken code."
    - id: AC-07
      text: "Failures from the test-quality gates (AC-01–AC-04) trigger the same five-cycle back-pressure revision protocol defined in REQ-PROC-046 §Back-Pressure Protocol; this requirement does not redefine the protocol, only its application surface."
    - id: AC-08
      text: "The active set of test-quality gates, the mutation-kill-rate threshold, the property-test inventory rule, and the deterministic-run policy are documented in a single authoritative location consistent with this requirement (`doc/testing/`) so that a contributor or LLM agent can determine, without asking, what 'a good test' means in measurable terms."
    - id: AC-09
      text: "Integration tests under `integration_test/` exist for: (a) the primary data-entry workflow — app launch through to a saved entry; (b) the data-transfer pipeline — sender + receiver; (c) the cold-start measurement (covers REQ-PROC-046 AC-08 cold-start portion); (d) the data-entry frame-budget measurement (covers REQ-PROC-046 AC-08 frame-budget portion); (e) any end-user-visible workflow whose underlying code is on the REQ-PROC-046 AC-04 critical-path list. Each integration test uses stable selectors (semantic labels and `Key`s, never raw display text) so that UI refactoring does not invalidate the test. Integration tests run per-release-candidate, not per-change."
---

# Test Quality Standard (LLM Back-Pressure Gates)

## Overview

This requirement defines what it means for a test in this project to be **a good test** — concretely enough that an automated gate can decide pass/fail. Where REQ-PROC-046 AC-03 says "all tests pass" and AC-04 says "≥ 90 % line coverage on safety-critical paths," this requirement adds the dimension those two cannot express on their own: do the tests actually verify correct behaviour, or do they merely execute the code? Quality is enforced through the same back-pressure mechanism: an LLM cannot declare a code change complete while any active test-quality gate is failing.

## Purpose

Coverage measures execution, not correctness. A test suite that executes 100 % of lines while asserting nothing has 100 % coverage and 0 % verification value. This is not a hypothetical: published research (MuTAP study, Sci. Direct S0950584924000739) reports an LLM-generated test suite with 100 % line and branch coverage and **only 4 % mutation kill rate** — meaning that 96 % of injected bugs survived undetected. Mut@5 (arXiv 2508.00408, 2025) measured LLM tests at ~40 % mutation kill rate on real-world functions; AvgTest, Pynguin, and similar baselines fall further. The pattern is consistent: LLM-generated tests trend toward weak assertions (`expect(result, isNotNull)`), happy-path coverage, and shallow edge-case enumeration.

For a solo developer maintaining a mental-health application without a QA function (PERSONA-015), tests are not a quality-assurance courtesy — they are the only systematic safety net the project has. A weak test that passes against a broken encryption migration is worse than no test, because it produces *false confidence*: the gate reports green and the bug ships. PERSONA-004's *"zero tolerance for data loss"* is enforceable only if the tests on the data path have the strength to actually detect a regression. PERSONA-015's named fear — *"What if someone in crisis uses this app and it fails them — a lost entry, a confusing screen, a crash at the wrong moment?"* — is the consequence of weak tests on critical code, made concrete.

This requirement therefore promotes "the AI shall write good tests" — the project's original one-line testing rule, which this document supersedes — into a measurable contract: assertion strength is statically enforced (AC-01); the tests on safety-critical code are mutation-tested (AC-02); the value objects whose invariants matter most are property-tested (AC-03); the suite is independent and deterministic (AC-04, AC-06); test names describe behaviour rather than implementation (AC-05); and the LLM is structurally constrained to satisfy these properties before declaring work complete (AC-07).

The motivation, again, is sustainability: a test suite without quality gates degrades silently into a green light that no longer means anything. For a solo developer planning to maintain this codebase over years, that decay is not survivable.

## When This Requirement Applies

- Any change to test code under `test/` or `integration_test/`.
- Any change to production code in `lib/` whose tests are affected (which, in practice, is most changes).
- Any change to `analysis_options.yaml` that affects test-relevant rules.
- Before a task is marked complete (via `task-complete` or otherwise).
- Mutation testing (AC-02) and the deterministic-run check (AC-04) are exercised before any release-candidate is approved; the static portions (AC-01, AC-05, AC-06) are exercised per-change.

## When This Requirement Does NOT Apply

- Documentation under `doc/`, `requirements_tasks/`, `requirements_user_needs/`, `.claude/`.
- Process artifacts (skills, plans, protocols).
- Generated files (`*.g.dart`, `*.freezed.dart`).
- Code that has no tests because it is itself test infrastructure (`test/helpers/`); helpers are subject to AC-05 (naming) but are not themselves required to have property tests.

## Behavior

### The Test-Quality Gates

Four gates are active. Each is binary (pass / fail) and measurable from a clean checkout:

| Gate | Detection | Pass condition | Cadence |
|---|---|---|---|
| **TQ1 Assertion strength** | Custom `scripts/quality/check_test_smells.sh` (missing-assertion / empty-group / literal-expect heuristics) + Dart built-in lint `use_test_throws_matchers` | Script returns zero violations over `test/` and `integration_test/`; analyzer reports zero `use_test_throws_matchers` violations. | per-change |
| **TQ2 Mutation kill rate** | `mutation_test` or `dart_mutant` scoped via lcov to the AC-04 critical paths of REQ-PROC-046 | ≥ 80 % of injected mutants killed; surviving mutants documented or addressed. | per-release-candidate; per-change in diff-only mode for files in scope |
| **TQ3 Property-based invariant tests** | Inventory of value objects matching the criteria in AC-03 vs. presence of `glados` test files | Every qualifying type has ≥ 1 property test exercising the relevant invariant. | per-change |
| **TQ4 Independence + determinism** | `flutter test --test-randomize-ordering-seed=random`; 10 consecutive identical runs | Both pass with zero failures, zero new flakes. | per-release-candidate |

The gate set is closed: a test-quality property is either represented by one of these gates or is not part of this requirement. Adding or removing a gate is itself a change that must update this document and `analysis_options.yaml` together.

### Back-Pressure Protocol Inheritance

Failures from any of these gates trigger the same five-cycle revision protocol defined in REQ-PROC-046 §Back-Pressure Protocol. This requirement does not redefine the protocol, only its application surface. The cycle counter is shared with the REQ-PROC-046 protocol — a change that fails both a code-quality gate and a test-quality gate exhausts a single five-cycle budget, not two separate ones.

### Mutation Testing — Scoping the Cost

Naïve mutation testing is expensive: the tool injects mutations one at a time and re-runs the test suite for each, so a 1-minute test run can become a multi-hour mutated run on a full codebase. Two project-specific scoping rules keep the cost bounded:

- **lcov-scoped runs**: `mutation_test` accepts an lcov input and only mutates lines covered by the existing tests. Combined with the AC-04 path filter, this restricts mutation to "covered code on safety-critical paths" — a small fraction of `lib/`.
- **Diff-only runs in development**: `mutation_test` supports a diff-only mode that mutates only lines changed in the current branch. Per-change cadence uses this mode; full critical-path mutation runs once per release-candidate.

Surviving mutants are not silently accepted. They are recorded in `doc/testing/` with one of two annotations: a follow-up TODO (with task ID) to add a stronger test, or a rationale naming why the mutant is benign (e.g. logging-only change with no observable behaviour).

### Property-Based Tests — Scope of "Non-Trivial Invariants"

AC-03 lists six invariant categories. Concretely, for this codebase:

- **Bounded numeric range** — mood scores, scale-of-N answers, retention windows.
- **Enum totality** — every variant of every domain enum is exercised; deserialization of unknown variants is rejected.
- **String length / format constraints** — entry text length caps, identifier formats.
- **Ordering / comparison contracts** — `compareTo` reflexivity, anti-symmetry, transitivity for any type that implements `Comparable`.
- **Encode / decode round-trips** — every serializable type satisfies `decode(encode(x)) == x`.
- **Algebraic laws on aggregates** — accumulation operations on collections satisfy associativity and identity where applicable.

Types that have *only* trivial invariants (a wrapper holding a `String` with no constraints, for example) are not subject to AC-03. The judgment of "non-trivial" is recorded once when the type is added; types added without explicit consideration are flagged.

## Examples

**Example 1: TQ1 — assertion-strength gates fold into the analyzer ruleset**

The custom test-smells script `scripts/quality/check_test_smells.sh` (TASK-PROC-046-14) plus the Dart built-in `use_test_throws_matchers` lint are wired in. After this, a test body like `test('it works', () { someCall(); });` (no assertion) is flagged as a violation by the script — the LLM cannot ship it without addressing it. The DCM-era version of this gate is no longer used: the project has no commercial DCM license; the custom script is functionally equivalent (heuristic regex over test files) without the licensing concern. AC-01 ratifies this enforcement layer as mandatory.

**Example 2: TQ2 — mutation kill rate makes weak assertions visible**

Hypothetical (encryption / decryption are specified by REQ-FUNC-006 but not yet implemented in `lib/`; the example is illustrative of the *pattern* AC-02 catches): a test asserts `expect(decrypt(encrypt(x)), x)` for one input. Coverage: 100 %. Mutation testing injects a mutation that changes the cipher's `iv` argument from a fresh nonce to `Uint8List(12)` (zero IV). The test still passes — encrypt-then-decrypt with the *same* zero IV still round-trips. The surviving mutant flags the test: it is too weak to detect IV reuse. The fix is to add an assertion that two encryptions of the same plaintext with different calls produce different ciphertexts. Once encryption code lands and is on the AC-04 critical-path list, AC-02 catches this category of weakness at the gate level rather than in production.

**Example 3: TQ3 — property tests for `LikertOptions`**

`LikertOptions` (in `lib/core/domain/entities/questionnaire_plan_entities/likert_options.dart`) is a real value object with two non-trivial invariants: a bounded numeric range (`likertScaleSize` must be in `[2, 10]`) and a JSON round-trip. Property tests for it would look like:

```dart
Glados<int>(any.intInRange(2, 10)).test('round-trips through fromJson/toJson', (size) {
  final original = LikertOptions.create(likertScaleSize: size);
  final decoded = LikertOptions.fromJson(original.toJson());
  expect(decoded.likertScaleSize, size);
});

Glados<int>(any.intInRange(-100, 1)).test('rejects out-of-range values below the bound', (size) {
  expect(() => LikertOptions.create(likertScaleSize: size), throwsA(isA<InvalidLikertScaleSizeException>()));
});
```

The first property covers the round-trip across the entire valid input space; the second covers boundary-violation rejection. AC-03 makes property tests required for value objects whose invariants matter; for `LikertOptions`, the bounded range and the round-trip both qualify.

**Example 4: TQ4 — independence + determinism**

A test that writes to a shared `static late` field passes when run alone but fails when another test runs first. `flutter test --test-randomize-ordering-seed=random` exposes this immediately. A test that depends on `DateTime.now()` without a fake clock passes most days but fails when the suite runs at midnight UTC. Ten consecutive identical runs catch the latter (or, more often, prevent it from being committed). AC-04 makes both checks part of the release-candidate gate.

**Example 5: AC-05 — names describe behaviour**

`testParseEntry()` describes which method is exercised; the failure message gives no information about *what* was being verified. `parses_entry_with_unicode_content_preserves_grapheme_clusters()` describes the behaviour: a regression makes the failure self-explanatory in CI logs. AC-05 makes naming a property of the test as written, not a documentation TODO.

## Developer Guidelines

> Constraints and invariants the final test suite must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **Coverage and mutation kill rate are different gates.** Coverage tells you the line ran; mutation kill rate tells you the test caught a deliberate regression. Both are required for safety-critical paths; either alone is insufficient.
- **Mutation testing is scoped, not global.** Running mutation testing across all of `lib/` is impractical for a solo developer and would not pay off — most of the code base is not safety-critical. The AC-04 critical-path filter from REQ-PROC-046 doubles as the scope for AC-02 here.
- **Property tests cover the input space, not specific examples.** A `glados` property test that runs against 100 generated inputs has different failure modes than a hand-written `test()` against three specific inputs. The two complement each other; the property test is *not* a substitute for boundary-explicit examples.
- **Test independence is a property of the test, not of the runner.** `--test-randomize-ordering-seed=random` exposes order dependence; it does not create it. A test that mutates a global is broken; the random-order run merely surfaces it earlier.
- **Determinism is a release-candidate gate, not a per-change gate.** Ten consecutive runs is too expensive for every commit. Per-change cadence relies on per-change `--test-randomize-ordering-seed`; full ten-run determinism is part of the release pre-flight.
- **Test names are part of the source code.** Renaming a test to better describe its behaviour is a code change like any other, subject to the same back-pressure protocol; AC-05 cannot be satisfied "in a separate cleanup task" because the failure messages are the value.

### Common Pitfalls

- **`expect(x, isNotNull)` as the only assertion**: this is a test that runs the code and asserts nothing meaningful. AC-01 (the test-smells script's missing-assertion check) does not catch this directly because there *is* an assertion — but AC-02 (mutation testing) does, because nearly every mutation survives. The pitfall illustrates why both gates are needed.
- **Glados property tests with overly narrow generators**: `Glados<int>(any.intInRange(-3, 3)).test(...)` for a value object that accepts -5 to +5 misses the boundary cases. AC-03 requires the generator to span the documented invariant range, not a subset.
- **Mutation testing run only at release time**: skipping per-change diff-only mode means the per-change feedback loop never sees mutation results, and surviving mutants accumulate in batches that are hard to disentangle later. Diff-only mode is cheap and worth running.
- **Determinism failures dismissed as "flaky tests"**: a flaky test is a defect, not a fact of life. The 10-consecutive-run gate catches the easy cases; the harder cases (clock dependence, CPU-load-dependent timeouts) require investigation, not a `pub:retry`.
- **Fixing a surviving mutant by deleting the mutated code instead of strengthening the test**: this satisfies the gate while removing the property the test was meant to verify. The mutation tool tells you the test is weak; the response is to strengthen the test, not to remove the line that the weak test happened to cover.

## Related Requirements

- **REQ-PROC-046 (Code Quality Standard)** — sibling. Defines source-code-quality gates including AC-03 (tests pass) and AC-04 (≥ 90 % coverage on critical paths). This requirement adds the orthogonal axis: do the tests actually test the right things? Together they form the testing contract.
- **REQ-PROC-052 (Privacy & Security Hygiene)** — sibling. AC-05 of that requirement (PII redaction in `toString()`) is enforced via unit tests; the test-quality gates here apply to those tests as well.
- **REQ-PROC-001 (Context Window)** — unrelated; concerns conversational context, not code or test quality.

## References

- `analysis_options.yaml` — host of the static-detection rules for AC-01
- `doc/testing/testing.md` — test folder structure and execution process; documented set of safety-critical paths subject to AC-02; surviving-mutant register
- `CLAUDE.md` — operational checklist that invokes the gates per task
- MuTAP / Effective Test Generation Using LLMs and Mutation Testing (Sci. Direct S0950584924000739) — source of the 100 %-coverage / 4 %-mutation-score finding
- Mut@5: Benchmarking LLMs for Unit Test Generation (arXiv 2508.00408, 2025) — LLM-tests-on-real-functions mutation kill-rate baseline
- Mutation-Guided LLM-Based Test Generation at Meta (FSE 2025) — mutation testing as canonical quality signal in industry
- `mutation_test` (pub.dev) — Dart mutation testing tool with lcov scoping and diff-only mode
- `dart_mutant` (dartmutant.dev) — AST-aware Rust-implemented Dart mutation tool
- `glados` (pub.dev) — property-based testing for Dart, integrates with `package:test`
- F.I.R.S.T. principles — Object Mentor / Robert C. Martin, *Clean Code* Ch. 9 (2008); origin: Tim Ottinger and Brett Schuchert
- Bill Wake, "3A — Arrange, Act, Assert" (2001); Gerard Meszaros, *xUnit Test Patterns* (2007)
- `scripts/quality/check_test_smells.sh` (TASK-PROC-046-14) — custom DCM-free script for AC-01 (replaces DCM `missing-test-assertion`, `avoid-empty-test-groups`, `prefer-test-matchers` since the project has no commercial DCM license)
- Dart linter `use_test_throws_matchers` — built-in static rule for AC-01
