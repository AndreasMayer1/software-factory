# Plan — TASK-PROC-051-04 phased cleanup

**Approach**: agent-assisted, one-gate-at-a-time (per goal.md Notes).
**Risk control**: YAML migration preserves behavior at each site (regression test BEFORE swap).
**Cadence**: background `general-purpose` impl agent per phase; main session
holds a 4:30 heartbeat loop while each runs (CLAUDE.md §2 long-running rule).

## Baseline (captured 2026-05-17 from `bash scripts/quality/check_python_gates.sh`)

| Gate | Status | Volume |
|---|---|---|
| G1 ruff lint | FAIL | 981 errors; 127 auto-fixable; 681 hidden-unsafe fixes |
| G2 mypy | FAIL | + config bug: `python_version: 3.9` rejected (must be ≥3.10) |
| G3 pytest | FAIL | 1 failing test in `test_validate_scripts_org.py::test_cli_check_flag_runs_without_error` (415 pass) |
| G4 no-handrolled YAML | FAIL | 21 files |
| G5 print discipline | FAIL | 591 violations |

Full baseline: `/tmp/python_gates_baseline.txt` (captured this session).

## Phases

### Phase 0 — Pre-flight (INLINE, this session)
- Fix `pyproject.toml` mypy `python_version` 3.9 → 3.10.
- Fix the single failing pytest case (almost certainly a -02 regression).
- Persist this plan + baseline notes.
- Success check: G2 stops erroring on config; G3 has only ACTUAL test failures left (if any).

### Phase 1 — G4 YAML helper migration (background agent)
Sites surfaced by gate: `automation/orchestrate.py`, `artifacts/generate_status_overview.py`,
`artifacts/generate_id_registry.py`, `release/check_release_preconditions.py`,
`release/release_readiness.py`, `release/execute_release.py`,
`requirements/check_requirements_ready.py`, `requirements/sync_task_packages.py`,
`requirements/coverage_report.py`, `requirements/validate_epic_requirements.py`,
`requirements/validate_meta.py`, `tasks/check_task_against_plan.py`,
`tasks/find_orchestration_tasks.py`, `tasks/next_tasks.py`,
`tasks/parse_task_creation_plan.py`, `tasks/reconcile_after_chains.py`,
`tasks/top_blocked_task.py`, `util/should_use_agents.py`.

Per-site protocol: (a) add a regression test pinning current parser output for
representative fixtures, (b) swap to `scripts.util.yaml_frontmatter`,
(c) re-run regression test, (d) commit-style note in protocol if behavior
diverged and why the helper's behavior is correct.

Success: G4 exits 0.

### Phase 2 — G1 ruff cleanup (background agent)
Two passes: safe `--fix` first (~127), then `--unsafe-fixes` selectively after
diff review, then triage remaining (~170) per AC-13 (fix > suppress-with-just >
propose-rule-change). Each `# noqa` MUST have inline reason.
Success: G1 exits 0.

### Phase 3 — G2 mypy cleanup (background agent)
TIER A modules first (strict-clean). `orchestrate.py` is the largest annotation
effort. TIER B/C run default mypy. `# type: ignore[<code>] — <reason>` allowed.
Success: G2 exits 0.

### Phase 4 — G5 print discipline (background agent)
CLI modules: add docstring `Output:` contract + route protocol output through a
named helper. Non-CLI modules: convert to `logging`.
Success: G5 exits 0.

### Phase 5 — G3 / AC-10 test backfill (background agent)
Audit imported modules without a direct test; add one smoke test per missing
module. TIER C one-shots exempt.
Success: G3 exits 0; AC-10 satisfied structurally.

### Phase 6 — Tier annotation pass (background agent)
Apply `# tier: A | B | C` after docstring on every module under `scripts/`.
Use the convention finalized by TASK-PROC-051-02.
Success: ~69 modules tier-annotated.

### Phase 7 — Suppression review (inline if small)
Audit `# noqa`, `# type: ignore`, tool-specific disables. Each carries an
adjacent justification per AC-13. Likely already enforced by phases 2–3 work.

### Phase 8 — Final integration (inline)
- Re-run `scripts/quality/check_python_gates.sh` → must exit 0.
- Remove the "existing scripts/ may still violate" intermediate-state note from
  CLAUDE.md.
- Remove the "develop baseline failures are expected" note from
  `check_python_gates.sh`.
- Update goal.md `requirements_version.commit` / `file` if applicable.
- `task-complete` skill (single commit per CLAUDE.md §4).

## Rules in force

- **Behavior preservation** (goal AC-11): no feature removed; YAML migration
  preserves existing parser behavior.
- **No silent gate-relaxation** (REQ-PROC-051 Developer Guidelines): if a finding
  suggests the gate is wrong, write a proposal task; do not weaken config.
- **WHY comments**: only on non-obvious code in `lib/` / `test/` / `integration_test/`
  (CLAUDE.md §5). Scripts cleanup is NOT subject to that rule — but per AC-13,
  every suppression DOES need an inline justification.
- **Long-running**: each spawned impl agent runs background with main-session
  4:30 heartbeat loop.
