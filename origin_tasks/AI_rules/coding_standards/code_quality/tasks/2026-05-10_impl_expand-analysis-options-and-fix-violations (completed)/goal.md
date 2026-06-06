---
task_id: TASK-PROC-046-03
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-17
effort: L
created: 2026-05-10
updated: 2026-05-17
started: 2026-05-16
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-05, AC-12]
  sections: []
scope_description: "Adopt very_good_analysis as the analyzer baseline (replaces flutter_lints), add bloc_lint and clean_architecture_kit as dev-deps, drop every DCM-dependent rule (project has no DCM commercial license), document the WHY behind every active rule inline, fix violations that surface. Custom replacements for DCM-provided gates (complexity metrics, type-name regex, architectural imports, ban-name, test smells, folder taxonomy) are owned by TASK-PROC-046-14 separately."
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: ""
session_account: gmail
---

# Goal: Adopt very_good_analysis + bloc_lint + clean_architecture_kit (no DCM)

## Recommended Skill

**Use `code-complex` skill for this task.** Switching analyzer baseline will surface a large violation set across `lib/`, `test/`, and `integration_test/`. The fix-vs-suppress decisions for many violations benefit from the plan-and-approve gate before implementation.

## Objective

The user has no commercial DCM license (per 2026-05-13 feedback K.3). All DCM-dependent rules from the previous TASK-PROC-046-03 scope must be dropped. The replacement baseline is `very_good_analysis` — 188 rules vs. `flutter_lints`' 101, MIT-licensed OSS, no commercial-license issue.

This task adopts the new baseline and drops DCM. The custom replacements for what DCM provided (complexity metrics, type-name regex, architectural-imports enforcement, ban-name, test-smells, folder-taxonomy) are owned by a separate task (TASK-PROC-046-14) because the complexity of writing them via the Dart `analyzer` package + grep is non-trivial and merits its own plan-and-approve cycle.

## Requirements Summary

REQ-PROC-046 AC-01 (source hygiene), AC-02 (complexity bounds — note: complexity metrics themselves move to TASK-PROC-046-14; here we adopt the rest of G1), AC-05 (architectural purity — replacement script owned by TASK-PROC-046-14), AC-12 (no debug artifacts — `avoid_print` is in VGA).

Current requirements: ../../requirements.md

## Scope

### In Scope

**Part A — Baseline switch.**

1. Add `very_good_analysis` to `pubspec.yaml` under `dev_dependencies` (latest stable; check pub.dev at task start).
2. Add `bloc_lint` to `pubspec.yaml` `dev_dependencies` (per 2026-05-13 K.5 confirmation).
3. Add `clean_architecture_kit` to `pubspec.yaml` `dev_dependencies` (per 2026-05-13 K.5 confirmation).
4. Replace `include: package:flutter_lints/flutter.yaml` in `analysis_options.yaml` with `include: package:very_good_analysis/analysis_options.yaml`.
5. Remove `dart_code_linter` package from `pubspec.yaml` if present (the DCM tool — separate from `dart_code_metrics_presets`).
6. Remove the entire `dart_code_linter:` top-level block from `analysis_options.yaml`. This drops:
   - `metrics:` (cyclomatic-complexity / number-of-parameters / source-lines-of-code / maximum-nesting-level) — replaced by TASK-PROC-046-14 custom scripts.
   - `rules:` — all DCM-specific rules including `prefer-correct-type-name`, `avoid-banned-imports`, `avoid-dynamic`, `no-object-declaration`, `avoid-global-state`, `ban-name`, `avoid-unnecessary-setstate`, `avoid-shrink-wrap-in-lists`, `prefer-extracting-callbacks`, `avoid-expensive-async-functions`, `avoid-passing-async-when-sync-expected`, `arguments-ordering`, `format-comment`, `member-ordering`, `newline-before-return`, `prefer-trailing-comma`, `prefer-intl-name`, `prefer-provide-intl-description`.

**Part B — Add the rules `very_good_analysis` does NOT include but we want.**

`very_good_analysis` already enables `unawaited_futures`, `only_throw_errors`, `avoid_catches_without_on_clauses`, `avoid_print`, `cancel_subscriptions`, `close_sinks`, `prefer_const_constructors` and friends, `use_test_throws_matchers`, `avoid_dynamic_calls`, `file_names`, `camel_case_types`, `non_constant_identifier_names`, `library_private_types_in_public_api`. Most of the previous scope's rules are picked up automatically by switching the baseline.

Explicit additions beyond VGA (if any) are listed at task-start by running `flutter analyze` once and checking what's missing. Likely additions:

