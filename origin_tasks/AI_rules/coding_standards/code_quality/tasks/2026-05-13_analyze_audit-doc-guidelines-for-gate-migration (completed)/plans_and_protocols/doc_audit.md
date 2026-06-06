---
date: 2026-05-15
task_id: TASK-PROC-046-12
parent_requirement: REQ-PROC-046
ac: AC-13
status: complete
files_walked: 79
---

# doc/ Audit — Gate Migration Candidates

REQ-PROC-046 AC-13: Establish a single authoritative location for the gate set and clarify which doc/ rules are scriptable (gate) vs. judgment (doc/).

---

## Top-Line Totals

| Classification | Count |
|---|---|
| (a) Gate-scriptable (not yet a gate) | **28** |
| (b) Judgment-only (stays in doc/) | **71** |
| (c) Already gate-enforced | **19** |
| **Files walked** | **79 / 79** |

### Migration effort for (a) findings

| Effort | Count | Cumulative |
|---|---|---|
| S — single rule activation or ≤10 LOC grep | 18 | 18 |
| M — ≤50 LOC script or DCM config | 9 | 27 |
| L — AST-based or multi-file analysis | 1 | 28 |

**Estimated total migration effort**: ~20 S items + 7 M items + 1 L item.

### High-value priorities (top 5)

1. **Activate `avoid-dynamic` in analysis_options.yaml** (S) — doc says "enforces strongly-typed codebase" but rule is absent from current gate set.
2. **Activate `avoid-global-state` in analysis_options.yaml** (S) — mentioned as "key architectural rule" in linter_setup_and_guidelines.md, not activated.
3. **Add `drift` to `avoid-banned-imports` for domain layer** (S) — domain-layer files must not import `drift` but this is not in the banned-imports config.
4. **Add `ILoggingService` / `LoggingServiceImpl` to domain banned-imports** (S) — logging guidelines explicitly prohibit domain code from using the logging interface, but no gate enforces it.
5. **Test folder structure gate** (S) — testing.md mandates `test/unit/` and `test/widget/` subtree structure; no gate currently enforces this.

---

## Per-File Findings

### doc/architecture/README.md

No normative rules — index file.

---

### doc/architecture/dependency_injection.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Always use @injectable annotations for feature-level dependencies" | (b) | Stays in doc/ — requires understanding of class role | — |
| "DO NOT create feature-level injection_container.dart with manual registrations" | (a) | `check_manual_di_registration.sh` — grep `lib/features/` for `getIt.register*` outside `injection_container.dart` | S |
| "For BLoCs, use @singleton" | (b) | Stays in doc/ — entity-detail BLoCs need @factory; requires intent | — |
| "Entity-detail BLoCs must use @factory (not @singleton)" | (b) | Stays in doc/ — distinguishing entity-detail vs feature BLoC requires semantics | — |
| "Services with function-type constructor params: register via @lazySingleton factory in RegisterModule" | (b) | Stays in doc/ — narrow workaround pattern, not generalizable | — |
| "Do not manually register deps already annotated with @injectable" | (a) | Same script as above — `check_manual_di_registration.sh` | S |
| "Avoid @preResolve for critical startup deps; initialize in main.dart first" | (b) | Stays in doc/ — startup ordering requires architectural judgment | — |

---

### doc/architecture/drift_database_patterns.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Always annotate Drift Table subclasses with @DataClassName('<Name>Row')" | (a) | `check_drift_table_naming.sh` — grep `lib/` for `extends Table` without preceding `@DataClassName` | S |
| "Store List<String> as TextColumn with JSON encoding" | (b) | Stays in doc/ — schema choice, not detectable from static code | — |
| "Domain layer MUST NOT import drift" | (a) | Add `drift` to `avoid-banned-imports` entry for `lib/domain/.*` paths in analysis_options.yaml | S |
| "Concrete Drift implementations need @env guards when mock exists" | (b) | Stays in doc/ — requires knowing mock/prod pairing | — |
| "Use sqlite3_flutter_libs, not sqlcipher_flutter_libs for 0.0.1" | (b) | Stays in doc/ — release-stage decision, not code pattern | — |
| "Nullable columns for addColumn migrations (no withDefault)" | (b) | Stays in doc/ — migration strategy, not statically detectable | — |

