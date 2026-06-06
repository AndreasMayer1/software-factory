# Web Research: Additional Production-Grade Quality Gates for Flutter/Dart

Date: 2026-05-13
Scope: Raw facts only — no recommendations or synthesis. Findings beyond the existing gate set.

---

## 1. Naming-Convention Enforcement

| Tool / Rule | What it catches | False-positive likelihood | License |
|---|---|---|---|
| `file_names` (core Dart linter) | Files not in `lowercase_with_underscores` | Low | Free / OSS (BSD) |
| `library_names` (core Dart linter) | Libraries not in `lowercase_with_underscores` | Low | Free / OSS |
| `library_prefixes` / `package_prefixed_library_names` / `package_names` (core Dart linter) | Library prefix and package naming style | Low | Free / OSS |
| `prefer-match-file-name` (DCM) | File name does not match the name of the primary class declared inside | Medium (files with multiple top-level types) | DCM — free for OSS, paid for commercial |
| `prefer-correct-type-name` (DCM) | Type names outside alphanumeric, UpperCamelCase, configurable length 3–40 | Low–Medium (acronyms, short types) | DCM — free for OSS, paid commercial |
| `prefer-correct-identifier-length` (DCM) | Identifier length bounds for variables/parameters | Medium | DCM paid/OSS-free |
| Effective Dart style guide rules: `camel_case_types`, `camel_case_extensions`, `non_constant_identifier_names`, `constant_identifier_names` (core) | Type, extension, mixin, typedef, constant naming style | Low | Free / OSS |
| `bloc_lint` rule `prefer_file_naming_conventions` | BLoC/Cubit file naming (`*_bloc.dart`, `*_event.dart`, `*_state.dart`, `*_cubit.dart`) | Low | OSS (BSD/MIT, pub.dev) |

Notes:
- No dedicated rule found for "widget class name must end in `Widget`/`Screen`/`Page`"; closest is custom DCM rule authoring.
- Private-member naming is partly covered by `library_private_types_in_public_api` (core) and `prefer-correct-type-name` (DCM).

---

## 2. Folder-Structure / Layering Enforcement

| Tool | What it catches | False-positive likelihood | License |
|---|---|---|---|
| `clean_architecture_linter` (pub.dev, v1.0.8) | 33 rules across `domain_rules`, `data_rules`, `presentation_rules`; cross-layer imports, dependency-rule violations; Riverpod-aware | Medium (opinionated, Riverpod-coupled) | OSS (pub.dev) |
| `clean_architecture_kit` (pub.dev) | Wrong-layer imports, data Models leaking into domain (detected via method signatures, return types, parameters, fields by naming convention), depending on concrete impl instead of abstraction; ships quick-fixes that generate UseCase classes and `toEntity()` mappers | Medium (naming-convention based detection causes some FP) | OSS (pub.dev) |
| `boundaries` (Dart equivalent) | Not found — no Dart port of JS `eslint-plugin-boundaries` exists at time of search | — | — |
| `avoid-banned-imports` (DCM) | Already in user's gate set | Low | DCM |
| Custom DCM rule packs via `dart_code_metrics_presets` | 20 presets, 18 lint presets; supports user-defined preset YAML to combine layer/folder rules | Low–Medium | OSS preset package; DCM engine paid |

No tool found that natively enforces "files in `domain/` must live under `entities/` OR `repositories/` OR `value_objects/` subfolder" via taxonomy declaration; closest mechanism is `avoid-banned-imports` glob rules or custom DCM rules.

---

## 3. Pattern-Usage Hints (BLoC / Repository / UseCase)

| Tool / Rule | What it catches | FP likelihood | License |
|---|---|---|---|
| `bloc_lint` package | Official BLoC lint rules. Rules: `avoid_flutter_imports`, `avoid_public_bloc_methods`, `avoid_public_fields`, `prefer_file_naming_conventions`, `prefer_void_public_cubit_methods`, `avoid_build_context_extensions`, `prefer_bloc`, `prefer_build_context_extensions`, `prefer_cubit` | Low–Medium | OSS (pub.dev) |
| DCM bloc rules: `avoid-bloc-public-methods`, `avoid-passing-bloc-to-bloc` | Public methods on Bloc; passing Bloc instances into other Blocs | Low | DCM paid / OSS-free |
| `clean_architecture_kit` | Repository abstract-vs-concrete enforcement; flags `class FooRepository implements …` missing abstract; flags use-case mixed responsibilities indirectly via model leakage | Medium | OSS |
| `clean_architecture_linter` | Use-case structural rules, domain purity, repository interface conformance (Riverpod-flavoured) | Medium | OSS |
| `riverpod_lint` | Provider-pattern enforcement; not directly relevant to BLoC | Low | OSS |

