---
date: 2026-05-16
type: plan
task: TASK-PROC-046-03
author: orchestrator (inline; no agent spawn — goal.md is already a fully-specified plan)
---

# Plan: Switch analyzer baseline to very_good_analysis (drop DCM)

## Context

The `goal.md` already specifies the complete five-part plan (Parts A–E). This file is
therefore a thin orchestration plan, not a re-derivation. It records the execution
order, the splitting decision, and the empirically measured violation set after the
baseline switch (filled in during execution).

## Execution Order

| Step | Action | Owner |
|------|--------|-------|
| 1 | Capture pre-switch baseline: `flutter analyze` output → `02_baseline-before.md` | inline |
| 2 | Edit `pubspec.yaml`: add `very_good_analysis`, `bloc_lint`, `clean_architecture_kit`; remove `dart_code_linter` | inline |
| 3 | `flutter pub get` | inline |
| 4 | Rewrite `analysis_options.yaml`: change `include:` to VGA; remove `dart_code_linter:` block; add WHY-commented project-specific rules | inline |
| 5 | `flutter analyze` → post-switch violation list → `03_baseline-after-vga.md` | inline |
| 6 | **Decision gate**: count violations. If > ~150 OR span > 30 files OR distinct rule categories > 8, split fix work into sub-tasks. Otherwise fix inline. | inline |
| 7 | Fix violations (in-task) OR create sub-tasks (split path) | inline / task-create |
| 8 | Update `doc/linter/linter_setup_and_guidelines.md`: DCM-removal note, migration to TASK-PROC-046-14 custom scripts | inline |
| 9 | `dart fix --apply` until idempotent | inline |
| 10 | `flutter analyze` final pass — zero errors / warnings | inline |
| 11 | `task-complete` skill | inline |

## Split-Decision Heuristic

Per code-complex skill step 3:

- **No split**: < 50 violations and ≤ 2 layers touched — fix inline in this task.
- **Soft split**: 50–150 violations — fix the highest-impact categories inline; spin off a
  follow-up task `2026-05-10_impl_expand-analysis-options-and-fix-violations_followup`
  for low-priority residual `// ignore:` cleanups.
- **Hard split**: > 150 violations or > 30 files affected — fix `pubspec` / `analysis_options`
  / doc in this task (Parts A–C + E) and create a sibling task
  `2026-05-10_impl_expand-analysis-options-and-fix-violations_violations` for Part D.

The actual split decision is recorded in `02_baseline-after-vga.md` once the analyzer runs.

## Out of Scope (reaffirmed)

- Custom complexity / type-name / architectural-import / ban-name / test-smell / folder-taxonomy
  scripts — owned by TASK-PROC-046-14.
- Threshold tuning (cyclomatic ≤ 20 etc.) — TASK-PROC-046-14.
- Adopting `dart_code_metrics_presets` — requires DCM engine which is being removed.

## Risk

| Risk | Mitigation |
|------|------------|
| VGA + bloc_lint + clean_architecture_kit produce thousands of violations | Split heuristic above; sub-task creation |
| `clean_architecture_kit` proves to be inactive/unmaintained on current pub.dev | Confirm package availability before pub-get; if abandoned, document and proceed without it (does not block AC since architectural enforcement is moving to TASK-PROC-046-14 custom scripts) |
| `dart fix --apply` introduces formatting churn unrelated to the gate | Run `dart fix --apply` after violation fixes, then verify idempotency |
| Switch breaks existing tests via behavioural lint rules | Run `flutter test` after the switch as part of step 10 |

## WHY-comment Policy for `analysis_options.yaml`

- Rules added on top of the VGA include: every one gets a `# Why: ...; Source: ...` block.
- Rules from the VGA include: no inline comment unless this project has a project-specific
  rationale (e.g. PERSONA-004 Galaxy-A40 perf framing) beyond "VGA recommends it". VGA's
  own README is the authority for style-only rules.