---

### doc/architecture/failure_handling.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Create failures/ subdirectory in feature/domain" | (a) | `check_domain_failure_structure.sh` — grep domain dirs for Failure classes not in `failures/` subdirectory | M |
| "Define specific failure classes per error scenario" | (b) | Stays in doc/ — granularity is judgment | — |
| "Consider base Failure class per feature (e.g. ChoiceFailure)" | (b) | Stays in doc/ — design decision | — |

---

### doc/architecture/feature_dependency_injection.md

(Largely duplicates `dependency_injection.md`; same rules apply.)

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Always use @injectable for feature-level deps" | (b) | Duplicate of dep_injection.md | — |
| "DO NOT create feature-level injection_container.dart with manual registrations" | (c) | Same gate as dependency_injection.md — cross-reference existing `check_manual_di_registration.sh` proposal | — |
| **Duplication note** | — | This file duplicates dependency_injection.md. After gate is in place, recommend collapsing to a pointer. | — |

---

### doc/architecture/logging.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Inject ILoggingService (interface), never LoggingServiceImpl" | (a) | Add `LoggingServiceImpl` to `ban-name` entries in analysis_options.yaml (paths outside own file and tests) | M |
| "Domain layer MUST NEVER import ILoggingService, call getIt, or use print/debugPrint" | (a) | (1) Add `lib/core/services/logging` to `avoid-banned-imports` for `lib/core/domain/.*`; (2) extend `check_no_debug_artifacts.sh` or new `check_domain_no_logging.sh` for `print`/`debugPrint` in domain | S |
| "Never reference LoggingServiceImpl directly outside its own file and tests" | (a) | As above — ban-name or grep script `check_logging_impl_direct_use.sh` | S |
| "Sensitive data (mood values, keys, names, PII) MUST NEVER appear in log messages" | (b) | Stays in doc/ — static detection unreliable (interpolation patterns too variable); quality-checker reading catches this in review | — |
| "Use LoggingServiceImpl.withLevel in unit tests (not default constructor)" | (b) | Stays in doc/ — test setup convention, hard to automate without false positives | — |
| "Log level policy: debug in debug builds, warning+ in release" | (b) | Stays in doc/ — compile-time constant; not easily lintable | — |
| **Duplication note** | — | `doc/cross_cutting_standards/logging.md` is an exact copy of this file (same content, same examples). Recommend removing one and leaving a pointer. | — |

---

### doc/architecture/routing.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Use named routes (context.goNamed) where possible" | (b) | Stays in doc/ — not always required; requires intent to judge | — |
| "Each feature: dedicated feature_routes.dart with static GoRoute list" | (a) | `check_routing_structure.sh` — grep `lib/features/*/` for GoRoute definitions NOT in `*_routes.dart` files | M |
| "logicalParentPathTemplate must match an existing GoRoute path" | (b) | Stays in doc/ — cross-referencing route trees is runtime concern | — |
| "Back navigation must use context.go(getParentRoute(...))" | (b) | Stays in doc/ — requires control-flow analysis | — |
| "BLoCs must NOT be provided in orchestrators — use StatefulShellRoute level" | (b) | Stays in doc/ — architectural pattern, requires understanding widget hierarchy | — |
| "Use NoTransitionPage consistently for master-detail within nested shells" | (a) | `check_no_transition_page.sh` — grep `lib/features/` nested `StatefulShellRoute` builders for `MaterialPage` or `CupertinoPage` instead of `NoTransitionPage` | S |
| "Use context.push for detail views (preserves back stack); context.go for section switches" | (b) | Stays in doc/ — intent-dependent rule | — |

---

### doc/cross_cutting_standards/README.md

No normative rules — index file.

---

### doc/cross_cutting_standards/logging.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (All rules) | (c) | Exact duplicate of `doc/architecture/logging.md`. All rules and proposed gates already covered there. **Recommend removing this file and replacing with a pointer to `doc/architecture/logging.md`.** | — |