No public rule found that specifically asserts "BLoC State extends Equatable" — must be authored as custom DCM rule. `bloc_lint` enforces structural BLoC patterns but not Equatable-extension specifically.

---

## 4. Production analysis_options.yaml Rule Sets (vs `flutter_lints`)

Coverage counts (from RydMike comparison + Very Good docs):

| Package | Rules enabled | Notes | License |
|---|---|---|---|
| `flutter_lints` 3.0.1 | 101 rules (~46.3% of available) | Default for new Flutter projects | OSS (BSD) |
| `lints` (Dart team `recommended`) | Smaller superset of core | Used as baseline by others | OSS |
| `very_good_analysis` | 188 rules (~86.2% of available) | Strictest curated set; most pedantic | OSS (MIT) |
| `netglade_analysis` | Curated Dart lints **plus** selected DCM rules; explicit strict-types stance (forces non-dynamic inference); built after analyzing very_good_analysis, leancode_lint, flutter_lints | OSS (pub.dev) |
| `leancode_lint` | Curated; referenced as input to netglade | OSS |
| `theodo_analysis` (bamlab) | Lint + DCM rules from Theodo Apps | OSS |
| `dart_code_metrics_presets` | 20 presets (18 lint presets): All, Recommended, Dart, Flutter, Bloc, Riverpod, etc.; custom presets supported | OSS (preset YAML); DCM engine paid for commercial |
| `pedantic` | Deprecated; historical reference | OSS |

Rules `very_good_analysis` enables that `flutter_lints` does NOT (sample, not exhaustive):
- `always_declare_return_types`, `always_put_required_named_parameters_first`, `always_use_package_imports`, `avoid_bool_literals_in_conditional_expressions`, `avoid_catches_without_on_clauses`, `avoid_catching_errors`, `avoid_double_and_int_checks`, `avoid_dynamic_calls`, `avoid_escaping_inner_quotes`, `avoid_field_initializers_in_const_classes`, `avoid_final_parameters`, `avoid_implementing_value_types`, `avoid_js_rounded_ints`, `avoid_multiple_declarations_per_line`, `avoid_positional_boolean_parameters`, `avoid_redundant_argument_values`, `avoid_setters_without_getters`, `avoid_slow_async_io`, `avoid_type_to_string`, `avoid_types_on_closure_parameters`, `avoid_unused_constructor_parameters`, `cancel_subscriptions`, `cascade_invocations`, `close_sinks`, `comment_references`, `deprecated_consistency`, `directives_ordering`, `do_not_use_environment`, `eol_at_end_of_file`, `flutter_style_todos`, `join_return_with_assignment`, `leading_newlines_in_multiline_strings`, `literal_only_boolean_expressions`, `missing_whitespace_between_adjacent_strings`, `no_adjacent_strings_in_list`, `noop_primitive_operations`, `one_member_abstracts`, `only_throw_errors`, `package_api_docs`, `parameter_assignments`, `prefer_asserts_in_initializer_lists`, `prefer_asserts_with_message`, `prefer_constructors_over_static_methods`, `prefer_foreach`, `prefer_int_literals`, `prefer_null_aware_method_calls`, `prefer_void_to_null`, `secure_pubspec_urls`, `sort_constructors_first`, `sort_unnamed_constructors_first`, `test_types_in_equals`, `throw_in_finally`, `tighten_type_of_initializing_formals`, `unawaited_futures`, `unnecessary_await_in_return`, `unnecessary_lambdas`, `unnecessary_null_aware_assignments`, `unnecessary_null_checks`, `unnecessary_parenthesis`, `unnecessary_raw_strings`, `unnecessary_statements`, `unnecessary_to_list_in_spreads`, `use_decorated_box`, `use_enums`, `use_if_null_to_convert_nulls_to_bools`, `use_is_even_rather_than_modulo`, `use_late_for_private_fields_and_variables`, `use_named_constants`, `use_raw_strings`, `use_setters_to_change_properties`, `use_string_buffers`, `use_test_throws_matchers`, `use_to_and_as_if_applicable`. FP likelihood: Low–Medium overall; `cascade_invocations` and `prefer_final_parameters`-style rules generate higher noise.

