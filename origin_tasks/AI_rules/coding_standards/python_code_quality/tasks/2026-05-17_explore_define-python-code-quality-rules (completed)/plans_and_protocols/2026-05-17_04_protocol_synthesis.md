# Synthesis Protocol — TASK-PROC-051-01

## Phase summary

- **Investigation** (inline, no agent spawned): read seed files (`00_user_initial_input.md`, `01_prior_findings_for_exploration.md`), surveyed the four sibling requirements in `coding_standards/` (REQ-PROC-001, 002, 046, 052), inventoried `scripts/` Python (30 401 lines, 63 files, 8 test files), surveyed `doc/` Dart-side shape, checked package-assignment posture.
- **Decisions** (user-facing): four forks resolved via `AskUserQuestion` (sibling vs parent vs rename; all-Python scope; back-pressure inheritance; tooling in scope).
- **Drafting** (inline): `requirements.md` with id REQ-PROC-051; two next-stage seed goal.md files for the impl phase.

## Decisions taken (with user input)

| Fork | Choice | Why |
|---|---|---|
| Relation to REQ-PROC-046 | Sibling — leave REQ-PROC-046 alone | REQ-PROC-046's ACs are already explicit-Dart in their bodies; the implicit thing was the title, not the scope. Adding a sibling avoids touching a stable, in-flight requirement. |
| Python coverage | All Python in `scripts/` (30k lines) | Hand-rolled YAML (10+ files) and print-conflation (3 files at 87 / 24 / 18 calls) are repo-wide, not orchestrator-only. Restricting scope would leave most of the bug surface ungoverned. |
| Tier model | Three tiers (A long-lived stateful / B reusable lib / C one-shot CLI) | Honest about the asymmetry: Deps-DI is correct for the orchestrator and over-engineering for a 50-line ID printer. |
| Back-pressure protocol | Inherit verbatim from REQ-PROC-046 §Back-Pressure Protocol | The protocol is language-agnostic; only the gate set differs. Avoid duplication. |
| Tooling scope | In-scope (`pyproject.toml` + `ruff` + `mypy` + `pytest`) | Mirrors REQ-PROC-046 owning `analysis_options.yaml`. Without the config, the gates are not actually runnable. |

## Decisions taken (without explicit user input — flagged as judgment calls)

- **No parent requirements.md at `coding_standards/`.** None existed before; adding one is bureaucracy without a clear value. The cross-link via Related Requirements does the job.
- **5 gates, not 8** (vs REQ-PROC-046's 8). Justified: no Python-side accessibility, performance, or bundle-size equivalent makes sense; the surface is internal tooling.
- **Two new custom check scripts** (`check_no_handrolled_yaml.py`, `check_print_discipline.py`) instead of trying to encode them in `ruff` rules. Both patterns are repo-specific; off-the-shelf tooling does not have rules for them.
- **AC-10 = "imported modules need tests"**, not a coverage threshold. Justified: the codebase has 8 test files for 53 non-test modules today; a coverage threshold would either be performative (low bar) or unrealistic (high bar). Coupling tests to reuse risk is honest.
- **PERSONA-004 listed** (system maintenance) because the orchestrator is the unattended factory that produces the daily flow of work — a defect there has compounding cost, fitting PERSONA-004's profile.

## What stayed uncertain

- **Tooling versions.** The requirement names `ruff`, `mypy`, `pytest` but does not pin versions. The impl task pins them in `requirements-dev.txt`. This is intentional — version selection is implementation detail.
- **The exact `doc/python/` file list.** Listed 7 files in the impl seed but the impl task may consolidate (e.g. fold `style.md` and `type_hints.md` together). The end-state contract (entry point + `doc/README.md` reference) is what AC-12 enforces; the file layout is the impl task's choice.
- **Whether `requirements-dev.txt` is the right lockfile shape** (vs `pyproject.toml` `[project.optional-dependencies.dev]` or `uv.lock`). Deferred to the impl task; flagged in the seed.
- **Whether `scripts/windows/` PowerShell scripts need a parallel requirement.** Out of scope today; called out under "When This Requirement Does NOT Apply" with explicit ad-hoc-convention status.

## Patterns elevated to canon

From `scripts/automation/orchestrate.py` (per AC-04 through AC-09):

1. **Deps dataclass-of-callables** — `OrchestratorDeps` (~10 fields) — AC-04.
2. **Frozen-clock testing** — `get_now_utc` / `get_now_local` through Deps — AC-05.
3. **Context manager for invariants** — `active_session(state, uuid, deps)` — AC-06.
4. **Helper method for dual-tracking mutations** — `RunData.mark_exhausted` — Developer Guidelines pitfall.
5. **Enum over bool for 3+ outcomes** — `PromoteResult` — AC-07.
6. **Factory function for record construction** — `make_session_record` — Example 1 / 2 area.
7. **No hand-rolled YAML** — central helper in `scripts/util/` — AC-08.
8. **`print()` vs `logging` discipline** — `_emit_status` for protocol, `logging` for debug — AC-09.

## Open meta-question dispositions (from seed file)

| Seed question | Disposition |
|---|---|
| Make REQ-PROC-046 explicitly Dart-only in title? | **No** — ACs are already explicit. Title stays. |
| Shared parent `coding_standards/requirements.md`? | **No** — folder is structural grouping; no parent. |
| Rename `code_quality/` → `code_quality_dart/`? | **No** — user chose sibling-without-rename. |
| Parallel for `testing/`? | **Deferred** — folded into AC-10 of this requirement; if a Python-side test-quality-equivalent of REQ-PROC-002 becomes needed it will be a separate sibling. |
| `pyproject.toml` in scope? | **Yes** — AC-02 + impl seed `2026-05-17_03_seed_goal_python_tooling_config.md`. |
| Cover only orchestrator or all Python? | **All `scripts/` Python** — three-tier model handles the asymmetry. |
| Back-pressure for Python? | **Yes — same protocol** — AC-11 inherits REQ-PROC-046 §Back-Pressure Protocol. |

## Next-stage seeds produced

- `2026-05-17_02_seed_goal_doc_python_authoring.md` — impl task to author `doc/python/`.
- `2026-05-17_03_seed_goal_python_tooling_config.md` — impl task to land `pyproject.toml`, `requirements-dev.txt`, custom check scripts, central YAML helper, tier annotations.

Both seeds reference REQ-PROC-051 ACs they cover. They are picked up by `task-create` (or manual scaffolding) when the user decides to start implementation.