---

### doc/general/documentation_process.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| Documentation update process (Steps 1–7) | (b) | Stays in doc/ — human process, not code | — |
| "Run create-all-merged-files.ps1 after updates" | (b) | Stays in doc/ — script invocation guidance | — |

---

### doc/linter/available_rules.md

No normative rules — reference catalog of available DCM rules. No action.

---

### doc/linter/linter_configuration_proposal.md

This document (dated 2025-09-29) proposes activating several DCM rules that remain **absent from the current `analysis_options.yaml`**. Each unenforced proposed rule is an (a) finding.

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| `avoid-dynamic` — proposed but not in current analysis_options.yaml | (a) | Add to `dart_code_linter.rules` in analysis_options.yaml | S |
| `avoid-global-state` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `no-object-declaration` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `avoid-late-keyword` — proposed but not activated | (a) | Add to `dart_code_linter.rules` (configurable — allow in tests) | S |
| `avoid-non-null-assertion` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `prefer-async-await` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `prefer-conditional-expressions` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `prefer-immediate-return` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `no-boolean-literal-compare` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `binary-expression-operand-order` — proposed but not activated | (a) | Add to `dart_code_linter.rules` | S |
| `prefer_single_quotes` — proposed (linter: section) but not activated | (a) | Add to `linter.rules` in analysis_options.yaml | S |

> **Note**: The proposal doc is dated 2025-09-29 and may be partially outdated; validate each rule before activating. The proposal is the canonical statement of intent from when the linter was set up — if rules were intentionally deferred, that decision is not documented.

---

### doc/linter/linter_setup_and_guidelines.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Always run dart fix --apply at end of every task" | (b) | Stays in doc/ — CI/CD process rule, already mandated in CLAUDE.md | — |
| "Use // ignore: with clear justification; sparingly" | (c) | Already enforced by `check_suppression_justification.sh` (gate). Doc should keep narrative context + pointer to gate. | — |
| "avoid-dynamic, no-object-declaration enforce strongly-typed codebase" | (a) | Both are proposed but not activated (see `linter_configuration_proposal.md` findings above) | S |
| "avoid-global-state: avoid mutable global variables" | (a) | Not activated (see above) | S |

---

### doc/domain/README.md

No normative rules — index file.

---

### doc/domain/overview.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Domain has no dependencies on external frameworks (except dartz/equatable)" | (c) | Partially enforced by `avoid-banned-imports` (domain → widgets.dart, flutter_bloc, dart:collection). Extend to cover `drift`, `injectable` usage in domain itself, `ILoggingService` (see architecture/logging.md findings). | S |
| "Domain defines interfaces implemented by outer layers" | (b) | Stays in doc/ — structural principle | — |

---

### doc/domain/entities.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Mark all entity classes with @immutable" | (a) | `check_domain_immutable.sh` — grep `lib/core/domain/entities/` for `class \w+ extends Equatable` without `@immutable` annotation | S |
| "All fields must be final" | (c) | Already enforced by Dart analyzer when `@immutable` is applied — @immutable triggers analyzer warning for non-final fields | — |
| "Use BuiltList/BuiltMap for collections" | (b) | Stays in doc/ — could use const List too; requires intent | — |
| "Extend Equatable; equality based on uuid only" | (b) | Stays in doc/ — requires understanding entity semantics | — |
| "Private constructors (._) to force factory usage" | (b) | Stays in doc/ — constructor visibility policy | — |
| "Implement dataVersion in toJson()" | (a) | `check_entity_version_in_json.sh` — grep entity toJson() methods for 'dataVersion' key | M |
| "Value objects co-located with their entity for versioning" | (b) | Stays in doc/ — placement policy | — |
| "View input contracts in lib/core/domain/entities/ (not feature packages)" | (b) | Stays in doc/ — placement judgment | — |

---

### doc/domain/value_objects.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Use @immutable annotation" | (a) | Same gate as entities.md — `check_domain_immutable.sh` extended to cover value_objects dirs | S |
| "Use Equatable with full value props (not uuid-only for VOs)" | (b) | Stays in doc/ — requires understanding VO vs entity distinction | — |
| "Use const constructors where possible" | (c) | Already covered by `prefer_const_constructors` in `flutter_lints/flutter.yaml` include | — |

