---
task_id: TASK-PROC-051-04
type: impl
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-17
started: 2026-05-17
completed: 2026-05-18
after: [TASK-PROC-051-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-08, AC-10, AC-13]
  sections: []
scope_description: "Bring the existing ~30 000 LOC of scripts/ to a clean pass against all five Python gates. Includes migrating 10+ hand-rolled YAML parser sites to the central helper, full tier annotation, suppression review, and adding any missing tests required by AC-10."
release_description: ""
opus_recommended: true   # reason: 30k-LOC cleanup with judgment calls per finding (fix vs suppress vs propose-rule-change) across ~60 files; benefits from longer reasoning + may surface latent bugs in the YAML migration
writes_requirements: false
requirements_version:
  commit:
  file: ../requirements.md
---

# Goal: Bring `scripts/` to a Clean Pass Against the Python Gates

## Objective

After TASK-PROC-051-02 lands the mechanism (configuration + gate scripts + central YAML helper + a small POC of tier annotations), this task does the cleanup pass that brings the existing `scripts/` codebase — ~30 000 LOC across ~60 files — to a state where all five gates exit clean from a clean checkout.

This is the task that closes REQ-PROC-051 AC-01 (`scripts/` passes the gates) and AC-08 (hand-rolled YAML is gone in favour of the central helper). It also satisfies AC-10's structural minimum (every imported module has a test) by adding what is missing, and AC-13 by reviewing every existing suppression for justification.

## Requirements Summary

REQ-PROC-051 AC-01 makes "all Python sources under `scripts/` produce zero violations" a property of the codebase. TASK-PROC-051-02 lands the gates that measure the property; this task changes the codebase to satisfy them.

The triage rule per finding is simple in principle, judgmental in practice:
- **Fix** — the finding represents a real issue (a real bug, a real style violation, a real type error). Default.
- **Suppress with justification** — the rule does not apply to this specific case for a documented reason. Use `# noqa: <code> — <reason>` or `# type: ignore[<code>] — <reason>`. Per AC-13, bare suppressions are themselves violations.
- **Propose a rule change** — the gate is wrong for this case in a way that suggests a systematic gap. Open a separate proposal task per REQ-PROC-051 Developer Guidelines ("gate-set changes require user approval, not LLM autonomy"). Do NOT silently relax the configuration delivered by TASK-PROC-051-02.

Current requirements: ../requirements.md

## Scope

### In Scope

