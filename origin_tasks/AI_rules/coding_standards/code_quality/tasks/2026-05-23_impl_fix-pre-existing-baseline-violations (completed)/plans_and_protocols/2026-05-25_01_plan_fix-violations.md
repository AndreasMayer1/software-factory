# Plan: Fix Pre-Existing Baseline Violations

## Current State
- 89 AC02 complexity violations (55 params, 32 SLOC, 2 cyclomatic)
- 16 type-naming violations (all private classes with `_` prefix)

## Phase 1: Gate Script Fixes (false positives)

### 1a. Type-naming gate
- Skip private classes (name starts with `_`) — standard Flutter convention
- Add `*.config.dart` to generated-file skip list
- Resolves: all 16 type-naming violations

### 1b. Complexity gate — constructor parameter exemption
- Modify `complexity_analyzer.dart` to output `"kind": "constructor"|"method"|"function"`
- Modify `check_complexity.py` to exempt constructors and copyWith/create methods from parameter threshold
- Resolves: ~50 of 55 parameter violations

### 1c. Generated file exclusions
- Add `injection_container.config.dart` and `theme.dart` to exclusions.txt
- Resolves: ~10 violations (1 SLOC in config, 7 SLOC + 2 params in theme)

### 1d. File proposals for all gate changes

## Phase 2: Code Fixes (remaining true violations)

After Phase 1, remaining violations estimated:
- ~25 SLOC > 50 violations (build methods, business logic)
- 2 cyclomatic > 20 violations (question.dart)
- ~2-3 parameter violations (non-constructor methods)

Fix approach:
- Extract sub-widgets from long build methods
- Extract helper methods from long business logic
- Simplify question.dart create/fromJson with helper methods
- Refactor remaining param-heavy methods

## Phase 3: Verify and Complete
- Run `check_quality_gates.sh` → exit 0
- Run `flutter test` → all pass
- Remove CLAUDE.md section 12 (back pressure disabled)