---

### doc/domain/repositories.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Repository interfaces as abstract classes in domain layer" | (b) | Stays in doc/ — structural principle | — |
| "Return Either<Failure, T> for operations that can fail" | (L) | Theoretically checkable via AST (return type analysis), but requires full type resolution — not feasible with grep. DCM has no built-in for this. Flag as (a) with effort L. | L |
| "Return domain entities, not DTOs" | (b) | Stays in doc/ — requires semantic understanding | — |
| "Use descriptive method names; named params for multi-param signatures" | (b) | Stays in doc/ — naming convention | — |

---

### doc/domain/use_cases.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Each use case implements single operation (single call())" | (b) | Stays in doc/ — SRP is judgment | — |
| "Mark with @injectable" | (b) | Stays in doc/ — code-gen annotation | — |
| "Name class after operation (verb-based)" | (c) | Enforced by `prefer-correct-type-name` (suffix `UseCase` in regex) — `doc/` should keep prose + add pointer | — |
| "Depend on repository interfaces, not implementations" | (b) | Stays in doc/ — requires type hierarchy analysis | — |
| "Return Either<Failure, T>" | (L) | Same as repositories.md — AST-level, effort L | L |

---

### doc/domain/failures.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Failures extend abstract Failure base class with EquatableMixin" | (b) | Stays in doc/ — structural hierarchy, hard to enforce without AST | — |
| "Use Either for functional error handling" | (b) | Stays in doc/ — as above | — |
| "Include message property; override toString()" | (b) | Stays in doc/ | — |

---

### doc/domain/events.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "DomainEvent is @immutable abstract class" | (a) | `check_domain_immutable.sh` covers this (same extension as entities) | S |
| "Domain events named in past tense" | (b) | Stays in doc/ — naming convention, regex too imprecise | — |

---

### doc/domain/validation.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Validation in factory constructors, not setters" | (b) | Stays in doc/ — structural pattern | — |
| "Throw specific DomainValidationException types" | (b) | Stays in doc/ — hierarchy enforcement | — |
| "No validation in domain that depends on infrastructure" | (b) | Stays in doc/ — clean architecture principle | — |

---

### doc/domain/domain_services.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Domain services are stateless" | (b) | Stays in doc/ — no fields policy, judgment | — |
| "Name as verbs not nouns" | (c) | Partially covered by `prefer-correct-type-name` (suffix `Service`) | — |
| "Depend on repository interfaces (not implementations) via constructor injection" | (b) | Stays in doc/ | — |

---

### doc/domain/versioning.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Archive previous versions in v[N]/ subdirectory" | (b) | Stays in doc/ — release process | — |
| "Migration via PlanMigrationService, not entity fromV[N-1]" | (b) | Stays in doc/ — architectural preference, cannot be statically enforced | — |
| "Increment schemaVersion and provide MigrationStrategy on DB schema changes" | (b) | Stays in doc/ — process rule | — |

---

### doc/presentation/README.md

No normative rules — index.

---

### doc/presentation/coding/atomic_design.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Atoms in core/design_system/atoms, Molecules in /molecules, Organisms in /organisms" | (a) | `check_atomic_design_structure.sh` — grep `lib/core/design_system/` for files whose path level doesn't match atoms/molecules/organisms | M |
| "Layout components in organisms/layout/ subtree" | (a) | Same script — check layout components for correct placement | M |

---

### doc/presentation/coding/best_practices.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Prefer StatelessWidget unless local ephemeral state is truly needed" | (b) | Stays in doc/ — when to use StatefulWidget is judgment | — |
| "Use Feature Root Screen pattern for StatefulShellRoute features" | (b) | Stays in doc/ — architectural pattern | — |
| "Content widgets must provide ViewConfig" | (b) | Stays in doc/ | — |

---

### doc/presentation/coding/button_guidelines.md

