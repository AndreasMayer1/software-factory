---
date: 2026-05-16
type: protocol
task: TASK-PROC-046-03
---

# Post-switch baseline — analyzer = very_good_analysis + bloc_lint + clean_architecture_kit

`flutter analyze` after Parts A–B of the baseline switch (2026-05-16, runtime ~585s):

```
7435 issues total
  34 errors    (post-exclusion: 0 in our scope lib/test/integration_test after adding Temp/**; packages/**)
 161 warnings
7240 info
```

## Breakdown by scope (AC-01 scope = lib/ test/ integration_test/ only)

| Severity | Count |
|---|---:|
| error    | 11  |
| warning  | 159 |
| info     | ~7240 (out of AC-01 scope) |

## Errors in AC-01 scope (11 total)

| File | Rule | Line | Fix applied |
|---|---|---|---|
| integration_test/integration_suite_test.dart | missing_required_argument | 164 | Added _FakeLogger + logger: param |
| lib/core/data/adapters/app_role_adapter.dart | argument_type_not_assignable | 10 | `as String` cast |
| lib/core/domain/services/questionnaire_plan/serialization_utils.dart | invalid_assignment | 25 | `as Map<String, dynamic>` cast |
| lib/features/therapist/data_transfer/domain/services/plan_transfer_pipeline.dart | invalid_assignment | 334 | `as Map<String, dynamic>` cast |
| test/helpers/bloc_test_helper.dart | missing_required_argument | 12 | DELETED (zero callers) |
| test/helpers/test_router_helpers.dart | undefined_class, undefined_function | 28,44,45,60 | DELETED (zero callers, ITokens/Tokens/DefaultTokens no longer exist) |
| test/unit/features/role_selection/domain/usecases/persist_role_use_case_test.dart | argument_type_not_assignable | 58 | cast added |
| test/unit/mocktail_test.dart | return_of_invalid_type | 6 | DELETED (zero callers) |

## Top warning categories (159 total)

| Rule | Count | Strategy |
|---|---:|---|
| inference_failure_on_instance_creation | 57 | Add explicit type args (Left<F,T>, Right<F,T>, Future<void>) |
| unused_local_variable | 34 | Prefix `_` or remove |
| unused_element | 15 | Suppress with justification or remove |
| strict_raw_type | 14 | Add explicit type args to Left/Right |
| override_on_non_overriding_member | 9 | Remove @override |
| inference_failure_on_collection_literal | 9 | Add element types to [] {} literals |
| unreachable_switch_default | 6 | Suppress with defensive-catch-all justification |
| others | 15 | Various targeted fixes |

## Info-level findings (~7240)

**Out of AC-01 scope** (AC-01 = zero errors / zero warnings; info not included).

Top info rules: `lines_longer_than_80_chars` (2642), `public_member_api_docs` (1337),
`directives_ordering` (388), `omit_local_variable_types` (357), `avoid_redundant_argument_values`
(346), `prefer_const_constructors` (313), `eol_at_end_of_file` (298).

These will be addressed in a separate hygiene task if desired (user decision D2: out of scope).

## Bridge rule (critical)

Running `flutter analyze` directly in the devcontainer is FORBIDDEN per CLAUDE.md and user
answer 2026-05-16 D1. All subsequent analyze runs MUST go through:
```
scripts/win-command-bridge/win_bridge.sh flutter_analyze
scripts/win-command-bridge/win_bridge.sh wait-result --timeout 1800
```

## Fix agents dispatched (2026-05-16)

10 background implementation-engineer agents dispatched in parallel covering all 74 violation files.
Split into batches of 5-9 files:
- Batch A: delete stale helpers + integration_suite_test + app_router
- Batch B: lib errors (casts) + questionnaire entity
- Batch C: entity files + injectable annotation removal  
- Batch D: misc lib files + integration test
- Batch E: presentation blocs + mock
- Batch F: integration tests unused vars
- Batch G: choice service tests Left/Right type args
- Batch H: questionnaire service tests Left/Right
- Batch I: theme bloc + role tests + misc
- Batch J: widget tests + more screens
