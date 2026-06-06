# Plan: Validate Gate Scripts with Pytest Tests

## Objective
Write pytest tests for 12+ custom quality gate scripts under `scripts/quality/`.
Each test has at least one true-positive (violation detected) and one true-negative (clean code passes).

## Scripts to Cover

### Explicitly in-scope (12)
| Script | Gate | Test File |
|---|---|---|
| check_complexity.py | G2 | test_check_complexity.py |
| check_type_naming.sh | - | test_check_type_naming.py |
| check_architectural_imports.sh | G4 | test_check_architectural_imports.py |
| check_no_direct_styling.sh | G4 | test_check_no_direct_styling.py |
| check_suppression_justification.sh | G5 | test_check_suppression_justification.py |
| check_no_debug_artifacts.sh | - | test_check_no_debug_artifacts.py |
| check_test_smells.py | TQ1 | test_check_test_smells.py |
| check_folder_taxonomy.sh | - | test_check_folder_taxonomy.py |
| check_no_network_io.sh | SP1 | test_check_no_network_io.py |
| check_no_telemetry_sdks.py | SP2 | test_check_no_telemetry_sdks.py |
| check_no_hardcoded_secrets.sh | SP3 | test_check_no_hardcoded_secrets.py |
| check_weak_crypto.sh | SP4 | test_check_weak_crypto.py |

### Also in scope per AC "every check_*.sh/check_*.py" (3 additional)
| Script | Test File |
|---|---|
| check_critical_path_coverage.py | test_check_critical_path_coverage.py |
| check_no_handrolled_yaml.py | test_check_no_handrolled_yaml.py |
| check_print_discipline.py | test_check_print_discipline.py |

### Excluded (orchestrators / Flutter-dependent)
- check_quality_gates.sh (master orchestrator)
- check_python_gates.sh (meta orchestrator)
- check_test_determinism.sh (requires flutter test)

## Key Validations
1. **check_type_naming.sh**: `_FooState` private State classes must PASS (not be flagged)
2. **check_folder_taxonomy.sh**: `usecases/` must be in allowlist or explicitly handled
3. **check_complexity.py**: verify thresholds match AC-02 (cyclomatic ≤ 20, params ≤ 4, SLOC ≤ 50, nesting ≤ 5)

## Test Approach
- Each test creates temporary files/directories with synthetic Dart/YAML/Python content
- Calls the script as a subprocess
- Asserts exit code (0 = pass, non-zero = fail)
- Asserts relevant output content
- Uses `tmpdir` pytest fixture for isolation

## Implementation Strategy
For shell scripts: `subprocess.run(['bash', 'scripts/quality/check_xxx.sh', tmpdir], ...)`
For Python scripts: `subprocess.run(['python3', 'scripts/quality/check_xxx.py', tmpdir], ...)`

## False Positive Documentation
If tests reveal false positives: file proposals under `scripts/quality/proposals/`

## Phases
1. Read all 15 gate scripts → understand logic
2. Write 15 test files in scripts/tests/
3. Run all tests: `python3 -m pytest scripts/tests/test_check_*.py -v`
4. Fix any failures (either test bugs or script bugs documented as proposals)
5. Run Python quality gates: `bash scripts/quality/check_python_gates.sh`
6. Document false positives in proposals/