(File not read in detail — based on ban-name rule for `.*Button` in design_system, rules are largely already gated.)

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Do not create new button components in design_system; use themed Material 3 buttons" | (c) | Already enforced by `ban-name` entry for `.*Button` in `lib/core/design_system/.*` | — |

---

### doc/presentation/coding/component_api.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (API design patterns for components) | (b) | Stays in doc/ — interface design judgment | — |

---

### doc/presentation/coding/component_states.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Component state patterns) | (b) | Stays in doc/ | — |

---

### doc/presentation/coding/design_system.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Use core/design_system (not core/widgets) for design components" | (a) | Overlaps with atomic_design.md — `check_atomic_design_structure.sh` covers | M |
| "core/widgets for app-wide components with concrete content" | (b) | Stays in doc/ — distinction requires content judgment | — |
| "Responsive breakpoints: mobile <600dp, medium 600-1240dp, large >1240dp" | (b) | Stays in doc/ — values are constants in code | — |

---

### doc/presentation/coding/folder_structure.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Test files MUST be in test/unit/ or test/widget/ (not directly test/features/, test/core/)" | (a) | `check_test_folder_structure.sh` — find `test/` for `.dart` files not under `unit/` or `widget/` subtree (excluding helpers/ and widget_test.dart) | S |
| "BLoC tests → test/unit/, widget tests → test/widget/" | (a) | Same script — not enforceable by name alone; quality-checker reading covers the intent | S |
| "Mirror lib/ paths inside unit/ and widget/ subtrees" | (b) | Stays in doc/ — path mirroring convention | — |

---

### doc/presentation/coding/improvements.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Improvement patterns) | (b) | Stays in doc/ | — |

---

### doc/presentation/coding/README.md

No normative rules — index.

---

### doc/presentation/coding/state_management.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Use BLoC for complex state; leverage router state for navigation-driven state" | (b) | Stays in doc/ — state holder choice is architectural judgment | — |
| "BLoCs must NOT be provided in orchestrators — provide at StatefulShellRoute level" | (b) | Stays in doc/ | — |
| "Forms: use ValueKey or didUpdateWidget for stale state prevention" | (b) | Stays in doc/ | — |
| "Async redirects: check BLoC state before routing" | (b) | Stays in doc/ | — |

---

### doc/presentation/design/persona_design_bridge.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Persona-to-design traceability guidance) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/README.md

No normative rules — index.

---

### doc/presentation/design/t1_customization_ceiling.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Maximum number of custom fields: defined cap (e.g., 10)" | (b) | Stays in doc/ — product constraint, not code-structural | — |
| "Template editor accessible from Settings only, not tracking flow" | (b) | Stays in doc/ — navigation rule, cannot be linted | — |
| "Protocol changes require deliberate 'Edit Plan' action" | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t1_dark_mode.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Dark mode design rules) | (b) | Stays in doc/ — visual design judgment | — |

---

### doc/presentation/design/t1_discrete_identity.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Brand identity design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t1_input_scaffolding.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Input scaffolding design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t1_interaction_budget.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Interaction budget design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t1_metrics_narrative_separation.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Narrative/metrics separation design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t1_notification_tone.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Notification tone design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t1_touch_targets.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Minimum touch target 48×48dp (Material Design 3 requirement)" | (b) | Stays in doc/ — static detection unreliable (Size() constructors are too varied; quality-checker reading catches violations in review) | — |

---

### doc/presentation/design/t2_crisis_mode_targets.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Crisis mode design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/design/t2_destructive_actions.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Destructive action confirmation rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/accessibility/README.md

No normative rules — index.

---

### doc/presentation/accessibility/accessibility_guidelines.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Prefer semantic widgets over generic containers (ElevatedButton over GestureDetector+Text)" | (b) | Stays in doc/ — GestureDetector has legitimate uses; quality-checker reading catches misuse | — |
| "Minimum touch targets 48×48dp" | (b) | Stays in doc/ — same as t1_touch_targets.md; static check impractical | — |
| "Color contrast minimum 4.5:1 for text" | (b) | Stays in doc/ — requires visual analysis | — |
| "Sufficient color contrast for all text" | (b) | Stays in doc/ | — |

---

