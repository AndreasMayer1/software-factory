# Plan — TASK-PROC-046-14: Custom DCM-Free Replacement Scripts

Date: 2026-05-19
Owner: automated session (gmail2)

## Scope

Implement six custom scripts under `scripts/quality/` that replace the DCM
capabilities the gate set previously depended on, plus a tiny Dart helper
package for AST-level complexity metrics. Wire all six into the existing
`check_quality_gates.sh` aggregate runner and the `quality-checker` agent.

## Deliverables

1. `scripts/quality/check_complexity.py` (+ Dart helper at
   `scripts/quality/_complexity_analyzer/`)
2. `scripts/quality/check_type_naming.sh`
3. `scripts/quality/check_architectural_imports.sh`
   (+ `scripts/quality/architectural_imports_policy.yaml`)
4. `scripts/quality/check_no_direct_styling.sh`
5. `scripts/quality/check_test_smells.sh`
6. `scripts/quality/check_folder_taxonomy.sh`
   (+ `scripts/quality/folder_taxonomy_allowlist.txt`)
7. Updated `scripts/quality/check_quality_gates.sh` (invokes all six new
   gates after the existing six)
8. Updated `scripts/quality/README.md`
9. Updated `.claude/agents/quality-checker.md` (knows about the new gates)
10. Updated `doc/linter/linter_setup_and_guidelines.md` (already cross-refs
    the new scripts; verify accuracy)
11. Baseline-run output recorded in `plans_and_protocols/`

## Design Decisions

### Exit-code convention (all scripts)
- `0` — pass (no violations)
- `1` — fail (violations; details on stdout)
- `2` — invocation error (missing input file, parser crash, etc.)

This mirrors the existing privacy/security gates and the aggregate runner's
expectations.

### Exclusion mechanism
All six scripts re-use the existing `scripts/quality/_lib.sh` helpers
(`parse_exclude_arg`, `load_exclude_patterns`, `is_excluded`). Default
exclusion file remains `scripts/quality/exclusions.txt`; per-invocation
override via `--exclude-paths <file>`.

For the Python complexity script, an equivalent helper is implemented as a
tiny `_exclude.py` module (read pattern lines, substring match) — keeps
behaviour identical without re-implementing in a different language.

### Externalised policies
Two scripts use sidecar policy files so the rule set can be tightened
without editing the script:

- `scripts/quality/architectural_imports_policy.yaml` — path-glob → deny
  list (regex patterns matched against import URI).
- `scripts/quality/folder_taxonomy_allowlist.txt` — newline-separated
  allowed sub-folder names under any `*/domain/` directory.

### Complexity analyzer (item 1) — Dart-side
- Dart package: `scripts/quality/_complexity_analyzer/`
- Depends on `analyzer` (BSD-licensed, dev-only). No Flutter dep.
- `bin/complexity_analyzer.dart` walks supplied paths, parses each `.dart`
  file with `parseFile()`, visits all FunctionDeclaration /
  MethodDeclaration / ConstructorDeclaration nodes and computes:
  - cyclomatic complexity (1 + count of branching nodes:
    `IfStatement`, `ForStatement`, `WhileStatement`, `DoStatement`,
    `SwitchCase`, `CatchClause`, `ConditionalExpression`,
    binary `&&` / `||`)
  - parameter count (FormalParameterList length)
  - SLOC of the function body (closing brace line − opening brace line;
    blank lines and standalone-comment lines subtracted)
  - max control-flow nesting (depth of nested IfStatement /
    ForStatement / WhileStatement / DoStatement / SwitchStatement; NOT
    widget composition / map-literals — per REQ-PROC-046 AC-02 clarification)
- Output: single JSON document to stdout with shape:
  ```json
  {
    "version": 1,
    "files": [
      {"path": "lib/foo.dart",
       "functions": [
         {"name": "doThing", "line": 42, "cyclomatic": 3,
          "parameters": 2, "sloc": 18, "max_nesting": 2}
       ]
      }
    ]
  }
  ```
- Exit codes: 0 on success, 2 on parser error.

### Complexity analyzer (item 1) — Python wrapper
- `scripts/quality/check_complexity.py` (tier B).
- Shells out to `dart run` against the helper package, captures JSON,
  applies thresholds (cyclomatic ≤ 20, params ≤ 4, sloc ≤ 50, nesting ≤ 5),
  prints `file:line: <metric> exceeds <threshold> (<actual>)` per violation.
