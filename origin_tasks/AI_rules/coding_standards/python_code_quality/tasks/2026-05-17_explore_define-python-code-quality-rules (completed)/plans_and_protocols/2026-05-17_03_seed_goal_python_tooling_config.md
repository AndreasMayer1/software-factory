# Seed goal.md — Python tooling configuration + custom gate scripts

> Not a real `goal.md` yet. Picked up by `task-create` (or manual scaffolding) when the user is ready to start the implementation.

---

```yaml
type: impl
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
effort: L
opus_recommended: true   # reason: cross-cutting config + custom AST/grep scripts + bringing existing 30k-line codebase to a passing state
covers:
  acceptance_criteria: [AC-01, AC-02, AC-08]   # G1/G2/G3 baseline + G4 enabler
  sections: []
```

# Goal: Python Tooling Configuration + Gate Scripts + YAML Helper

## Objective

Land the tooling (`pyproject.toml`, `requirements-dev.txt`, gate scripts under `scripts/quality/`, central YAML helper) that makes REQ-PROC-051's gates runnable, then bring the existing `scripts/` codebase to a clean pass.

This is the implementation deliverable for REQ-PROC-051's G1–G4 gates. G5 (print discipline) is included as part of the same task because the implementation is parallel to G4.

## What lands

| Deliverable | Notes |
|---|---|
| `pyproject.toml` | Repo-root. `[tool.ruff]` with selected rule set (see REQ-PROC-051 G1 row); `[tool.mypy]` with TIER A `strict = true` overrides; `[tool.pytest.ini_options]`. |
| `requirements-dev.txt` | Pinned versions of `ruff`, `mypy`, `pytest`, `PyYAML`. |
| `scripts/quality/check_no_handrolled_yaml.py` | G4 implementation. AST or regex; allow-list for the central helper itself. Exit non-zero on match. |
| `scripts/quality/check_print_discipline.py` | G5 implementation. Walks `scripts/` and flags `print()` calls in modules not declared as CLI entry points (module docstring contract). |
| `scripts/util/frontmatter.py` | The central YAML helper that AC-08 implies. Provides `read_frontmatter(path)` and `update_frontmatter(path, **updates)` with comment preservation where required (`ruamel.yaml` if needed; else PyYAML). |
| Refactor: every hand-rolled parser call site moves to `scripts/util/frontmatter.py` | 10+ files identified in REQ-PROC-051 §Examples 4. |
| Tier annotation pass: `# tier: A | B | C` headers added | Or the equivalent folder-convention doc in `doc/python/`. |
| Initial passing state: `ruff check`, `mypy`, `pytest`, G4, G5 all exit zero on `scripts/` | The cleanup may surface many small issues — that's expected; the task converges by fixing or suppressing-with-justification per AC-13. |

## Background

REQ-PROC-051 was authored on 2026-05-17 (TASK-PROC-051-01). It names `pyproject.toml` as the authoritative source for G1/G2/G3 configuration and reserves AC-08 (no hand-rolled YAML) as the headline pattern to fix because it has demonstrably already produced bugs in the orchestrator.

The codebase is 30 401 lines across 63 Python files today. Many of those files have no annotations, use `print()` for internal debug, hand-parse YAML, or both. The cleanup is meaningful work — not a one-line config drop. Expect the implementation to discover patterns that the requirement did not anticipate; route any rule-set proposal through a `task-create` for user review, not by silently relaxing `pyproject.toml` (per REQ-PROC-051 Developer Guidelines "gate-set changes require user approval").

## Out of scope

- Authoring `doc/python/` narrative — separate impl task.
- Changing REQ-PROC-051's gate set or thresholds — out of scope; if encountered, file a separate proposal task.
- Adding privacy/security gates for Python (no telemetry SDKs, no network I/O) — not in REQ-PROC-051; if needed, a separate Python-side REQ-PROC-052 equivalent.

## Acceptance Criteria

- [ ] `pyproject.toml` exists at repo root and is the authoritative config source per REQ-PROC-051 AC-02.
- [ ] `requirements-dev.txt` pins exact versions of `ruff`, `mypy`, `pytest`, `PyYAML`.
- [ ] `ruff check scripts/` exits 0 on `develop`.
- [ ] `mypy scripts/` exits 0 on `develop` (TIER A strict; TIER B/C default).
- [ ] `pytest` exits 0 on `develop` with the configured collection roots.
- [ ] `scripts/quality/check_no_handrolled_yaml.py` exists and exits 0 on `develop`.
- [ ] `scripts/quality/check_print_discipline.py` exists and exits 0 on `develop`.
- [ ] `scripts/util/frontmatter.py` exists; every previous hand-rolled call site now imports from it.
- [ ] Tier classification is applied (header tags or folder-convention doc) so AC-03 can be verified by inspection.
- [ ] CI invocation (or manual `scripts/quality/check_quality_gates_python.sh` equivalent) ties the five gates together as a single command for the back-pressure protocol.
