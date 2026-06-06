# Phase 5 + 6 Protocol — AC-10 Tests + Tier Annotations

**Date:** 2026-05-17
**Task:** TASK-PROC-051-04
**Phase:** 5 (tier annotations) + 6 (AC-10 direct-test audit)

## Agents

| Role | Agent ID |
|---|---|
| Prior agent (annotated 53/55 modules, started AC-10 tests, terminated mid-stream) | `a36e4c4e0fbc79a29` |
| This agent (finished annotations, fixed ruff regression, audited AC-10, wrote protocol) | `a4470eb455829fc74` |

## Entry state

- G1 ruff: FAIL — 2 errors in `scripts/tests/test_task_ordering.py` (1 auto-fixable I001 import-order, 1 RUF002 en-dash in docstring).
- G2 mypy: PASS.
- G3 pytest: PASS (573 passed, 1 skipped at entry — counted including newly added `test_task_ordering.py`).
- G4 no-handrolled YAML: PASS.
- G5 print discipline: PASS.
- Tier annotations: 53/55 — missing on `scripts/quality/check_no_handrolled_yaml.py` and (per task brief) `scripts/validate_scripts_org.py`. Verified: `validate_scripts_org.py` already had `# tier: C`; only `check_no_handrolled_yaml.py` was actually missing.

## Step 1 — ruff regression fix

- Ran `uv run ruff check --fix scripts/` — auto-fixed I001 in `scripts/tests/test_task_ordering.py` (reordered import block).
- Manually fixed RUF002 by replacing the en-dash `–` with a hyphen `-` in the docstring line `Phases 0-4 of TASK-PROC-051-04:`. (Other em-dashes `—` in the file are a distinct character — RUF001/002 ranges differ; only the en-dash tripped the gate.)
- Re-ran ruff: **All checks passed!**
- Re-ran pytest: **573 passed, 1 skipped** (no change).

## Step 2 — tier annotation backfill

| Module | Tier | Rationale |
|---|---|---|
| `scripts/quality/check_no_handrolled_yaml.py` | **B** | G4 gate script — invoked by `scripts/quality/check_python_gates.sh`; CI surface, no library callers. Single-line annotation added after closing docstring. |

`scripts/validate_scripts_org.py` was inspected and already carried `# tier: C  # one-shot CLI structural-lint script; only test imports check_domain_folders helper`. No edit needed.

## Step 3 — AC-10 audit

AST-based scan across all non-test Python modules under `scripts/` (excluding `__init__.py` and `tests/test_*.py`). For each `from scripts.* / from task_ordering.* / from automation.* / import scripts.* / ...` reference in non-test code, mapped the target module to an expected direct test file `test_<modname>.py` in either `scripts/tests/` or `scripts/automation/tests/`.

### Modules imported by non-test code (entry state)

| Module | Direct test | Notes |
|---|---|---|
| `scripts.util.yaml_frontmatter` | `test_yaml_frontmatter.py` | 9 importers. |
| `task_ordering` (package) | `test_task_ordering.py` | Added by prior agent (Phase 6 partial). 3 importers (`next_tasks.py`, `propose_after.py`, `simulate.py`). |
| `task_ordering.classifier` | `test_task_ordering.py` | Exercised via `classifier.classify_layer` smoke tests. |
| `task_ordering.rules` | `test_task_ordering.py` | Exercised via `rules.load_rules` and `rules.hardcoded_rules` smoke tests. |

The prior agent's `test_task_ordering.py` also covers `task_ordering.defaults`, `task_ordering.dependencies`, and `task_ordering.ranker` (re-exported through the package and imported via relative `from .X` chains inside the subpackage). All public names listed in `scripts/task_ordering/__init__.py::__all__` are smoke-tested.

### Modules NOT imported (CLI-only / one-shot — exempt under AC-10)

