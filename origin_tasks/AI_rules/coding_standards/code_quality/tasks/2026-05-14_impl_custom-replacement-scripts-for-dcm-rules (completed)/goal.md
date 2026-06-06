---
task_id: TASK-PROC-046-14
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-14
started: 2026-05-19
completed: 2026-05-19
session_completed_at: 2026-05-19T06:36:34Z
after: [TASK-PROC-046-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-05]
  sections: []
scope_description: "Replace the gate-set capabilities that DCM previously provided with custom DCM-free scripts under scripts/quality/. Targets: complexity metrics (cyclomatic / params / SLOC / nesting) via dart analyze --json parsing; type-name regex enforcement; architectural-imports enforcement (replaces avoid-banned-imports); ban-name for direct styling classes; test smells (missing-assertion etc.); folder taxonomy enforcement under domain/. Implements user feedback 2026-05-13 K.3 (no DCM license) + K.2 (folder taxonomy script)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: ce8784d5-358d-432b-bf50-958e1b950c83
session_account: gmail2
---
# Goal: Custom DCM-free replacement scripts for the gate set

## Objective

DCM provided several capabilities the gate set depends on: complexity metric measurement, type-name regex enforcement, architectural import-boundary enforcement, name banning, test-smell detection. Since the project has no DCM commercial license (user 2026-05-13 K.3), these capabilities are now replaced with custom scripts living next to the other quality gates under `scripts/quality/`.

The Dart `analyzer` package (open-source, BSD-licensed, installable as a pub-cache dev-dep) emits a JSON AST via `dart analyze --json` that supports all the complexity-style introspection DCM did. The rest are grep-based or AST-based scripts.

## Requirements Summary

REQ-PROC-046 AC-02 (complexity bounds — measurement now custom), AC-05 (architectural purity — enforcement now custom). User feedback 2026-05-13 K.2 (folder taxonomy script confirmed) and K.3 (no DCM, find alternatives).

Current requirements: ../../requirements.md

## Scope

### In Scope

Each item below is a script (or small package of scripts) under `scripts/quality/`. Each script:

- Exits 0 on pass, non-zero with a clear failure message on fail.
- Supports `--exclude-paths <file>` (defaults to `scripts/quality/exclusions.txt`) for legitimate exceptions.
- Has a per-script entry in `scripts/quality/README.md`.

**1. `scripts/quality/check_complexity.py` — replaces DCM metrics (cyclomatic, params, SLOC, nesting).**

Approach: use Dart's `analyzer` package via a small Dart CLI that parses each file's AST and computes the four metrics per function / method. Wire from Python: `python3 check_complexity.py` shells out to the Dart CLI and parses the JSON output.

Alternative: use `dart analyze --format=json` and post-process. This output already includes some diagnostics but lacks first-class complexity metrics. The custom Dart CLI is the more reliable path.

Thresholds (carried over from REQ-PROC-046 AC-02; subject to refinement once empirical data exists):

- Cyclomatic complexity ≤ 20 per function
- Parameters ≤ 4 per function
- Source-lines-of-code ≤ 50 per function body
- Maximum control-flow nesting level ≤ 5 (control-flow only, NOT widget composition — per REQ-PROC-046 AC-02 explicit clarification)

The Dart-side helper (e.g. `scripts/quality/_complexity_analyzer/`) is a `pubspec.yaml` package with `analyzer` as a dependency. Built separately from the main app; bin entry point invoked by the Python script.

**2. `scripts/quality/check_type_naming.sh` — replaces DCM `prefer-correct-type-name`.**

Grep `lib/` for class declarations: `^class \([A-Z][A-Za-z0-9_]*\)` (or use the Dart CLI from item 1 to be more accurate). For each class name, verify it matches the regex `^[A-Z][a-zA-Z0-9]*((Event)|(Failure)|(Bloc)|(State)|(Repository)|(Service)|(UseCase)|(Entity)|(ValueObject))?$`. Exempt: test files (different naming convention), generated files (`*.g.dart`, `*.freezed.dart`), enum names, mixin names — all excluded via path/pattern rules. Flag every non-conformant class with `file:line` and suggested fix.

**3. `scripts/quality/check_architectural_imports.sh` — replaces DCM `avoid-banned-imports`.**

Path-specific import policy (from `doc/linter/linter_configuration_proposal.md` historical reference, validated against current architecture):

- Files under `lib/core/domain/` and `lib/features/*/domain/`: zero imports of `package:flutter/*` or `package:flutter_bloc/*`.
- Files under `lib/features/*` (anywhere in the feature tree): zero direct imports of `package:flutter/material.dart` (must use design-system components via `lib/core/design_system/` instead).
- Files under `lib/core/domain/entities/` and similar value-object folders: zero imports of `dart:collection` (must use `package:built_collection` for immutable collections).

Script reads each file's imports and matches against per-path-glob deny lists. Exit non-zero on violations with `file:line:import_statement`.

**4. `scripts/quality/check_no_direct_styling.sh` — replaces DCM `ban-name` for styling classes.**

Per 2026-05-13 K.1 confirmation: forbidden inside `lib/features/`, allowed inside `lib/core/design_system/`. Grep `lib/features/` for: `\bButtonStyle\s*\(`, `\bTextStyle\s*\(`, `\bColor\s*\(`, `\bColors\.`, `\bThemeData\s*\(`. Each match must use the design-system components from `lib/core/design_system/`. Exit non-zero on violations.

**5. `scripts/quality/check_test_smells.sh` — replaces DCM `missing-test-assertion`, `avoid-empty-test-groups`, `prefer-test-matchers`.**

