# Seed goal.md — Author doc/python/ narrative guidance

> Not a real `goal.md` yet. Picked up by `task-create` (or manual scaffolding) when the user is ready to start the implementation.

---

```yaml
type: impl
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
effort: M
opus_recommended: true   # reason: narrative guidance authoring across 6-7 files with cross-references; benefits from longer reasoning
covers:
  acceptance_criteria: [AC-12]
  sections: []
```

# Goal: Author `doc/python/` Narrative Guidance

## Objective

Produce the `doc/python/` files that AC-12 of REQ-PROC-051 requires. Provide a contributor or LLM agent enough narrative to comply with the gates and apply the canonical patterns without re-reading the orchestrator's source.

## Files to produce

The exact file list may be tuned during authoring; the entry point must be `doc/python/README.md` and `doc/README.md` must reference it. Suggested set:

| File | Content |
|---|---|
| `doc/python/README.md` | Index of the folder; tier classification rule; pointer to `pyproject.toml` and `scripts/quality/check_*.py` as authoritative. |
| `doc/python/style.md` | What ruff enforces (referenced by rule code, not duplicated); naming; line length; module docstring conventions. |
| `doc/python/type_hints.md` | Strict vs default mypy; when `# type: ignore[<code>]` is acceptable; pattern for stub-less stdlib calls. |
| `doc/python/dependency_injection.md` | The Deps dataclass pattern with the `OrchestratorDeps` walkthrough; default_factory wiring; test-side fake construction. Includes the rule "if you reach for `mock.patch`, add it to Deps." |
| `doc/python/testing.md` | Pytest conventions; frozen-clock pattern via Deps; co-located vs central `tests/` layout; AC-10 import-implies-test rule restated; coverage stance (no global threshold). |
| `doc/python/architecture.md` | The three tiers with concrete examples; when a TIER B helper warrants promotion to TIER A; the context-manager-for-invariants rule; enum-over-bool. |
| `doc/python/anti_patterns.md` | Hand-rolled YAML (with the three orchestrator examples), `print()` conflation, parallel mutation of two fields, bare `except Exception`, `mock.patch` in TIER A. Each anti-pattern names a real incident or a real risk. |

## Background

REQ-PROC-051 was authored on 2026-05-17 as an exploration deliverable (TASK-PROC-051-01). It names the gates and rules but defers the narrative to this task. Without `doc/python/`, the gate set is enforceable but the *why* is buried in the orchestrator's source and in this requirement's Purpose section — a future agent will not find the pattern set by browsing.

The orchestrator (`scripts/automation/orchestrate.py`) and its test file (`scripts/automation/tests/test_orchestrate.py`) are the canonical examples for the Deps-DI, context-manager, enum, factory, and dual-mutation-helper patterns. Reference them by file:line, not by re-explaining the pattern in prose.

## Out of scope

- Implementing `pyproject.toml`, `ruff`/`mypy`/`pytest` config — that is a separate impl task.
- Implementing the G4 and G5 check scripts — separate impl task.
- Consolidating the hand-rolled YAML parsers into one helper — separate impl task.

## Acceptance Criteria

- [ ] `doc/python/README.md` exists and is the entry point.
- [ ] `doc/README.md` is updated to (a) state explicitly that `doc/` defaults to Dart (the project is a Flutter app) and (b) list `doc/python/` as the dedicated Python folder, with the convention that every non-Dart language gets a dedicated `doc/<lang>/` subfolder. This satisfies REQ-PROC-051 AC-14.
- [ ] No Python-specific guidance lives in the Dart-oriented folders (`doc/architecture/`, `doc/testing/`, `doc/linter/`, `doc/presentation/`, `doc/domain/`, `doc/cross_cutting_standards/`, `doc/general/`) — if any such content exists today, it is moved into `doc/python/`. This satisfies REQ-PROC-051 AC-12.
- [ ] Every file listed above (or its agreed substitute) exists and stays within REQ-PROC-048's size limits.
- [ ] Each canonical pattern in REQ-PROC-051 is covered by a file:line reference into `scripts/automation/orchestrate.py` (or its tests), not by re-derived prose.
- [ ] The anti-patterns file names real incidents (May 2026 frozen-clock failure; TASK-PROC-046-03 dual-tracker bug) where applicable.
- [ ] `quality-checker` agent's prompt is updated to read `doc/python/` for Python tasks.
