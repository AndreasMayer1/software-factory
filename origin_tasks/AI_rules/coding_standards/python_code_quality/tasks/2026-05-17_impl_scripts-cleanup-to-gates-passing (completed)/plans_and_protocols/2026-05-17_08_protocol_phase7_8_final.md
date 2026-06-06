# Protocol — Phase 7 + 8: Suppression review + Final integration

**Agents**: `a19f32effdca46711` (first attempt — partial, hit limit) → `aa587a4752e36ea37` (continuation — partial) → main session inline (final protocol authoring).
**Date**: 2026-05-17

## Phase 7 — AC-13 suppression review

Audit before: one unjustified suppression in `scripts/automation/orchestrate.py:1408`:
```python
result.elapsed_secs = elapsed  # type: ignore[attr-defined]
```

Fix applied: added inline justification. Critical detail learned the hard way:
`# type: ignore[...]` directives MUST end the ignore region with two spaces and a
fresh `#` for the human reason — **em-dash inside the directive is parsed by
mypy as `Invalid "type: ignore" comment` syntax**. Correct pattern:
```python
result.elapsed_secs = elapsed  # type: ignore[attr-defined]  # custom attribute extended dynamically here to record elapsed wall time so callers (run_session, ScratchpadResult assembly) can report kill latency without re-measuring
```
(Compare to the working pattern on line 1407 which already used this shape.)

Verification commands (all return empty):
```bash
grep -rnE "# noqa\s*$" scripts/ --include="*.py"
grep -rnE "# noqa: [A-Z][0-9]+\s*$" scripts/ --include="*.py"
grep -rnE "# type:\s*ignore(\[[a-z,-]+\])?\s*$" scripts/ --include="*.py"
grep -rnE "# type:\s*ignore\[[a-z, -]+\]\s*—" scripts/ --include="*.py"
```

All scripts/ suppressions now carry an AC-13-compliant inline justification.

## Phase 8 — Final integration

### CLAUDE.md update

The §7 Python gates "intermediate state" paragraph was replaced with a
positive-tense enforcement statement reflecting that TASK-PROC-051-04 has
landed and all five gates are expected to PASS on develop. The relevant
post-edit text:

> **Enforcement**: all five gates are expected to PASS on develop. A task
> that introduces a new gate violation MUST fix it before declaring complete;
> ignore-the-baseline behavior is no longer permitted now that TASK-PROC-051-04
> has landed.

### `scripts/quality/check_python_gates.sh` update

Removed:
- The multi-line `# NOTE: This runner is EXPECTED to produce failures on develop until TASK-PROC-051-04 ...` header comment block.
- The `echo "(develop baseline failures are expected until TASK-PROC-051-04 lands)"` line at the bottom of the FAIL branch.

The script's failure message now stands alone:
```
echo "One or more Python quality gates FAILED. See per-gate output above."
```

### Final per-gate state (captured 2026-05-17)

```
  PASS   G1 lint
  PASS   G2 type
  PASS   G3 tests
  PASS   G4 no-handrolled
  PASS   G5 print-discip.

All Python quality gates PASSED.
```

573 tests passed, 0 failed (was 416 at the start of the task; +157 regression and smoke tests added across phases).

## Acceptance criteria sign-off

| AC item from goal.md | State | Evidence |
|---|---|---|
| `ruff check scripts/` exits 0 | ✓ | G1 PASS in summary above |
| `mypy scripts/` exits 0 (strict in TIER A, default elsewhere) | ✓ | G2 PASS |
| `pytest` exits 0 against configured collection roots | ✓ | G3 PASS, 573 tests |
| G4 (no hand-rolled YAML) exits 0 | ✓ | G4 PASS; 21 sites migrated in Phase 1 |
| G5 (print discipline) exits 0 | ✓ | G5 PASS; 591 violations resolved in Phase 4 |
| Every imported module has at least one direct test (AC-10) | ✓ | Phase 5+6 protocol — yaml_frontmatter, task_ordering covered; others CLI/TIER-C exempt |
| Every existing suppression has adjacent justification (AC-13) | ✓ | Phase 7 audit empty |
| All modules under `scripts/` have tier annotation | ✓ | Phase 6 — 55/55 non-test non-`__init__` modules annotated |
| CLAUDE.md no longer carries the intermediate-state note | ✓ | This phase |
| Gate runner entry point exits 0 on develop | ✓ | `bash scripts/quality/check_python_gates.sh` → exit 0 |
| Modified Python files behave like before; no features removed | ✓ | 573 tests including 80+ regression tests pinning prior behavior (Phase 1) hold green |

## Hand-off to task-complete

The parent session will invoke the `task-complete` skill to commit all
changes from Phases 0–8 in a single commit. Per CLAUDE.md §4, this is the
only sanctioned way to close the task.
