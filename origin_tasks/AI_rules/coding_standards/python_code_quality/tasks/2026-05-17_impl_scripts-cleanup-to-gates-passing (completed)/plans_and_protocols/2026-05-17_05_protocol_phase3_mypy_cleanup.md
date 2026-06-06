# Phase 3 protocol — G2 mypy type-check cleanup

**Agent IDs**:
- Main pass: agent-ad64c67f2d4668e0a (hit rate limit at 4 mypy errors / 42 ruff regressions remaining)
- Finishing pass: agent-a94ceb4ca0e0c08e6

**Date**: 2026-05-17 → 2026-05-18
**Scope**: TASK-PROC-051-04 Phase 3 — bring `uv run bash scripts/quality/mypy_check.sh` to a clean pass without regressing G1/G3.
**Exit state**: G1 ruff clean · G2 mypy "Success: no issues found in 89 source files" · G3 pytest **541 passed, 0 failed** · G4 PASS · G5 FAIL (expected — owned by Phase 4).

## Main-pass summary (agent-ad64c67f2d4668e0a)

Took baseline from 471 mypy errors down to 4. Detailed history of the long pass is captured in that agent's session jsonl. The 4 residual errors at handoff were:

- `scripts/util/should_use_agents.py:218` — `Name "cast" is not defined`. Missing `from typing import cast` import.
- `scripts/quality/check_no_handrolled_yaml.py:97, 106, 117` — three `Unused "type: ignore" comment` findings on `# type: ignore[arg-type]` annotations attached to `ast.walk(ast.Module(body=nodes, type_ignores=[]))` calls. Mypy no longer needs the ignore for these — the upstream stubs improved (or the call expression no longer triggers the original error after Phase 1/2 cleanups).

Concurrently, **G1 had regressed to 42 ruff errors**. Cause: `ruff check --fix` (and the unsafe-fixes batch from Phase 2) reorganized many `from x import y` statements into multi-line form:

```python
from util.yaml_frontmatter import (
    _split_frontmatter,  # type: ignore[import-not-found]
)
```

When the `# type: ignore[import-not-found]` lands on the body line of a multi-line import, mypy reports the import error on the `from` line (no ignore present there) AND emits an `Unused "type: ignore"` warning on the body line — a double failure for the same logical import. This pattern affected 13 files (14 sites total — `propose_after.py` had two).

## Phase 3 finishing pass — agent-a94ceb4ca0e0c08e6

### Step 1 — ruff auto-fix sweep

`uv run ruff check --fix scripts/` → 42 errors detected, **42 auto-fixed**, 1 remaining (F821 `cast` undefined — same site as the mypy `name-defined` error). After this sweep G1 is clean modulo the F821, which is repaired by the mypy step below.

### Step 2 — fix residual mypy errors

1. `scripts/util/should_use_agents.py` — added `cast` to the existing `from typing import Any, Optional` import. One-line surgical fix, no behavioral change.
2. `scripts/quality/check_no_handrolled_yaml.py` — removed the three now-unused `# type: ignore[arg-type]` comments on lines 97, 106, 117. These were attached to `ast.walk(ast.Module(body=nodes, type_ignores=[]))` calls. (Touching `scripts/quality/*` is normally out of scope, but these three comments were the sole remaining blocker for G2 PASS; the change is a pure annotation removal with no runtime or behavioral impact.)

### Step 3 — relocate multi-line-import `# type: ignore` comments

Pattern fix: moved `# type: ignore[import-not-found]` from the body line of a multi-line `from ... import (...)` statement up to the `from` line itself, so mypy can apply the ignore to the import resolution attempt.

Files edited (10 unique files, 11 import sites):

- `scripts/requirements/check_ac_coverage.py`
- `scripts/requirements/check_requirement_implementation.py`
- `scripts/requirements/coverage_report.py`
- `scripts/requirements/validate_meta.py`
- `scripts/tasks/check_task_against_plan.py`
- `scripts/tasks/find_orchestration_tasks.py`
- `scripts/tasks/parse_task_creation_plan.py`
- `scripts/tasks/propose_after.py` (two sites: `task_ordering` and lazy `next_tasks` import)
- `scripts/tasks/reconcile_after_chains.py`
- `scripts/tasks/top_blocked_task.py`
- `scripts/tests/test_allocate_task_id.py`
- `scripts/user_needs/check_canon.py`
- `scripts/windows/smoke_test_llm.py` (PIL import)

Each edit preserves the original suppression rationale comment verbatim.

## Verification (final)

| Gate | Command | Result |
|---|---|---|
| G1 lint | `uv run ruff check scripts/` | `All checks passed!` |
| G2 type | `uv run bash scripts/quality/mypy_check.sh` | `Success: no issues found in 89 source files` |
| G3 tests | `uv run pytest` | `541 passed in ~31s` |
| G4 YAML | `bash scripts/quality/check_python_gates.sh` (G4 block) | PASS |
| G5 print | same | FAIL — 591 violations (expected — Phase 4 scope) |

`check_python_gates.sh` summary at exit:

```
  PASS   G1 lint
  PASS   G2 type
  PASS   G3 tests
  PASS   G4 no-handrolled
  FAIL   G5 print-discip.
```

## Hand-off to Phase 4

G1–G4 are green. The remaining work is G5 (`check_print_discipline.py` — 591 violations across 60+ files), tracked in TASK-PROC-051-04 Phase 4. No changes to `pyproject.toml` (TIER A overrides remain at the single `scripts.automation.orchestrate` module). No changes to `scripts/util/yaml_frontmatter.py` or the G1/G2/G3/G4 gate scripts beyond the three unused-ignore removals noted above.