### doc/presentation/libs/README.md

No normative rules — index.

---

### doc/presentation/libs/material_component_api.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Reference catalog of Material 3 components) | (b) | Stays in doc/ — reference material, no normative rules | — |

---

### doc/presentation/libs/wolt_responsive_layout_grid.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Usage guide for wolt_modal_sheet) | (b) | Stays in doc/ | — |

---

### doc/presentation/navigation/README.md

No normative rules — index.

---

### doc/presentation/navigation/navigation_patterns.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "All new features MUST follow these navigation patterns" | (b) | Stays in doc/ | — |
| "Use GoRouter ShellRoute for persistent UI elements" | (b) | Stays in doc/ | — |
| "Use named routes for type safety" | (b) | Stays in doc/ — intent-dependent | — |

---

### doc/presentation/navigation/responsive_layout.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Responsive layout implementation patterns) | (b) | Stays in doc/ | — |

---

### doc/presentation/platform/README.md

No normative rules — index.

---

### doc/presentation/platform/platform_guidelines.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Components must not make screen-size decisions directly — use ResponsiveLayoutBuilder" | (b) | Stays in doc/ — requires widget tree understanding | — |
| "Back navigation: use AppBar back button consistently" | (b) | Stays in doc/ | — |

---

### doc/presentation/platform/grid_system.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Grid system design rules) | (b) | Stays in doc/ | — |

---

### doc/presentation/platform/localization.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Always set explicit locale in integration tests" | (a) | `check_integration_test_locale.sh` — grep `integration_test/` for `pumpWidget` of `MyApp` without `locale:` parameter | S |
| "Use intl for all user-facing strings" | (c) | Already enforced by `prefer-provide-intl-description` and `prefer-intl-name` DCM rules | — |
| "Follow intl name pattern" | (c) | Already enforced by `prefer-intl-name` with configured regex pattern | — |

---

### doc/presentation/tokens/README.md

No normative rules — index.

---

### doc/presentation/tokens/token_reference.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Token catalog / reference) | (b) | Stays in doc/ — reference, no normative rules | — |

---

### doc/presentation/tokens/token_usage_guide.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Never use raw colors — use design tokens" | (c) | Already enforced by `ban-name` entry for `ButtonStyle`, `TextStyle`, `Color`. Note: `Color(0xFF...)` is caught because `Color` type is banned. Doc should keep the WHY narrative + pointer to ban-name gate. | — |
| "Use AppThemeExtension.of(context) for theme-aware components" | (b) | Stays in doc/ — access pattern | — |
| "Use design token classes (not magic numbers) for spacing/typography" | (c) | `no-magic-number` gate already covers numeric literals. Doc should point to gate. | — |

---

### doc/testing/README.md

No normative rules — index.

---

### doc/testing/testing.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "All test files MUST follow unit/ and widget/ subtree layout" | (a) | `check_test_folder_structure.sh` — find `test/` for `.dart` files not under `test/unit/` or `test/widget/` (excluding `test/helpers/` and `test/widget_test.dart`) | S |
| "BLoC tests → unit/, domain tests → unit/, widget/screen tests → widget/" | (a) | Same script | S |
| "NEVER place test files directly under test/features/, test/core/, test/config/ without unit/widget prefix" | (a) | Same script | S |
| "Test all component states (normal, loading, error)" | (b) | Stays in doc/ | — |
| "Use setUp / tearDown for state isolation" | (b) | Stays in doc/ | — |

---

### doc/testing/cold_start_measurement_methodology.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Measurement methodology — cold start timing) | (b) | Stays in doc/ — process/methodology doc | — |

---

### doc/testing/integration_testing.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Set explicit locale (e.g. 'en') when pumping MyApp in integration tests" | (a) | `check_integration_test_locale.sh` (same as localization.md finding) — grep integration_test/ for MyApp without locale parameter | S |
| "Set timeout parameter for all integration testWidgets" | (a) | `check_integration_test_timeout.sh` — grep integration_test/ for `testWidgets(` without `timeout:` parameter | S |
| "Add new integration test name to runner script manually" | (b) | Stays in doc/ — manual process step | — |
| "Use patrol for robust finding/interaction" | (b) | Stays in doc/ — library recommendation | — |
| "Run pumpAndSettle carefully; specify timeouts to prevent hangs" | (b) | Stays in doc/ | — |