All TIER C scripts in the tier table below; the task ordering subpackage's own `simulate.py` and `validate_rules.py`; every artifact, release, requirements, tasks, user_needs, quality, util CLI entry point. Their tests, where they exist (e.g. `test_complete_task.py`, `test_orchestrate.py`, `test_validate_epic_requirements.py`, etc.), exercise the CLI behavior. AC-10's "direct test per imported module" requirement does not bind on CLI-only modules.

### New smoke tests added

None — the audit found AC-10 already satisfied by `test_yaml_frontmatter.py` and the prior agent's `test_task_ordering.py`. No further import gaps existed.

## Step 4 — final gate run

```
PYTHON GATES SUMMARY
  PASS   G1 lint
  PASS   G2 type
  PASS   G3 tests
  PASS   G4 no-handrolled
  PASS   G5 print-discip.

All Python quality gates PASSED.
```

pytest: **573 passed, 1 skipped** (the skip is the PyYAML-optional `test_load_rules_parses_well_formed_file` documented at line 195 of `test_task_ordering.py`).

## Full tier table (55 modules)

| Tier | Count | Modules |
|---|---|---|
| **A** | 1 | `scripts/automation/orchestrate.py` |
| **B** | 9 | `scripts/quality/check_no_handrolled_yaml.py`, `scripts/requirements/check_requirements_ready.py`, `scripts/task_ordering/classifier.py`, `scripts/task_ordering/defaults.py`, `scripts/task_ordering/dependencies.py`, `scripts/task_ordering/ranker.py`, `scripts/task_ordering/rules.py`, `scripts/util/should_use_agents.py`, `scripts/util/yaml_frontmatter.py` |
| **C** | 45 | All other CLI / one-shot scripts (artifacts, release, requirements, tasks, user_needs, windows, plus simulate.py, validate_rules.py, validate_scripts_org.py, etc.). |

### TIER A justification

- `scripts.automation.orchestrate` — long-running daemon; failure modes silently consume budget and corrupt task state. Strict typing prevents the entire class of "wrong shape" runtime errors that would otherwise surface only after hours of wall-clock execution.

### TIER B justification (per module)

- `scripts.quality.check_no_handrolled_yaml` — G4 gate; false negative would let a hand-rolled YAML parser slip into a script and break frontmatter contract repo-wide.
- `scripts.requirements.check_requirements_ready` — gating script for requirement promotion; widely consumed by skills.
- `scripts.task_ordering.{classifier,defaults,dependencies,ranker,rules}` — reusable library imported by `next_tasks.py`, `propose_after.py`, `simulate.py`; ranking determines what work the factory picks up next.
- `scripts.util.should_use_agents` — central guardrail invoked by skills to decide between inline reads and agent spawns; wrong answer wastes tokens or risks context overflow.
- `scripts.util.yaml_frontmatter` — central YAML-frontmatter helper; 9 importers; a bug here cascades to status overviews, ID registries, requirement validation, release readiness, and epic validation.

### TIER C exemption rationale (AC-10)

Per AC-10, the structural-minimum rule applies to **imported** modules. CLI/one-shot scripts are exempt because their behavioral contract is exercised by integration-style tests of their `main()` invocation when present (e.g. `test_validate_epic_requirements.py`), or by hand-run end-to-end checks at release time. The `tier: C` annotation in each file documents the exempt-by-design status.

## Exit state

- All 5 Python gates PASS.
- 55/55 modules carry tier annotations.
- AC-10 satisfied: every non-test module imported by other non-test code has at least one direct smoke test.
- `pyproject.toml` `[[tool.mypy.overrides]]` TIER A `module = [...]` list remains `["scripts.automation.orchestrate"]` — no further additions needed; no other module met the TIER A bar in this audit.
- 573 pytest tests passing (1 PyYAML-optional skip).

## Hard constraints honored

- No edits to CLAUDE.md, `scripts/quality/*` configuration, or `scripts/util/yaml_frontmatter.py`.
- `pyproject.toml` TIER A list left unchanged (no candidates emerged).
- No git operations.
- The `claude-write-script` PreToolUse hook fired for the two Edit operations (ruff fix + tier annotation); continued inline per the documented exception established across Phases 0-4 of this task.