Wonderous / Reflectly / Folio analysis_options.yaml: search did not return direct rule diffs in this round; documented patterns from those repos typically extend `flutter_lints` with a small selection from the above set rather than enabling all.

---

## 5. Architecture-Specific Dart Analysis Tools

| Tool | What it is | FP | License |
|---|---|---|---|
| `clean_architecture_linter` (pub.dev v1.0.8) | 33-rule custom lint; layered rules; Riverpod-flavoured | Medium | OSS |
| `clean_architecture_kit` (pub.dev) | Opinionated Clean Architecture linter with quick-fixes that scaffold UseCase + `toEntity()` mappers; layer-import and model-leak detection by naming heuristics | Medium | OSS |
| `dart_code_metrics_presets` (CQLabs) | 20 presets (Bloc, Riverpod, Dart, Flutter, All, Recommended, …); custom presets via YAML; loadable in any DCM config | Low | OSS preset YAMLs; DCM engine paid commercial / free OSS |
| `theodo_analysis` (bamlab) | Theodo Apps internal lint + DCM rules; clean-architecture aware | Medium | OSS |
| `layer_kit` (pub.dev) | Flutter package; folder-layer scaffolding (less of a linter, more a generator) | n/a | OSS |
| `clean_feature_arch` (pub.dev) | Feature-first architecture helpers | n/a | OSS |
| `arc_lint` | Not found on pub.dev under that name | — | — |
| `boundaries` (Dart port) | Not found | — | — |
| DCM custom-rule authoring | Allows writing user-defined Dart rules (e.g., "repository must implement interface", "use-case must have single public method") | Depends on rule quality | DCM engine paid for commercial |

DCM licensing summary: Free for individual / OSS contributors via DCM OSS license (announced Oct 2023). Teams license required for commercial use; subscriptions handled via Lemon Squeezy; bank transfer available for annual licenses only. Free and Pro plan licenses do not require account creation; Teams license does.

---

## Sources

- https://dart.dev/tools/linter-rules/file_names
- https://dart.dev/tools/linter-rules/library_names
- https://dart.dev/tools/linter-rules/package_names
- https://dart.dev/tools/linter-rules/package_prefixed_library_names
- https://dart.dev/effective-dart/style
- https://dcm.dev/docs/rules/common/prefer-match-file-name/
- https://dcm.dev/docs/rules/common/prefer-correct-type-name/
- https://dcm.dev/docs/rules/bloc/avoid-bloc-public-methods/
- https://dcm.dev/docs/rules/bloc/avoid-passing-bloc-to-bloc/
- https://dcm.dev/pricing/
- https://dcm.dev/blog/2023/10/18/announcing-dcm-license-for-oss-projects/
- https://pub.dev/packages/clean_architecture_linter/versions/1.0.8
- https://pub.dev/packages/clean_architecture_kit
- https://pub.dev/packages/dart_code_metrics_presets
- https://github.com/CQLabs/dart-code-metrics-presets
- https://pub.dev/packages/bloc_lint
- https://github.com/vmichalak/bloc_lint
- https://bloclibrary.dev/lint/
- https://bloclibrary.dev/lint-rules/avoid_flutter_imports/
- https://bloclibrary.dev/lint-rules/avoid_public_bloc_methods/
- https://pub.dev/packages/very_good_analysis
- https://github.com/VeryGoodOpenSource/very_good_analysis
- https://rydmike.com/blog_flutter_linting.html
- https://pub.dev/packages/netglade_analysis
- https://www.netglade.cz/en/blog/fluter-apps-linter-dart-netglade-analysis
- https://github.com/bamlab/theodo_analysis
- https://pub.dev/packages/layer_kit
- https://pub.dev/packages/clean_feature_arch