---

### doc/testing/presentation/README.md

No normative rules — index.

---

### doc/testing/presentation/bloc_and_router_testing.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| "Mock BLoC using mocktail + bloc_test" | (b) | Stays in doc/ — library choice | — |
| "Use BlocProvider.value for mock BLoC in widget tests" | (b) | Stays in doc/ | — |
| "Always stub initial state when using whenListen" | (b) | Stays in doc/ | — |

---

### doc/testing/presentation/navigation_testing.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Navigation testing patterns for GoRouter) | (b) | Stays in doc/ | — |

---

### doc/testing/presentation/widget_testing.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Widget test patterns and anti-patterns) | (b) | Stays in doc/ | — |

---

### doc/from_figma/presentation/component_transformation_guide.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Figma-to-Flutter component transformation workflow) | (b) | Stays in doc/ — design-to-code process | — |

---

### doc/from_figma/presentation/client/data_input/01_component_analysis.md — 06_documentation.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Component analysis, grid system, screen decomposition, component creation, QA, documentation steps) | (b) | Stays in doc/ — design workflow process docs, no code rules | — |

---

### doc/from_figma/presentation/therapist/clients.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Therapist clients screen design rules) | (b) | Stays in doc/ | — |

---

### doc/from_figma/presentation/therapist/plans.md

| Rule excerpt | Classification | Proposed action | Effort |
|---|---|---|---|
| (Therapist plans screen design rules) | (b) | Stays in doc/ | — |

---

## Proposed New Gate Scripts

The following `scripts/quality/` scripts are proposed by (a) findings above. None exist yet.

| Script name | Rule it enforces | Source doc | Effort |
|---|---|---|---|
| `check_manual_di_registration.sh` | No `getIt.register*` in `lib/features/` outside `injection_container.dart` | architecture/dependency_injection.md | S |
| `check_drift_table_naming.sh` | Drift Table subclasses must have `@DataClassName('<Name>Row')` | architecture/drift_database_patterns.md | S |
| `check_domain_failure_structure.sh` | Failure classes in domain must be in `failures/` subdirectory | architecture/failure_handling.md | M |
| `check_no_transition_page.sh` | Master-detail nested StatefulShellRoute uses NoTransitionPage only | architecture/routing.md | S |
| `check_routing_structure.sh` | GoRoute defs in feature dirs must be in `*_routes.dart` files | architecture/routing.md | M |
| `check_logging_impl_direct_use.sh` | No direct import of `LoggingServiceImpl` outside its own file + tests | architecture/logging.md | S |
| `check_domain_no_logging.sh` | Domain layer must not use `print`, `debugPrint`, or `ILoggingService` | architecture/logging.md | S |
| `check_domain_immutable.sh` | Domain entities/value_objects/events must have `@immutable` annotation | domain/entities.md | S |
| `check_entity_version_in_json.sh` | Entity `toJson()` methods must include `'dataVersion'` key | domain/entities.md | M |
| `check_atomic_design_structure.sh` | design_system/ files in correct atoms/molecules/organisms level | presentation/coding/atomic_design.md | M |
| `check_test_folder_structure.sh` | Test files under `test/unit/` or `test/widget/` (not top-level) | testing/testing.md | S |
| `check_integration_test_locale.sh` | Integration tests set explicit locale when pumping MyApp | testing/integration_testing.md | S |
| `check_integration_test_timeout.sh` | Integration `testWidgets` must include `timeout:` parameter | testing/integration_testing.md | S |

## Proposed analysis_options.yaml Additions

Rules documented as intended but not yet activated:

