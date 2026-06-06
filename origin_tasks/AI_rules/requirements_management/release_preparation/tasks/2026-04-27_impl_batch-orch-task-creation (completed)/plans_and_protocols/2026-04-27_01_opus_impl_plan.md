# Opus Plan: Batch Orchestration Task Creation + Orch-First Ranking

**Date**: 2026-04-27
**Author**: Opus
**Task**: TASK-PROC-035-13
**Phase**: 2 (Implementation) — Phase 1 (REQ-PROC-035 SEC-05/06 update) already complete and approved.

---

## Objective

Two coordinated changes to the release orchestration chain:

1. **Batch creation**: Each orchestration task creates ALL pending impl tasks for one package (capped at 6 per session) instead of exactly one task. Same-package constraint keeps session context focused; six-entry ceiling prevents context blowup.
2. **Orch-first ranking**: A new special_flag `orchestration_task: true` (weight −1100) elevates orchestration tasks above implementation tasks in `next_tasks.py`. Consequence: the entire orch chain runs to completion (all impl tasks materialized) before any impl task is surfaced. Eliminates false-positive "UNCOVERED ACs" warnings during the materialization phase.

---

## Analysis Summary

### Why batching, not single-task

User intent (from `2026-04-27_analysis_task_creation_models.md`): keep Model B's just-in-time chain infrastructure but recover Model A's "all tasks visible up-front" property *per package*. Batching one full package per orch session is the smallest variant that achieves both goals — cap at 6 keeps context safe.

### Why a new special_flag instead of reusing `factory_urgent`

Reviewed both options:
- **Option A — set `factory_urgent: true` on orch tasks**: zero new rule-file code, but semantically wrong. `factory_urgent` already documents its meaning as "urgent cross-cutting factory prerequisites" (see `task_ordering_rules.yaml:172-183`). Orch tasks aren't urgent factory work; they're release-pipeline coordination. Conflating the two muddies both flags.
- **Option B — new `orchestration_task: true` flag** *(chosen)*: explicit, self-documenting, satisfies REQ-PROC-042 AC-12 (every special_flag carries `rationale:` and `rationale_source:`). Costs one new entry in `special_flags` plus one frontmatter line in the orch goal.md template.