- Honours `exclusions.txt` substring matching.
- Skips the run gracefully (exit 0 with a NOTICE on stderr) if the Dart
  helper has not been `pub get`-ed yet — this avoids a chicken-and-egg
  failure on a fresh clone. The CI / contributor instruction is to run
  `dart pub get` inside the helper directory before the first gate run;
  the README documents this.

### Naming script (item 2)
Bash + grep + regex on `lib/` only. Acceptable suffixes (Event, Failure,
Bloc, State, Repository, Service, UseCase, Entity, ValueObject) come from
the goal scope; pattern is the goal-verbatim regex
`^[A-Z][a-zA-Z0-9]*((Event)|(Failure)|(Bloc)|(State)|(Repository)|(Service)|(UseCase)|(Entity)|(ValueObject))?$`.
Generated files (`*.g.dart`, `*.freezed.dart`) auto-excluded. enum and
mixin declarations not flagged (regex only matches `class ` openings).

### Architectural-imports script (item 3)
Bash, reads the YAML policy with a tiny `yq`-free parser (each block is
indent-based, two-section: `path:` glob and `deny:` regex list — both single
lines or simple lists). For each policy block: enumerate matching files;
for each file, read its `import 'package:...';` lines and flag any matching
a `deny` regex.

Policy (initial):
```yaml
- path: "lib/core/domain/**"
  deny: ["^package:flutter/", "^package:flutter_bloc/"]
- path: "lib/features/*/domain/**"
  deny: ["^package:flutter/", "^package:flutter_bloc/"]
- path: "lib/features/**"
  deny: ["^package:flutter/material\\.dart$"]
- path: "lib/core/domain/entities/**"
  deny: ["^dart:collection$"]
```

### Direct-styling script (item 4)
Bash + grep against `lib/features/` for the literal class-constructor /
member patterns from the goal. Whitelist `lib/core/design_system/`.

### Test-smells script (item 5)
Bash + grep. Three sub-checks (missing assertion / empty group / literal
expect) each report independently.

For the assertion check: extract `test(` / `testWidgets(` block bodies via
balanced-brace scan in awk, and look for any of `expect(`, `verify(`,
`tester.ensureSemantics(`, `expectLater(`, `expectAsync`.

For empty group: any `group(` whose body has no `test(` call inside.

For literal `expect(...length, <int>)`: regex match
`expect\(\s*[^,]+\.length\s*,\s*[0-9]+`.

### Folder-taxonomy script (item 6)
Bash. Walks `lib/core/domain/` and `lib/features/*/domain/`. For each
`*.dart`:
- If it lives directly at `*/domain/` (no sub-folder) — flag.
- If it lives in a sub-folder not in `folder_taxonomy_allowlist.txt` — flag.

Allowlist initial content (one per line, with comments allowed):
```
entities
repositories
value_objects
services
failures
events
```

## Sequencing

1. Phase A — small scripts in parallel-readable order:
   - check_no_direct_styling.sh
   - check_folder_taxonomy.sh
   - check_type_naming.sh
   - check_architectural_imports.sh
   - check_test_smells.sh
2. Phase B — Dart complexity analyzer:
   - pubspec.yaml, bin/complexity_analyzer.dart
   - run `dart pub get` (inside helper dir)
3. Phase C — Python wrapper `check_complexity.py` + run gates
4. Phase D — Wire all six into `check_quality_gates.sh`
5. Phase E — README + quality-checker agent + doc/linter
6. Phase F — Baseline runs, recorded to plans_and_protocols/
7. Phase G — Final gate run, claude-log, task-complete

## Risk / Notes

- `dart pub get` for the helper package may fail offline. The wrapper's
  graceful-skip behaviour (with stderr NOTICE) preserves the gate-set's
  pass-by-default posture; the failure path is loud enough to spot.
- The current codebase will produce many baseline violations (the whole
  point of putting the gates in place). Per the goal's out-of-scope note,
  tightening thresholds is for TASK-PROC-046-13. We record the baseline
  output and let the gate FAIL until violations are remediated by a
  follow-up backlog task.

## Verify-Quality Skill Wiring

The goal calls for updating the `verify-quality` skill (created by
TASK-PROC-046-11). That task is still **pending** and the skill does not
yet exist. We defer the skill wiring to TASK-PROC-046-11 itself — the
quality-checker agent update in item 9 carries the change for the
review-by-agent path, which is the path actively used today.
