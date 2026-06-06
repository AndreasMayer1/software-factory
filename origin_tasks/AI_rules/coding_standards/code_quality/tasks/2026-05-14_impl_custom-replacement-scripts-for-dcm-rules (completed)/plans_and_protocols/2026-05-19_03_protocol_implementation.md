# Protocol — TASK-PROC-046-14 Implementation

Date: 2026-05-19
Agent session: ce8784d5-358d-432b-bf50-958e1b950c83

## What was built

### scripts/quality/_complexity_analyzer/ (Dart helper package)
- `pubspec.yaml` — declares `analyzer ^6.4.0` and `path ^1.9.0`; dev-only,
  no Flutter dep.
- `bin/complexity_analyzer.dart` — walks input paths, parses each .dart
  file with `package:analyzer`, visits FunctionDeclaration /
  MethodDeclaration / ConstructorDeclaration nodes, emits per-function
  metrics (cyclomatic, parameters, sloc, max_nesting) as JSON. Handles
  enum / extension-type / class constructor parents; skips
  `.g.dart` / `.freezed.dart` files.
- `pubspec.lock` produced by `dart pub get`.

### scripts/quality/check_complexity.py  (tier B)
- Python wrapper. Resolves project-root path from JSON output (absolute
  paths emitted by the Dart side), applies thresholds 20/4/50/5,
  honours `exclusions.txt` substring matching.
- Gracefully skips with stderr NOTICE if `pubspec.lock` is absent
  (analyzer not yet `pub get`-resolved) or `dart` is not on PATH.

### scripts/quality/check_type_naming.sh
- Bash + grep. Detects `class Foo` declarations (with modifiers) and
  validates against the goal-prescribed regex. Excludes `.g.dart` /
  `.freezed.dart`.

### scripts/quality/check_architectural_imports.sh
- Bash. Parses the sidecar
  `scripts/quality/architectural_imports_policy.yaml` with a tiny
  purpose-built parser, walks `lib/`, applies each path-glob → deny-regex
  policy to every file's import lines.

### scripts/quality/check_no_direct_styling.sh
- Bash + grep on `lib/features/`. Flags `ButtonStyle(`, `TextStyle(`,
  `Color(`, `Colors.*`, `ThemeData(`.

### scripts/quality/check_test_smells.py  (tier B)
- Replaces the originally drafted `.sh` (which had an unrecoverable
  awk newline-in-body bug producing thousands of false positives).
- Python state machine: strips comments + string literals, then runs
  balanced-brace scans for `test()`, `testWidgets()`, and `group()`
  blocks. Sub-checks: missing assertion, empty group, literal-length
  expect.

### scripts/quality/check_folder_taxonomy.sh
- Bash. Walks `lib/core/domain/` and `lib/features/*/domain/`,
  cross-references the sidecar `folder_taxonomy_allowlist.txt`.

### Wiring
- `scripts/quality/check_quality_gates.sh` — added the six new gates
  after the existing six. Aggregate runner still exits 0/1/2 by max.
- `scripts/quality/README.md` — six new sub-sections under "Individual
  gates" plus updated header counts.
- `.claude/agents/quality-checker.md` — Phase-1 step 4 now references
  each of the six new gates' policies; critical-checks summary
  expanded.

## Notes on dependency status

- TASK-PROC-046-03 (very_good_analysis baseline) is **completed**.
- TASK-PROC-046-11 (`verify-quality` skill creation) is **still
  pending**. Per the plan, the `verify-quality` skill wiring is
  deferred to that task; the `quality-checker` agent update in this
  task carries the change for the agent-based review path used today.

## Baseline gate results

Recorded in `2026-05-19_02_baseline_gate-runs.txt`. Summary:

| Gate                              | Exit | Findings (approx) |
|-----------------------------------|------|-------------------|
| check_complexity.py               | 1    | 99 functions      |
| check_type_naming.sh              | 1    | 22 classes        |
| check_architectural_imports.sh    | 1    | 13 imports        |
| check_no_direct_styling.sh        | 1    | 14 sites          |
| check_test_smells.py              | 1    | 9 literal-length  |
| check_folder_taxonomy.sh          | 1    | 3 files (`usecases/`) |

Per the goal's out-of-scope note, tightening thresholds and remediating
the baseline are explicitly **not** in this task. A follow-up backlog
task (or `usecases/` becoming an allow-listed sub-folder via the proposals
loop TASK-PROC-046-13) will address each finding.

## Python gate run (G1–G5)

| Gate                  | Result                                      |
|-----------------------|---------------------------------------------|
| G1 lint (ruff)        | PASS                                        |
| G2 type (mypy)        | PASS                                        |
| G3 tests (pytest)     | FAIL (pre-existing, unrelated to this task) |
| G4 no hand-rolled YAML| PASS                                        |
| G5 print discipline   | PASS                                        |

The G3 failure is `scripts/automation/tests/test_orchestrate.py::
TestBuildEnv::test_no_session_id_when_empty` — a develop baseline failure
in `scripts/automation/`, which this task does not modify. No new finding
is introduced by this change.

## Acceptance Criteria mapping

| AC | Where satisfied |
|---|---|
| All six scripts exist with executable permissions and `--exclude-paths` | scripts/quality/check_*.{sh,py}, all chmodded; `--exclude-paths` honoured via `_lib.sh` or local Python equivalent |
| `check_quality_gates.sh` invokes all six and aggregates exit codes | updated GATES array; aggregate runner unchanged |
| README documents each new script | scripts/quality/README.md "Individual gates" section expanded |
| `_complexity_analyzer/` buildable, pubspec.yaml, emits stable JSON | confirmed by smoke run; pubspec.lock present |
| Each script runs against current codebase; baseline recorded | 2026-05-19_02_baseline_gate-runs.txt |
| `verify-quality` skill updated | DEFERRED to TASK-PROC-046-11 (skill does not yet exist) |
| `quality-checker` agent updated | .claude/agents/quality-checker.md edited |
| doc/linter/linter_setup_and_guidelines.md mentions new scripts | already references TASK-PROC-046-14 scripts (lines 30, 44, 52–55) |

## Decisions / Trade-offs

1. **Verify-quality skill wiring deferred**: TASK-PROC-046-11 owns the
   skill creation; wiring it into not-yet-existent files would be wasted
   work. The agent update (item 7) is the actively-used review path.
2. **Test-smells implemented in Python**, not bash: the balanced-brace
   parse needed for body extraction is brittle in awk (newlines inside
   the body break the line-oriented protocol). Python's state-machine
   approach is clear and correct.
3. **No baseline-violation cleanup**: explicitly out of scope per the
   goal. The gates are now in place and failing loudly; remediation is
   downstream work.

## Files touched

- New: 6 gate scripts, 2 sidecar config files, 1 Dart package (3 files
  + lockfile), 3 plan/protocol markdown files.
- Modified: `scripts/quality/check_quality_gates.sh`,
  `scripts/quality/README.md`, `.claude/agents/quality-checker.md`,
  `requirements_tasks/.../goal.md` (status + started + session_id).