Three sub-checks against `test/unit/`, `test/widget/`, `integration_test/`:

- **Missing assertion**: every `test('...', () { ... })` / `testWidgets('...', (...) { ... })` body must contain at least one `expect(`, `verify(`, `tester.ensureSemantics()`, or similar assertion-style call. Tests with zero assertion-style calls flagged.
- **Empty group**: `group('...', () { ... })` with empty body (zero `test(` calls in the closure body) flagged.
- **Literal expect**: `expect(x.length, 1)` (and similar) flagged in favour of `expect(x, hasLength(1))`. This is heuristic-only; a small grep for `expect\(.*\.length,\s*\d` is a good enough first pass.

**6. `scripts/quality/check_folder_taxonomy.sh` — implements REQ-PROC-046 K.2 (user 2026-05-13).**

Walk `lib/core/domain/` and `lib/features/*/domain/`. Every `.dart` file MUST live in one of the allowed sub-folders: `entities/`, `repositories/`, `value_objects/`, `services/`, `failures/`, `events/`, or other documented additions to the taxonomy. Files at the bare `domain/` level (no sub-folder) flagged. Files in unexpected sub-folder names flagged. The allowed-sub-folder list is configurable via `scripts/quality/folder_taxonomy_allowlist.txt` so future additions don't require a script change.

**7. Entry point + integration.**

`scripts/quality/check_quality_gates.sh` (existing) updated to invoke each of the six new scripts in sequence. Each script's output is appended to the entry-point's summary. Total exit code is the max of the individual exit codes.

`scripts/quality/README.md` updated with descriptions of each new script.

**8. Wire into the back-pressure protocol.**

`verify-quality` skill (created by TASK-PROC-046-11) is updated to invoke the new scripts. The `quality-checker` agent is updated to parse the scripts' output (per-script JSON or structured text — implementer chooses the format).

### Out of Scope

- Custom replacements for Flutter-perf DCM rules (`avoid-unnecessary-setstate`, `avoid-shrink-wrap-in-lists`, `avoid-rebuilds`, `avoid-returning-widgets`, `prefer-extracting-callbacks`, `avoid-expensive-async-functions`, `avoid-passing-async-when-sync-expected`). Per 2026-05-13 C decision: these move to `doc/presentation/coding/best_practices.md`. Quality-checker reads + judges; no script.
- Custom replacement for `avoid-dynamic` / `no-object-declaration`. VGA's `avoid_dynamic_calls` covers most cases; the residual checks move to `doc/`.
- Tightening thresholds. Initial values match the previous (DCM-era) thresholds; refinement comes via the proposals-loop (TASK-PROC-046-13).
- Performance optimisation of the scripts. Correctness first; speed second.

## Acceptance Criteria

- [x] All six scripts exist under `scripts/quality/` with executable permissions and `--exclude-paths` support.
- [x] `scripts/quality/check_quality_gates.sh` invokes all six and aggregates exit codes.
- [x] `scripts/quality/README.md` documents each new script (purpose, threshold, exit codes, exclusion mechanism).
- [x] `scripts/quality/_complexity_analyzer/` (the Dart helper for `check_complexity.py`) is buildable, has `pubspec.yaml`, and emits stable JSON.
- [x] Each script runs successfully against the current codebase. Baseline output recorded in `plans_and_protocols/`.
- [x] `verify-quality` skill (from TASK-PROC-046-11) is updated to invoke and parse the new scripts. *(Deferred: TASK-PROC-046-11 still pending; skill does not yet exist. The `quality-checker` agent — the actively-used review path — has been updated; the skill wiring is owned by TASK-PROC-046-11. See `plans_and_protocols/2026-05-19_03_protocol_implementation.md`.)*
- [x] `quality-checker` agent updated similarly.
- [x] `doc/linter/linter_setup_and_guidelines.md` mentions the new scripts as the DCM replacement layer.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-03 | Pending | `very_good_analysis` baseline must be live so the new scripts only need to cover what's NOT in VGA |
| TASK-PROC-046-11 | Pending | `verify-quality` skill is the consumer that invokes the new scripts |

## Notes

The complexity-metric Dart helper is the riskiest item. Two paths:

1. **Build it as a Dart CLI** using `package:analyzer` (the same parser flutter analyze uses). Pros: AST-level precision; the cleanest cyclomatic count. Cons: ~200 lines of Dart, requires building a small package.
2. **Use `dart analyze --format=json` + post-process**. Pros: zero new code in Dart. Cons: the JSON does not expose per-function complexity directly; would need lexical heuristics that are less accurate.

Recommendation: path 1 for correctness. The Dart CLI lives in `scripts/quality/_complexity_analyzer/` as a small dev-only Dart package (no Flutter dependency). Builds via `dart pub get` in CI. Output: JSON with one entry per function `{path, function_name, line, cyclomatic, parameters, sloc, max_nesting}` plus a top-level summary.

The folder-taxonomy script's allowlist file means new taxonomy categories can be added without a script change. If the user later wants to add `usecases/` (separate from the existing `services/` convention), they add the line to `folder_taxonomy_allowlist.txt` and the gate accepts it. This keeps the gate flexible without per-change script edits.

The architectural-imports script's per-path policy file is similarly externalised: `scripts/quality/architectural_imports_policy.yaml` lists path-glob → deny-imports pairs. New policies can be added without touching the script.

If any script's false-positive rate is high after baselining, the proposals-loop (TASK-PROC-046-13) is the right channel to tighten / loosen the rule — not autonomous script edits.
