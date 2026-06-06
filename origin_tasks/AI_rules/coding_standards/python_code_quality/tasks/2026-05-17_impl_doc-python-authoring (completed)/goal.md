---
task_id: TASK-PROC-051-03
type: impl
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-17
completed: 2026-05-17
after: [TASK-PROC-051-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-12, AC-14]
  sections: []
scope_description: "Author the doc/python/ narrative guidance and update doc/README.md so Python gets a dedicated documentation folder and the Dart-default language-isolation convention is discoverable from the doc entry point."
release_description: ""
opus_recommended: true   # reason: cross-cutting narrative authoring across 6-7 files with cross-references; benefits from longer reasoning
writes_requirements: false
requirements_version:
  commit:
  file: ../requirements.md
---

# Goal: Author `doc/python/` Narrative Guidance

## Objective

Produce the `doc/python/` files that REQ-PROC-051 AC-12 requires, and update `doc/README.md` to make the Dart-default language-isolation convention explicit (AC-14).

After this task, a contributor or LLM agent doing Python work can read `doc/python/` and understand:
- Which tier their module is in and why
- Which canonical patterns apply (Deps-DI, frozen-clock, context-manager-for-invariants, enum-over-bool, central YAML helper, print/logging discipline)
- Which anti-patterns to avoid and why those specific patterns matter to this repo
- How the Python gates relate to the back-pressure protocol inherited from REQ-PROC-046

…without having to read the orchestrator's source from end to end.

## Requirements Summary

REQ-PROC-051 §Behavior names patterns and gates; the narrative `doc/python/` is the supporting documentation. AC-12 requires Python guidance to live in `doc/python/` and nowhere else under `doc/`. AC-14 requires the language-isolation convention to be documented in `doc/README.md`.

`doc/README.md` was already updated during TASK-PROC-051-01 to state the convention and list `doc/python/` as the dedicated Python folder. This task fleshes out the folder's contents and verifies `doc/README.md`'s entry is accurate and complete.

Current requirements: ../requirements.md

## Scope

### In Scope

Suggested file set (the exact list may be tuned during authoring; only the entry point and `doc/README.md` linkage are gated):

| File | Content |
|---|---|
| `doc/python/README.md` | Index of the folder; tier classification rule; pointer to the tooling configuration and gate scripts as authoritative (delivered by TASK-PROC-051-02). |
| `doc/python/style.md` | What the static-lint gate enforces (by rule category, not by every rule code); naming; line length; module docstring conventions. |
| `doc/python/type_hints.md` | When the type-check gate runs in strict mode (TIER A) vs default (TIER B/C); when `# type: ignore[<code>]` is acceptable; pattern for stub-less stdlib calls. |
| `doc/python/dependency_injection.md` | The substitutable-boundary pattern with the orchestrator as the reference (file:line into `scripts/automation/orchestrate.py`); production-default vs test-fake wiring. Includes the rule "if you reach for module-level stdlib monkey-patching in TIER A, add the call to the boundary." |
| `doc/python/testing.md` | Pytest conventions; frozen-clock pattern via the substitutable boundary; co-located vs central `tests/` layout; AC-10 import-implies-test rule restated; coverage stance (no global threshold; AC-10 is the structural minimum). |
| `doc/python/architecture.md` | The three tiers with concrete examples; when a TIER B helper warrants promotion to TIER A; the context-manager-for-invariants rule; named-outcomes vs `bool`. |
| `doc/python/anti_patterns.md` | Hand-rolled YAML, `print()` conflation, parallel mutation of two fields, blanket `except Exception`, module-level stdlib monkey-patching in TIER A. Each anti-pattern names a real incident or a real risk to anchor the *why*. |

Other in-scope items:

- **Updates to `doc/README.md`**: verify the "Language Scope" section accurately reflects the final `doc/python/` file list and the Python routing entry resolves to a real file.
- **Updates to the `quality-checker` agent prompt** so it reads `doc/python/` for Python tasks (mirrors how it reads `doc/architecture/`, `doc/testing/`, etc. for Dart).
- **References into existing code** — every canonical pattern named in `doc/python/` cites a file:line in `scripts/automation/orchestrate.py` (or its tests) rather than re-deriving the pattern in prose.

### Out of Scope

- Landing the tooling configuration, gate scripts, or central YAML helper — TASK-PROC-051-02.
- Bringing existing `scripts/` to a passing state — TASK-PROC-051-04.
- Modifying any Dart-oriented `doc/` folder — only `doc/python/` and `doc/README.md` are touched.

## Acceptance Criteria

- [x] `doc/python/README.md` exists and is the entry point of the folder.
- [x] `doc/README.md`'s "Language Scope" section is reviewed and remains consistent with what `doc/python/` actually contains; the routing-table row for Python work resolves to a real file (REQ-PROC-051 AC-14).
- [x] No Python-specific guidance lives in Dart-oriented `doc/` folders (`architecture/`, `testing/`, `linter/`, `presentation/`, `domain/`, `cross_cutting_standards/`, `general/`); any such content found is moved to `doc/python/` (REQ-PROC-051 AC-12).
- [x] Every `doc/python/` file stays within REQ-PROC-048's size limits (600-line bound per file; split per its mechanism if needed).
- [x] Each canonical pattern in REQ-PROC-051 (AC-04 through AC-09) is covered by at least one file:line reference into existing code, not by re-derived prose.
- [x] The anti-patterns file names the real incidents that motivated each anti-pattern (May 2026 frozen-clock test failures; the dual-tracker bug from TASK-PROC-046-03) where applicable.
- [x] The `quality-checker` agent's prompt is updated to read `doc/python/` for Python work.
- [x] If a tier-annotation convention has been settled by TASK-PROC-051-02 (header comment vs folder rule), `doc/python/architecture.md` documents it as authoritative.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-051-01 | in_progress | Exploration task that creates REQ-PROC-051 — must complete first. |
| TASK-PROC-051-02 | pending | Mechanism task. Independent in implementation; the two can run in parallel. Coordinate on tier-annotation convention if both are active. |

## Notes

- **Reference the code, do not re-derive the pattern.** The orchestrator (`scripts/automation/orchestrate.py`) is the canonical TIER A example. A reader of `doc/python/dependency_injection.md` who follows the file:line reference into `OrchestratorDeps` learns more in 30 seconds than from any amount of prose abstraction.
- **The "why" carries the weight.** A rule like "no hand-rolled YAML" is forgettable; "no hand-rolled YAML because three independent state machines in the orchestrator shared a bug surface and a fix in one did not propagate" is memorable. Lead with the incident.
- **Coordinate file structure with TASK-PROC-051-02.** If that task settles the tooling at `pyproject.toml`, `doc/python/style.md` references it by that name. If TASK-PROC-051-02 hasn't landed yet, write `doc/python/` with placeholders and revisit when -02 lands.
- **Per CLAUDE.md long-running-agent rules**: narrative authoring across 6–7 files likely exceeds 5 minutes; spawn the implementation agent in background with a 4:30 heartbeat.