| Cleanup area | What it covers |
|---|---|
| **G1 static-lint cleanup** | Triage every linter finding under `scripts/`. Fix the real issues; suppress-with-justification the rest. Update inline justifications to AC-13's standard. |
| **G2 type-check cleanup** | Annotate functions/methods enough for the type checker to exit clean — strict mode in TIER A modules, default elsewhere. `# type: ignore[<code>]` is acceptable per AC-13. Adding sufficient type annotations to make TIER A strict-clean is the largest sub-task here. |
| **G3 test backfill (AC-10 structural minimum)** | Identify every imported module that currently has no direct test. Add at least one direct test per module (a smoke test exercising the documented contract is sufficient). TIER C one-shot scripts are exempt. |
| **G4 hand-rolled YAML migration (AC-08)** | Migrate every hand-rolled frontmatter parser site to the central YAML helper delivered by TASK-PROC-051-02. Known sites at exploration time: `scripts/automation/orchestrate.py` (3 functions), `scripts/artifacts/generate_status_overview.py`, `scripts/artifacts/generate_id_registry.py`, `scripts/release/check_release_preconditions.py`, `scripts/release/release_readiness.py`, `scripts/release/execute_release.py`, `scripts/requirements/check_requirements_ready.py`, `scripts/requirements/sync_task_packages.py`, `scripts/requirements/coverage_report.py`, `scripts/requirements/validate_epic_requirements.py`, and any further sites G4 surfaces. After migration, the only parsing of YAML frontmatter in the codebase happens inside the helper module. |
| **G5 print discipline cleanup** | For non-CLI modules: route every `print()` through structured logging. For CLI modules: add the docstring contract; route protocol output (the orchestrator's `[orchestrator <ts>] ...` lines) through a single named helper so the protocol surface is greppable. |
| **Full tier annotation** | Apply the tier-annotation convention settled by TASK-PROC-051-02 to all ~60 modules under `scripts/`. After this pass, every module's tier is determinable without ambiguity. |
| **Suppression review (AC-13)** | Audit every existing `# noqa`, `# type: ignore`, or tool-specific disable in `scripts/`. Each must have an adjacent inline justification per AC-13. |
| **CLAUDE.md update** | Remove the "existing scripts/ may still violate the gates; cleanup is TASK-PROC-051-04" note added by TASK-PROC-051-02 once cleanup is complete and the gates are enforced unconditionally. |

### Out of Scope

- Landing or modifying the gate scripts, configuration, or central helper API — that is TASK-PROC-051-02; if the cleanup surfaces an API friction point, propose the fix back to that task or open a follow-up.
- Authoring `doc/python/` narrative — TASK-PROC-051-03.
- Refactoring beyond what the gates require. The cleanup is "bring code to passing"; structural refactors (e.g. splitting `orchestrate.py` into multiple files, which has been discussed separately) are NOT part of this task.
- Adding privacy/security gates for Python — not in REQ-PROC-051.
- Test-quality gates beyond AC-10's structural minimum.

## Acceptance Criteria

- [x] `ruff check scripts/` (or equivalent G1 invocation) exits 0 on `develop`.
- [x] `mypy scripts/` (or equivalent G2 invocation) exits 0 on `develop` — strict in TIER A, default in TIER B/C.
- [x] `pytest` (or equivalent G3 invocation) exits 0 on `develop` against the configured collection roots.
- [x] The G4 (no hand-rolled YAML) check exits 0 on `develop`; every previous hand-rolled site imports from the central helper.
- [x] The G5 (print discipline) check exits 0 on `develop`.
- [x] Every imported module under `scripts/` has at least one direct test (REQ-PROC-051 AC-10 structural minimum).
- [x] Every existing suppression (`# noqa`, `# type: ignore`, etc.) has an adjacent justification comment per AC-13.
- [x] All ~60 modules under `scripts/` have their tier classification applied per the convention settled by TASK-PROC-051-02.
- [x] CLAUDE.md no longer carries the "existing scripts/ may still violate" intermediate-state note.
- [x] The single gate-runner entry point (delivered by TASK-PROC-051-02) exits 0 on `develop`.
- [x] The modified python files still behave like before the adjustments. No features removed. 

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-051-02 | pending | Mechanism task. The central YAML helper, the G4/G5 check scripts, the tooling configuration, and the tier-annotation convention all come from there. This task is unblocked only after -02 is completed. |
| TASK-PROC-051-03 | pending | Doc-python authoring. NOT a hard dependency, but the cleanup pass becomes a useful proof-point for the `doc/python/` narrative — running this task while `doc/python/` is being authored produces good feedback in both directions. |

## Notes

- **Budget carefully.** 30 000 LOC under no prior governance will surface many findings — each judged individually. A reasonable cadence is one-tool-at-a-time (finish G1 cleanup, then G2, then G3, etc.) rather than file-at-a-time, because each tool is its own mental model.
- **The YAML migration is the riskiest part.** The parallel parsers in the orchestrator and elsewhere are not identical — some preserve comments, some handle empty values differently, some strip trailing newlines. Add a regression test at each site *before* swapping in the central helper so behavior-preservation is verifiable.
- **TIER A `mypy --strict` is the largest type-annotation effort.** `scripts/automation/orchestrate.py` is 3 300+ lines with sparse annotations today. Plan that this single module will be a significant fraction of the type-check cleanup.
- **Per CLAUDE.md long-running-agent rules**: this task will exceed 5 minutes many times over. Every spawned `implementation-engineer` agent runs in background with a 4:30 heartbeat. Consider sub-task scoping — e.g. "G1 cleanup pass," "G2 cleanup pass for TIER A," "YAML migration for the release toolchain" — each as its own spawn rather than one mega-spawn.
- **Per REQ-PROC-051 Developer Guidelines: if a finding suggests the gate is wrong, do NOT relax it.** File a separate proposal task. Silently relaxing the configuration during cleanup would let the gates be weakened under pressure, which is exactly the failure mode the requirement protects against.
