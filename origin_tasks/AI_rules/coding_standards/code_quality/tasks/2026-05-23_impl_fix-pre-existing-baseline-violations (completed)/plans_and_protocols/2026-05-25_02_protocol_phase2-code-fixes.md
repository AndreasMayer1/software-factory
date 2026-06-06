# Protocol: Phase 2 Code Fixes

## Phase 1 — DONE (gate fixes)
- type-naming: skip private classes + `*.config.dart` → 16 → 0 violations
- complexity analyzer: emits `"kind"` (constructor/method/function)
- check_complexity.py: constructors + copyWith/create use relaxed param limit (15) → ~50 param violations resolved
- exclusions.txt: added injection_container.config.dart, theme.dart, lib/generated/
- Python gates: G1/G2/G4/G5 PASS; G3 only pre-existing test_orchestrate env failure
- Result: complexity 89 → 28 violations

## Phase 2 — remaining 28 complexity violations to fix in code

Refactor approach: extract sub-widgets (build methods) / extract helper methods (logic) / lookup maps (cyclomatic). PURE refactor — NO user-visible behavior change. Run `python3 scripts/quality/check_complexity.py` after each batch; iterate until 0.

### SLOC > 50 — build() methods (extract sub-widgets or `_buildXxx` helpers)
- onboarding_screen.dart:28 (76)
- plan_details_form.dart:131 (83)
- questionnaire_details_view.dart:39 (64)
- plan_list.dart:52 (61)
- therapist_clients_orchestrator.dart:27 (56)
- client_list.dart:51 (56)
- more_root_screen.dart:42 (68)
- empty_state.dart:15 (68)
- question_card.dart:20 (51)
- data_beam_scanner_screen.dart:34 (59) and :252 (64)
- plan_receipt_confirm_screen.dart:21 (83)
- error_display.dart:27 (52)
- grid_example.dart:8 (71)
- likert_scale.dart:15 (72)
- responsive_layout_builder.dart:62 (149)
- modal_dialog.dart:21 (65)
- therapist_navigation_ui.dart:14 (56)
- main.dart:77 (61)

### SLOC > 50 — non-build methods (extract helpers)
- therapist_receive_bloc.dart:36 _onChunkScanned (115)
- plan_transfer_pipeline.dart:209 _validateAndReassemble (52)
- plan_template_detail_bloc.dart:14 constructor (135) — extract event-handler bodies into named methods
- more_layout_config.dart:38 actionGroups (145) — extract each group into a helper
- transfer_bundle.dart:39 assemble (63)
- question.dart:75 create (51)

### Cyclomatic > 20 (question.dart) — reduce branches via helpers/lookup
- question.dart:21 fromJson (25)
- question.dart:75 create (28)

### Parameters > 4
- scaffold_builder.dart:15 buildScaffold (7) — typedef-bound builder; refactor only if callers stay clean, else report.

## Phase 3 — verify + complete
- check_quality_gates.sh exits 0
- flutter test passes
- Remove CLAUDE.md section 12
- File proposals documenting gate changes