**Weight choice**: −1100. Below `writes_requirements: -10000` (still the most critical) and above `factory_urgent: -1000`. When both `orchestration_task` and `factory_urgent` are set on different open tasks (rare but possible), the active-release pipeline takes precedence over generic factory work. Choice does not affect ordering against impl tasks (any value ≤ −1 below `current_package_scope`'s scale wins).

### Identified plan-parser bug (must fix as part of Change 1)

`parse_task_creation_plan.py::_find_next_uncreated` compares `pkg["id"]` (heading text, e.g. `"PKG: Transfer Data Model"`) against `target_package` values from goal.md frontmatter (e.g. `"Transfer Data Model"`). The "PKG: " prefix in headings means the comparison never matches, so the function always returns the first plan package's first task. The new `--next-uncreated-package` mode must use the **task-level** `target_package` field (from the task YAML block) for both the package identity and the "already created" check. The existing `--next-uncreated` mode is left unchanged (backward compat) but the bug is shadowed by the new mode taking over its role.

### "Already created" matching strategy

Goal.md files materialised by `task-create-code` have:
- `target_package: "Transfer Data Model"`
- `parent_requirement: "REQ-FUNC-007-03"`
- `covers: { acceptance_criteria: [AC-06, AC-07], sections: [] }`

Plan task entries have:
- `target_package: "Transfer Data Model"`
- `req_id: "REQ-FUNC-007-03"`
- `covers_acs: [AC-06, AC-07]`

Match a plan entry to a goal.md by tuple `(target_package, req_id, set(covers_acs))`. Counting goal.md files by `target_package` alone is insufficient — unrelated tasks (test/bugfix tasks for the same package) would inflate the count.

---

## Execution Plan

Three implementation-engineer agents run **in parallel**. Each works against the documented interface contracts in this plan (no run-time dependency between agents). Integration is verified after all three complete via the smoke-test step.

### Agent A — `parse_task_creation_plan.py` (`--next-uncreated-package` mode)

**Files touched (write):**
- `scripts/parse_task_creation_plan.py`
- `scripts/tests/test_parse_task_creation_plan.py` (new file)

**Steps:**

1. Add new helper `_load_all_created_tasks(root: Path) -> List[Dict[str, Any]]`
   - Walks `root.rglob("goal.md")`, parses frontmatter, returns list of dicts (skip files that fail to parse)
   - Read once per CLI invocation (cached by caller via direct call; the module is also import-friendly)

2. Add new helper `_is_task_created(task_entry, created_tasks_fm) -> bool`
   - Match on `(target_package, parent_requirement|req_id, set(covers.acceptance_criteria))`
   - `task_entry` uses `req_id`; goal.md uses `parent_requirement` — handle both
   - Normalise `covers_acs` (plan) vs `covers.acceptance_criteria` (goal.md) into sets for comparison

3. Add new helper `_find_next_uncreated_package(plan, root, max_tasks=6) -> Optional[List[Dict]]`
   - Iterate `plan["packages"]` in document order
   - For each `pkg_block`, walk its `tasks` and collect those where `_is_task_created` is False
   - When a `pkg_block` has any uncreated tasks, return up to `max_tasks` of them (preserve plan order)
   - Skip `pkg_block` entirely when `pkg_block["tasks"]` is empty or `pkg_block["id"] == "_ungrouped"`
   - Return `None` only when all packages are fully created

4. Add CLI flag `--next-uncreated-package` to `main()`:
   - Mutually exclusive with `--next-uncreated` (or simply prefer `--next-uncreated-package` when both passed)
   - Always JSON output (no `--field` companion); ignores `--format text` for this mode (the CLI is for scripts, not humans)
   - Exit 0 when batch returned (prints `json.dumps(batch, indent=2, default=str)`)
   - Exit 3 when all packages created (prints nothing to stdout; same convention as `--next-uncreated`)

5. **Do NOT modify** `_find_next_uncreated` or `--next-uncreated` mode — backward compat. (The pre-existing pkg-id mismatch bug is shadowed; a separate cleanup task can remove `--next-uncreated` later if desired.)

**Public-API contract** (used by Agent B):
```
$ python3 scripts/parse_task_creation_plan.py --plan PATH --next-uncreated-package
# stdout: JSON array of task dicts; exit 0
# OR: empty stdout; exit 3 (all packages created)
```
Each task dict contains at least: `task_name`, `target_package`, `req_id`, `covers_acs`, `task_type`, `effort`, `layer`.

**Tests** in `scripts/tests/test_parse_task_creation_plan.py`:

| ID | Test |
|---|---|
| T-A1 | `--next-uncreated-package` returns all tasks for first uncreated package as JSON array |
| T-A2 | Cap at 6 tasks even when package has 8 plan entries |
| T-A3 | Exits 3 when every plan entry has a matching goal.md |
| T-A4 | Skips a fully-created package and returns the next package's tasks |
| T-A5 | Match uses task-level `target_package` (regression test for pkg-id prefix bug — heading "PKG: X" with task `target_package: "X"` still matches goal.md `target_package: "X"`) |
| T-A6 | Backward compat: `--next-uncreated` still returns first task only and behaves as before |
| T-A7 | Match tuple ignores extra goal.md files with same `target_package` but different `parent_requirement` (no false positive) |
| T-A8 | Returns empty list never — either ≥1 task or exit 3 |

Use a temp directory with a synthetic `task_creation_plan.md` and synthetic goal.md files (no fixtures from the live repo).

---

### Agent B — `create_orchestration_task.py` (batch goal.md template)

**Files touched (write):**
- `scripts/create_orchestration_task.py`
- `scripts/tests/test_create_orchestration_task.py` (rewrite stale file)

**Steps:**

1. Replace the `_find_next_uncreated` subprocess call with `--next-uncreated-package`:
   ```python
   parse_result = deps.run_subprocess(
       [sys.executable, "scripts/parse_task_creation_plan.py",
        "--plan", args.plan_path, "--next-uncreated-package"],
       cwd=str(PROJECT_ROOT),
   )
   batch_tasks: List[Dict[str, Any]] = []
   if parse_result.returncode == 0:
       plan_has_uncreated = True
       try:
           batch_tasks = json.loads(parse_result.stdout) or []
       except (json.JSONDecodeError, ValueError):
           batch_tasks = []  # parse failure → fall through to fallback
   elif parse_result.returncode == 3:
       plan_has_uncreated = False
   ```
   `import json` at module level (currently absent).

2. Build dynamic AC list (helper `_build_ac_block(batch_tasks, task_id, plan_path) -> str`):
   - One `- [ ] Run \`task-create-code\` skill in zero-parameter mode for \`{task_name}\` (covers ACs: {acs})` per task
   - For tasks with `task_type == "scribble"`: use `\`ui-create-scribble\`` instead of `\`task-create-code\``
   - One `- [ ] Run \`python3 scripts/create_orchestration_task.py --after-task {task_id} --plan-path {plan_path}\` — creates next orch task OR validation task`
   - One `- [ ] Run \`task-complete\` on this orchestration task ({task_id})`

3. Replace `_GOAL_TEMPLATE` so it accepts `{ac_block}` (multi-line) and `{package_name}` instead of `{step1_ac}` and `{task_type}` interpolation in scope_description. Resulting orch goal.md:
   - `scope_description: "Orchestration: create impl tasks for package {package_name} ({n} tasks) on release {version}. Same-package per session; chain self-perpetuates."`
   - `task_type:` field stays (set from `batch_tasks[0]["task_type"]` for backward compat with downstream consumers; document that it's the type of the first batch entry)
   - **Add `orchestration_task: true` to the frontmatter** — this is the key line that triggers the new ranking rule
   - Acceptance Criteria section ends with `{ac_block}`

4. Same change to `_VALIDATION_GOAL_TEMPLATE`: add `orchestration_task: true` to frontmatter (validation orch tasks should also rank #1).

5. Drop the obsolete helpers `_build_step1_ac` and `_build_after_field` if no longer needed (or keep `_build_after_field` if still used by the validation template).

6. **Edge case — empty batch**: if `parse_result.returncode == 0` but `batch_tasks == []` (parse decoded but empty), treat as fallback (always not-all-covered, create impl orch with a single placeholder). Log a warning. This should never happen if Agent A is correct, but defensive.

7. The dry-run path stays the same — it prints "would create impl/validation orch task" without writing anything.

**Tests** — full rewrite of `scripts/tests/test_create_orchestration_task.py`:

| ID | Test |
|---|---|
| T-B1 | `parse_release_from_releases_md` — keep all existing tests (function unchanged) |
| T-B2 | `find_existing_orchestration_task` — keep existing tests (function uses `target_release` + `Orchestration:` scope_description signature; already correct) |
| T-B3 | `get_requirements_commit` — keep existing tests |
| T-B4 | `create_orchestration_task(deps, args)` exits 1 when no active release |
| T-B5 | Exits 2 when an existing orch task is found |
| T-B6 | Exits 4 when `allocate_task_id` fails |
| T-B7 | **NEW**: When parse returns batch of 2 tasks, goal.md contains exactly 4 ACs (2 task-create-code + 1 create_orchestration_task + 1 task-complete) and `orchestration_task: true` in frontmatter |
| T-B8 | **NEW**: When parse returns batch of 6 tasks, goal.md contains exactly 8 ACs |
| T-B9 | **NEW**: Scribble task in batch → AC mentions `ui-create-scribble`, not `task-create-code` |
| T-B10 | **NEW**: scope_description includes `package {target_package} ({n} tasks)` — verifies wording matches REQ-PROC-035 SEC-05 |
| T-B11 | **NEW**: When parse exits 3 → validation orch task created with `orchestration_task: true` and validation ACs |
| T-B12 | **NEW**: `args.dry_run=True` → no write/makedirs calls regardless of all_covered |
| T-B13 | **NEW**: Empty stdout from parse (returncode 0) triggers fallback path (impl orch task created, single placeholder AC) |
| T-B14 | Reserve marker removed on success (existing test, update API call) |
| T-B15 | task_id present in goal.md (existing test, update API call) |

**Drop entirely** (no longer relevant):
- `TestParseReleaseFromNextTasks` — function `parse_release_from_next_tasks` was deleted
- `TestHasUncoveredPackages` — function `has_uncovered_packages` was deleted
- `TestCreateOrchestrationTaskNothingToDo::test_exits_3_when_no_uncovered_packages` — exit 3 behaviour replaced by validation task creation

All `create_orchestration_task(deps)` calls become `create_orchestration_task(deps, _make_args(...))` with a small `_make_args` helper that builds an `argparse.Namespace`.

---

### Agent C — `next_tasks.py` guard widening + `task_ordering_rules.yaml` new flag

**Files touched (write):**
- `scripts/next_tasks.py`
- `.claude/task_ordering_rules.yaml`

**Steps:**

1. **Sub-change A** — `next_tasks.py` lines 614–645: widen the coverage-warning guard.

   Add helper above the guard block:
   ```python
   def _is_orch_task_for_active_release(t, active_release):
       return (
           t["type"] == "explore"
           and t.get("target_release") == active_release
           and str(t.get("scope_description", "")).startswith("Orchestration:")
       )
   ```
   Replace the `open_explore_for_package = any(...)` and `if not open_explore_for_package:` block with:
   ```python
   active_release = load_active_release()
   open_coverage_mechanism = any(
       t for t in tasks
       if t["status"] not in EXCLUDED_STATUSES
       and not is_blocked(t, completed_ids, known_ids)
       and (
           (t.get("target_package") == next_package and t["type"] == "explore")
           or _is_orch_task_for_active_release(t, active_release)
       )
   )
   if not open_coverage_mechanism:
       # … existing UNCOVERED ACs warning …
   ```
   Net effect: an open orch task for the active release suppresses the warning across all packages of that release.

2. **Sub-change B** — `.claude/task_ordering_rules.yaml`: add a new `special_flags` entry.

   Insert after the `factory_urgent` entry (preserve declaration order so weights read top-down by importance):
   ```yaml
     - flag: orchestration_task
       value: true
       effect: priority_boost
       weight: -1100
       rationale: >
         Release orchestration tasks must run to completion before any
         implementation task is surfaced for execution. Without this boost,
         orch tasks (which carry target_release but no target_package) would
         lose to current-release impl tasks under current_package_scope. The
         orch chain materialises all impl tasks for a release; running it to
         completion before impl starts gives the developer a complete picture
         of the release and prevents false-positive coverage warnings on
         partially-materialised releases. Weight -1100 places orch tasks
         above factory_urgent (-1000) — when both exist, the active-release
         pipeline takes precedence over generic factory work — and well
         below writes_requirements (-10000), which remains the most
         critical signal. See REQ-PROC-035 SEC-05 "Orchestration-first
         ordering".
       rationale_source: "TASK-PROC-035-13 design decision, 2026-04-27"
   ```
   Bump `updated:` field at the top of the file to `2026-04-27`.

3. Verify the `scripts/task_ordering/` engine actually picks up new `special_flags` entries from the YAML. If the rules engine hardcodes the known flags, file a follow-up task — but skim-read of the rule file's existing rationale ("Sum of weight from matching special_flags entries") suggests it iterates the list. **Verification step before merging: read `scripts/task_ordering/` ranking module and confirm the iterator is data-driven.** If the engine is hardcoded, add a small change there too.

4. After (3) confirms data-driven iteration, run `python3 scripts/task_ordering/validate_rules.py` (per CLAUDE.md §10 task-ordering note) to confirm the rule file is still valid.

5. **No new tests** for `next_tasks.py` directly — the integration smoke test (Step 5 below) verifies behaviour end-to-end. The guard change is small and obviously correct from inspection.

---

### Step 4 — Retrofit existing orchestration task (TASK-PROC-035-12)

**Why:** the user requested this so the existing pending orch task ranks #1 immediately when `next_tasks.py` runs after the changes land. Without the retrofit, only orch tasks created *after* the change get the new flag.

**Inline (no agent), after Agents A/B/C complete:**

1. Edit `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-26_explore_create-impl-tasks-release-0.0.1/goal.md`:
   - Add `orchestration_task: true` to the YAML frontmatter (e.g. immediately after `target_release:` line)
   - Do **not** modify any other field — the existing ACs and scope_description stay as-is so the running orch chain's history is preserved. The next orch task in the chain (created by Agent B's updated script) will use the new template.

2. Verify by running `python3 scripts/next_tasks.py` — TASK-PROC-035-12 should now appear at rank #1.

This is a one-line edit; safe to do inline by the orchestrator.

---

### Step 5 — Integration smoke test

After Agents A, B, C, and the retrofit complete:

1. `python3 scripts/task_ordering/validate_rules.py` — exit 0 (rule file valid)
2. `python3 -m pytest scripts/tests/ -q` — all green
3. `python3 scripts/parse_task_creation_plan.py --plan "$(find requirements_tasks -name task_creation_plan.md | head -1)" --next-uncreated-package` — exits 0 with JSON array; **expected**: array of remaining uncreated tasks for the next package in the live plan
4. `python3 scripts/next_tasks.py` — verify:
   - TASK-PROC-035-12 ranks #1
   - No "UNCOVERED ACs — DEPENDENCY GRAPH INCOMPLETE" warning appears
   - The full impl task that's currently #2 drops below the orch task

If any of (1)–(4) fail, halt and report — do **not** auto-fix.

---

## Quality Criteria

- [ ] `parse_task_creation_plan.py --next-uncreated-package` returns ALL remaining tasks for the next uncreated package as a JSON array, capped at 6
- [ ] Exit code 3 still means "all packages created" (consistent with `--next-uncreated`)
- [ ] `_find_next_uncreated_package` matches plan entries to goal.md files by `(target_package, req_id, set(covers_acs))` — not by pkg-heading id
- [ ] `create_orchestration_task.py` produces orch goal.md with N+2 ACs (N = batch size, 1 ≤ N ≤ 6) and `orchestration_task: true` in frontmatter
- [ ] Validation orch task also carries `orchestration_task: true`
- [ ] Scope description matches REQ-PROC-035 SEC-05 wording: "create impl tasks for package X (N tasks)"
- [ ] Scribble batch entries get `ui-create-scribble` AC text; impl/verify entries get `task-create-code`
- [ ] `next_tasks.py` guard suppresses the UNCOVERED ACs warning when an open orch task for the active release exists, regardless of `target_package`
- [ ] `task_ordering_rules.yaml` has a new `orchestration_task: true` special_flag with `rationale:` and `rationale_source:` (REQ-PROC-042 AC-12 compliance)
- [ ] TASK-PROC-035-12 is retrofitted with `orchestration_task: true` and ranks #1 in `next_tasks.py` output
- [ ] All existing tests still pass; new tests cover the new modes
- [ ] No code in `lib/` is touched

## Risks

- **Risk 1 — Engine doesn't iterate special_flags from YAML**: Mitigation: Step 3 of Agent C verifies before integration. If hardcoded, add a small change to `scripts/task_ordering/engine.py` (or wherever the iteration lives) and document in this plan's protocol.
- **Risk 2 — `_is_task_created` matching is too strict**: Plan entries may have additional ACs added during plan iteration that don't match an already-created goal.md. Mitigation: match `set(covers_acs)` equality — if a plan entry's covers_acs is later widened, the previously-created goal.md becomes "uncreated" and gets re-materialised. This is the right behaviour (the plan is authoritative). Document in code comment.
- **Risk 3 — Tests in `test_create_orchestration_task.py` are entangled with stale API**: Mitigation: full rewrite (already planned). The `_make_args` helper isolates Namespace construction so future signature changes only touch one helper.
- **Risk 4 — Live plan parsing finds zero uncreated when it shouldn't**: Mitigation: Step 5.3 of the smoke test validates against the live plan. If the JSON array is empty, fall back to manual inspection of `_is_task_created` matching.
- **Risk 5 — Retrofit breaks running chain**: Mitigation: only adding one frontmatter field; the rest of TASK-PROC-035-12's goal.md is untouched. No effect on current ACs or downstream commands.

## Out of Scope

- Removing the legacy `--next-uncreated` mode (left for backward compat; can be a follow-up task)
- Changing `release-begin-impl` Phase 6 (continues to create the first orch task as today; the new template applies because Phase 6 calls `create_orchestration_task.py`)
- Parallelising impl tasks across sessions (still sequential post-orch)
- Touching `check_ac_coverage.py` (analysis recommended `--plan` option as defensive measure; not needed once orch-first ranking is in place)
