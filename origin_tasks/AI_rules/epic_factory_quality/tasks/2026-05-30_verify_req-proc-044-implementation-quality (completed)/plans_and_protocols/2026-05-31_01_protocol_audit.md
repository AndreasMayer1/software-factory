---
skills_used:
  - claude-automated-mode
  - claude-route
  - requ-verify-flow-coverage
  - task-create
  - task-complete
  - claude-commit
---

# Protocol — REQ-PROC-044 Implementation-Quality Audit

Task: TASK-PROC-044-13 (verify)
Session: ee1c0324-9655-4333-b2d4-a55233459568 (web)
Date: 2026-05-31
Auditor model: Opus (opus_recommended — synthesis across ~12 artifacts)

## Method

Audited the artifacts produced by tasks 03–12 against each of REQ-PROC-044's six
ACs independently, without assuming the implementing agents were correct. Where
possible, evidence is *empirical* (ran the real validators/linters against the
real production corpus) rather than by inspection.

Artifact inventory confirmed present:
- 63 `.claude/skills/*/contract.yaml` (waves 1–3)
- 8 `.claude/schemas/*.yaml` (goal_metadata, requirements_frontmatter, revision_target,
  external_contract, pending_question, concept_canon_entry, flutter_handoff, scribble_metadata)
- Validators: `scripts/quality/validate_against_schema.py`, `check_skill_contracts.py`,
  `check_boundary_contracts.py`
- Factory map: `scripts/factory/render_factory_map.py` → `requirements_tasks/STATUS.factory_map.html`
- Script test suites under `scripts/tests/`

## Per-AC findings

### AC-01 (Functional Reliability) — PASS (with one note)
- `check_skill_contracts.py` → `PASS — 63 contract(s) checked, 0 violations` (exit 0).
- `check_boundary_contracts.py` → `PASS — 8 contract(s) checked, 0 violations` (exit 0).
- Test suites (`test_validate_against_schema`, `test_check_skill_contracts`,
  `test_check_boundary_contracts`, `test_render_factory_map`): 62 passed, 1 skipped.
- Synthetic-bad-input detection is exercised by the test suites and passes.
- NOTE: the runtime validator deliberately checks only 3 things (required-present,
  unknown-key, enum-membership) per D-2; it does NOT check `pattern`. This is documented
  scope, not a bug — but it means schema `pattern:` fields are documentary only and a
  wrong pattern (see DEFECT-3) is invisible at runtime.

### AC-02 (Transparency / Traceability) — PASS
- Factory map is rendered from the 63 contracts; `render_factory_map.py` runs and its
  test suite passes. The contract `derived_from`/`produces` cross-references that the map
  is built from are lint-clean, so the producer→consumer artifact flow is represented
  end-to-end for the full skill set (well beyond the 3-skill minimum).

### AC-03 (Maintainability / Extensibility) — PASS
- The contract mechanism is per-file and additive: a new skill's `contract.yaml` is
  picked up by the linter and the map renderer without editing any existing contract or
  unrelated skill. Lint check #5 ("every SKILL.md folder has a contract.yaml") and the
  1:1 skill:contract count (63:63) confirm the convention scales additively.

### AC-04 (Robustness) — PASS (partial gap)
- `validate_against_schema.py` surfaces actionable, per-field errors for THREE malformed
  categories (requirement needs ≥2): missing-required-field, unknown-key, enum-violation.
  Empirically observed on real files, e.g. `unknown key 'cancellation_reason' not declared
  in the schema`, `missing required key 'created'`, `key 'type' value 'analyze' is not one
  of [...]`. No silent pass on these categories.
- GAP: a wrong `pattern:` value passes silently (validator ignores patterns by design).
  Combined with DEFECT-3 this means the broken target_package pattern is undetectable.

### AC-05 (Determinism / schema-corpus correspondence) — **FAIL (systemic)**
The AC text: *"All schema patterns, enum values, and required fields in goal_metadata.yaml
and requirements_frontmatter.yaml match the actual values found in the production artifact
corpus."* They do not — by a wide margin. Ran each schema against the entire real corpus:

**goal_metadata.yaml vs 540 real goal.md files: 123 FAIL / 417 PASS (22.8% fail).**
- 206 unknown-key errors. Top offenders are fields actively produced/consumed by skills:
  `source_flows` (22), `cross_flow_impact` (22), `depends_on_foundations` (16),
  `related_flows` (15), `target_release` (13), `foundation_for` (12), `backlog_id` (10),
  `verification_gaps` (6), `verification_foundations` (6), `source_matrix` (6),
  `orchestration_task` (5), `updated` (4), `blocks` (4), `expected_tool_calls` (4) …
  — NB: `verification_gaps` / `verification_foundations` / `source_matrix` are read by
  `requ-verify-flow-coverage` Phase 0 itself, yet the canonical goal schema does not declare them.
- 37 missing-required errors (legacy goal.md missing task_id/type/parent_requirement/status/created).
- 17 enum violations: `type` ∈ {analyze×12, review×3, explore+impl×1, define×1} — values the
  schema folded into `explore` but that still exist across the live corpus.

**requirements_frontmatter.yaml vs 156 real requirements.md files: 155 FAIL / 1 PASS (99.4% fail).**
- 679 unknown-key errors. The top keys appear in nearly EVERY file: `created` (151),
  `stakeholder` (134), `after` (133), `blocks` (130), `updated` (62), `parent` (19),
  `personas_served` (17), `parent_epic` (17), `parent_requirement` (7) …
- enum violations: `effort` value `ongoing` (×2); `status` ∈ {draft, deprecated, completed}.

**target_package pattern (goal_metadata.yaml L149):** `PKG-[0-9]+\.[0-9]+\.[0-9]+-[a-z]+`
matches ZERO of the real values. Every real value is a plain package name —
"Transfer Data Model" (55), "Adaptive Scanner Settings" (13), "claude-optimize" (10),
"Therapist Plan Management" (5), … — exactly as flagged in the triggering evidence,
still unfixed.

Conclusion: both flagged schemas are effectively non-functional as corpus validators —
they would reject the overwhelming majority of real artifacts. The 2026-05-30 triggering
evidence was not an isolated pair of typos; it is the visible tip of a systemic
schema↔corpus drift.

### AC-06 (Documentation / Single Authoritative Location) — PASS
- 63 skill folders, 63 contracts → 1:1, lint-clean. No skill listed is missing its
  contract.yaml (lint check #5 passes). `.claude/factory_flows.md` + the generated
  factory map are the single authoritative location and are self-consistent with the
  contracts they describe.

## Secondary finding (test robustness)
`scripts/tests/test_validate_against_schema.py::test_real_goal_md_against_real_schema`
is the ONLY test that checks the real schema against a real goal.md. It `pytest.skip`s on
a stale hardcoded path
(`.../2026-05-29_impl_skill-contracts-wave-2-consumers/goal.md` — the folder has since
been renamed/moved), so it silently provides zero protection. This is precisely the test
that should have caught the AC-05 drift; it is disabled by path brittleness.

## Verdict
| AC | Result |
|----|--------|
| AC-01 | PASS (pattern not runtime-checked — documented scope) |
| AC-02 | PASS |
| AC-03 | PASS |
| AC-04 | PASS (pattern-category gap, ties to DEFECT-3) |
| AC-05 | **FAIL — systemic schema↔corpus drift** |
| AC-06 | PASS |

5 of 6 ACs satisfied. AC-05 fails decisively. Follow-up impl task created (see
defects log). Audit-only — no fixes applied here.
