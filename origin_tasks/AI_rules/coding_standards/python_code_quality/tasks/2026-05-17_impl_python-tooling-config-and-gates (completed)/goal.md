---
task_id: TASK-PROC-051-02
type: impl
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-17
started: 2026-05-17
completed: 2026-05-17
after: [TASK-PROC-051-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03]
  sections: []
scope_description: "Mechanism only: Python tooling configuration + custom G4/G5 gate scripts + central YAML helper module + tier annotation system + single gate-runner entry point. Does NOT bring existing code to passing state — that is TASK-PROC-051-04."
release_description: ""
opus_recommended: true   # reason: cross-cutting config + custom AST/grep scripts; design choices (tool selection, config layout, helper API) benefit from longer reasoning
writes_requirements: false
requirements_version:
  commit:
  file: ../requirements.md
---

# Goal: Python Tooling Mechanism — Gates + Helper, No Existing-Code Cleanup

## Objective

Land the *capability* to enforce REQ-PROC-051: tooling configuration, custom G4/G5 gate scripts, the central YAML helper module, the tier-annotation system, and a single command that runs all five gates as a set.

This task explicitly does NOT bring the existing `scripts/` codebase to a passing state. After this task lands, the gates exist and are runnable but `scripts/` may still violate them — that's expected and is the job of TASK-PROC-051-04 (compliance / cleanup).

The split keeps this task scoped to design choices (which tools, which config shape, which helper API) and small new code (gate scripts + helper). The cleanup pass — which will be much larger and touch every file with a finding — is its own deliverable.

## Requirements Summary

REQ-PROC-051 §Behavior names five gates as roles and leaves implementation choices to the impl. Tooling defaults mentioned in conversation (`ruff`, `mypy`, `pytest`, `PyYAML`) are reasonable starting points; final selection is this impl's decision.

ACs covered by this task:
- **AC-02** — Python tooling configuration is authoritative, version-controlled, and reproducible.
- **AC-03** — Tier classification system is in place; the convention (header comment or folder-level rule) is documented so every module's tier is determinable without ambiguity.

ACs that this task makes *runnable* but does NOT satisfy yet — they fall to TASK-PROC-051-04:
- **AC-01** — `scripts/` is clean against all five gates. Gates run; passes are not yet guaranteed.
- **AC-08** — Every hand-rolled YAML site uses the central helper. The helper exists after this task; call-site migration is TASK-PROC-051-04.

Current requirements: ../requirements.md

## Scope

### In Scope

| Deliverable | Notes |
|---|---|
| Python tooling configuration file(s) | Linter rule selection, type-checker strictness per tier, test-collection contract. Format is the impl's choice (`pyproject.toml` is the obvious default; alternative file-per-tool layouts are acceptable). |
| Pinned dev-dependency lockfile | Exact versions of every tool used by the gates. Format is the impl's choice. |
| G4 gate implementation | An automated check that fails when the hand-rolled YAML-frontmatter parser pattern is present outside the centralized helper. Approach is the impl's choice (AST visitor, regex grep, ruff custom rule). The helper itself must be allow-listed in the check. |
| G5 gate implementation | An automated check that fails when `print()` is used in non-CLI modules, or in CLI modules without a documented contract in the module docstring. |
| Central YAML helper module | Read and read-modify-write API with comment preservation where required. The module exists at the end of this task; call-site migration is TASK-PROC-051-04. The helper module is allow-listed in G4. |
| Tier annotation system | Either `# tier: A | B | C` header comment convention OR a folder-level rule documented in `doc/python/` (coordinate with TASK-PROC-051-03 if the latter — that task creates `doc/python/`). The annotation is *applied to a small representative subset* (orchestrate.py, at least one TIER B module, at least one TIER C module) as proof-of-concept; full annotation across all ~60 modules is TASK-PROC-051-04. |
| Single gate-runner entry point | Script or `make`-style target that runs G1, G2, G3, G4, G5 as a set, returns non-zero on any failure. |
| CLAUDE.md updated | New Python work invokes the Python gate set the same way Dart work invokes the Dart gates. Note the intermediate state explicitly: "existing scripts/ may still violate the gates; the cleanup is TASK-PROC-051-04." |