- `discarded_futures` (if not in VGA)
- `avoid_returning_null` for null-safety transitions
- Whatever specific Flutter / Bloc rules `bloc_lint` enables (review the package's exported rule set)

**Part C — WHY-comment each rule.**

Per user feedback 2026-05-13 K.1: every active rule in `analysis_options.yaml` gets a YAML comment with its rationale. Format:

```yaml
linter:
  rules:
    # Why: domain layer integrity — unhandled Futures in the data path silently
    # lose mental-health entries on slow eMMC storage when the process is killed.
    # Source: REQ-PROC-046 AC-05; PERSONA-004 zero-data-loss.
    unawaited_futures: true

    # Why: const widgets avoid rebuilds; PERSONA-004 names the Galaxy A40 (4 GB
    # mid-tier 2019) as the reference target — const-correctness keeps the frame
    # budget reachable. Source: REQ-PROC-046 AC-08 + G7 static perf.
    prefer_const_constructors: true
```

For rules added by the `include:` (VGA base), document inline only the *non-obvious* ones — e.g. rules where this project has a specific reason beyond "VGA recommends it" (the Galaxy-A40 perf reasons, the persona-driven motivations). Pure-style rules are left without comments — VGA's own documentation is the authority for those.

**Part D — Fix resulting violations.**

Run `flutter analyze` after the baseline switch and address every error / warning. Per REQ-PROC-046 protocol: fix the cause, not the symptom. Suppress with `// ignore: <rule>` + adjacent justification per AC-11 only where the rule's intent does not apply to the specific case. Record the violation count + categories in `plans_and_protocols/`.

**Part E — Document the DCM removal.**

Add a short note to `doc/linter/linter_setup_and_guidelines.md`: "DCM (dart_code_linter) was removed 2026-05-14 because the project has no commercial license. The complexity-metric, type-name, architectural-imports, ban-name, and test-smell gates DCM previously provided are implemented as custom scripts under `scripts/quality/` — see TASK-PROC-046-14." Reference `doc/linter/linter_configuration_proposal.md` as historical reference only; do not adopt its content (it predates the DCM licensing change and is now obsolete in those areas).

### Out of Scope

- Writing the custom replacement scripts for complexity metrics, type-name regex, architectural-imports enforcement, ban-name, test smells, folder taxonomy. **TASK-PROC-046-14 owns those.**
- Tightening or loosening threshold values (cyclomatic ≤ 20, params ≤ 4, SLOC ≤ 50, nesting ≤ 5). Those move to TASK-PROC-046-14; we keep them at the previously-documented values until evidence to change.
- Adopting `dart_code_metrics_presets` package. That requires the DCM engine which we just removed.
- Custom Flutter-perf rule re-implementation (`avoid-unnecessary-setstate` etc.). Per 2026-05-13 C decision: these move to `doc/presentation/coding/best_practices.md` for `quality-checker` to read; not new gates.

## Acceptance Criteria

- [ ] `pubspec.yaml` has `very_good_analysis`, `bloc_lint`, `clean_architecture_kit` under `dev_dependencies`; `dart_code_linter` is removed.
- [ ] `analysis_options.yaml`'s `include:` directive points at `very_good_analysis`.
- [ ] The `dart_code_linter:` block is completely removed from `analysis_options.yaml`.
- [ ] Each active rule (beyond the VGA include) has a `# Why: ...; Source: ...` comment block.
- [ ] `flutter analyze` produces zero errors / warnings against `lib/`, `test/`, `integration_test/`.
- [ ] `dart fix --apply` is idempotent on the resulting tree.
- [ ] Any added `// ignore:` suppressions have adjacent justification comments per AC-11.
- [ ] Violation-count baseline (before fix) recorded in `plans_and_protocols/` so the next task that touches these rules has a reference.
- [ ] `doc/linter/linter_setup_and_guidelines.md` documents the DCM removal and the migration path to TASK-PROC-046-14 custom scripts.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

The baseline switch will surface a large violation set — `very_good_analysis` is significantly stricter than `flutter_lints`. Expect 100–500 new findings depending on codebase state. The implementer is expected to:

1. Run analyzer once to size the violation set.
2. Categorise by rule (which rules contribute most?).
3. Triage: which can be auto-fixed by `dart fix --apply`, which need manual code changes, which need `// ignore:` with justification.
4. Address in batches. If the total work exceeds one focused session, split into sub-tasks (per REQ-PROC-046 protocol, escalation is via the project's automation Q&A mechanism, not silent shortcuts).

The K.1 question on `avoid-dynamic` / `no-object-declaration`: **these are about TYPE SAFETY, not performance**. `dynamic` disables static type checking — runtime type-errors instead of compile-time. The performance angle is secondary (the analyzer can't optimise without types). Both rules were DCM-only; their replacements via VGA: `avoid_dynamic_calls` (catches `dynamic` method calls — narrower scope than `avoid-dynamic`). For JSON deserialisation: `Map<String, dynamic>` from `json.decode` is an acceptable boundary; cast immediately to typed objects, never let `dynamic` propagate into business logic. The `ban-name` for `ButtonStyle` / `TextStyle` / `Color` is replaced by a custom grep in TASK-PROC-046-14.
