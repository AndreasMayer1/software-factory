---
task_id: TASK-PROC-051-05
type: explore
parent_requirement: REQ-PROC-051
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-27
started: 2026-05-27
completed: 2026-05-28
session_completed_at: 2026-05-27T23:15:19Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Audit Python coding quality gaps beyond existing gates, compare to Dart protections, then update doc/python/ guidelines and claude-write-script skill accordingly"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore (Python + Dart + skill) requiring large mental model; explicit compare-approaches nature
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: cdf79a66
  file: ../requirements.md
session_id: 646df1bb-a9bd-4bd4-b452-fe4a45445944
session_account: gmail2
---
# Goal: Audit Python Coding Quality Gaps vs Dart and Close Them

## Objective

We know the existing Python gates (REQ-PROC-051 AC-01 through AC-15) catch a specific set of structural and stylistic problems. But we don't know how far the **uncovered surface** extends — particularly for code-structure properties like single responsibility, function size, coupling/cohesion, naming clarity, and abstraction boundaries.

This exploration enters that unknown: systematically audit what "bad coding" looks like beyond what the gates already measure, score those criteria against the largest Python file, and then close the gaps by updating guidelines and the write-script skill.

## Background

The five Python quality gates (lint, type check, tests, no-hand-rolled-YAML, print-discipline) are binary pass/fail and measurable. They do not constrain function length, cyclomatic complexity, SRP violations, deep nesting, magic values, god functions, or cohesion — dimensions that Dart's AC-02 and Clean Architecture do constrain.

The `orchestrator.py` file (~3300 LOC, TIER A) is the richest target for this audit: it is the oldest and most complex Python file, it has grown organically, and any patterns present there are likely to be reproduced in new Python code because the existing guidelines don't forbid them.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-27_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show cdf79a66:requirements_tasks/process/AI_rules/coding_standards/python_code_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **What does "bad code" mean structurally, beyond style?** — What criteria would a senior engineer use to call a function, class, or module "bad"? Think beyond lint rules: SRP violations, function SLOC, parameter count, deep nesting, coupling, cohesion, magic values, naming clarity, god-function/god-class patterns, missing abstraction boundaries. Can these be scored objectively or only subjectively?

2. **How bad is orchestrator.py really?** — Against the criteria from seed 1, measure the actual state. Where are the worst offenders? How many functions exceed a reasonable SLOC threshold? How many have too many parameters? Is responsibility scattered or concentrated? Are there god functions that do 10 things?

3. **What does Dart already protect against?** — For each criterion identified, trace whether Dart code would be caught: AC-02 SLOC/complexity/parameter limits, Clean Architecture layer enforcement, analysis_options.yaml rules, quality-checker doc/ judgment. What is genuinely protected vs what passes through unchecked?

4. **What guidance is missing from doc/python/?** — Read ALL existing `doc/python/` files (architecture.md, style.md, anti_patterns.md, dependency_injection.md, type_hints.md, testing.md, README.md) and the full REQ-PROC-051 requirements.md before drawing conclusions. What is already covered? What is explicitly absent? Where would a new Python author be left without guidance on a dimension that matters?

5. **Where should the line be?** — Not every Dart rule should be copied to Python. The Dart SLOC ≤ 50 limit was calibrated for Flutter widget build methods. What are the right thresholds for Python scripts in this repo? What is pragmatic vs what is aspirational?

6. **How should the skill be updated?** — The `claude-write-script` skill is the entry point for all Python script creation and modification. Does it currently mandate reading doc/python/ guidelines? If not, how should that mandatory step be inserted without bloating the skill or adding token overhead?

7. **What Dart gaps surface from the comparison?** — After doing the Python side, look back: are there dimensions the Python audit found that Dart's existing guidelines also leave unaddressed? List these as findings for a follow-up task without editing Dart docs.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch — Opus is recommended for this task (`opus_recommended: true`). No mid-session model switching.

**Mandatory reads before any other work** (in parallel):
- ALL files under `doc/python/` (README.md, architecture.md, style.md, anti_patterns.md, dependency_injection.md, type_hints.md, testing.md)
- `requirements_tasks/process/AI_rules/coding_standards/python_code_quality/requirements.md` (REQ-PROC-051, all ACs)
- `requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md` (REQ-PROC-046, especially AC-02 for Dart comparison)
- `.claude/skills/claude-write-script/SKILL.md` (current state before updating)

**Measuring orchestrator.py**: Read the file in sections — do not try to hold 3300 LOC in context at once. Focus on function signatures, function lengths, parameter lists, nesting depth, and responsibility boundaries. Use `wc -l`, `grep -n "^def \|^    def "`, and similar to get structural metrics first before reading bodies.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities — delegate to a spawned `general-purpose` agent with a focused question. Never run WebSearch inline.

**Updating guidelines**: Changes to `doc/python/` are documentation updates, not code changes — no quality gate cycle required. Use Edit tool directly on the relevant files.

**Updating the skill**: Use `claude-modify-skill` for ANY change to `claude-write-script/SKILL.md`. Do not edit the skill file directly.

**Dart gap findings**: Write to `plans_and_protocols/` as a findings document. Do NOT edit any `doc/` Dart files.

## Output

A future implementer reading this task's output should understand:
- Which specific code-quality criteria are unaddressed by existing Python gates, with evidence from orchestrator.py
- Which of those criteria Dart already protects against, and exactly how
- What new guidance was added to `doc/python/` and why each addition was justified by the audit
- That `claude-write-script` now mandates reading Python guidelines before writing
- What follow-up work (if any) is needed on the Dart side

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round (criteria rubric + orchestrator.py findings documented in plans_and_protocols/)
- [x] The synthesis defines the problem space in terms that were not fully known at task creation (gap list beyond existing AC-01–AC-15 coverage)
- [x] `doc/python/` files are updated with missing guidance; each addition is justified by a specific finding from the audit
- [x] `claude-write-script` skill updated (via `claude-modify-skill`) to mandate reading Python guidelines
- [x] Dart gap findings documented in plans_and_protocols/ as input for a follow-up task
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | All previous REQ-PROC-051 tasks are completed |
