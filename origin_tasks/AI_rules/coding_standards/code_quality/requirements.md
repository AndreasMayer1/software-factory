---
id: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: L
stakeholder: app_provider
created: 2026-05-10
updated: 2026-05-22
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
personas_served: [PERSONA-015, PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "All Dart sources under `lib/`, `test/`, and `integration_test/` produce zero errors and zero warnings from `flutter analyze` (with the project's `analysis_options.yaml` active); `dart fix --apply` is idempotent on a checked-in tree; `dart pub get --enforce-lockfile` succeeds (no `pubspec.lock` drift)."
    - id: AC-02
      text: "Every function and method body in `lib/` satisfies: cyclomatic complexity ≤ 20, parameter count ≤ 4, source-lines-of-code ≤ 50, maximum control-flow nesting level ≤ 5. 'Control-flow nesting' counts `if` / `for` / `while` / `try` / `switch` blocks only; widget tree construction depth in Flutter `build()` methods is NOT counted (a `Scaffold` > `SafeArea` > `Padding` > `Column` > `Row` > `Container` > `Text` chain is six levels of widget composition but zero levels of control-flow nesting). Measurement is by `scripts/quality/check_complexity.py` (custom Dart-analyzer-based script, per TASK-PROC-046-14)."
    - id: AC-03
      text: "All tests under `test/unit/`, `test/widget/`, and `integration_test/` pass with zero failures and zero errors when executed via `flutter test` from a clean checkout."
    - id: AC-04
      text: "Code paths where data loss is catastrophic — encryption / decryption, key derivation (Argon2id), atomic file rotation, version migration, and the data-transfer serialization pipeline — have ≥ 90 % line coverage as measured by lcov from `flutter test --coverage`. The set of paths subject to this threshold is documented (in `doc/testing/` or this requirement's references) so the LLM and the coverage tooling agree on what is critical."
    - id: AC-05
      text: "The domain layer (`lib/core/domain/`, `lib/features/*/domain/`) contains zero imports from `package:flutter/*` and `package:flutter_bloc/*`; feature modules (`lib/features/*`) contain zero direct imports of `package:flutter/material.dart` (design-system components are used instead)."
    - id: AC-06
      text: "Code in `lib/` contains zero unawaited `Future` expressions outside explicit `unawaited(...)` wrappers; zero bare `catch` clauses without an `on Type` and a matched logged failure path in code that touches persistence, encryption, or transfer; zero `throw` statements that throw a non-`Error`/non-`Exception` value."
    - id: AC-07
      text: "Every screen in `lib/` (a widget reachable via `GoRouter` route configuration or `MaterialApp.routes`) is covered by widget tests that collectively verify every currently-active accessibility commitment in REQ-NFUNC-002. Concretely this means: (a) `tester.ensureSemantics()` passes Flutter's `AccessibilityGuideline` checks — `androidTapTargetGuideline` (48 dp), `iOSTapTargetGuideline` (44 pt), `textContrastGuideline` (WCAG AA 4.5:1 text, 3:1 UI), `labeledTapTargetGuideline`; (b) a test verifies the screen renders without layout overflow at `MediaQuery.textScaleFactor: 2.0` (REQ-NFUNC-002 AC-11); (c) a test verifies non-essential animations are disabled when `MediaQuery.disableAnimations` is true (REQ-NFUNC-002 AC-12); (d) screens containing organic graphics or non-essential animations also pass under the user's Simple-Mode setting (REQ-NFUNC-002 AC-02 / AC-03); (e) the linguistic-complexity gate (REQ-NFUNC-002 cognitive-accessibility AC) returns no violations on the `.arb` strings shown by the screen. The set of checks tracks REQ-NFUNC-002's currently-active acceptance criteria — promoting a Phase-2 AC there (e.g. focus-order, advanced semantic descriptions) automatically extends this gate when its `target_package` becomes a released version."
    - id: AC-08
      text: "On the project's reference test device — Samsung Galaxy A40 (Android, Exynos 7904, 4 GB RAM, released 2019) — cold-start time-to-first-rasterized-frame is ≤ 7 500 ms (measured via `flutter run --trace-startup --profile` reading `timeToFirstFrameRasterizedMicros` from `build/start_up_info.json`; threshold calibrated from 10 cold-start runs, p95 = 5 623 ms, rule: p95 + 30 % headroom rounded to next 250 ms — see TASK-PROC-046-02); during data-entry interaction in integration tests, `average_frame_build_time_millis` ≤ 16 ms and `missed_frame_build_budget_count` is 0 across the measured action."
    - id: AC-09
      text: "On `flutter build apk --analyze-size --target-platform=android-arm64`, the resulting per-ABI APK is ≤ 30 MB; on `flutter build appbundle --analyze-size`, the AAB is ≤ 50 MB. Size-analysis JSON is preserved alongside release artifacts so size regressions are visible across releases."
    - id: AC-10
      text: "Code that fails any active quality gate is never declared complete: every gate failure triggers a revision cycle until the failure is resolved or, if unresolvable within 5 iterations, escalated to the user with a documented reason recorded in the task's `plans_and_protocols/`."
    - id: AC-11
      text: "Every active suppression of a quality rule (`// ignore:`, `// ignore_for_file:`, or any analyzer-specific per-line disable directive) is accompanied by an adjacent inline comment explaining why the rule does not apply to that specific case."
    - id: AC-12
      text: "Code under `lib/` outside an active bugfix task contains zero raw `print()` calls, zero `debugPrint()` calls without the `[DIAG-*]` prefix, and zero blocks marked `// TEMPORARY:` (these markers belong only to in-flight bugfix tasks, per CLAUDE.md)."
    - id: AC-13
      text: "The active set of quality gates, their thresholds, and the back-pressure protocol are documented in a single authoritative location (`doc/linter/` and the LLM-facing entries in `CLAUDE.md`) and are kept consistent with `analysis_options.yaml` — a contributor or LLM agent can determine, without asking, which gates apply and what passing means."
---

# Code Quality Standard (LLM Back-Pressure Gates)

## Overview

This requirement defines what "good code quality" means for code produced in this project — concretely enough that an automated gate can decide pass/fail, and explicitly enough that an LLM agent receiving a gate failure knows what it must do next. Quality covers eight dimensions: source-code hygiene, complexity, test correctness (including coverage on safety-critical paths), architectural purity, error-handling discipline, accessibility, runtime performance on low-end hardware, and bundle size. All are enforced through *back-pressure*: an LLM cannot declare a code change complete while any active gate is failing — the gate's pass/fail signal is the feedback loop that bounds LLM behavior.

## Purpose

The app provider (PERSONA-015) is a single solo developer maintaining a mental-health application alongside a full-time job. The persona's grounded values are explicit: *"longevity over velocity"*, *"the codebase must survive periods where the creator has no time to touch it"*, *"simplicity is a survival strategy for one-person maintenance over years"*. There is no QA department, no DevOps team — every defect that reaches main becomes the creator's personal maintenance burden.

The system/maintenance constraints (PERSONA-004) compound this: the application must run reliably on 2017-era Android hardware (2 GB RAM, eMMC storage, slow CPU), must never lose mental-health entries, and depends on architectural purity (pure domain layer, no global state) for predictability on slow devices. Users in mental-health contexts often arrive at the app to make a quick entry — sometimes in a fragile emotional state. A slow cold start or a janky input field is not a minor UX issue; it can be the difference between an entry being captured or abandoned. Combined with the persona's commitment that the app must be usable by people on the oldest hardware (often the same population facing financial constraints), performance and accessibility are not "polish" — they are core acceptance properties. App size is part of the same concern: bloat over years pushes the app off devices with limited storage and is a slow form of abandonment.

In a project where most code is now produced by LLM agents, "good code quality" cannot remain a subjective standard reviewed by a human after the fact — there is no human capacity to do that consistently for every change. Quality must be encoded as machine-checkable gates, and the LLM must be structurally constrained to satisfy them before declaring work complete. This is the back-pressure mechanism: rather than the LLM optimizing for "looks done," each gate becomes an unavoidable signal that the LLM must address. Published research on LLM feedback loops (LLMLOOP, ICSME 2025) reports that effectiveness plateaus after 3–5 cycles and that LLMs tend to address one gate's failure while degrading another — both findings are reflected in the protocol below (five-cycle bound; gates re-run as a set after each revision).

The motivation for this requirement is therefore not stylistic preference. It is sustainability: without it, complexity, dead suppressions, broken layer boundaries, swallowed exceptions, accessibility regressions, performance decay, and size bloat accumulate faster than one person can clean up, and the codebase reaches the point where maintenance becomes infeasible — which would mean abandonment of users who came to depend on the app for their therapeutic records.

## When This Requirement Applies

- Any change to Dart code under `lib/`, `test/`, or `integration_test/` produced by an LLM agent or a human contributor.
- Before a task is marked complete (via `task-complete` or otherwise).
- Before a commit is created on `develop`.
- Performance gate (G7 dynamic measurement) and bundle-size gate (G8) are additionally exercised before any release-candidate is approved.

## When This Requirement Does NOT Apply

- Generated files (`*.g.dart`, `*.freezed.dart`) — already excluded in `analysis_options.yaml`.
- Files under `figma/` and other excluded paths.
- Documentation-only changes under `doc/`, `requirements_tasks/`, `requirements_user_needs/`, `.claude/`.
- Process artifacts (skills, plans, protocols) — these are not Dart code and are governed separately.
- Commits where the staged set contains zero files under `lib/`, `test/`, or `integration_test/`. The pre-commit hook detects this and auto-skips the gate run without requiring `SKIP_QUALITY_GATES=1`. The skipped run is logged to stderr (`[verify-quality] SKIPPED for git commit (no staged files under lib/, test/, or integration_test/ — auto-bypass per REQ-PROC-046 scope)`). No commit-message annotation is required; this is a scope-derived skip, not a developer override.
- The `// TEMPORARY:` and `[DIAG-*]` artifacts inside an actively in-flight bugfix task (per CLAUDE.md bugfix conventions) are exempt from AC-12 *until that task completes*; the bugfix-completion skill is responsible for removing them.

## Behavior

### The Quality Gates

Eight gates are active. Each is binary (pass / fail) and measurable from a clean checkout:

| Gate | Tool | Pass condition | Cadence |
|---|---|---|---|
| **G1 Source hygiene** | `flutter analyze` (with `very_good_analysis` baseline) + `dart fix --apply` + `dart pub get --enforce-lockfile` | Zero errors / warnings; fix is idempotent; lockfile is clean. The analyzer ruleset includes the 188 rules from `very_good_analysis` (covering error-handling: `unawaited_futures`, `only_throw_errors`, `avoid_catches_without_on_clauses`; const-correctness: `prefer_const_constructors` and friends; debug-artifact: `avoid_print`; resource hygiene: `cancel_subscriptions`, `close_sinks`; soundness: `avoid_dynamic_calls`) plus `bloc_lint` (BLoC-specific rules including `prefer_file_naming_conventions`, `avoid_public_bloc_methods`) and `clean_architecture_kit` (layer-leak detection by naming heuristics). Flutter-performance patterns not lint-checkable (e.g. `RepaintBoundary` placement, `ListView.builder` for long lists, BLoC-selector granularity) live in `doc/presentation/coding/best_practices.md`; quality-checker reads them as judgment-level rules. | per-change |
| **G2 Complexity bounds** | Custom Dart-analyzer-based script `scripts/quality/check_complexity.py` + `_complexity_analyzer/` Dart helper (TASK-PROC-046-14) | All bounds in AC-02 satisfied for every function / method body. | per-change |
| **G3 Test correctness & critical-path coverage** | `flutter test` + `flutter test --coverage` (lcov) | Zero failures across all test folders; ≥ 90 % line coverage on the documented set of safety-critical paths. | per-change |
| **G4 Architectural purity** | Custom grep script `scripts/quality/check_architectural_imports.sh` with per-path-glob deny policy in `scripts/quality/architectural_imports_policy.yaml` (TASK-PROC-046-14) | Domain has no Flutter / BLoC imports; features have no direct `material.dart` imports; design-system styling classes (`ButtonStyle`, `TextStyle`, `Color`) not used directly in feature code (separate `check_no_direct_styling.sh` script). | per-change |
| **G5 Suppression discipline** | grep over `lib/`, `test/`, `integration_test/` | Every active `// ignore:` / `// ignore_for_file:` has an adjacent justification comment. | per-change |
| **G6 Accessibility compliance** | `tester.ensureSemantics()` + Flutter's `AccessibilityGuideline` API in widget tests | Every screen has at least one widget test; every interactive widget test passes `androidTapTargetGuideline`, `iOSTapTargetGuideline`, `textContrastGuideline`, `labeledTapTargetGuideline`. | per-change |
| **G7 Performance budget** | `flutter run --trace-startup --profile` (cold start) + `IntegrationTestWidgetsFlutterBinding.traceAction()` (frame budget) | Cold-start TTFR ≤ 7 500 ms on the Samsung Galaxy A40 reference device; data-entry frame build time ≤ 16 ms average with zero missed-frame-build-budget events. | dynamic (per-release-candidate; static perf lints fold into G1 per-change) |
| **G8 Bundle-size budget** | `flutter build apk --analyze-size --target-platform=android-arm64` and `flutter build appbundle --analyze-size` | Per-ABI APK ≤ 30 MB; AAB ≤ 50 MB; size-analysis JSON archived with release artifacts. | per-release-candidate |

The gate set is closed: a quality property is either represented by one of these gates or is not part of this requirement. Adding or removing a gate is itself a change that must update this document and `analysis_options.yaml` together.

### Static vs Dynamic Cadence

G1–G6 are *per-change* gates: the LLM agent runs them after every code change and resolves any failure before declaring the change complete. G7 has two surfaces:

- **Static** — const-correctness lints, no sync I/O on the main isolate, no expensive operations in widget `build()` and `initState()`. These are absorbed into G1 via the analyzer ruleset and are enforced per-change.
- **Dynamic** — cold-start trace and frame-budget measurement on the Galaxy A40 reference device. These require running the app on physical or emulated hardware and are enforced before any release-candidate is approved, not on every commit. A change that plausibly affects startup or input responsiveness (e.g. work added to `main()`, a new repository in the startup path, a heavy widget on a primary entry screen) MUST trigger an interim dynamic G7 run before being declared complete; the agent surfaces this judgment explicitly.

G8 is also a per-release-candidate gate: bundle size is meaningless to measure on a single-file change but accumulates across releases. The size-analysis JSON is archived so trends are visible.

### The Back-Pressure Protocol

When an LLM agent (or any contributor) modifies code:

1. **Self-check**: After producing the change, the agent runs all per-change gates locally.
2. **On failure**: The change is not complete. The failure messages are read back and treated as required input for the next revision. The agent revises and re-runs *all* gates as a set — partial fixes are not partial completions.
3. **Iteration bound**: A maximum of five revision cycles is permitted on a single change before escalation. This bound is grounded in published findings on LLM feedback-loop diminishing returns (LLMLOOP, ICSME 2025 — effectiveness plateaus after 3–5 cycles), and protects against infinite-loop behaviour on unsolvable inputs.
4. **Escalation via the project's automation Q&A mechanism**: If gates still fail after five cycles, the agent stops and writes a `question.md` to **`automation/pending_feedback/<TASK_ID>/question.md`** following the canonical template at `automation/pending_feedback/TEMPLATE_question.md`. The agent simultaneously copies `automation/pending_feedback/TEMPLATE_answer.md` to `<TASK_ID>/answer.md` and then runs `bash scripts/automation/terminate_session.sh` per the procedure in `.claude/skills/claude-automated-mode/skill.md` §lines 76–139.

   Required frontmatter (verbatim from the live `automation/pending_feedback/TASK-PROC-006-02/question.md`):

   ```yaml
   ---
   task_id: <TASK-ID>
   session_id: <UUID of the running session, OR the sentinel NEW_SESSION_REQUIRED if no JSONL exists>
   account: <web | local | the active account>
   status: awaiting_answer
   asked_at: <ISO-8601 UTC timestamp>
   skill: verify-quality
   ---
   ```

   The body is free-form Markdown — the orchestrator does not parse it. Suggested sections for the gate-cap escalation case:

   ```
   # Pending Question — <TASK-ID>: Gate back-pressure cap reached

   ## Where this task is
   ## Gates still failing
   ## Cycle log (5 cycles)
   ## Suspected root cause
   ## Decisions
   ### D1.
   **Proposal:** ...
   **Alternative:** ...
   **Your answer:** _(developer fills in)_
   ## How this task closes
   ```

   The agent does NOT write to `answer.md` — the template-sentinel `<!-- AWAITING_HUMAN_ANSWER -->` must remain until the developer answers. The orchestrator's `scripts/automation/orchestrate.py:find_answered_feedback` (lines 1362–1419) and `scripts/tasks/next_tasks.py:load_pending_feedback_ids` (lines 74–122) detect the pending question and keep the task off the queue until `answer.md` becomes non-template.

   When the developer fills `answer.md`, `orchestrate.py:process_answered_feedback` (lines 1667–1819) resumes the session via `claude --resume <session_id> -p <answer.md content>` (or launches a fresh session via `run_fresh_session_with_answer` if `session_id` is `NEW_SESSION_REQUIRED`). The cycle counter resets when the resumed session starts. Per task convention the question/answer folder is moved to `automation/answered_feedback/<TASK-ID>/` after successful resume.

   Silent acceptance of a failing gate is not an option. Marking the task complete without going through this escalation is not an option. The `question.md` is the contract between the LLM and the user — the only legitimate way out of cycle 5.
5. **Suppression**: The escape valve `// ignore: rule_name` is permitted only when (a) the rule's intent does not apply to the specific case and (b) an adjacent comment records why. Suppressions are themselves visible in code review as a signal that judgment was applied.
6. **Capture non-obvious fix patterns**: when a gate failure is resolved via a fix that is non-obvious (framework quirk, library workaround, subtle interaction between rules, novel pattern the LLM did not derive from existing `doc/`), the LLM invokes the `doc-update-guidelines` skill before declaring the task complete. The threshold is the same as for WHY-comments per CLAUDE.md §5: capture only what a future agent would not reach by reading current `doc/` plus the code. This is documentation evolution, *not* gate-set evolution — the gate definition remains unchanged; only the narrative of how to satisfy it grows. Gate-set changes still require user approval per Developer Guidelines.

### What "Complete" Means

A code change is complete when, against a clean checkout, all per-change gates pass without intervention and any release-cadence gate (G7 dynamic, G8) triggered by the change's surface area has been exercised. "Complete" is not a self-assessment by the LLM — it is a derivable property of the tree.

### Reference Test Device

The Samsung Galaxy A40 is the project's named reference test device for G7. It was chosen because the app provider owns it physically and can verify measurements directly. Specs: Exynos 7904 (8-core, 14 nm), 4 GB RAM, 64 GB storage, Android 9 → 11, 5.9″ 1080×2340 Super AMOLED, released April 2019.

The A40 is mid-tier 2019 hardware — somewhat better than PERSONA-004's worst-case baseline of "2017 Android, 2 GB RAM". This mismatch is acknowledged: the 7 500 ms cold-start threshold is calibrated from 10 actual A40 measurements (profile mode, May 2026; median = 4 283 ms, p95 = 5 623 ms; methodology in `doc/testing/cold_start_measurement_methodology.md`). The original 3 000 ms placeholder significantly underestimated A40 start time — cold start takes 3.4–5.6 s in practice, primarily due to Flutter VM init, shader compilation, and the app's startup path on a budget Exynos 7904 SoC. The threshold is an upper bound, not a performance target; a measurement near 7 500 ms is a regression signal warranting separate optimisation work.

## Examples

**Example 1: G1 / G2 / G4 — what each gate uses (post-DCM-removal)**

The project does NOT have a commercial DCM (`dart_code_linter`) license, so DCM rules are not part of the gate set. Instead:

- **G1** is enforced by `very_good_analysis` as the analyzer baseline (188 rules, MIT-OSS) plus `bloc_lint` and `clean_architecture_kit`. Configured in `analysis_options.yaml`'s `include:` directive and per-rule `linter.rules:` overrides.
- **G2** thresholds (cyclomatic ≤ 20, parameters ≤ 4, SLOC ≤ 50, max nesting ≤ 5) are measured by a custom Python script `scripts/quality/check_complexity.py` that shells out to a small Dart CLI under `scripts/quality/_complexity_analyzer/` using `package:analyzer` for AST-level introspection.
- **G4** layer boundaries are enforced by `scripts/quality/check_architectural_imports.sh` (per-path-glob deny policy externalised in `scripts/quality/architectural_imports_policy.yaml`) and `check_no_direct_styling.sh` (ban-name for `ButtonStyle` / `TextStyle` / `Color` in `lib/features/`).

AC-01, AC-02, and AC-05 ratify this configuration as mandatory. The migration from DCM to custom scripts is the deliverable of TASK-PROC-046-03 (analyzer baseline switch) and TASK-PROC-046-14 (custom replacement scripts).

**Example 2: Error-handling discipline (AC-06) extends the analyzer ruleset**

`unawaited_futures`, `discarded_futures`, `only_throw_errors`, and `avoid_catches_without_on_clauses` (from `very_good_analysis` / Flutter linter) catch the most common mental-health-relevant defects: a fire-and-forget save that silently fails, a bare `catch` that masks a real `Error`, or a `throw 'string'` that loses stack-trace context. AC-06 makes these properties of the codebase itself, not just analyzer settings.

**Example 3: Critical-path coverage (AC-04) is targeted, not global**

The project explicitly does not enforce a global coverage percentage. Instead, AC-04 names categories of code where data-loss is catastrophic — the encryption / decryption path, Argon2id key derivation, atomic file rotation (REQ-FUNC-015), version migration, and the data-transfer serialization pipeline (REQ-FUNC-007). For these paths, ≥ 90 % line coverage is the gate. Other code is subject only to G3 (tests pass), not to a coverage threshold. The exact set of file paths subject to AC-04 is maintained in `doc/testing/` so the LLM and the lcov filter agree.

**Example 4: G6 accessibility is a v1 commitment, lifted to enforceable shape**

PERSONA-015 commits in v1 scope to WCAG AA contrast (4.5:1 text, 3:1 UI), 48 dp touch targets, basic semantic labels on every interactive element, and 200 % text scaling without overflow. AC-07 promotes these from persona-level commitments to test-enforceable gate criteria via Flutter's `AccessibilityGuideline` API, and adds a structural rule: every screen reachable via `GoRouter` has at least one widget test (so untested screens cannot silently bypass the gate). Backfilling tests for already-existing untested screens is part of the implementation work for this requirement.

**Example 5: G7 dynamic performance — what triggers a measurement on the A40**

Adding a new repository call to the app's startup path is a change that plausibly affects cold start. The agent runs `flutter run --trace-startup --profile` against the Galaxy A40, reads `timeToFirstFrameRasterizedMicros` from `build/start_up_info.json`, and confirms it is ≤ 7 500 000 µs. Adding a new field to a data-entry form is a change that plausibly affects frame budget; the agent runs the existing data-entry integration test under `IntegrationTestWidgetsFlutterBinding.traceAction()` on the A40 and confirms `average_frame_build_time_millis` ≤ 16 and `missed_frame_build_budget_count` = 0. A change that touches neither path (e.g. a domain-layer refactor) does not require a dynamic G7 run.

**Example 6: G8 bundle size — visible across releases**

Each release-candidate runs `flutter build apk --analyze-size --target-platform=android-arm64`. The resulting `*-code-size-analysis_*.json` is archived with the release artifacts (alongside the APK). A release that exceeds 30 MB per-ABI APK fails G8; the `--analyze-size` JSON is opened in DevTools "App Size" tool to identify the contributor. Trend visibility across releases turns size discipline into a sustained property, not a one-off check.

**Example 7: G3 — test failures are not "known issues"**

A failing test, even one tagged `// TODO: flaky on Windows`, fails G3. There is no permitted state in which a test in `test/` exists and is failing on `develop`. If a test is genuinely irrelevant, it is removed; if it is a known-failure in a context, it is `skip`'d with a justification (treated as an active suppression, subject to AC-11).

## Developer Guidelines

> Constraints and invariants the final code must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **Gates are mandatory, not advisory.** The LLM may not declare a change complete with any per-change gate failing. There is no "ship now, fix later" path inside a single task.
- **Gate configuration lives in `analysis_options.yaml`, not in this document.** This requirement is the contract; the analyzer config is the authority for static gates. If they diverge, the analyzer config is wrong and is corrected.
- **Suppressions are visible decisions.** Every `// ignore:` is read by the next reviewer; the inline justification is part of the code, not a commit-message footnote.
- **The five-cycle bound is a guard, not a target.** Most changes pass on the first or second cycle. Reaching cycle five usually indicates the change itself is wrong, not that the gates are too strict.
- **The domain layer is pure.** No `package:flutter/*` import survives in `lib/core/domain/` or `lib/features/*/domain/`. This is not stylistic — it is what allows old-device reliability and headless testing.
- **Coverage is targeted, not global.** AC-04 enumerates categories where catastrophe-on-failure justifies the cost of writing and maintaining tests to 90 %. Code outside those categories is not subject to a coverage threshold; pursuing global coverage at the expense of focus on critical paths is a sustainability anti-pattern for a solo dev.
- **Performance is treated as a correctness property, not a polish property.** Cold-start regressions are bugs against PERSONA-015's grounded commitment that the app helps users in fragile states make quick entries on the hardware they own.
- **Accessibility is a structural commitment, not a feature flag.** PERSONA-015's grounding in distributive equity ("the argument 'it affects only a few' is not valid") translates to AC-07 being non-negotiable. The structural extension — every screen has a widget test — is what closes the silent-bypass loophole.
- **Bundle size is a slow-burn property.** A 200 KB regression per release is invisible week-to-week and lethal year-over-year. G8 archives the size-analysis JSON to make the trend observable.
- **The reference test device is named, not implicit.** AC-08 is meaningful only against the Samsung Galaxy A40. If the A40 is unavailable (broken, lost, replaced), the requirement is updated to name the new reference device and the threshold is recalibrated against it.
- **The border between `doc/` guidelines and the gate set is the scriptability test.** A rule whose compliance can be decided yes-or-no from a syntactic / structural property of the code belongs in the gate set (analyzer config or `scripts/quality/`). A rule that requires reading the code's intent — *"when to use a BLoC vs. a provider", "how to compose a failure"* — stays in `doc/` and is enforced by the `quality-checker` agent that reads both code and the relevant `doc/` files. The gate set is the deterministic floor; `doc/` is the judgment-level ceiling. Both run as part of the back-pressure protocol — `doc/`-rule violations surface from `quality-checker`'s reading; gate violations surface from the scripts. A rule does not live in both places at the same level of authority: if it is scriptable, the script is the authority and `doc/` references the script rather than restating the rule.
- **Changes to the gate set require user approval, not LLM autonomy.** An LLM agent may *propose* a new gate (or a tightened threshold) by creating a task via `task-create`. It must not silently modify `analysis_options.yaml` rule lists, `scripts/quality/` scripts, or the acceptance-criteria of REQ-PROC-046 / REQ-PROC-002 / REQ-PROC-052 during the same task that triggered the proposal. This prevents the LLM from weakening its own constraints under pressure (the Goodhart's-Law failure mode named in the Common Pitfalls below). The `doc-update-guidelines` skill remains the legitimate path for evolving narrative guidance; gate-set evolution goes through `task-create` plus user review.
- **The gate-set may detail rules beyond the acceptance-criteria of the requirements it enforces.** A requirement (e.g. REQ-NFUNC-002 accessibility) states the intent at AC granularity; the actual analyzer rules, grep scripts, and threshold values in `analysis_options.yaml` and `scripts/quality/check_*.sh` may add *finer-grained* detection (e.g. AC-15 keyboard navigation in REQ-NFUNC-002 is enforced by a specific `tester.sendKeyEvent(LogicalKeyboardKey.tab)` test pattern that the AC text does not enumerate). **Neither side alone is the single point of truth** — the requirement is the *what*, the gates are the verifiable *how*, and the `doc/` guidelines fill the judgment band between them. When a rule in the gate set conflicts with the intent of a requirement, the requirement wins and the gate is corrected.
- **The AC-04 path list reflects implementation reality, not aspiration.** Some safety-critical categories named in AC-04 (encryption / decryption, Argon2id key derivation) correspond to features specified by REQ-FUNC-006 but not yet implemented in `lib/`. The lcov filter in `doc/testing/critical_paths.md` lists only paths that exist; categories with no code today contribute zero to the gate computation but remain on the list as named so they pick up enforcement automatically when their code lands. Deleting a category from the list because it isn't implemented yet would silently un-gate it later.

### Common Pitfalls

- **Gates passing locally but not in CI**: The gate check is "from a clean checkout." Stale `.dart_tool/` or uncommitted local fixes mask real failures. The end-state to verify is what a fresh `flutter pub get && flutter analyze && flutter test` produces — not what the local IDE shows.
- **Splitting a function only to satisfy SLOC**: Mechanically extracting helpers to dodge the 50-line bound creates worse code than the original. The bound exists to surface complexity that should not be there; the right response is usually to remove the complexity, not to redistribute it.
- **Suppressions without context**: `// ignore: avoid_dynamic_calls` followed by no comment is itself a defect under AC-11, regardless of whether the analyzer is satisfied.
- **Treating G3 as "the tests I know about pass"**: G3 is "all tests pass." A new file under `test/` with a failing assertion fails G3 even if no one explicitly ran it.
- **Optimizing one gate at the cost of another**: Published research (AugmentCode harness engineering) reports that LLMs frequently address one gate's failure while degrading another. After each revision cycle, all gates are re-run — partial fixes are not partial completions.
- **Swallowed `Future`s in the data path**: An unawaited save returns "instantly" — and silently loses an entry on slow eMMC storage when the process is killed. AC-06 (`unawaited_futures`) is what makes this category of defect machine-detectable.
- **Heavy work in `initState` without an isolate**: A synchronous decryption or large-file read in `initState` blocks the first frame, blowing G7's cold-start budget on the A40 long before any user-visible cause is obvious. The static perf lints (in G1) catch the common variants.
- **`debugPrint` used as production logging**: `debugPrint` without the `[DIAG-*]` prefix is treated as a leftover artifact under AC-12 and fails G1's `avoid_print` rule when used outside the bugfix-debug convention.
- **Coverage as a goal in itself**: Pushing AC-04 paths past 90 % by adding shallow tests that exercise lines without verifying behaviour weakens the gate. Coverage is a floor, not a substitute for designed assertions.
- **Bundle size 'just because of assets'**: An asset bloat (a forgotten 6 MB PNG, an unstripped font with all glyph ranges) is the most common G8 failure. The size-analysis JSON identifies asset contributions distinctly from code.

## Related Requirements

- **REQ-PROC-044 (Software Factory Quality Properties)** — covers the *factory's* reliability in producing correct artifacts (skills, transitions, traceability). This requirement covers the quality of the *artifacts themselves* (the code). The two are complementary: a reliable factory producing low-quality code is not a healthy system, nor is the inverse.
- **REQ-PROC-002 (Test Quality Standard)** — sibling. AC-03 of this requirement says "all tests pass"; AC-04 says "≥ 90 % line coverage on safety-critical paths." REQ-PROC-002 adds the orthogonal axis: do the tests actually test the right things? Specifically, mutation kill rate (REQ-PROC-002 AC-02) on the same critical paths that AC-04 covers, plus assertion-strength static gates (REQ-PROC-002 AC-01), property-based tests for value-object invariants (REQ-PROC-002 AC-03), and test-suite independence and determinism (REQ-PROC-002 AC-04). Coverage without mutation kill rate is a known false signal — both are required.
- **REQ-PROC-001 (Context Window)** — unrelated; concerns conversational context, not code quality.
- **REQ-PROC-048 (Guideline File Organization)** — governs `doc/` size limits and split mechanics. The back-pressure step 6 ("capture non-obvious fix patterns") adds to `doc/`; REQ-PROC-048's 600-line bound + auto-split via `scripts/doc_governance.py` prevents unbounded growth. The two requirements together ensure the captured patterns remain findable by LLM agents within context-window budget.
- **REQ-PROC-052 (Privacy & Security Hygiene)** — sibling requirement covering what code is forbidden from doing (no hardcoded secrets, no PII in logs, no weak crypto). Together with REQ-PROC-046 they form the full code-correctness contract for LLM-produced code.
- **REQ-PROC-049 (Language Coherence Across Product Artifacts)** — orthogonal coherence layer covering user-facing names, states, and operations. The G6 linguistic-complexity sub-check (REQ-PROC-046) and the concept-canon audit `scripts/user_needs/check_canon.py` (REQ-PROC-049) share the `.arb` parser infrastructure under `scripts/quality/` so both gates parse localization files through one code path. Closes the bidirectional link from REQ-PROC-049's side.
- **PERSONA-015 v1 accessibility commitments** — the source of the specific WCAG AA, 48 dp, semantic-label, and 200 %-text-scaling requirements that AC-07 promotes from values to test-enforceable gates.

## References

- `analysis_options.yaml` — authoritative source of G1 rule configuration (via `very_good_analysis` baseline + `bloc_lint` + `clean_architecture_kit`).
- `scripts/quality/` — home of the custom DCM-free gate scripts: `check_complexity.py` (G2 + AC-02), `check_architectural_imports.sh` (G4 + AC-05), `check_no_direct_styling.sh` (ban-name for design-system enforcement), `check_suppression_justification.sh` (G5 + AC-11), `check_no_debug_artifacts.sh` (AC-12), `check_test_smells.sh` (REQ-PROC-002 AC-01), `check_folder_taxonomy.sh` (REQ-PROC-046 K.2), `check_no_network_io.sh` / `check_no_telemetry_sdks.py` / `check_no_hardcoded_secrets.sh` / `check_weak_crypto.sh` (REQ-PROC-052 SP1–SP4), `check_quality_gates.sh` (entry point).
- `scripts/quality/proposals/` — accumulating rule-change proposals (filed by AI agents per the proposals-loop mechanism in TASK-PROC-046-13). Reviewed periodically via the loop-task's automation Q&A.
- `doc/linter/linter_setup_and_guidelines.md` — narrative explanation of the linter's role.
- `doc/linter/linter_configuration_proposal.md` — historical configuration proposal (pre-DCM-removal; retained for context, do not adopt directly).
- `doc/testing/testing.md` — test folder structure, test execution process, and the documented set of safety-critical paths subject to AC-04.
- `doc/presentation/coding/best_practices.md` — judgment-level Flutter performance patterns (`RepaintBoundary` placement, `ListView.builder` usage, BLoC selector granularity) that are not lint-checkable; `quality-checker` reads + judges.
- `CLAUDE.md` — operational checklist that invokes the gates per task; bugfix conventions for `[DIAG-*]` and `// TEMPORARY:`.
- `automation/pending_feedback/TEMPLATE_question.md`, `TEMPLATE_answer.md` — canonical templates for the back-pressure escalation file format (step 4).
- `.claude/skills/claude-automated-mode/skill.md` lines 76–139 — single source of truth for the automation Q&A procedure used in the escalation step.
- LLMLOOP (Ravi et al., ICSME 2025) — feedback-loop diminishing-returns finding underlying the five-cycle bound.
- AugmentCode, "Harness Engineering for AI Coding Agents" — multi-gate optimization conflict pattern.
- Flutter docs, *Profiling integration tests* — `IntegrationTestWidgetsFlutterBinding.traceAction()` and `--trace-startup` mechanism.
- Flutter docs, *Accessibility testing* — `tester.ensureSemantics()` + `AccessibilityGuideline` API.
- Flutter docs, *Measuring app size* — `--analyze-size` flag and DevTools "App Size" tool.
- VeryGoodOpenSource `very_good_analysis` — analyzer baseline (188 rules, MIT-OSS).
- `bloc_lint` (pub.dev, OSS) — BLoC-pattern lint rules.
- `clean_architecture_kit` (pub.dev, OSS) — Clean-Architecture layer-leak detection by naming heuristics.
