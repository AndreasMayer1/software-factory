# Resume Protocol: TASK-PROC-058-08

**Date**: 2026-05-26 — session interrupted at ~80% context

---

## What is DONE

| Finding | Change | Status |
|---------|--------|--------|
| D | SKILL.md Phase 1.5.1: `detect_cross_ref_gaps.py` → `check_cross_refs.py` | ✅ Done |
| E | SKILL.md Phase 1.5.1: invocation `--target <path> --json` → positional `<path>` + `--terms` guidance | ✅ Done |
| F (partial) | `check_cross_refs.py`: User Story boilerplate stop words added (`user`, `want`, `story`, `developer`, `stakeholder`, `persona`, `actor`) | ✅ Done |
| F (partial) | `check_cross_refs.py`: `max_terms` param on `_derive_search_terms`, `_MAX_TERM_CANDIDATES=20`, `_MAX_TERM_FREQ=15`, `_MIN_GOOD_HITS=10` added | ✅ Code written, gates pass |
| G | SKILL.md Phase 5: `--task-type [impl\|mixed]` → `[implement\|verify\|scribble\|scribble_to_flutter]` | ✅ Done |
| H | SKILL.md Phase 5: routing note added (verify/explore→task-create; scribble→ui-create-scribble; etc.) | ✅ Done |
| H | `create_orchestration_task.py` `_build_ac_block`: full skill routing logic added | ✅ Done, gates pass |
| Tests | Regression tests for all new branches in both scripts | ✅ Added, all pass |

All Python quality gates pass (G1–G5, 774 tests).

---

## What is NOT YET DONE

### 1. Finding F — frequency filter has a bug (edge case `good_hit_count == 10 == _MIN_GOOD_HITS`)

**Problem**: `_MIN_GOOD_HITS = 10` uses `>=` comparison. For REQ-PROC-001:
- `good = ["forgets"(2), "emtpy"(1), "might"(7)]`, `good_hit_count = 10`
- `10 >= 10` → `use_good = True` → uses ["forgets", "emtpy", "might"] as terms → only 6 candidates, missing context/window genuine matches

**Fix needed**: Change `_MIN_GOOD_HITS = 10` to `_MIN_GOOD_HITS = 11` OR change the condition from `>=` to `>`. The exact boundary needs one more test. After fix, REQ-PROC-001 should fall back to ["context", "window", "stay", "small"] → ~73 candidates (acceptable for this pathological requirement), and REQ-PROC-058 should use ["Planning", "satisfies", "guarantee", "criterion"] → 26 candidates ✓.

**Verification target (AC)**:
- REQ-PROC-058 (the main test case): ≤ 30 candidates ✓ (currently 26)
- REQ-PROC-001 (pathological case): accepts fallback to ~73; the two genuine matches (REQ-PROC-008, REQ-PROC-058) are already cross-referenced so they're correctly excluded regardless

**File to edit**: `scripts/requirements/check_cross_refs.py` line with `_MIN_GOOD_HITS`
→ Must use `claude-write-script` skill.

### 2. Verify all 5 findings end-to-end

After the `_MIN_GOOD_HITS` fix, run:
```bash
# Finding F verification
python3 scripts/requirements/check_cross_refs.py \
  requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md \
  2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'REQ-PROC-058: {len(d)} candidates')"
# Expect: ≤ 30

# Also confirm REQ-PROC-001 falls back correctly (not 6)
python3 scripts/requirements/check_cross_refs.py \
  requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md \
  2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'REQ-PROC-001: {len(d)} candidates')"
# Expect: ~73 (fallback behavior, acceptable for this pathological requirement)
```

### 3. `verify-quality` skill

Run:
```
/verify-quality
```
(or `Skill("verify-quality")` in automated mode)

No Dart/Flutter code was changed, so gates G1–G4 (analyzer, dart fix, Flutter tests) should be skipped or green. Python gates already pass.

### 4. `task-complete` skill

Run:
```
/task-complete
```
This marks TASK-PROC-058-08 as done, updates requirements coverage, and commits all staged changes.

**Files to commit** (staged by task-complete):
- `.claude/skills/task-derive-from-requ/SKILL.md` (Findings D, E, G, H)
- `scripts/requirements/check_cross_refs.py` (Finding F)
- `scripts/tests/test_check_cross_refs.py` (Finding F tests)
- `scripts/tasks/create_orchestration_task.py` (Finding H)
- `scripts/tests/test_create_orchestration_task.py` (Finding H tests)
- `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-26_impl_align-skill-with-implemented-scripts/goal.md` (status: in_progress)
- `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-26_impl_align-skill-with-implemented-scripts/plans_and_protocols/` (protocol files)

---

## Quick resume steps (next session)

```
1. claude-write-script: change _MIN_GOOD_HITS from 10 to 11 in check_cross_refs.py
2. Verify REQ-PROC-058 ≤ 30, REQ-PROC-001 ~73
3. Run quality gates (should still pass)
4. verify-quality skill
5. task-complete skill
```