### Out of Scope (Belongs to TASK-PROC-051-04)

- Bringing `scripts/` to a passing state under any gate.
- Migrating the 10+ existing hand-rolled YAML parser sites to use the central helper.
- Full tier-annotation pass across all ~60 modules.
- Suppression review (`# noqa`, `# type: ignore`) for existing code.

### Out of Scope (Belongs Elsewhere or to Future Tasks)

- Authoring `doc/python/` narrative — TASK-PROC-051-03.
- Changes to REQ-PROC-051's gate set or thresholds — would require a separate proposal task per REQ-PROC-051 Developer Guidelines.
- Privacy/security gates for Python — not in REQ-PROC-051.
- Test-quality gates for Python — AC-10 structural minimum only; richer test-quality is a future sibling.
- PowerShell scripts under `scripts/windows/` — explicitly out of scope of REQ-PROC-051.

## Acceptance Criteria

- [x] Python tooling configuration file(s) exist, are version-controlled, are the authoritative source for tool behavior (REQ-PROC-051 AC-02).
- [x] A pinned dev-dependency lockfile exists; a fresh dependency install on any developer machine plus a gate run produces the same gate behavior as the CI baseline (REQ-PROC-051 AC-02 reproducibility property).
- [x] G1 (static lint) is configured and *runnable* via the single gate-runner. Pass/fail behavior on `scripts/` is recorded for TASK-PROC-051-04's intake.
- [x] G2 (type check) is configured with strict mode for TIER A and default mode for TIER B/C; runnable via the gate-runner.
- [x] G3 (test runner) is configured with the agreed collection roots; runnable via the gate-runner.
- [x] G4 (no hand-rolled YAML) script is implemented and runnable; fails on the existing hand-rolled sites (proves it works) and passes on the central helper (proves the allow-list works).
- [x] G5 (print discipline) script is implemented and runnable.
- [x] Central YAML helper module exists with read and read-modify-write API; documented in its own module docstring; has its own tests.
- [x] Tier annotation convention is documented (in `doc/python/` if that exists by this task's start, else in the task's own README and a top-of-file comment block in the helper) and applied to ≥ 1 module per tier as proof-of-concept.
- [x] The single gate-runner exists and exits with the union of gate exit codes.
- [x] CLAUDE.md is updated with the Python gate-runner invocation and the explicit note that `scripts/` cleanup is TASK-PROC-051-04.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-051-01 | in_progress | Exploration task that creates REQ-PROC-051 — must complete first. |
| TASK-PROC-051-03 | pending | Doc-python authoring. Independent; can run in parallel. If TASK-PROC-051-03 is completed first, this task documents tier-annotation convention in `doc/python/`; otherwise it documents the convention locally and TASK-PROC-051-03 inherits it. |
| TASK-PROC-051-04 | pending | Compliance / cleanup task that depends on the helper, gate scripts, and configuration delivered here. |

## Notes

- **The central YAML helper API matters for TASK-PROC-051-04.** Spend the design budget here — TASK-PROC-051-04 will call this helper from 10+ sites and any API friction multiplies. At minimum: a read function that returns frontmatter + body separately, an update function that preserves comment ordering, and a context-manager-style API for read-modify-write with atomic write on exit.
- **G4 should fail on existing sites by design.** If G4 doesn't fail on the hand-rolled parsers in `orchestrate.py`, `generate_status_overview.py`, etc., the check is too lax. The intermediate state of "G4 fails on develop until TASK-PROC-051-04 lands" is acknowledged in CLAUDE.md and is the correct shape.
- **Tier annotation is a small POC here.** Picking the right convention (header comment vs folder rule) and proving it on three modules. The full-pass annotation is the cleanup task — there is no point annotating 60 modules until the convention is settled.
- **Per CLAUDE.md long-running-agent rules**: implementation likely exceeds 5 minutes (tool selection + config tuning + writing G4/G5 + writing helper + tests). When implementation begins, spawn the `implementation-engineer` agent with `run_in_background: true` and start a 4:30 heartbeat to protect the prompt cache.