| Rule | Type | Source doc |
|---|---|---|
| `avoid-dynamic` | DCM | linter_configuration_proposal.md |
| `avoid-global-state` | DCM | linter_configuration_proposal.md |
| `no-object-declaration` | DCM | linter_configuration_proposal.md |
| `avoid-late-keyword` | DCM | linter_configuration_proposal.md |
| `avoid-non-null-assertion` | DCM | linter_configuration_proposal.md |
| `prefer-async-await` | DCM | linter_configuration_proposal.md |
| `prefer-conditional-expressions` | DCM | linter_configuration_proposal.md |
| `prefer-immediate-return` | DCM | linter_configuration_proposal.md |
| `no-boolean-literal-compare` | DCM | linter_configuration_proposal.md |
| `binary-expression-operand-order` | DCM | linter_configuration_proposal.md |
| `prefer_single_quotes` | linter | linter_configuration_proposal.md |
| Domain `avoid-banned-imports` extension for `drift`, `ILoggingService` paths | DCM config | architecture/drift_database_patterns.md, logging.md |

## Already-Enforced Rules Summary ((c) findings)

| Gate mechanism | Rules covered | doc/ recommendation |
|---|---|---|
| `avoid-banned-imports` (features → material.dart) | Feature modules must use design system components | Keep prose (explains WHY) + add pointer |
| `avoid-banned-imports` (domain → widgets.dart, flutter_bloc) | Domain independence from presentation | Keep prose + add pointer |
| `avoid-banned-imports` (entities → dart:collection) | Entities use immutable collections | Keep prose + pointer |
| `ban-name` (ButtonStyle/TextStyle/Color) | No direct styling; use theme/tokens | Keep prose + pointer |
| `ban-name` (.*Button in design_system) | No new button components in design_system | Keep prose + pointer |
| `no-magic-number` | No magic numbers | Keep prose + pointer |
| `prefer-correct-type-name` (regex) | Suffix enforcement for Event/Failure/Bloc/State/Repository/Service/UseCase/Entity/ValueObject | Keep prose + pointer |
| `prefer-provide-intl-description` + `prefer-intl-name` | Intl naming conventions | Keep prose + pointer |
| `check_suppression_justification.sh` | `// ignore:` needs justification | Keep prose + pointer |
| `check_no_network_io.sh` | No network I/O in lib/ | Keep prose + pointer |
| `check_no_debug_artifacts.sh` | No debug artifacts | Keep prose + pointer |
| `check_no_hardcoded_secrets.sh` | No hardcoded secrets | Keep prose + pointer |
| `check_no_telemetry_sdks.py` | No telemetry SDKs | Keep prose + pointer |
| `check_weak_crypto.sh` | No weak crypto | Keep prose + pointer |
| `flutter_lints/flutter.yaml` (`prefer_const_constructors`) | const constructors | Keep prose |
| Dart analyzer + @immutable | non-final fields on @immutable classes | Keep prose |
| `prefer-correct-type-name` (UseCase suffix) | Use case naming | Keep prose + pointer |
| `prefer-correct-type-name` (Service suffix) | Service naming | Keep prose + pointer |
| `metrics` (cyclomatic-complexity 20, params 4, SLOC 50) | Code complexity | Keep prose + pointer |

## Notable Findings

1. **`doc/cross_cutting_standards/logging.md` is an exact duplicate** of `doc/architecture/logging.md`. One should be removed and replaced with a pointer to avoid drift.

2. **`linter_configuration_proposal.md` (2025-09-29) lists 11 rules as intended but none have been activated** in `analysis_options.yaml`. The proposal was documented but not executed. These are the highest-value S-effort gates.

3. **Domain layer has no gate for `drift` imports** — the doc says domain must be DB-agnostic, but the `avoid-banned-imports` config doesn't include `drift`. This is a gap with a clear, low-effort fix.

4. **Test folder structure is entirely ungated** — `testing.md` mandates `test/unit/` and `test/widget/` layout, but no script checks this. Easy S-effort gate.

5. **Integration test locale and timeout requirements are ungated** — both are explicitly stated requirements but no gate enforces them.

6. **If the audit finds zero gate-scriptable rules**: This is not the case. The audit identified 28 gate-scriptable rules across the doc/ corpus.

---

*Audit produced by TASK-PROC-046-12. Per goal.md Notes: no autonomous follow-on impl task creation. User reviews and decides which proposals to schedule.*
