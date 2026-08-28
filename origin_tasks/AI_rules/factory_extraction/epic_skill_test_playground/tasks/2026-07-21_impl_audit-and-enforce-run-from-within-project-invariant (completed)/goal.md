---
task_id: TASK-PROC-068-36
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-STRUCTURAL
impact: 4
impact_reason: I4-RISK
status: completed
effort: M
created: 2026-07-21
started: 2026-07-21
completed: 2026-07-21
session_completed_at: 2026-07-21T11:51:21Z
expected_tool_calls: 40
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
egp:
  - { ac: AC-09, archetype: S, referent: "a real untrusted candidate factory launched as a child session attempting to reach the host factory tree via absolute paths or working-directory escape" }
consequence: HIGH
scope_description: "Audit scripts/ for provider-hardwired path resolution and add a mechanical guard enforcing that scripts only ever operate on the project they are run from — never reaching into the host tree."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: edddd25f
  file: ../requirements.md
session_id: 7c4cf7e8-105f-4f62-8f93-4483956d4972
session_account: gmail2
session_last_run: 2026-07-21T11:46:00.171673+00:00
---
# Goal: Audit and Enforce the Run-From-Within-Project Invariant

## Objective

Establish and **mechanically enforce** the invariant:

> **Factory scripts are only ever called from WITHIN the project they operate on — never from outside it.**

The test harness app is **deployed as an independent standalone project**, with the scripts deployed
alongside it. Scripts are then invoked *from within that deployed project* and resolve their paths
relative to it. **No script may reach back into the provider (host) project tree.**

This discharges **AC-09**, which today is archetype **S** / consequence **HIGH** but is only assertable
by manual inspection — there is no mechanical check that a script cannot escape its project root.

## Requirements Summary

REQ-PROC-068 already states the surrounding invariants: **"Deploy & isolate"** (the candidate factory is
deployed into the harness and run **with the harness as cwd**, then git-reset between runs) and the
**"Real-Project Mirror"** hard requirement (`test_harness_app/` mirrors a real project's structure "so
factory skills resolve their conventional root-relative paths correctly when run with the harness as
cwd"). CLAUDE.md asserts the same rule for IDs: *"The ID scripts are path-scoped to their `<root>/…` and
never cross trees; the path **is** the namespace."*

This task supplies the missing **enforcement** for those stated invariants.

For complete requirements at task creation time:
```
git show edddd25f:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Verified Findings (do NOT re-derive)

`scripts/requirements/allocate_req_id.py` is **CLEAN** — verified 2026-07-21:

- `LOCK_FILE = "requirements_tasks/_meta/.task_id_lock"` (L49) and
  `REGISTRY_FILE = "requirements_tasks/_meta/id_registry.md"` (L50) are **relative** paths, resolved
  against the current working directory. No absolute path anywhere in the resolution chain.
- The tree is derived at L146 via `Path(REGISTRY_FILE).parent.parent` — i.e. from the relative constant,
  so it follows cwd.
- Run with the deployed harness as cwd, it therefore operates on **the harness's own tree** correctly.
- It also **self-bootstraps**: L109 `os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)` creates the
  `_meta/` directory, and L140 `if os.path.isfile(REGISTRY_FILE)` tolerates a missing registry.

**Consequences — treat as settled:**

- The earlier proposal to add a `--root` flag making the allocator tree-scoped is **REJECTED**. It would
  create precisely the cross-tree escape hatch AC-09 exists to prevent.
- **No harness-specific ID namespace is needed.** The harness reuses the standard prefixes in its own
  tree, because the path disambiguates (CLAUDE.md ID-scope rule).

## Scope

### In Scope

1. **AUDIT every script under `scripts/`** for provider-hardwiring:
   - absolute paths;
   - `..` traversal escaping the project root;
   - hardcoded references to the host project's name or location;
   - resolution anchored to the script's own file location (e.g. `Path(__file__).parents[N]`) in a way
     that, after deployment, would point back at the **provider** tree rather than at the **deployed**
     project.

   Report all findings. **Fix** any script that is genuinely provider-hardwired.

2. **ADD A MECHANICAL GUARD** giving AC-09 the check it currently lacks — a test/script that **fails**
   if a script resolves outside its own project root. This turns AC-09 from manually-assertable into
   mechanically-enforced.

3. Follow the project's script conventions: any edit under `scripts/**` goes through the
   `claude-write-script` skill, and the Python gates (`scripts/quality/check_python_gates.sh`) must pass.

### Out of Scope

- Changing `allocate_req_id.py`'s interface (it is already correct).
- Inventing a harness ID namespace (not needed — the path is the namespace).
- Anything about layer derivation (that engine is being retired).
- **Adding cross-tree capability to any script.** The fix direction is always *"make it project-relative
  and run it from within"* — never *"let it target another tree from outside."* A fix that adds an
  out-of-tree targeting option fails this task's purpose.

## Acceptance Criteria

- [x] AC-09 — EGP: S (a real untrusted candidate factory launched as a child session attempting to reach the host factory tree via absolute paths or working-directory escape); consequence: HIGH

Task-level completion conditions:

- [x] Every script under `scripts/` audited for provider-hardwiring; findings reported
- [x] Any provider-hardwired resolution found is fixed (project-relative), with no cross-tree option added
- [x] A mechanical guard exists that fails when a script resolves outside its own project root
- [x] Python quality gates pass (`scripts/quality/check_python_gates.sh`)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies — the verified findings above remove the original blocker |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-071-06-11 — layer-derivation-task-home](../../../epic_layer_derivation/feat_backfill_orchestration/tasks/2026-07-19_impl_layer-derivation-task-home/goal.md) | **Superseded by this task (harness-ID half).** Its blocking question asked how to allocate a requirement ID into `test_harness_app/`; that dissolves because the allocator already works when run from within the deployed project. Its other half (a layer-derivation anchor) dies with the fixpoint-engine retirement. |

## Notes

- **`--standalone-override` was used** at creation (as the skill requires logging): this is a single
  targeted task discharging one existing AC (AC-09), not a decomposition of REQ-PROC-068, so the
  redirect to `task-derive-from-requ` was deliberately skipped.
- **Developer-stated architecture** (the reason this task exists in this shape): the test harness app is
  deployed as an independent standalone project with the scripts deployed alongside it; scripts are
  called from *within* the deployed project and reference the project they run in. If any script turns
  out to be partly wired to the provider project, that "would be very bad, of course, and then it would
  have to be fixed." If none is, the right move is to **strengthen the only-call-from-within invariant**
  rather than add cross-tree capability.
- `target_package` intentionally absent — `process/` category tasks carry no release package.
